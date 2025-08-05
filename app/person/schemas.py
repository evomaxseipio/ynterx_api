from datetime import date, datetime
from uuid import UUID
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, constr
from decimal import Decimal

###
### Common Schemas (Mantenidos para compatibilidad con otros endpoints)
###

class GenderBase(BaseModel):
    gender_name: constr(min_length=1, max_length=50)
    is_active: bool = True


class GenderResponse(GenderBase):
    model_config = ConfigDict(from_attributes=True)

    gender_id: int


class MaritalStatusBase(BaseModel):
    status_name: constr(min_length=1, max_length=50)
    is_active: bool = True


class MaritalStatusResponse(MaritalStatusBase):
    model_config = ConfigDict(from_attributes=True)

    marital_status_id: int


class EducationLevelBase(BaseModel):
    level_name: constr(min_length=1, max_length=100)
    is_active: bool = True


class EducationLevelResponse(EducationLevelBase):
    model_config = ConfigDict(from_attributes=True)

    education_level_id: int


class CountryBase(BaseModel):
    country_name: constr(min_length=1, max_length=100)
    country_code: constr(min_length=2, max_length=3)
    phone_code: str | None = Field(None, max_length=5)
    is_active: bool = True


class CountryResponse(CountryBase):
    model_config = ConfigDict(from_attributes=True)

    country_id: int


###
### Person Schemas (Actualizados para nueva estructura)
###

class PersonBase(BaseModel):
    first_name: constr(min_length=1, max_length=50)
    last_name: constr(min_length=1, max_length=50)
    middle_name: str | None = Field(None, max_length=50)
    date_of_birth: date | None = None
    gender: str | None = Field(None, max_length=50)
    nationality_country: str | None = Field(None, max_length=50)
    marital_status: str | None = Field(None, max_length=50)
    occupation: str | None = Field(None, max_length=50)
    is_active: bool = True


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    first_name: constr(min_length=1, max_length=50) | None = None
    last_name: constr(min_length=1, max_length=50) | None = None
    middle_name: str | None = Field(None, max_length=50)
    date_of_birth: date | None = None
    gender: str | None = Field(None, max_length=50)
    nationality_country: str | None = Field(None, max_length=50)
    marital_status: str | None = Field(None, max_length=50)
    occupation: str | None = Field(None, max_length=50)
    is_active: bool | None = None


class PersonSchema(PersonBase):
    model_config = ConfigDict(from_attributes=True)

    person_id: UUID
    created_at: datetime
    updated_at: datetime


###
### Schemas for Complete Person Creation
###

class PersonDocumentCreate(BaseModel):
    """Schema para documentos de persona"""
    is_primary: bool = False
    document_type: constr(min_length=1, max_length=50)
    document_number: constr(min_length=1, max_length=50)
    issuing_country_id: str
    document_issue_date: date | None = None
    document_expiry_date: date | None = None


class PersonAddressCreate(BaseModel):
    """Schema para direcciones de persona"""
    address_line1: constr(min_length=1, max_length=255)
    address_line2: str | None = Field(None, max_length=255)
    city_id: str
    postal_code: str | None = Field(None, max_length=20)
    address_type: constr(min_length=1, max_length=50)
    is_principal: bool = False


class PersonCompleteCreate(BaseModel):
    """Schema para crear persona completa con documentos y direcciones"""
    # Datos básicos de persona (alineados con nueva estructura)
    p_first_name: constr(min_length=1, max_length=50)
    p_last_name: constr(min_length=1, max_length=50)
    p_middle_name: str | None = Field(None, max_length=50)
    p_date_of_birth: date | None = None
    p_gender: str | None = Field(None, max_length=50)
    p_nationality_country: str | None = Field(None, max_length=50)
    p_marital_status: str | None = Field(None, max_length=50)
    p_occupation: str | None = Field(None, max_length=50)

    # Arrays para documentos y direcciones
    p_documents: List[PersonDocumentCreate] | None = Field(None, description="Lista de documentos de la persona")
    p_addresses: List[PersonAddressCreate] | None = Field(None, description="Lista de direcciones de la persona")
    p_additional_data: dict | None = Field(None, description="Datos adicionales en formato JSON")

    # Campos adicionales del stored procedure
    p_person_role_id: int | None = Field(1, description="ID del rol de la persona")
    p_created_by: UUID | None = Field(None, description="Usuario que crea el registro")
    p_updated_by: UUID | None = Field(None, description="Usuario que actualiza el registro")


class PersonCompleteResponse(BaseModel):
    """Schema para respuesta de creación de persona completa"""
    success: bool
    message: str
    person_id: UUID | None = None
    data: dict | None = None
    errors: List[str] | None = None

    # Campos adicionales del stored procedure
    person_exists: bool | None = None
    status_code: int | None = None
    timestamp: datetime | None = None
    error_details: dict | None = None


###
### Contract Integration Schemas (basado en el JSON del documento)
###

class ContractPersonCreate(BaseModel):
    """Schema simplificado para personas en contratos"""
    first_name: str
    last_name: str
    middle_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    nationality: str | None = None
    marital_status: str | None = None
    phone_number: str | None = None
    email: str | None = None


class ContractPersonDocument(BaseModel):
    """Schema para documentos en contratos"""
    document_type: str
    document_number: str
    issuing_country: str
    document_issue_date: date | None = None
    document_expiry_date: date | None = None


class ContractPersonAddress(BaseModel):
    """Schema para direcciones en contratos"""
    address_line1: str
    address_line2: str | None = None
    city: str
    postal_code: str | None = None
    address_type: str | None = None


class ContractPersonComplete(BaseModel):
    """Schema completo para personas en contratos"""
    person: ContractPersonCreate
    person_document: ContractPersonDocument | None = None
    address: ContractPersonAddress | None = None


###
### Legacy Support Schemas (Para mantener compatibilidad con código existente)
###

class PersonLegacyCreate(BaseModel):
    """Schema legacy para compatibilidad con código existente que usa IDs"""
    first_name: constr(min_length=1, max_length=255)
    last_name: constr(min_length=1, max_length=255)
    middle_name: str | None = Field(None, max_length=255)
    date_of_birth: date | None = None
    gender_id: int | None = None  # Para compatibilidad
    nationality_country_id: int | None = None  # Para compatibilidad
    marital_status_id: int | None = None  # Para compatibilidad
    education_level_id: int | None = None  # Para compatibilidad
    is_active: bool = True
<<<<<<< HEAD
=======


class ReferrerBase(BaseModel):
    person_id: UUID
    referral_code: Optional[str] = Field(None, max_length=255)
    referrer_phone_number: Optional[str] = Field(None, max_length=50)
    bank_name: Optional[str] = Field(None, max_length=255)
    bank_account: Optional[str] = Field(None, max_length=50)
    commission_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    notes: Optional[str] = None
    is_active: bool = Field(True)


class ReferrerCreate(ReferrerBase):
    pass


class ReferrerUpdate(BaseModel):
    referral_code: Optional[str] = Field(None, max_length=255)
    referrer_phone_number: Optional[str] = Field(None, max_length=50)
    bank_name: Optional[str] = Field(None, max_length=255)
    bank_account: Optional[str] = Field(None, max_length=50)
    commission_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ReferrerResponse(ReferrerBase):
    referrer_id: UUID
    referred_clients_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
