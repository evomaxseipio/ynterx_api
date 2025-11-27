import json
import asyncpg
from asyncpg import Pool
from fastapi import APIRouter, Depends, Request, status
from typing import Any

from app.auth.dependencies import DepCurrentUser
from app.auth.jwt_service import jwt_service
from app.auth.schemas import AuthLoginRequest
from app.enums import ErrorCodeEnum

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/jwt-info")
async def get_jwt_info(current_user: DepCurrentUser) -> Any:
    """
    Endpoint de prueba para verificar información JWT.
    """
    return {
        "message": "JWT funcionando correctamente",
        "user_id": current_user,
        "success": True,
        "error_code": ErrorCodeEnum.SUCCESSFULLY_OPERATION.value,
    }


@router.post("/create-test-token")
async def create_test_token() -> Any:
    """
    Endpoint de prueba para crear un token JWT de prueba.
    """
    user_data = {
        "user_id": "22d27ac6-ae45-486b-a3f4-587a05b3932a",
        "person_id": "33e38bd7-bf56-597c-b4g5-698b16c4043b",
        "username": "test_user",
        "email": "test@ynterxal.com",
        "role": {
            "role_name": "admin",
            "permissions": ["read:contracts", "write:contracts", "delete:contracts"]
        }
    }
    
    access_token = jwt_service.create_access_token(user_data)
    refresh_token = jwt_service.create_refresh_token(user_data["user_id"])
    
    return {
        "message": "Token de prueba creado",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": 1800,  # 30 minutos
        "success": True,
        "error_code": ErrorCodeEnum.SUCCESSFULLY_OPERATION.value,
    }


@router.post("/login-db-response")
async def test_login_db_response(request: Request, login_data: AuthLoginRequest) -> Any:
    """
    Endpoint de prueba para ver la respuesta cruda de la base de datos del login.
    Muestra exactamente qué devuelve el stored procedure sp_login_user.
    """
    pool: Pool = request.app.state.db_pool
    
    # Ejecutar el stored procedure
    async with pool.acquire() as conn:
        conn: asyncpg.Connection
        
        result: asyncpg.Record | None = await conn.fetchrow(
            "SELECT sp_login_user($1, $2);",
            login_data.username,
            login_data.password,
        )
    
    if not result:
        return {
            "success": False,
            "message": "No se obtuvo respuesta de la base de datos",
            "raw_result": None,
            "error_code": ErrorCodeEnum.UNDEFINED.value,
        }
    
    # Obtener la respuesta cruda
    raw_db_response = result["sp_login_user"] if result.get("sp_login_user") else None
    
    # Intentar parsear el JSON para mostrarlo formateado
    parsed_response = None
    if raw_db_response:
        try:
            parsed_response = json.loads(raw_db_response)
        except json.JSONDecodeError:
            parsed_response = {"error": "No se pudo parsear como JSON", "raw": raw_db_response}
    
    return {
        "success": True,
        "message": "Respuesta de la base de datos obtenida",
        "raw_db_response": raw_db_response,
        "parsed_db_response": parsed_response,
        "result_keys": list(result.keys()) if result else [],
        "full_result_record": dict(result) if result else None,
        "error_code": ErrorCodeEnum.SUCCESSFULLY_OPERATION.value,
    } 