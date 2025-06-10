import json
import logging
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
        return await service.create_user(user_data, created_by=current_user_uuid)
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

    print(user)

    return {
        "data": user,
        "success": True,
        "message": "User retrieved successfully",
        "error_code": ErrorCodeEnum.SUCCESSFULLY_OPERATION.value,
    }


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: UUID, request: Request, db: DepDatabase):
    service = UserService(db, request.app.state.db_pool)
    user = await service.get_user(user_id)
    if not user:
        raise NotFound("User not found")
    return {
        "data": user,
        "success": True,
        "message": "User retrieved successfully",
        "error_code": ErrorCodeEnum.SUCCESSFULLY_OPERATION.value,
    }


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
        # Log any unexpected errors
        log.error(f"Error updating user {user_id}: {e!s}")
        raise BadRequest(f"Error updating user {user_id}: {e!s}") from e


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    request: Request,
    db: DepDatabase,
    current_user_uuid: DepCurrentUser,
) -> None:
    log.info(f"Deleting user {user_id} by {current_user_uuid}")

    service = UserService(db, request.app.state.db_pool)
    success = await service.delete_user(user_id)
    if success is None:
        raise NotFound("User not found")
    if not success:
        raise BadRequest("Could not delete user")
