from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncConnection

from app.database import execute, fetch_all, fetch_one
from app.person.service import PersonService
from app.users.models import users
from app.users.schemas import UserCreate, UserUpdate
from app.utils.security import get_password_hash


class UserService:
    @staticmethod
    async def create_user(
        user_data: UserCreate,
        created_by: str | None = None,
        connection: AsyncConnection | None = None,
    ) -> dict:
        """Create a new user."""
        # Verify person exists
        person = await PersonService.get_person(
            person_id=user_data.person_id,
            connection=connection,
        )
        if not person:
            raise ValueError(f"Person with ID {user_data.person_id} not found")

        # Create the user
        password_hash, password_salt = get_password_hash(user_data.password)

        user_query = users.insert().values(
            person_id=user_data.person_id,
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash,
            password_salt=password_salt,
            user_role_id=user_data.user_role_id,
            language=user_data.language,
            is_active=user_data.is_active,
            created_by=created_by,
        )

        user_result = await execute(user_query, connection=connection, commit_after=True)
        return {**user_result, "person_id": user_data.person_id}

    @staticmethod
    async def get_user(
        user_id: UUID,
        connection: AsyncConnection | None = None,
    ) -> dict | None:
        """Get a user by ID."""
        query = select(users).where(users.c.user_id == user_id)
        return await fetch_one(query, connection=connection, compile_query=True)

    @staticmethod
    async def get_user_by_username(
        username: str,
        connection: AsyncConnection | None = None,
    ) -> dict | None:
        """Get a user by username."""
        query = select(users).where(users.c.username == username)
        return await fetch_one(query, connection=connection)

    @staticmethod
    async def get_users(
        skip: int = 0,
        limit: int = 100,
        connection: AsyncConnection | None = None,
    ) -> list[dict]:
        """Get a list of users with pagination."""
        query = select(users).offset(skip).limit(limit)
        return await fetch_all(query, connection=connection)

    @staticmethod
    async def update_user(
        user_id: UUID,
        user_data: UserUpdate,
        updated_by: UUID | None = None,
        connection: AsyncConnection | None = None,
    ) -> dict | None:
        """Update a user."""
        update_data = user_data.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_by"] = updated_by
            update_data["updated_at"] = datetime.utcnow()

            query = (
                users.update().where(users.c.user_id == user_id).values(**update_data)
            )
            await execute(query, connection=connection, commit_after=True)

        return await UserService.get_user(user_id, connection=connection)

    @staticmethod
    async def delete_user(
        user_id: UUID,
        connection: AsyncConnection | None = None,
    ) -> bool:
        """Delete a user (soft delete by setting is_active to False)."""
        query = (
            users.update()
            .where(and_(users.c.user_id == user_id, users.c.is_active))
            .values(is_active=False)
        )
        result = await execute(query, connection=connection, commit_after=True)
        return bool(result)
