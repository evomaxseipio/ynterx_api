import logging
from uuid import UUID

from fastapi import APIRouter, Request, status

from app.auth.dependencies import DepCurrentUser
from app.database import DepDatabase
from app.exceptions import BadRequest, NotFound
from app.users.schemas import UserCreate, UserResponse, UserUpdate
from app.users.service import UserService

log = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    request: Request,
    db: DepDatabase,
    current_user: DepCurrentUser,
) -> dict:
    # Check if username already exists
    async with request.app.state.db_pool.acquire() as connection:
        existing_user = await connection.fetchrow(
            "SELECT * FROM users WHERE username = $1",
            user_data.username,
        )
    if existing_user:
        raise BadRequest("Username already registered")

    return await UserService.create_user(
        user_data,
        created_by=current_user,
        connection=db,
    )


@router.get("/", response_model=list[UserResponse])
async def get_users(
    _: DepCurrentUser,
    request: Request,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    async with request.app.state.db_pool.acquire() as connection:
        query = """
            SELECT
                users.*
            FROM users
            OFFSET $1 LIMIT $2
        """
        users = await connection.fetch(query, skip, limit)
        return [dict(user) for user in users]


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    request: Request,
    current_user: DepCurrentUser,
) -> dict:
    query = """
        SELECT
            u.*
        FROM users u
        WHERE u.user_id = $1 AND u.is_active = true
    """

    async with request.app.state.db_pool.acquire() as connection:
        user = await connection.fetchrow(query, current_user)

    if not user:
        raise NotFound("User not found")

    return dict(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    _: DepCurrentUser,
    user_id: UUID,
    request: Request,
) -> dict:
    query = "SELECT * FROM users WHERE user_id = $1"
    # Usar el pool para lectura para priorizar la velocidad
    async with request.app.state.db_pool.acquire() as connection:
        user = await connection.fetchrow(query, user_id)
    if not user:
        raise NotFound("User not found")
    return dict(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    request: Request,
    db: DepDatabase,  # Usar inyección de dependencias para transacciones
    current_user: DepCurrentUser,
) -> dict:
    try:
        async with request.app.state.db_pool.acquire() as connection:
            existing_user = await connection.fetchrow(
                "SELECT * FROM users WHERE user_id = $1",
                user_id,
            )
            if not existing_user:
                raise NotFound("User not found")

            # If updating username, check it's not taken
            if user_data.username and user_data.username != existing_user["username"]:
                username_exists = await connection.fetchrow(
                    "SELECT * FROM users WHERE username = $1",
                    user_data.username,
                )
                if username_exists:
                    raise BadRequest("Username already taken")

        # Usar la conexión de transacción para la actualización
        updated_user = await UserService.update_user(
            user_id,
            user_data,
            updated_by=current_user,
            connection=db,  # Usar la conexión transaccional
        )
        return updated_user
    except Exception as e:
        # Log any unexpected errors
        log.error(f"Error updating user {user_id}: {e!s}")
        raise BadRequest(f"Error updating user {user_id}: {e!s}") from e


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: DepDatabase,
    current_user: DepCurrentUser,
) -> None:
    user = await UserService.get_user(user_id, connection=db)
    if not user:
        raise NotFound("User not found")

    success = await UserService.delete_user(user_id, connection=db)
    if not success:
        raise BadRequest("Could not delete user")
