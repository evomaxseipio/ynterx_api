"""Schemas for witnesses module."""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date
from uuid import UUID


class WitnessPersonSchema(BaseModel):
    """Schema for witness person data."""
    first_name: str = Field(..., description="First name of the witness")
    last_name: str = Field(..., description="Last name of the witness")
    middle_name: str = Field(..., description="Middle name of the witness")
    date_of_birth: date = Field(..., description="Date of birth")
    gender: str = Field(..., description="Gender")
    nationality_country: str = Field(..., description="Nationality country")
    marital_status: str = Field(..., description="Marital status")
    occupation: str = Field(..., description="Occupation")


class WitnessDocumentSchema(BaseModel):
    """Schema for witness document data."""
    is_primary: bool = Field(..., description="Whether this is the primary document")
    document_type: str = Field(..., description="Type of document")
    document_number: str = Field(..., description="Document number")
    issuing_country_id: str = Field(..., description="Issuing country ID")
    document_issue_date: Optional[date] = Field(None, description="Document issue date")
    document_expiry_date: Optional[date] = Field(None, description="Document expiry date")


class WitnessAddressSchema(BaseModel):
    """Schema for witness address data."""
    address_line1: str = Field(..., description="Address line 1")
    address_line2: str = Field(..., description="Address line 2")
    city_id: str = Field(..., description="City ID")
    postal_code: str = Field(..., description="Postal code")
    address_type: str = Field(..., description="Address type")
    is_principal: bool = Field(..., description="Whether this is the principal address")


class WitnessAdditionalDataSchema(BaseModel):
    """Schema for witness additional data."""
    witness_id: str = Field(..., description="Witness ID")
    relationship: str = Field(..., description="Relationship to the contract")


class WitnessSchema(BaseModel):
    """Schema for complete witness data."""
    person: WitnessPersonSchema = Field(..., description="Person data")
    person_document: WitnessDocumentSchema = Field(..., description="Document data")
    address: WitnessAddressSchema = Field(..., description="Address data")
    person_role_id: int = Field(..., description="Person role ID")
    additional_data: WitnessAdditionalDataSchema = Field(..., description="Additional witness data")


class WitnessesResponseSchema(BaseModel):
    """Schema for witnesses response."""
    success: bool = Field(..., description="Whether the operation was successful")
    error: Optional[str] = Field(None, description="Error code if any")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Response data")


class WitnessesListResponse(BaseModel):
    """Schema for witnesses list response."""
    witnesses: List[WitnessSchema] = Field(..., description="List of witnesses") 