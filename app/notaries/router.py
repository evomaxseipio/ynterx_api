"""Router for notary-related endpoints."""

from uuid import UUID
from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Optional

from app.auth.dependencies import DepCurrentUser
from app.notaries.service import NotaryService
from app.notaries.schemas import NotariesResponseSchema

router = APIRouter(prefix="/notaries", tags=["notaries"])


@router.get("", response_model=NotariesResponseSchema)
async def get_notaries(
    _: DepCurrentUser,
    request: Request,
) -> dict:
    """
    Get all notaries.
    
    Returns:
        Dictionary with all notaries data
    """
    async with request.app.state.db_pool.acquire() as connection:
        result = await NotaryService.get_notaries(connection=connection)
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=404 if result.get("error") == "NO_DATA" else 500,
                detail=result.get("message", "Error al obtener notarios")
            )
        
        return result


@router.get("/{notary_id}", response_model=NotariesResponseSchema)
async def get_notary_by_id(
    notary_id: UUID,
    _: DepCurrentUser,
    request: Request,
) -> dict:
    """
    Get a specific notary by ID.
    
    Args:
        notary_id: UUID of the notary to retrieve
        
    Returns:
        Dictionary with the specific notary data
    """
    async with request.app.state.db_pool.acquire() as connection:
        result = await NotaryService.get_notaries(
            notary_id=notary_id,
            connection=connection
        )
        
        if not result.get("success", False):
            error_code = result.get("error")
            if error_code == "NOTARY_NOT_FOUND":
                raise HTTPException(status_code=404, detail=result.get("message"))
            elif error_code == "NO_DATA":
                raise HTTPException(status_code=404, detail=result.get("message"))
            else:
                raise HTTPException(status_code=500, detail=result.get("message"))
        
        return result 