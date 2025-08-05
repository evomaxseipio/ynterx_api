# app/contracts/loan_property_schemas.py
"""
Schemas para Contract Loan y Property
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator


###
### Loan Schemas
###

class LoanPaymentDetailsCreate(BaseModel):
    """Schema para detalles de pago del préstamo"""
    monthly_payment: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    final_payment: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    discount_rate: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=4)
    payment_qty_quotes: Optional[int] = Field(None, ge=1)
    payment_type: Optional[str] = Field(None, max_length=20)


class ContractLoanCreate(BaseModel):
    """Schema para crear un loan de contrato"""
    amount: Decimal = Field(..., ge=0, decimal_places=2, description="Monto del préstamo")
    currency: str = Field("USD", max_length=3, description="Código de moneda")
    interest_rate: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=4, description="Tasa de interés mensual")
    term_months: Optional[int] = Field(None, ge=1, description="Plazo en meses")
    loan_type: Optional[str] = Field(None, max_length=30, description="Tipo de préstamo")
    start_date: Optional[str] = Field(None, description="Fecha de inicio")
    end_date: Optional[str] = Field(None, description="Fecha de vencimiento")

    # Detalles de pago anidados
    loan_payments_details: Optional[LoanPaymentDetailsCreate] = None

    @validator('currency')
    def validate_currency(cls, v):
        allowed_currencies = ['USD', 'DOP', 'EUR']
        if v not in allowed_currencies:
            raise ValueError(f'Currency must be one of: {allowed_currencies}')
        return v

    @validator('loan_type')
    def validate_loan_type(cls, v):
        if v is not None:
            allowed_types = ['hipotecario', 'personal', 'comercial', 'vehicular']
            if v not in allowed_types:
                raise ValueError(f'Loan type must be one of: {allowed_types}')
        return v


class ContractLoanResponse(BaseModel):
    """Schema para respuesta de loan creado"""
    contract_loan_id: int
    contract_id: UUID
    loan_amount: Decimal
    currency: str
    interest_rate: Optional[Decimal]
    term_months: Optional[int]
    loan_type: Optional[str]
    monthly_payment: Optional[Decimal]
    final_payment: Optional[Decimal]
    discount_rate: Optional[Decimal]
    payment_qty_quotes: Optional[int]
    payment_type: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


###
### Property Schemas
###

class PropertyCreate(BaseModel):
    """Schema para crear una propiedad"""
    property_type: str = Field(..., max_length=50, description="Tipo de propiedad")
<<<<<<< HEAD
    cadastral_number: Optional[str] = Field(None, max_length=50, description="Número catastral")
    title_number: Optional[str] = Field(None, max_length=50, description="Número de título")
    surface_area: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Área de superficie en m²")
    covered_area: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Área techada en m²")
    property_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Valor de la propiedad")
    currency: str = Field("USD", max_length=3, description="Código de moneda")
    description: Optional[str] = Field(None, description="Descripción de la propiedad")

    # Dirección
    address_line1: Optional[str] = Field(None, max_length=100, description="Dirección línea 1")
    address_line2: Optional[str] = Field(None, max_length=100, description="Dirección línea 2")
    city: Optional[str] = Field(None, description="Ciudad")
    city_id: Optional[int] = Field(None, description="ID de ciudad")
    postal_code: Optional[str] = Field(None, max_length=20, description="Código postal")

    # Campos de contrato
    property_role: Optional[str] = Field("garantia", max_length=30, description="Rol en el contrato")
    notes: Optional[str] = Field(None, description="Notas adicionales")
=======
    cadastral_number: str = Field(..., max_length=50, description="Número catastral")
    title_number: str = Field(..., max_length=50, description="Número de título")
    surface_area: Decimal = Field(..., ge=0, decimal_places=2, description="Área de superficie en m²")
    covered_area: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Área techada en m²")
    property_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Valor de la propiedad")
    property_owner: Optional[str] = Field(None, max_length=100, description="Propietario de la propiedad")
    currency: str = Field("USD", max_length=3, description="Código de moneda")
    property_description: Optional[str] = Field(None, description="Descripción de la propiedad")
    address_line1: Optional[str] = Field(None, max_length=100, description="Dirección línea 1")
    address_line2: Optional[str] = Field(None, max_length=100, description="Dirección línea 2")
    city_id: Optional[int] = Field(None, description="ID de ciudad")
    is_active: Optional[bool] = Field(True, description="Propiedad activa")
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f

    @validator('property_type')
    def validate_property_type(cls, v):
        allowed_types = ['casa', 'apartamento', 'terreno', 'local', 'oficina', 'bodega', 'finca']
        if v not in allowed_types:
            raise ValueError(f'Property type must be one of: {allowed_types}')
        return v

    @validator('currency')
    def validate_currency(cls, v):
        allowed_currencies = ['USD', 'DOP', 'EUR']
        if v not in allowed_currencies:
            raise ValueError(f'Currency must be one of: {allowed_currencies}')
        return v

<<<<<<< HEAD
    @validator('property_role')
    def validate_property_role(cls, v):
        if v is not None:
            allowed_roles = ['garantia', 'objeto', 'accesoria']
            if v not in allowed_roles:
                raise ValueError(f'Property role must be one of: {allowed_roles}')
        return v

=======
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f

class PropertyResponse(BaseModel):
    """Schema para respuesta de propiedad creada"""
    property_id: int
    property_type: str
<<<<<<< HEAD
    cadastral_number: Optional[str]
    title_number: Optional[str]
    surface_area: Optional[Decimal]
    covered_area: Optional[Decimal]
    property_value: Optional[Decimal]
    currency: str
    description: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    city_id: Optional[int]
    postal_code: Optional[str]
=======
    cadastral_number: str
    title_number: str
    surface_area: Decimal
    covered_area: Optional[Decimal]
    property_value: Optional[Decimal]
    property_owner: Optional[str]
    currency: str
    property_description: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    city_id: Optional[int]
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ContractPropertyResponse(BaseModel):
    """Schema para respuesta de relación contrato-propiedad"""
    contract_property_id: int
    contract_id: UUID
    property_id: int
    property_role: str
    is_primary: bool
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


###
### Combined Schemas for API Responses
###

class LoanPropertyResult(BaseModel):
    """Schema para resultado de creación de loan y properties"""
    contract_id: str
    loan_result: Optional[dict] = None
    properties_result: Optional[dict] = None
    overall_success: bool


class ContractCompleteCreate(BaseModel):
    """Schema principal para crear contrato completo con loan y properties"""
    contract_type: str
    contract_type_id: int
    description: Optional[str] = None

    # Loan data
    loan: Optional[ContractLoanCreate] = None

    # Properties data
    properties: Optional[List[PropertyCreate]] = None

    # Participants (se mantienen como Dict por simplicidad)
    clients: Optional[List[dict]] = None
    investors: Optional[List[dict]] = None
    witnesses: Optional[List[dict]] = None
    notaries: Optional[List[dict]] = None
    referrers: Optional[List[dict]] = None


###
### Update Schemas
###

class ContractLoanUpdate(BaseModel):
    """Schema para actualizar loan"""
    loan_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    currency: Optional[str] = Field(None, max_length=3)
    interest_rate: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=4)
    term_months: Optional[int] = Field(None, ge=1)
    loan_type: Optional[str] = Field(None, max_length=30)
    monthly_payment: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    final_payment: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    discount_rate: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=4)
    payment_qty_quotes: Optional[int] = Field(None, ge=1)
    payment_type: Optional[str] = Field(None, max_length=20)


class PropertyUpdate(BaseModel):
    """Schema para actualizar propiedad"""
    property_type: Optional[str] = Field(None, max_length=50)
    cadastral_number: Optional[str] = Field(None, max_length=50)
    title_number: Optional[str] = Field(None, max_length=50)
    surface_area: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    covered_area: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    property_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
<<<<<<< HEAD
    currency: Optional[str] = Field(None, max_length=3)
    description: Optional[str] = None
    address_line1: Optional[str] = Field(None, max_length=100)
    address_line2: Optional[str] = Field(None, max_length=100)
    city_id: Optional[int] = None
    postal_code: Optional[str] = Field(None, max_length=20)
=======
    property_owner: Optional[str] = Field(None, max_length=100)
    currency: Optional[str] = Field(None, max_length=3)
    property_description: Optional[str] = None
    address_line1: Optional[str] = Field(None, max_length=100)
    address_line2: Optional[str] = Field(None, max_length=100)
    city_id: Optional[int] = None
    is_active: Optional[bool] = None
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
