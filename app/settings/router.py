from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional

from app.auth.dependencies import DepCurrentUser
from app.database import DepDatabase
from app.settings.schemas import (
    ContractParagraphCreate,
    ContractParagraphUpdate,
    ContractParagraphResponse,
    ContractParagraphFilter,
    ContractParagraphBulkCreate,
    ContractParagraphBulkOrderUpdate,
)
from app.settings.service import ContractParagraphService

router = APIRouter(prefix="/contract-paragraphs", tags=["contract-paragraphs"])


@router.post("", response_model=ContractParagraphResponse)
async def create_contract_paragraph(
    paragraph_data: ContractParagraphCreate,
    db: DepDatabase,
    current_user: DepCurrentUser,
) -> dict:
    """Create a new contract paragraph."""
    try:
        return await ContractParagraphService.create_paragraph(
            paragraph_data, connection=db
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[ContractParagraphResponse])
async def list_contract_paragraphs(
    db: DepDatabase,
    current_user: DepCurrentUser,
    person_role: Optional[str] = Query(None, description="Filter by person role"),
    contract_type: Optional[str] = Query(None, description="Filter by contract type"),
    section: Optional[str] = Query(None, description="Filter by section"),
    contract_services: Optional[str] = Query(None, description="Filter by contract services"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
) -> List[dict]:
    """List contract paragraphs with optional filters."""
    filters = ContractParagraphFilter(
        person_role=person_role,
        contract_type=contract_type,
        section=section,
        contract_services=contract_services,
        is_active=is_active,
        skip=skip,
        limit=limit,
    )
    return await ContractParagraphService.list_paragraphs(filters, connection=db)


@router.get("/for-contract", response_model=List[ContractParagraphResponse])
async def get_paragraphs_for_contract(
    person_role: str = Query(..., description="Person role (e.g., 'debtor', 'creditor')"),
    contract_type: str = Query(..., description="Contract type"),
    contract_services: str = Query("mortgage", description="Contract services type"),
    db: DepDatabase = Depends(),
    current_user: DepCurrentUser = Depends(),
) -> List[dict]:
    """Get all active paragraphs for a specific contract configuration."""
    return await ContractParagraphService.get_paragraphs_for_contract(
        person_role=person_role,
        contract_type=contract_type,
        contract_services=contract_services,
        connection=db,
    )


@router.get("/search", response_model=List[ContractParagraphResponse])
async def search_contract_paragraphs(
    q: str = Query(..., min_length=3, description="Search term (minimum 3 characters)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    db: DepDatabase = Depends(),
    current_user: DepCurrentUser = Depends(),
) -> List[dict]:
    """Search contract paragraphs by title or content."""
    return await ContractParagraphService.search_paragraphs(
        search_term=q, connection=db, limit=limit
    )


@router.get("/{paragraph_id}", response_model=ContractParagraphResponse)
async def get_contract_paragraph(
    paragraph_id: int,
    db: DepDatabase,
    current_user: DepCurrentUser,
) -> dict:
    """Get a contract paragraph by ID."""
    paragraph = await ContractParagraphService.get_paragraph(paragraph_id, connection=db)
    if not paragraph:
        raise HTTPException(status_code=404, detail="Contract paragraph not found")
    return paragraph


@router.put("/{paragraph_id}", response_model=ContractParagraphResponse)
async def update_contract_paragraph(
    paragraph_id: int,
    paragraph_data: ContractParagraphUpdate,
    db: DepDatabase,
    current_user: DepCurrentUser,
) -> dict:
    """Update a contract paragraph."""
    try:
        paragraph = await ContractParagraphService.update_paragraph(
            paragraph_id, paragraph_data, connection=db
        )
        if not paragraph:
            raise HTTPException(status_code=404, detail="Contract paragraph not found")
        return paragraph
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{paragraph_id}", response_model=ContractParagraphResponse)
async def delete_contract_paragraph(
    paragraph_id: int,
    soft_delete: bool = Query(True, description="Perform soft delete (set is_active=False)"),
    db: DepDatabase = Depends(),
    current_user: DepCurrentUser = Depends(),
) -> dict:
    """Delete a contract paragraph (soft delete by default)."""
    paragraph = await ContractParagraphService.delete_paragraph(
        paragraph_id, connection=db, soft_delete=soft_delete
    )
    if not paragraph:
        raise HTTPException(status_code=404, detail="Contract paragraph not found")
    return paragraph


@router.get("/{paragraph_id}/variables")
async def get_paragraph_variables(
    paragraph_id: int,
    db: DepDatabase = Depends(),
    current_user: DepCurrentUser = Depends(),
) -> dict:
    """Get paragraph variables for a specific paragraph."""
    variables = await ContractParagraphService.get_paragraph_variables(
        paragraph_id, connection=db
    )
    if variables is None:
        raise HTTPException(status_code=404, detail="Contract paragraph not found")
    return {"paragraph_id": paragraph_id, "variables": variables}


@router.post("/bulk", response_model=List[dict])
async def bulk_create_contract_paragraphs(
    bulk_data: ContractParagraphBulkCreate,
    db: DepDatabase = Depends(),
    current_user: DepCurrentUser = Depends(),
) -> List[dict]:
    """Create multiple contract paragraphs in bulk."""
    if len(bulk_data.paragraphs) > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 paragraphs can be created in a single bulk operation"
        )

    return await ContractParagraphService.bulk_create_paragraphs(bulk_data, connection=db)


@router.patch("/bulk-order", response_model=List[ContractParagraphResponse])
async def bulk_update_paragraph_orders(
    bulk_order_data: ContractParagraphBulkOrderUpdate,
    db: DepDatabase = Depends(),
    current_user: DepCurrentUser = Depends(),
) -> List[dict]:
    """Update order positions for multiple paragraphs."""
    if len(bulk_order_data.order_updates) > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximum 50 order updates can be processed in a single operation"
        )

    return await ContractParagraphService.update_paragraph_orders(
        bulk_order_data, connection=db
    )


# Additional utility endpoints
@router.get("/config/contract-types")
async def get_contract_types(
    current_user: DepCurrentUser = Depends(),
) -> dict:
    """Get available contract types."""
    return {
        "contract_types": [
            {"value": "juridica", "label": "Persona Jurídica"},
            {"value": "fisica_soltera", "label": "Persona Física Soltera"},
            {"value": "fisica_casada", "label": "Persona Física Casada"},
        ]
    }


@router.get("/config/contract-services")
async def get_contract_services(
    current_user: DepCurrentUser = Depends(),
) -> dict:
    """Get available contract services."""
    return {
        "contract_services": [
            {"value": "mortgage", "label": "Hipoteca"},
            {"value": "services", "label": "Servicios"},
            {"value": "loan", "label": "Préstamo"},
        ]
    }
