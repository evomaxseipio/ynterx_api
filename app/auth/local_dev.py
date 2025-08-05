import json
from pathlib import Path
from uuid import UUID

from app.config import settings
from app.session_cache import set_user_by_token

# Archivo para persistir el token de desarrollo
DEV_TOKEN_FILE = Path(__file__).parent.parent / "dev_token.json"
LOCAL_DEV_TOKEN = "local-dev-token"
# LOCAL_DEV_USER_ID = UUID("00000000-0000-0000-0000-000000000001")
LOCAL_DEV_USER_ID = UUID("22d27ac6-ae45-486b-a3f4-587a05b3932a")

async def setup_local_dev_auth():
    """Configura la autenticación para desarrollo local persistente."""
    if settings.ENVIRONMENT.is_debug:
        # Si existe el archivo, úsalo; si no, créalo
        if DEV_TOKEN_FILE.exists():
            with open(DEV_TOKEN_FILE, "r") as f:
                data = json.load(f)
                token = data.get("token", LOCAL_DEV_TOKEN)
                user_id = data.get("user_id", str(LOCAL_DEV_USER_ID))
        else:
            token = LOCAL_DEV_TOKEN
            user_id = str(LOCAL_DEV_USER_ID)
            with open(DEV_TOKEN_FILE, "w") as f:
                json.dump({"token": token, "user_id": user_id}, f)
        # Registra el token en la caché
        await set_user_by_token(token, user_id)
