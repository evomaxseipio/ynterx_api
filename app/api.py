from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.person.router import router as person_router
from app.users.router import router as users_router
from app.contracts.router import router as contracts_router


def register_routers(app: FastAPI) -> None:
    """
    Registers all API routers with the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(person_router)
    app.include_router(contracts_router)

    # Add other routers here as needed
    # e.g., app.include_router(another_router)
