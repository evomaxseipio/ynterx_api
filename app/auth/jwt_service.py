import jwt
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from uuid import UUID

from app.config import settings


class JWTService:
    """Servicio JWT para autenticación en API fintech."""
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        self.refresh_token_expire = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Crear token de acceso JWT."""
        payload = {
            "sub": user_data["user_id"],
            "person_id": user_data.get("person_id"),
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "role": user_data.get("role", {}).get("role_name"),
            "permissions": user_data.get("role", {}).get("permissions", []),
            "aud": "ynterxal-api",
            "iss": "ynterxal-auth",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + self.access_token_expire,
            "jti": str(uuid.uuid4()),  # JWT ID para revocación
            "type": "access"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Crear token de refresco JWT."""
        payload = {
            "sub": user_id,
            "type": "refresh",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + self.refresh_token_expire,
            "jti": str(uuid.uuid4())
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verificar y decodificar token JWT."""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                audience="ynterxal-api",
                issuer="ynterxal-auth"
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expirado")
        except jwt.InvalidTokenError:
            raise ValueError("Token inválido")
        except Exception as e:
            raise ValueError(f"Error al verificar token: {str(e)}")
    
    def get_user_id_from_token(self, token: str) -> str:
        """Obtener user_id del token."""
        payload = self.verify_token(token)
        return payload["sub"]
    
    def is_token_expired(self, token: str) -> bool:
        """Verificar si el token está expirado."""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
            exp = payload.get("exp")
            if not exp:
                return True
            
            exp_datetime = datetime.fromtimestamp(exp)
            return datetime.utcnow() > exp_datetime
        except:
            return True
    
    def get_token_expiration(self, token: str) -> Optional[datetime]:
        """Obtener fecha de expiración del token."""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
            exp = payload.get("exp")
            if exp:
                return datetime.fromtimestamp(exp)
            return None
        except:
            return None


# Instancia global del servicio JWT
jwt_service = JWTService() 