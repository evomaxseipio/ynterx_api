import json
import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from app.auth.dependencies import DepCurrentUser, DepCurrentUserFn
from app.database import DepDatabase
from app.enums import ErrorCodeEnum
from app.exceptions import BadRequest, NotFound

from .schemas import (
    UserCreate,
    UserListResponse,
    UserRead,
    UserUpdate,
)
from .service import UserService

log = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"], dependencies=[DepCurrentUserFn])


###
### Routes - Roles
###


@router.get("/roles")
async def get_roles(request: Request):
    async with request.app.state.db_pool.acquire() as connection:
        query = "SELECT * FROM user_roles"
        roles = await connection.fetch(query)
        return {
            "data": [
                {**dict(role), "permissions": json.loads(role.get("permissions", "[]"))}
                for role in roles
            ],
            "success": True,
            "message": "Roles retrieved successfully",
            "error_code": ErrorCodeEnum.SUCCESSFULLY_OPERATION.value,
        }


###
### Routes - Users
###


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    request: Request,
    db: DepDatabase,
    current_user_uuid: DepCurrentUser,
):
    try:
        service = UserService(db, request.app.state.db_pool)
        result = await service.create_user(user_data, created_by=current_user_uuid)
        return result
    except Exception as e:
        log.error(f"Error creating user: {e}")
        raise BadRequest(str(e)) from e


@router.get("/", response_model=UserListResponse)
async def get_users(request: Request, db: DepDatabase):
    service = UserService(db, request.app.state.db_pool)
    return JSONResponse(content=await service.get_users())


@router.get("/me", response_model=UserRead)
async def get_current_user_info(
    request: Request,
    db: DepDatabase,
    current_user_uuid: DepCurrentUser,
):
    service = UserService(db, request.app.state.db_pool)
    user = await service.get_user(current_user_uuid)

    if not user:
        raise NotFound("User not found")

    return {
        "data": user,
        "success": True,
        "message": "User retrieved successfully",
        "error_code": ErrorCodeEnum.SUCCESSFULLY_OPERATION.value,
    }


@router.get("/{user_id}")
async def get_user(user_id: UUID, request: Request, db: DepDatabase):
    try:
        service = UserService(db, request.app.state.db_pool)
        user = await service.get_user(user_id)
        
        if not user:
            return JSONResponse(content={
                "data": None,
                "success": False,
                "message": "User not found",
                "error_code": ErrorCodeEnum.NOT_FOUND.value,
            })
        
        # Determinar el mensaje basado en el estado del usuario
        if user.get("is_active", True):
            message = "User retrieved successfully"
        else:
            message = "User retrieved successfully (inactive)"
        
        # Respuesta exitosa con la misma estructura
        return JSONResponse(content={
            "data": user,
            "success": True,
            "message": message,
            "error_code": ErrorCodeEnum.SUCCESSFULLY_OPERATION.value,
        })
        
    except Exception as e:
        log.error(f"Error retrieving user {user_id}: {str(e)}")
        return JSONResponse(content={
            "data": None,
            "success": False,
            "message": f"Error retrieving user: {str(e)}",
            "error_code": ErrorCodeEnum.INTERNAL_SERVER_ERROR.value,
        })


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    request: Request,
    db: DepDatabase,  # Usar inyección de dependencias para transacciones
    current_user_uuid: DepCurrentUser,
):
    try:
        service = UserService(db, request.app.state.db_pool)
        updated_user = await service.update_user(
            user_id, user_data, updated_by=current_user_uuid
        )
        if not updated_user:
            raise NotFound("User not found")

        return {
            "data": updated_user,
            "success": True,
            "message": "User updated successfully",
            "error_code": ErrorCodeEnum.SUCCESSFULLY_OPERATION.value,
        }
    except Exception as e:
        error_message = str(e)
        log.error(f"Error updating user {user_id}: {error_message}")
        raise BadRequest(f"Error updating user {user_id}: {error_message}") from e


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: UUID,
    request: Request,
    db: DepDatabase,
    current_user_uuid: DepCurrentUser,
) -> dict:
    log.info(f"Deleting user {user_id} by {current_user_uuid}")

    service = UserService(db, request.app.state.db_pool)
    success = await service.delete_user(user_id)
    
    if success is None:
        raise NotFound("User not found")
    if not success:
        raise BadRequest("Could not delete user")
    
    return {
        "data": {
            "user_id": str(user_id),
            "deleted_at": datetime.utcnow().isoformat(),
            "deleted_by": str(current_user_uuid)
        },
        "success": True,
        "message": "User deleted successfully",
        "error_code": ErrorCodeEnum.SUCCESSFULLY_OPERATION.value,
    }
