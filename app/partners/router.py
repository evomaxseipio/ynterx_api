"""Router for partner-related endpoints."""

from fastapi import APIRouter, Request, HTTPException, Depends, Query
from typing import Optional

from app.auth.dependencies import DepCurrentUser
from app.partners.service import PartnerService
from app.partners.schemas import PartnersResponseSchema

router = APIRouter(prefix="/partners", tags=["partners"])


@router.get("", response_model=PartnersResponseSchema)
async def get_partners(
    _: DepCurrentUser,
    request: Request,
    person_type_id: int = Query(default=2, description="Person type ID (default: 2 for partners)"),
    search_term: Optional[str] = Query(default=None, description="Search term to filter partners"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of results to return"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
) -> dict:
    """
    Get list of partners.
    
    Args:
        person_type_id: Person type ID (default: 2 for partners)
        search_term: Optional search term to filter partners
        limit: Maximum number of results to return (default: 20, max: 100)
        offset: Number of results to skip (default: 0)
    
    Returns:
        Dictionary with partners data including client summary and list of partners
    """
    async with request.app.state.db_pool.acquire() as connection:
        try:
            result = await PartnerService.get_partners(
                person_type_id=person_type_id,
                search_term=search_term,
                limit=limit,
                offset=offset,
                connection=connection
            )
            
            # Check if the stored procedure returned success=false
            if not result.get("success", True):
                error_code = result.get("error", "UNKNOWN_ERROR")
                message = result.get("message", "Error al obtener partners")
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

