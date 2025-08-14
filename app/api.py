from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.person.router import router as person_router, router_referrers as referrer_router
from app.users.router import router as users_router
from app.contracts.router import router as contract_router

from app.email_config.router import router as email_router
from app.company.router import router as company_router
from app.notaries.router import router as notaries_router
from app.witnesses.router import router as witnesses_router
from app.referrers.router import router as referrers_router
# from app.settings.router import router as settings_router

def register_routers(app: FastAPI) -> None:
    """
    Registers all API routers with the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(person_router)
    app.include_router(referrer_router)
    app.include_router(contract_router)

    app.include_router(email_router)
    app.include_router(company_router)
    app.include_router(notaries_router)
    app.include_router(witnesses_router)
    app.include_router(referrers_router)
    # app.include_router(settings_router)
    # Add other routers here as needed
    # e.g., app.include_router(another_router)
