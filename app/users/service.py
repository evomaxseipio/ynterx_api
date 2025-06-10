from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, select, text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.database import execute, fetch_all, fetch_one
from app.users.models import users
from app.users.schemas import UserCreate, UserUpdate


class UserService:
    @staticmethod
    async def create_user(
        user_data: UserCreate,
        created_by: str,
        connection: AsyncConnection,
    ) -> dict:
        """Create a new user."""

        # Prepare parameters with named parameters
        params = {
            "p_person_id": user_data.person_id,
            "p_username": user_data.username,
            "p_email": user_data.email,
            "p_password": user_data.password,
            "p_user_role_id": user_data.user_role_id,
            "p_language": user_data.language,
            "p_preferences": user_data.preferences.model_dump_json(
                exclude_none=True, exclude_defaults=True
            ),
            "p_created_by": created_by,
        }

        stmt = text(
            """
            SELECT create_user(
                :p_person_id,
                :p_username,
                :p_email,
                :p_password,
                :p_user_role_id,
                :p_language,
                :p_preferences,
                :p_created_by
            )
            """
        )

        result = await connection.execute(stmt, params)
        user_data = result.scalar_one()
        await connection.commit()

        return user_data

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
        updated_by: UUID,
        connection: AsyncConnection | None = None,
    ) -> dict | None:
        """Update a user."""
        update_data = user_data.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_by"] = updated_by
            update_data["updated_at"] = datetime.utcnow()

            query = (
                users.update()
                .where(users.c.user_id == user_id)
                .values(**update_data)
                .returning(users)
            )
            result = await fetch_one(query, connection=connection, commit_after=True)
            return result
        return None

    @staticmethod
    async def delete_user(
        user_id: UUID,
        connection: AsyncConnection | None = None,
    ) -> bool:
        """Delete a user (soft delete by setting is_active to False)."""
        query = (
            users.update()
            .where(users.c.user_id == user_id)
            .values(is_active=False)
        )
        await execute(query, connection=connection, commit_after=True)
        return True
