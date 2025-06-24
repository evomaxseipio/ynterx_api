from fastapi import APIRouter, HTTPException, Response
from .schemas import (
    ContractData,
    ContractResponse,
    ContractListResponse,
    TemplateListResponse,
    DeleteResponse
)
from .service import ContractService

# Initialize router and service
router = APIRouter(prefix="/contracts", tags=["contracts"])
contract_service = ContractService()

@router.post("/generate", response_model=ContractResponse)
async def generate_contract(data: ContractData):
    """
    Generate contract from Word template by inserting provided data
    """
    # Convert Pydantic model to dictionary
    context = data.dict(exclude_unset=True)

    # Merge additional data if exists
    if data.additional_data:
        context.update(data.additional_data)

    return contract_service.generate_contract(context)

@router.get("/test-template")
async def test_template():
    """
    Test template with minimal data to verify it works
    """
    return contract_service.test_template()

@router.get("/templates", response_model=TemplateListResponse)
async def list_templates():
    """List all available templates in templates folder"""
    return contract_service.list_templates()

@router.get("/list", response_model=ContractListResponse)
async def list_contracts():
    """List all generated contracts"""
    return contract_service.list_contracts()

@router.get("/download/{filename}")
async def download_contract(filename: str):
    """Download a specific contract"""
    file_path = contract_service.get_contract_file(filename)

    # Read file
    with open(file_path, "rb") as file:
        content = file.read()

    # Return file as response
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.delete("/delete/{filename}", response_model=DeleteResponse)
async def delete_contract(filename: str):
    """Delete a specific contract"""
    return contract_service.delete_contract(filename)

@router.get("/example-data")
async def get_example_data():
    """Returns an example of the data structure accepted by the endpoint"""
    return contract_service.get_example_data()
