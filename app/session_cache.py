from fastapi_cache import FastAPICache

from app.config import settings

SESSION_TTL = settings.AUTH_SESSION_TTL_SECONDS  # segundos


def get_session_key(token: str) -> str:
    return f"auth_session:{token}"


async def create_session(token: str, user_id: str) -> str:
    # Setea en cache: key = session:<token>, value = user_id, TTL
    backend = FastAPICache.get_backend()
    await backend.set(
        get_session_key(token),
        user_id.encode("utf-8"),
        expire=SESSION_TTL,
    )
    return token


async def get_user_by_token(token: str) -> str | None:
    # Obtiene el user_id por token (y extiende el TTL, sliding window)
    key = get_session_key(token)
    backend = FastAPICache.get_backend()
    user_id = await backend.get(key)
    if user_id:
        # Renueva TTL (sliding)
        await backend.set(key, user_id, expire=SESSION_TTL)
        return user_id.decode("utf-8")
    return None


async def remove_session(token: str):
    key = get_session_key(token)
    backend = FastAPICache.get_backend()
    user_id = await backend.get(key)
    if user_id:
        await backend.clear(key=key)
