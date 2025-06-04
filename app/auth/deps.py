from fastapi import Header

from app.exceptions import NotAuthenticated
from app.session_cache import get_user_by_token


async def get_current_user(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user_id = await get_user_by_token(token)
    if not user_id:
        raise NotAuthenticated()
    return user_id
