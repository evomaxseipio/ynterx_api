from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.local_dev import LOCAL_DEV_TOKEN
from app.config import settings
from app.exceptions import NotAuthenticated
from app.session_cache import get_user_by_token


# Esquema de seguridad HTTP Bearer que permite auto-login en ambiente local
class LocalDevHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request):
        if settings.ENVIRONMENT.is_debug:
            # En ambiente local, si no hay token, usar el token de desarrollo
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return HTTPAuthorizationCredentials(
                    scheme="Bearer", credentials=LOCAL_DEV_TOKEN
                )
        return await super().__call__(request)


# Esquema de seguridad HTTP Bearer
security = LocalDevHTTPBearer()

# Dependencia de seguridad
dep_security = Annotated[HTTPAuthorizationCredentials, Depends(security)]


async def get_current_user(credentials: dep_security):
    """Obtiene el usuario actual a partir del token JWT."""
    token = credentials.credentials
    user_id = await get_user_by_token(token)
    if not user_id:
        raise NotAuthenticated()
    return user_id


# Dependencia tipada para el usuario actual
DepCurrentUserFn = Depends(get_current_user, use_cache=True)
DepCurrentUser = Annotated[str, DepCurrentUserFn]
