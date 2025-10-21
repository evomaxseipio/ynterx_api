"""Schemas for notaries module."""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date
from uuid import UUID


class NotaryPersonSchema(BaseModel):
    """Schema for notary person data."""
    person_id: Optional[UUID] = Field(None, description="Person ID")
    first_name: str = Field(..., description="First name of the notary")
    last_name: str = Field(..., description="Last name of the notary")
    middle_name: str = Field(..., description="Middle name of the notary")
    date_of_birth: date = Field(..., description="Date of birth")
    gender: str = Field(..., description="Gender")
    nationality_country: str = Field(..., description="Nationality country")
    marital_status: str = Field(..., description="Marital status")
    occupation: str = Field(..., description="Occupation")


class NotaryDocumentSchema(BaseModel):
    """Schema for notary document data."""
    is_primary: bool = Field(..., description="Whether this is the primary document")
    document_type: str = Field(..., description="Type of document")
    document_number: str = Field(..., description="Document number")
    issuing_country_id: str = Field(..., description="Issuing country ID")
    document_issue_date: Optional[date] = Field(None, description="Document issue date")
    document_expiry_date: Optional[date] = Field(None, description="Document expiry date")


class NotaryAddressSchema(BaseModel):
    """Schema for notary address data."""
    address_line1: str = Field(..., description="Address line 1")
    address_line2: str = Field(..., description="Address line 2")
    city_id: str = Field(..., description="City ID")
    postal_code: str = Field(..., description="Postal code")
    address_type: str = Field(..., description="Address type")
    is_principal: bool = Field(..., description="Whether this is the principal address")


class NotaryAdditionalDataSchema(BaseModel):
    """Schema for notary additional data."""
    notary_id: str = Field(..., description="Notary ID")
    license_number: str = Field(..., description="License number")
    jurisdiction: str = Field(..., description="Jurisdiction")
    office_name: str = Field(..., description="Office name")
    professional_email: str = Field(..., description="Professional email")
    professional_phone: str = Field(..., description="Professional phone")


class NotarySchema(BaseModel):
    """Schema for complete notary data."""
    person: NotaryPersonSchema = Field(..., description="Person data")
    person_document: NotaryDocumentSchema = Field(..., description="Document data")
    address: NotaryAddressSchema = Field(..., description="Address data")
    person_role_id: int = Field(..., description="Person role ID")
    additional_data: NotaryAdditionalDataSchema = Field(..., description="Additional notary data")


class NotariesResponseSchema(BaseModel):
    """Schema for notaries response."""
    success: bool = Field(..., description="Whether the operation was successful")
    error: Optional[str] = Field(None, description="Error code if any")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Response data")


class NotariesListResponse(BaseModel):
    """Schema for notaries list response."""
    notaries: List[NotarySchema] = Field(..., description="List of notaries") 