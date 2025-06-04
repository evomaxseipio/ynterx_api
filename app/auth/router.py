import logging
from typing import Any

import asyncpg
from asyncpg import Pool
from fastapi import APIRouter, Header, Request, status

from app.exceptions import BadRequest, GenericHTTPException
from app.session_cache import create_session, remove_session

from .models import ErrorCodeEnum, LoginUserQueryResult
from .schemas import AuthLoginRequest, AuthLoginResponse

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
    return {"message": "Logout successful", "success": True}
