from uuid import UUID

from app.config import settings
from app.session_cache import set_user_by_token

# Token fijo para desarrollo local
LOCAL_DEV_TOKEN = "local-dev-token"
# LOCAL_DEV_USER_ID = UUID("00000000-0000-0000-0000-000000000001")
LOCAL_DEV_USER_ID = UUID("22d27ac6-ae45-486b-a3f4-587a05b3932a")

async def setup_local_dev_auth():
    """Configura la autenticación para desarrollo local."""
    if settings.ENVIRONMENT.is_debug:
        # Almacena el token de desarrollo local en la caché
        await set_user_by_token(LOCAL_DEV_TOKEN, str(LOCAL_DEV_USER_ID))
