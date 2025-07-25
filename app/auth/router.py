import json
import logging
from typing import Any

import asyncpg
from asyncpg import Pool
from fastapi import APIRouter, Header, Request, status

from app.email import send_email
from app.enums import ErrorCodeEnum
from app.exceptions import BadRequest, GenericHTTPException
from app.session_cache import create_session, remove_session
from app.utils.alphanum import generate_random_alphanum

from .dependencies import DepCurrentUser
from .models import LoginUserQueryResult
from .schemas import (
    AuthLoginRequest,
    AuthLoginResponse,
    PasswordChangeRequest,
    PasswordRecoveryRequest,
)

log = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=AuthLoginResponse,
    status_code=status.HTTP_200_OK,
)
async def login(request: Request, login_data: AuthLoginRequest) -> Any:
    raise_error = BadRequest("Error inesperado al iniciar sesión")

    pool: Pool = request.app.state.db_pool
    # Take a connection from the pool
    async with pool.acquire() as conn:
        conn: asyncpg.Connection

        result: asyncpg.Record | None = await conn.fetchrow(
            "SELECT sp_login_user($1, $2);",
            login_data.username,
            login_data.password,
        )

    if not result or not result[0] or not result["sp_login_user"]:
        log.error("Unable to get the result of the login query")
        raise raise_error

    user_query_result = LoginUserQueryResult.from_json(result["sp_login_user"])
    if (
        user_query_result.success
        and user_query_result.error_code is ErrorCodeEnum.SUCCESSFULLY_OPERATION
    ):
        session = user_query_result.session
        user_data = user_query_result.user

        if not session or not session.session_token:
            log.error("Session data is missing or invalid in the login response")
            raise raise_error

        user = user_query_result.get_user()
        if not user or not user.user_id:
            log.error("User data is missing or invalid in the login response")
            raise raise_error

        # Create a session in the cache
        await create_session(session.session_token, user.user_id)

        return AuthLoginResponse.model_validate(
            {
                "error_code": user_query_result.error_code.value,
                "message": user_query_result.message,
                "success": user_query_result.success,
                "data": {
                    "access_token": session.session_token,
                    "token_type": "Bearer",
                    "user": user_data,
                },
            },
            from_attributes=True,
        )

    raise GenericHTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        error_code=user_query_result.error_code,
        message=user_query_result.message,
        success=user_query_result.success,
    )


@router.post("/logout")
async def logout(authorization: str = Header(...)) -> Any:
    """
    Endpoint to log out the current user.
    This endpoint should invalidate the user's session.
    """
    token = authorization.replace("Bearer ", "")
    await remove_session(token)
    return {
        "message": "Logout successful",
        "success": True,
        "error_code": ErrorCodeEnum.SUCCESSFULLY_OPERATION.value,
    }


@router.post("/recover-password")
async def recover_password(
    request: Request, recovery_data: PasswordRecoveryRequest
) -> Any:
    """
    Endpoint to request a password recovery.
    This endpoint validates the email, generates a temporary password and sends it via email.
    """
    pool: Pool = request.app.state.db_pool

    # Check if user exists
    async with pool.acquire() as conn:
        conn: asyncpg.Connection
        user = await conn.fetchrow(
            "SELECT user_id, preferences FROM users WHERE email = $1 AND is_active = true;",
            recovery_data.email,
        )

    if not user:
        raise GenericHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCodeEnum.NOT_FOUND,
            message="El correo no existe",
            success=False,
        )

    # Generate temporary password
    temp_password = generate_random_alphanum(12)

    # Update user's password and preferences
    json_preferences = user["preferences"] or "{}"
    preferences = json.loads(json_preferences)
    preferences["temp_password"] = "true"
    json_preferences = json.dumps(preferences)

    async with pool.acquire() as conn:
        conn: asyncpg.Connection
        await conn.execute(
            """
            UPDATE users
            SET password_hash = crypt($1, gen_salt('bf', 12)),
                password_salt = encode(gen_random_bytes(16), 'hex'),
                preferences = $2
            WHERE user_id = $3;
            """,
            temp_password,
            json_preferences,
            user["user_id"],
        )

    # Send email with temporary password
    await send_email(
        to_email=recovery_data.email,
        subject="Recuperación de Contraseña",
        body=(
            f"Tu contraseña temporal es: {temp_password}\n\n"
            "Por favor, cambia tu contraseña después de iniciar sesión.\n\n"
            "Gracias por usar ynterxal"
        ),
    )

    return {
        "message": "Si el correo existe, recibirás instrucciones para recuperar tu contraseña",
        "success": True,
        "error_code": ErrorCodeEnum.SUCCESSFULLY_OPERATION.value,
    }


@router.post("/change-password")
async def change_password(
    request: Request,
    password_data: PasswordChangeRequest,
    current_user: DepCurrentUser,
) -> Any:
    raise_error = BadRequest("Error inesperado al cambiar la contraseña")

    pool: Pool = request.app.state.db_pool
    # Take a connection from the pool
    async with pool.acquire() as conn:
        conn: asyncpg.Connection

        async with conn.transaction():
            result: asyncpg.Record | None = await conn.fetchrow(
                "SELECT sp_change_password($1, $2, $3);",
                current_user,
                password_data.current_password,
                password_data.new_password,
            )

    if not result or not result[0] or not result["sp_change_password"]:
        log.error("Unable to get the result of the password change query")
        raise raise_error

    data = json.loads(result["sp_change_password"] or "{}")
    if "success" not in data or "error_code" not in data or "email" not in data:
        log.error("Data from password change query is invalid")
        raise raise_error

    error_code = (
        ErrorCodeEnum(data["error_code"])
        if data.get("error_code", None) and data["error_code"] in ErrorCodeEnum
        else ErrorCodeEnum.UNDEFINED
    )

    if (
        data.get("success", False)
        and error_code is ErrorCodeEnum.SUCCESSFULLY_OPERATION
    ):
        await send_email(
            to_email=data.get("email"),
            subject="Cambio de Contraseña",
            body=("Cambio de Contraseña exitoso\n\n" "Gracias por usar ynterxal"),
        )
        return {
            "message": "Contraseña cambiada exitosamente",
            "success": True,
            "error_code": ErrorCodeEnum.SUCCESSFULLY_OPERATION.value,
        }

    raise GenericHTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        error_code=error_code,
        message=data.get("message", ""),
        success=data.get("success", False),
    )
