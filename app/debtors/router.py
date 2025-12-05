"""Router for debtor-related endpoints."""

from fastapi import APIRouter, Request, HTTPException, Depends, Query
from typing import Optional

from app.auth.dependencies import DepCurrentUser
from app.debtors.service import DebtorService
from app.debtors.schemas import DebtorsResponseSchema

router = APIRouter(prefix="/debtors", tags=["debtors"])


@router.get("", response_model=DebtorsResponseSchema)
async def get_debtors(
    _: DepCurrentUser,
    request: Request,
    person_type_id: int = Query(default=1, description="Person type ID (default: 1 for debtors)"),
    search_term: Optional[str] = Query(default=None, description="Search term to filter debtors"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of results to return"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
) -> dict:
    """
    Get list of debtors.
    
    Args:
        person_type_id: Person type ID (default: 1 for debtors)
        search_term: Optional search term to filter debtors
        limit: Maximum number of results to return (default: 50, max: 100)
        offset: Number of results to skip (default: 0)
    
    Returns:
        Dictionary with debtors data including client summary and list of debtors
    """
    async with request.app.state.db_pool.acquire() as connection:
        try:
            result = await DebtorService.get_debtors(
                person_type_id=person_type_id,
                search_term=search_term,
                limit=limit,
                offset=offset,
                connection=connection
            )
            
            # Check if the stored procedure returned success=false
            if not result.get("success", True):
                error_code = result.get("error", "UNKNOWN_ERROR")
                message = result.get("message", "Error al obtener deudores")
                status_code = 404 if error_code == "NO_DATA" else 500
                raise HTTPException(
                    status_code=status_code,
                    detail=message
                )
            
            return result
        except HTTPException:
            # Re-raise HTTPException as-is
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=404,
                detail=str(e)
            )
        except RuntimeError as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )


