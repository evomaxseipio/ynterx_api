"""Schemas for referrers module."""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date
from uuid import UUID


class ReferrerPersonSchema(BaseModel):
    """Schema for referrer person data."""
    first_name: str = Field(..., description="First name of the referrer")
    last_name: str = Field(..., description="Last name of the referrer")
    middle_name: str = Field(..., description="Middle name of the referrer")
    date_of_birth: date = Field(..., description="Date of birth")
    gender: str = Field(..., description="Gender")
    nationality_country: str = Field(..., description="Nationality country")
    marital_status: str = Field(..., description="Marital status")
    occupation: str = Field(..., description="Occupation")


class ReferrerDocumentSchema(BaseModel):
    """Schema for referrer document data."""
    is_primary: bool = Field(..., description="Whether this is the primary document")
    document_type: str = Field(..., description="Type of document")
    document_number: str = Field(..., description="Document number")
    issuing_country_id: str = Field(..., description="Issuing country ID")
    document_issue_date: Optional[date] = Field(None, description="Document issue date")
    document_expiry_date: Optional[date] = Field(None, description="Document expiry date")


class ReferrerAddressSchema(BaseModel):
    """Schema for referrer address data."""
    address_line1: str = Field(..., description="Address line 1")
    address_line2: str = Field(..., description="Address line 2")
    city_id: str = Field(..., description="City ID")
    postal_code: str = Field(..., description="Postal code")
    address_type: str = Field(..., description="Address type")
    is_principal: bool = Field(..., description="Whether this is the principal address")


class ReferrerAdditionalDataSchema(BaseModel):
    """Schema for referrer additional data."""
    referrer_id: str = Field(..., description="Referrer ID")
    company_name: str = Field(..., description="Company name")
    position: str = Field(..., description="Position in the company")
    notes: str = Field(..., description="Additional notes")


class ReferrerSchema(BaseModel):
    """Schema for complete referrer data."""
    person: ReferrerPersonSchema = Field(..., description="Person data")
    person_document: ReferrerDocumentSchema = Field(..., description="Document data")
    address: ReferrerAddressSchema = Field(..., description="Address data")
    person_role_id: int = Field(..., description="Person role ID")
    additional_data: ReferrerAdditionalDataSchema = Field(..., description="Additional referrer data")


class ReferrersResponseSchema(BaseModel):
    """Schema for referrers response."""
    success: bool = Field(..., description="Whether the operation was successful")
    error: Optional[str] = Field(None, description="Error code if any")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Response data")


class ReferrersListResponse(BaseModel):
    """Schema for referrers list response."""
    referrers: List[ReferrerSchema] = Field(..., description="List of referrers") 