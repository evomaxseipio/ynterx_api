from fastapi import APIRouter, Depends, status
from typing import Any

from app.auth.dependencies import DepCurrentUser
from app.auth.jwt_service import jwt_service
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