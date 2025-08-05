"""Router for witness-related endpoints."""

from uuid import UUID
from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Optional

from app.auth.dependencies import DepCurrentUser
from app.witnesses.service import WitnessService
from app.witnesses.schemas import WitnessesResponseSchema

router = APIRouter(prefix="/witnesses", tags=["witnesses"])


@router.get("", response_model=WitnessesResponseSchema)
async def get_witnesses(
    _: DepCurrentUser,
    request: Request,
) -> dict:
    """
    Get all witnesses.
    
    Returns:
        Dictionary with all witnesses data
    """
    async with request.app.state.db_pool.acquire() as connection:
        result = await WitnessService.get_witnesses(connection=connection)
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=404 if result.get("error") == "NO_DATA" else 500,
                detail=result.get("message", "Error al obtener testigos")
            )
        
        return result


@router.get("/{witness_id}", response_model=WitnessesResponseSchema)
async def get_witness_by_id(
    witness_id: UUID,
    _: DepCurrentUser,
    request: Request,
) -> dict:
    """
    Get a specific witness by ID.
    
    Args:
        witness_id: UUID of the witness to retrieve
        
    Returns:
        Dictionary with the specific witness data
    """
    async with request.app.state.db_pool.acquire() as connection:
        result = await WitnessService.get_witnesses(
            witness_id=witness_id,
            connection=connection
        )
        
        if not result.get("success", False):
            error_code = result.get("error")
            if error_code == "WITNESS_NOT_FOUND":
                raise HTTPException(status_code=404, detail=result.get("message"))
            elif error_code == "NO_DATA":
                raise HTTPException(status_code=404, detail=result.get("message"))
            else:
                raise HTTPException(status_code=500, detail=result.get("message"))
        
        return result 