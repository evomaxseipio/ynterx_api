from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.auth.jwt_service import jwt_service
from app.exceptions import GenericHTTPException
from app.enums import ErrorCodeEnum


async def token_refresh_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware para manejar automáticamente el refresh de tokens expirados.
    """
    # Solo aplicar a endpoints protegidos (excluir auth endpoints)
    if request.url.path.startswith("/auth/"):
        return await call_next(request)
    
    # Verificar si hay token en headers
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return await call_next(request)
    
    token = auth_header.replace("Bearer ", "")
    
    try:
        # Verificar si el token está expirado
        if jwt_service.is_token_expired(token):
            # Token expirado, retornar 401 con indicador de refresh
            return JSONResponse(
                status_code=401,
                content={
                    "error_code": "TOKEN_EXPIRED",
                    "message": "Token expirado. Use refresh token para obtener nuevo access token.",
                    "success": False,
                    "requires_refresh": True
                }
            )
    except Exception:
        # Error al verificar token, continuar normalmente
        pass
    
    return await call_next(request) 