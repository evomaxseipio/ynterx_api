from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class CompanyBase(BaseModel):
    """Base model for company data"""
    company_name: str = Field(..., max_length=200, description="Company name")
    rnc: Optional[str] = Field(None, max_length=20, description="RNC number")
    rm: Optional[str] = Field(None, max_length=20, description="RM number")
    email: Optional[str] = Field(None, max_length=100, description="Company email")
    phone: Optional[str] = Field(None, max_length=20, description="Company phone")
    website: Optional[str] = Field(None, max_length=100, description="Company website")
    company_type: Optional[str] = Field(None, max_length=30, description="Type of company")
    tax_id: Optional[str] = Field(None, max_length=30, description="Tax ID")
    is_active: bool = Field(True, description="Whether the company is active")


class CompanyCreate(CompanyBase):
    """Model for creating a new company"""
    pass


class CompanyUpdate(BaseModel):
    """Model for updating company data"""
    company_name: Optional[str] = Field(None, max_length=200, description="Company name")
    rnc: Optional[str] = Field(None, max_length=20, description="RNC number")
    rm: Optional[str] = Field(None, max_length=20, description="RM number")
    email: Optional[str] = Field(None, max_length=100, description="Company email")
    phone: Optional[str] = Field(None, max_length=20, description="Company phone")
    website: Optional[str] = Field(None, max_length=100, description="Company website")
    company_type: Optional[str] = Field(None, max_length=30, description="Type of company")
    tax_id: Optional[str] = Field(None, max_length=30, description="Tax ID")
    is_active: Optional[bool] = Field(None, description="Whether the company is active")


class CompanyResponse(CompanyBase):
    """Model for company response"""
    company_id: int = Field(..., description="Company ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class CompanyWithRNCData(CompanyResponse):
    """Model for company with RNC consultation data"""
    rnc_data: Optional[dict] = Field(None, description="RNC consultation data from DGII")


class CompanyListResponse(BaseModel):
    """Model for company list response"""
    companies: list[CompanyResponse] = Field(..., description="List of companies")
    total: int = Field(..., description="Total number of companies")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of items per page")


# Standard Response Models
class StandardResponse(BaseModel):
    """Standard response model with success, error, and message fields"""
    success: bool = Field(..., description="Whether the operation was successful")
    error: Optional[str] = Field(None, description="Error code if operation failed")
    message: str = Field(..., description="Response message")


class CompanySuccessResponse(StandardResponse):
    """Success response with company data"""
    data: Optional[CompanyResponse] = Field(None, description="Company data")


class CompanyListSuccessResponse(StandardResponse):
    """Success response with company list data"""
    data: Optional[CompanyListResponse] = Field(None, description="Company list data")


class CompanyListSimpleResponse(StandardResponse):
    """Success response with simple company list"""
    data: Optional[List[CompanyResponse]] = Field(None, description="List of companies")


class RNCSuccessResponse(StandardResponse):
    """Success response with RNC data"""
    data: Optional[dict] = Field(None, description="RNC consultation data")


class DeleteSuccessResponse(StandardResponse):
    """Success response for delete operations"""
    data: Optional[dict] = Field(None, description="Delete operation result") 