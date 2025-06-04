from fastapi import APIRouter, Depends

from app.auth.deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", summary="Get current user information")
async def get_current_user_async(user_id: str = Depends(get_current_user)):
    """
    Endpoint to retrieve the current user's information.
    This endpoint should be protected and require authentication.
    """
    # Placeholder for actual user retrieval logic
    return {"user": user_id}
