from pydantic import BaseModel, Field
from typing import Optional, List


class TokenResponse(BaseModel):
    """Respuesta de token JWT."""
    access_token: str = Field(..., description="Token de acceso JWT")
    refresh_token: str = Field(..., description="Token de refresco JWT")
    token_type: str = Field(default="Bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")
    user: dict = Field(..., description="Datos del usuario")


class RefreshTokenRequest(BaseModel):
    """Request para refrescar token."""
    refresh_token: str = Field(..., description="Token de refresco")


class RefreshTokenResponse(BaseModel):
    """Respuesta de refresh token."""
    access_token: str = Field(..., description="Nuevo token de acceso")
    token_type: str = Field(default="Bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")


class TokenPayload(BaseModel):
    """Payload del token JWT."""
    sub: str = Field(..., description="ID del usuario")
    person_id: Optional[str] = Field(None, description="ID de la persona")
    username: Optional[str] = Field(None, description="Nombre de usuario")
    email: Optional[str] = Field(None, description="Email del usuario")
    role: Optional[str] = Field(None, description="Rol del usuario")
    permissions: Optional[List[str]] = Field(None, description="Permisos del usuario")
    aud: str = Field(..., description="Audiencia")
    iss: str = Field(..., description="Emisor")
    iat: int = Field(..., description="Timestamp de emisión")
    exp: int = Field(..., description="Timestamp de expiración")
    jti: str = Field(..., description="JWT ID")
    type: str = Field(..., description="Tipo de token")


class TokenRevokeRequest(BaseModel):
    """Request para revocar token."""
    token: str = Field(..., description="Token a revocar")


class TokenRevokeResponse(BaseModel):
    """Respuesta de revocación de token."""
    message: str = Field(..., description="Mensaje de confirmación")
    success: bool = Field(..., description="Estado de la operación") 