import json
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.pool import Pool

from app.database import execute, fetch_one
from app.users.models import users
from app.users.schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncConnection, pool: Pool):
        self.db = db
        self.pool = pool

    async def create_user(self, user_data: UserCreate, created_by: str) -> dict:
        """Create a new user."""

        # Validate username and person_id
        async with self.pool.acquire() as conn:
            if await self._exists_user_by_username(user_data.username, conn):
                raise Exception("User already registered")
            if await self._exists_user_by_email(user_data.email, conn):
                raise Exception("Email already registered")
            if not await self._exists_person_by_person_id(user_data.person_id, conn):
                raise Exception("Person not found")

            p_created_by = await self._get_person_id_by_current_user(created_by, conn)
            if not p_created_by:
                raise Exception("Current user not found")

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
            "p_created_by": p_created_by,
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

        result = await self.db.execute(stmt, params)
        user_data = result.scalar_one()
        await self.db.commit()

        return user_data

    async def get_user(self, user_id: UUID) -> dict | None:
        """Get a user by ID."""
        query = """
            SELECT
                json_build_object(
                    'user_id', u.user_id,
                    'username', u.username,
                    'email', u.email,
                    'language', u.language,
                    'is_active', u.is_active,
                    'created_at', u.created_at,
                    'updated_at', u.updated_at,
                    'created_by', u.created_by,
                    'updated_by', u.updated_by,
                    'user_role_id', u.user_role_id,
                    'person', row_to_json(p),
                    'role', row_to_json(ur)
                ) as user
            FROM users u
            JOIN person p ON u.person_id = p.person_id
            JOIN user_roles ur ON u.user_role_id = ur.user_role_id
            WHERE u.user_id = $1
        """

        async with self.pool.acquire() as connection:
            result = await connection.fetchrow(query, user_id)
        return json.loads(result['user']) if result and result['user'] else None

    async def get_user_by_username(self, username: str) -> dict | None:
        """Get a user by username."""
        query = """
            SELECT
                json_build_object(
                    'user_id', u.user_id,
                    'username', u.username,
                    'email', u.email,
                    'language', u.language,
                    'is_active', u.is_active,
                    'created_at', u.created_at,
                    'updated_at', u.updated_at,
                    'created_by', u.created_by,
                    'updated_by', u.updated_by,
                    'user_role_id', u.user_role_id,
                    'person', row_to_json(p),
                    'role', row_to_json(ur)
                ) as user
            FROM users u
            JOIN person p ON u.person_id = p.person_id
            JOIN user_roles ur ON u.user_role_id = ur.user_role_id
            WHERE u.username = $1 AND u.is_active = true
        """

        async with self.pool.acquire() as connection:
            result = await connection.fetchrow(query, username)
        return json.loads(result['user']) if result and result['user'] else None

    async def get_users(self, skip: int = 0, limit: int = 100) -> dict:
        """Get a list of users with pagination."""
        async with self.pool.acquire() as connection:
            result = await connection.fetchrow("SELECT sp_get_all_users() LIMIT 1")
            if not result or not result[0] or not result["sp_get_all_users"]:
                raise Exception("No users found")
            users = result["sp_get_all_users"]
            return json.loads(users)

    async def update_user(self, user_id: UUID, user_data: UserUpdate, updated_by: UUID) -> dict | None:
        """Update a user."""
        async with self.pool.acquire() as connection:
            existing_user = await connection.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
            if not existing_user:
                return None

            # Si se está actualizando la contraseña, verificar permisos
            if user_data.new_password is not None and len(user_data.new_password.strip()) > 0:
                # Permitir si:
                # 1. El usuario está cambiando su propia contraseña, O
                # 2. El usuario es administrador
                is_self_update = (str(user_id) == str(updated_by))
                is_admin = await self._is_admin(updated_by)

                if not is_self_update and not is_admin:
                    raise Exception("Solo puedes cambiar tu propia contraseña o debes ser administrador para cambiar la de otros usuarios")

                # Actualizar contraseña
                await self._update_password(user_id, user_data.new_password)

            # If updating username, check it's not taken
            if user_data.username and user_data.username != existing_user["username"]:
                if await self._exists_user_by_username(user_data.username, connection):
                    raise Exception("Username already exists")

            p_updated_by = await self._get_person_id_by_current_user(updated_by, connection)
            if not p_updated_by:
                raise Exception("Current user not found")

        # Actualizar otros campos (excluyendo new_password que ya se manejó arriba)
        update_data = user_data.model_dump(exclude_unset=True, exclude={'new_password'})

        # Siempre actualizar updated_by y updated_at si hay algún cambio
        if update_data or user_data.new_password:
            update_data["updated_by"] = p_updated_by
            update_data["updated_at"] = datetime.utcnow()

            if update_data:
                query = (
                    users.update()
                    .where(users.c.user_id == user_id)
                    .values(**update_data)
                    .returning(users)
                )
                await fetch_one(query, connection=self.db, commit_after=True)

        # Retornar el usuario completo con relaciones después de la actualización
        return await self.get_user(user_id)

    async def delete_user(self, user_id: UUID) -> bool | None:
        """Delete a user (soft delete by setting is_active to False)."""
        async with self.pool.acquire() as connection:
            if not await self._exists_user_by_user_id(user_id, connection):
                return None

        query = users.update().where(users.c.user_id == user_id).values(is_active=False)
        await execute(query, connection=self.db, commit_after=True)

        return True

    async def _is_admin(self, user_id: UUID) -> bool:
        """Verificar si el usuario es administrador"""
        async with self.pool.acquire() as connection:
            result = await connection.fetchrow(
                """
                SELECT ur.role_name 
                FROM users u
                JOIN user_roles ur ON u.user_role_id = ur.user_role_id
                WHERE u.user_id = $1 AND u.is_active = true
                """,
                user_id
            )
            return result and result["role_name"] == "Administrador"

    async def _update_password(self, user_id: UUID, new_password: str) -> None:
        """Actualizar contraseña del usuario"""
        async with self.pool.acquire() as connection:
            await connection.execute(
                """
                UPDATE users
                SET password_hash = crypt($1, gen_salt('bf', 12)),
                    password_salt = encode(gen_random_bytes(16), 'hex'),
                    updated_at = NOW()
                WHERE user_id = $2
                """,
                new_password,
                user_id
            )

    async def _exists_user_by_username(self, username: str, connection) -> bool:
        return (
            await connection.fetchrow(
                "SELECT EXISTS (SELECT 1 FROM users WHERE username = $1)",
                username,
            )
        )[0]

    async def _exists_user_by_email(self, email: str, connection) -> bool:
        return (
            await connection.fetchrow(
                "SELECT EXISTS (SELECT 1 FROM users WHERE email = $1)",
                email,
            )
        )[0]

    async def _exists_user_by_user_id(self, user_id: UUID, connection) -> bool:
        return (
            await connection.fetchrow(
                "SELECT EXISTS (SELECT 1 FROM users WHERE user_id = $1)",
                user_id,
            )
        )[0]

    async def _exists_person_by_person_id(self, person_id: UUID, connection) -> bool:
        return (
            await connection.fetchrow(
                "SELECT EXISTS (SELECT 1 FROM person WHERE person_id = $1)",
                person_id,
            )
        )[0]

    async def _get_person_id_by_current_user(
        self, current_user: UUID, connection
    ) -> UUID | None:
        return (
            await connection.fetchrow(
                "SELECT person_id FROM users WHERE user_id = $1",
                current_user,
            )
        )["person_id"]
