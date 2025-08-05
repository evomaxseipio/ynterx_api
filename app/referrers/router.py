"""Router for referrer-related endpoints."""

from uuid import UUID
from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Optional

from app.auth.dependencies import DepCurrentUser
from app.referrers.service import ReferrerService
from app.referrers.schemas import ReferrersResponseSchema

router = APIRouter(prefix="/referrers", tags=["referrers"])


@router.get("", response_model=ReferrersResponseSchema)
async def get_referrers(
    _: DepCurrentUser,
    request: Request,
) -> dict:
    """
    Get all referrers.
    
    Returns:
        Dictionary with all referrers data
    """
    async with request.app.state.db_pool.acquire() as connection:
        result = await ReferrerService.get_referrers(connection=connection)
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=404 if result.get("error") == "NO_DATA" else 500,
                detail=result.get("message", "Error al obtener referentes")
            )
        
        return result


@router.get("/{referrer_id}", response_model=ReferrersResponseSchema)
async def get_referrer_by_id(
    referrer_id: UUID,
    _: DepCurrentUser,
    request: Request,
) -> dict:
    """
    Get a specific referrer by ID.
    
    Args:
        referrer_id: UUID of the referrer to retrieve
        
    Returns:
        Dictionary with the specific referrer data
    """
    async with request.app.state.db_pool.acquire() as connection:
        result = await ReferrerService.get_referrers(
            referrer_id=referrer_id,
            connection=connection
        )
        
        if not result.get("success", False):
            error_code = result.get("error")
            if error_code == "REFERRER_NOT_FOUND":
                raise HTTPException(status_code=404, detail=result.get("message"))
            elif error_code == "NO_DATA":
                raise HTTPException(status_code=404, detail=result.get("message"))
            else:
                raise HTTPException(status_code=500, detail=result.get("message"))
        
        return result 