from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

class ContractData(BaseModel):
    """Schema for contract data to be inserted into template"""
    client_name: Optional[str] = None
    contract_date: Optional[str] = None
    amount: Optional[str] = None
    description: Optional[str] = None

    # Simple company fields (no nested objects)
    company_name: Optional[str] = None
    company_tax_id: Optional[str] = None
    company_address: Optional[str] = None
    company_email: Optional[str] = None
    company_phone: Optional[str] = None

    # Simple contractor fields
    contractor_name: Optional[str] = None
    contractor_email: Optional[str] = None
    contractor_phone: Optional[str] = None

    # Project fields
    project: Optional[str] = None
    duration: Optional[str] = None
    work_mode: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    # Payment fields
    payment_method: Optional[str] = None
    payment_terms: Optional[str] = None

    # Additional data for complex structures
    additional_data: Optional[Dict[str, Any]] = {}

    class Config:
        extra = "allow"  # Allows extra fields not defined in the model
        schema_extra = {
            "example": {
                "client_name": "John Doe",
                "contract_date": "2025-06-24",
                "amount": "15,000.00",
                "description": "Technology consulting services",
                "company_name": "Tech Solutions S.A.",
                "company_tax_id": "12345678901",
                "company_address": "Main Avenue 123",
                "company_email": "contact@techsolutions.com",
                "company_phone": "+1234567890",
                "contractor_name": "Jane Smith",
                "contractor_email": "jane@company.com",
                "contractor_phone": "+1234567890",
                "project": "ERP Implementation",
                "duration": "6 months",
                "work_mode": "Remote",
                "start_date": "2025-07-01",
                "end_date": "2025-12-31",
                "payment_method": "Bank transfer",
                "payment_terms": "30 days"
            }
        }

class ContractResponse(BaseModel):
    """Schema for contract generation response"""
    success: bool
    message: str
    filename: Optional[str] = None
    path: Optional[str] = None
    processed_data: Optional[Dict[str, Any]] = None

class ContractListItem(BaseModel):
    """Schema for contract list item"""
    filename: str
    created_at: str
    size_bytes: int

class ContractListResponse(BaseModel):
    """Schema for contract list response"""
    success: bool
    contracts: List[ContractListItem]
    total: int

class TemplateListResponse(BaseModel):
    """Schema for template list response"""
    success: bool
    templates: List[str]
    total: int

class DeleteResponse(BaseModel):
    """Schema for delete response"""
    success: bool
    message: str

class TemplateTestResponse(BaseModel):
    """Schema for template test response"""
    success: bool
    message: str
    template_file: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
