from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class CompanyBase(BaseModel):
    """Base model for company data"""
    company_name: str = Field(..., max_length=200, description="Company name")
    company_rnc: Optional[str] = Field(None, max_length=20, description="RNC number")
    mercantil_registry: Optional[str] = Field(None, max_length=20, description="Mercantil registry number")
    nationality: Optional[str] = Field(None, max_length=100, description="Company nationality")
    email: Optional[str] = Field(None, max_length=100, description="Company email")
    phone: Optional[str] = Field(None, max_length=20, description="Company phone")
    website: Optional[str] = Field(None, max_length=100, description="Company website")
    company_type: Optional[str] = Field(None, max_length=30, description="Type of company")
    company_description: Optional[str] = Field(None, description="Company description")
    frontImagePath: Optional[str] = Field(None, description="Front image path")
    backImagePath: Optional[str] = Field(None, description="Back image path")
    is_active: bool = Field(True, description="Whether the company is active")


class CompanyCreate(CompanyBase):
    """Model for creating a new company"""
    pass


class CompanyUpdate(BaseModel):
    """Model for updating company data"""
    company_name: Optional[str] = Field(None, max_length=200, description="Company name")
    company_rnc: Optional[str] = Field(None, max_length=20, description="RNC number")
    mercantil_registry: Optional[str] = Field(None, max_length=20, description="Mercantil registry number")
    nationality: Optional[str] = Field(None, max_length=100, description="Company nationality")
    email: Optional[str] = Field(None, max_length=100, description="Company email")
    phone: Optional[str] = Field(None, max_length=20, description="Company phone")
    website: Optional[str] = Field(None, max_length=100, description="Company website")
    company_type: Optional[str] = Field(None, max_length=30, description="Type of company")
    company_description: Optional[str] = Field(None, description="Company description")
    frontImagePath: Optional[str] = Field(None, description="Front image path")
    backImagePath: Optional[str] = Field(None, description="Back image path")
    is_active: Optional[bool] = Field(None, description="Whether the company is active")


class CompanyResponse(CompanyBase):
    """Model for company response"""
    company_id: int = Field(..., description="Company ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


# Company Address Models
class CompanyAddressBase(BaseModel):
    """Base model for company address data"""
    address_line1: str = Field(..., max_length=100, description="Primary address line")
    address_line2: Optional[str] = Field(None, max_length=100, description="Secondary address line")
    city: Optional[str] = Field(None, max_length=100, description="City")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal code")
    address_type: str = Field("Business", max_length=20, description="Type of address")
    email: Optional[str] = Field(None, max_length=100, description="Address email")
    phone: Optional[str] = Field(None, max_length=20, description="Address phone")
    is_principal: bool = Field(False, description="Whether this is the principal address")
    is_active: bool = Field(True, description="Whether the address is active")


class CompanyAddressCreate(CompanyAddressBase):
    """Model for creating a new company address"""
    company_id: int = Field(..., description="Company ID")


class CompanyAddressUpdate(BaseModel):
    """Model for updating company address data"""
    address_line1: Optional[str] = Field(None, max_length=100, description="Primary address line")
    address_line2: Optional[str] = Field(None, max_length=100, description="Secondary address line")
    city: Optional[str] = Field(None, max_length=100, description="City")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal code")
    address_type: Optional[str] = Field(None, max_length=20, description="Type of address")
    email: Optional[str] = Field(None, max_length=100, description="Address email")
    phone: Optional[str] = Field(None, max_length=20, description="Address phone")
    is_principal: Optional[bool] = Field(None, description="Whether this is the principal address")
    is_active: Optional[bool] = Field(None, description="Whether the address is active")


class CompanyAddressResponse(CompanyAddressBase):
    """Model for company address response"""
    company_address_id: int = Field(..., description="Company address ID")
    company_id: int = Field(..., description="Company ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


# Company Manager Models
class CompanyManagerBase(BaseModel):
    """Base model for company manager data"""
    manager_full_name: Optional[str] = Field(None, max_length=200, description="Manager full name")
    manager_position: Optional[str] = Field(None, max_length=100, description="Manager position")
    manager_address: Optional[str] = Field(None, description="Manager address")
    manager_document_number: Optional[str] = Field(None, max_length=50, description="Manager document number")
    manager_nationality: Optional[str] = Field(None, max_length=50, description="Manager nationality")
    manager_civil_status: Optional[str] = Field(None, max_length=50, description="Manager civil status")
    is_principal: bool = Field(False, description="Whether this is the principal manager")
    is_active: bool = Field(True, description="Whether the manager is active")


class CompanyManagerCreate(CompanyManagerBase):
    """Model for creating a new company manager"""
    company_id: int = Field(..., description="Company ID")
    created_by: Optional[str] = Field(None, description="Person ID who created the record")


class CompanyManagerUpdate(BaseModel):
    """Model for updating company manager data"""
    manager_full_name: Optional[str] = Field(None, max_length=200, description="Manager full name")
    manager_position: Optional[str] = Field(None, max_length=100, description="Manager position")
    manager_address: Optional[str] = Field(None, description="Manager address")
    manager_document_number: Optional[str] = Field(None, max_length=50, description="Manager document number")
    manager_nationality: Optional[str] = Field(None, max_length=50, description="Manager nationality")
    manager_civil_status: Optional[str] = Field(None, max_length=50, description="Manager civil status")
    is_principal: Optional[bool] = Field(None, description="Whether this is the principal manager")
    is_active: Optional[bool] = Field(None, description="Whether the manager is active")
    updated_by: Optional[str] = Field(None, description="Person ID who updated the record")


class CompanyManagerResponse(CompanyManagerBase):
    """Model for company manager response"""
    manager_id: int = Field(..., description="Manager ID")
    company_id: int = Field(..., description="Company ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="Person ID who created the record")
    updated_by: Optional[str] = Field(None, description="Person ID who updated the record")

    class Config:
        from_attributes = True


# Company with related data
class CompanyWithRelations(CompanyResponse):
    """Model for company with related addresses and managers"""
    addresses: List[CompanyAddressResponse] = Field(default_factory=list, description="Company addresses")
    managers: List[CompanyManagerResponse] = Field(default_factory=list, description="Company managers")


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


class CompanyWithRelationsSuccessResponse(StandardResponse):
    """Success response with company and related data"""
    data: Optional[CompanyWithRelations] = Field(None, description="Company with related data")


class CompanyListSuccessResponse(StandardResponse):
    """Success response with company list data"""
    data: Optional[CompanyListResponse] = Field(None, description="Company list data")


class CompanyListSimpleResponse(StandardResponse):
    """Success response with simple company list"""
    data: Optional[List[CompanyResponse]] = Field(None, description="List of companies")


class CompanyAddressSuccessResponse(StandardResponse):
    """Success response with company address data"""
    data: Optional[CompanyAddressResponse] = Field(None, description="Company address data")


class CompanyManagerSuccessResponse(StandardResponse):
    """Success response with company manager data"""
    data: Optional[CompanyManagerResponse] = Field(None, description="Company manager data")


class RNCSuccessResponse(StandardResponse):
    """Success response with RNC data"""
    data: Optional[dict] = Field(None, description="RNC consultation data")


class DeleteSuccessResponse(StandardResponse):
    """Success response for delete operations"""
    data: Optional[dict] = Field(None, description="Delete operation result") 