import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import (
    CursorResult,
    Insert,
    MetaData,
    Select,
    Update,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine, AsyncSession, async_sessionmaker

from app.config import settings
from app.constants import DB_NAMING_CONVENTION

log = logging.getLogger(__name__)

DATABASE_URL = str(settings.DATABASE_ASYNC_URL).replace("?sslmode=require", "")

# Configurar opciones de conexión
connect_args = {}
if "sslmode" in str(settings.DATABASE_ASYNC_URL):
    connect_args["ssl"] = True

engine = create_async_engine(
    DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    pool_recycle=settings.DATABASE_POOL_TTL,
    pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
    connect_args=connect_args,
)
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)

# Create async session factory
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def fetch_one(
    select_query: Select | Insert | Update,
    connection: AsyncConnection | None = None,
    commit_after: bool = False,
    compile_query: bool = False,
) -> dict[str, Any] | None:
    if not connection:
        async with engine.connect() as connection:
            cursor = await _execute_query(
                select_query, connection, commit_after, compile_query
            )
            row = cursor.first()
            if not row:
                return None
            return row._asdict() if cursor.rowcount > 0 else None

    cursor = await _execute_query(select_query, connection, commit_after, compile_query)
    row = cursor.first()
    if not row:
        return None
    return row._asdict() if cursor.rowcount > 0 else None


async def fetch_all(
    select_query: Select | Insert | Update,
    connection: AsyncConnection | None = None,
    commit_after: bool = False,
    compile_query: bool = False,
) -> list[dict[str, Any]]:
    if not connection:
        async with engine.connect() as connection:
            cursor = await _execute_query(
                select_query, connection, commit_after, compile_query
            )
            return [r._asdict() for r in cursor.all()]

    cursor = await _execute_query(select_query, connection, commit_after, compile_query)
    return [r._asdict() for r in cursor.all()]


async def execute(
    query: Insert | Update,
    connection: AsyncConnection | None = None,
    commit_after: bool = False,
    compile_query: bool = False,
) -> None:
    if not connection:
        async with engine.connect() as connection:
            await _execute_query(query, connection, commit_after, compile_query)
            return

    await _execute_query(query, connection, commit_after, compile_query)


async def _execute_query(
    query: Select | Insert | Update,
    connection: AsyncConnection,
    commit_after: bool = False,
    compile_query: bool = False,
) -> CursorResult:
    if compile_query:
        # Compilar la consulta SQL usando el dialecto PostgreSQL
        compiled = query.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
        # Convertir a string
        sql = str(compiled)
        log.debug(f"Executing SQL: {sql}")
        result = await connection.execute(sql)
    else:
        result = await connection.execute(query)

    if commit_after:
        await connection.commit()

    return result


async def get_db_connection() -> AsyncConnection:  # type: ignore
    """Obtener una conexión para transacciones usando FastAPI dependency injection."""
    connection = await engine.connect()
    try:
        yield connection  # type: ignore
    finally:
        await connection.close()


@asynccontextmanager
async def use_pool_connection(pool) -> AsyncGenerator[AsyncConnection, None]:
    """Context manager para usar una conexión del pool.

    Ejemplo:
        async with use_pool_connection(request.app.state.db_pool) as connection:
            result = await UserService.get_user(user_id, connection=connection)
    """
    async with pool.acquire() as raw_connection:
        # Crear una conexión SQLAlchemy usando la conexión raw del pool
        connection = AsyncConnection(engine, raw_connection)
        try:
            yield connection
        finally:
            await connection.close()


DepDatabase = Annotated[AsyncConnection, Depends(get_db_connection)]
