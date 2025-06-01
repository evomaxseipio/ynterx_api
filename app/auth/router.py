from typing import Any

import asyncpg
from asyncpg import Pool
from fastapi import APIRouter, HTTPException, Request, status

from .models import ErrorCodeEnum, LoginUserQueryResult
from .schemas import AuthLoginRequest, AuthLoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=AuthLoginResponse,
    status_code=status.HTTP_200_OK,
)
async def login(request: Request, login_data: AuthLoginRequest) -> Any:
    raise_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
    )

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
        raise raise_error

    user_query_result = LoginUserQueryResult.from_json(result["sp_login_user"])
    if (
        user_query_result.success
        and user_query_result.error_code is ErrorCodeEnum.SUCCESSFULLY_OPERATION
        and user_query_result.user
        and user_query_result.session
    ):
        session = user_query_result.session
        user = user_query_result.user

        return {
            "access_token": session.session_token,
            "token_type": "bearer",
            "user": user,
        }

    raise raise_error


@router.post("/logout")
async def logout() -> Any:
    # Lógica para cerrar sesión (opcional, depende de tu implementación)
    return {"msg": "Successfully logged out"}
