from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.users.router import router as users_router


def register_routers(app: FastAPI) -> None:
    """
    Registers all API routers with the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    app.include_router(auth_router)
    app.include_router(users_router)
    # Add other routers here as needed
    # e.g., app.include_router(another_router)
