# schemas.py
from typing import Dict, Any, Optional, List, Union
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

from app.contracts.loan_property_schemas import (
    ContractLoanCreate,
    PropertyCreate,
    LoanPropertyResult,
    LoanPaymentDetailsCreate
)


# ========================================
# Request Models
# ========================================

class PersonBase(BaseModel):
    """Modelo base para persona"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    marital_status: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None


class PersonDocument(BaseModel):
    """Documento de identidad"""
    document_type: Optional[str] = None
    document_number: Optional[str] = None
    issuing_country: Optional[str] = None
    document_issue_date: Optional[str] = None
    document_expiry_date: Optional[str] = None


class NotaryDocument(PersonDocument):
    """Documento específico de notario"""
    notary_number: Optional[str] = None


class Address(BaseModel):
    """Dirección"""
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    address_type: Optional[str] = None


class Client(BaseModel):
    """Cliente del contrato"""
    person: Optional[PersonBase] = None
    person_document: Optional[PersonDocument] = None
    address: Optional[Address] = None
    p_person_role_id: Optional[int] = None


class Investor(BaseModel):
    """Inversionista del contrato"""
    person: Optional[PersonBase] = None
    person_document: Optional[PersonDocument] = None
    address: Optional[Address] = None
    p_person_role_id: Optional[int] = None


class Witness(BaseModel):
    """Testigo del contrato"""
    person: Optional[PersonBase] = None
    person_document: Optional[PersonDocument] = None
    address: Optional[Address] = None
    p_person_role_id: Optional[int] = None


class Notary(BaseModel):
    """Notario del contrato"""
    person: Optional[PersonBase] = None
    notary_document: Optional[NotaryDocument] = None
    address: Optional[Address] = None
    p_person_role_id: Optional[int] = None


class BankAccount(BaseModel):
    """Cuenta bancaria"""
    account_number: Optional[str] = None
    account_type: Optional[str] = None
    bank_name: Optional[str] = None









# ========================================
# Response Models
# ========================================

# Actualizar el ContractResponse principal
class ContractResponse(BaseModel):
    """Schema para respuesta de generación de contrato completo"""
    success: bool
    message: str
    contract_id: str
    contract_number: str
    filename: str
    path: Optional[str] = None
    folder_path: Optional[str] = None
    template_used: Optional[str] = None

    # Datos procesados
    processed_data: Optional[Dict[str, Any]] = None

    # Google Drive (si aplica)
    drive_success: Optional[bool] = None
    drive_folder_id: Optional[str] = None
    drive_file_id: Optional[str] = None
    drive_link: Optional[str] = None
    drive_view_link: Optional[str] = None

    # Advertencias
    warnings: Optional[Dict[str, Any]] = None


# ========================================
# Schemas para Contract Detail Response
# ========================================

# Extender schemas existentes para respuesta de detalle

class BankAccountDetail(BaseModel):
    """Schema para cuenta bancaria en detalle de contrato"""
    bank_name: Optional[str] = None
    bank_account_type: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_account_currency: Optional[str] = None


class LoanDetail(BaseModel):
    """Schema para loan en detalle de contrato"""
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    loan_type: Optional[str] = None
    term_months: Optional[int] = None
    bank_account: Optional[BankAccountDetail] = None
    interest_rate: Optional[Decimal] = None
    loan_payments_details: Optional[LoanPaymentDetailsCreate] = None  # Reutiliza schema existente


class PersonDocumentDetail(PersonDocument):
    """Schema para documento de persona en detalle - extiende PersonDocument"""
    is_primary: Optional[bool] = None
    issuing_country_id: Optional[Union[str, int]] = None  # Campo adicional para respuesta


class PersonAddressDetail(Address):
    """Schema para dirección de persona en detalle - extiende Address"""
    city_id: Optional[Union[str, int]] = None  # Campo adicional
    is_principal: Optional[bool] = None  # Campo adicional


class PersonAdditionalData(BaseModel):
    """Schema para datos adicionales de persona"""
    email: Optional[str] = None
    phone_number: Optional[str] = None


class PersonDetail(BaseModel):
    """Schema para persona completa en detalle de contrato"""
    p_gender: Optional[str] = None
    p_addresses: Optional[List[PersonAddressDetail]] = None
    p_documents: Optional[List[PersonDocumentDetail]] = None
    p_last_name: Optional[str] = None
    p_first_name: Optional[str] = None
    p_occupation: Optional[str] = None
    p_middle_name: Optional[str] = None
    p_date_of_birth: Optional[str] = None
    p_marital_status: Optional[str] = None
    p_person_role_id: Optional[int] = None
    p_additional_data: Optional[PersonAdditionalData] = None
    p_nationality_country: Optional[str] = None


class ParticipantDetail(BaseModel):
    """Schema para participante (cliente, inversionista, testigo) en detalle"""
    person: Optional[PersonDetail] = None


class DrivePathDetail(BaseModel):
    """Schema para información de Google Drive en detalle"""
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_folder: Optional[str] = None


class CompanyDetail(BaseModel):
    """Schema para empresa (cliente o inversionista) en detalle"""
    rm: Optional[str] = None
    rnc: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None


class PropertyDetail(BaseModel):
    """Schema para propiedad en detalle de contrato - basado en PropertyCreate pero con campos adicionales"""
    city_id: Optional[Union[int, str]] = None
    currency: Optional[str] = None
    owner_name: Optional[str] = None  # Similar a property_owner pero nombre diferente en respuesta
    description: Optional[str] = None  # Similar a property_description pero nombre diferente
    postal_code: Optional[str] = None
    covered_area: Optional[Decimal] = None
    surface_area: Optional[Decimal] = None
    title_number: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    property_role: Optional[str] = None  # Campo adicional para respuesta
    property_type: Optional[str] = None
    property_value: Optional[Decimal] = None
    cadastral_number: Optional[str] = None
    owner_nationality: Optional[str] = None
    owner_civil_status: Optional[str] = None
    owner_document_number: Optional[str] = None


class ParagraphRequestDetail(BaseModel):
    """Schema para paragraph_request en detalle"""
    section: Optional[str] = None
    person_role: Optional[str] = None
    contract_type: Optional[str] = None
    contract_services: Optional[str] = None


class ContractDetailData(BaseModel):
    """Schema para el objeto data en ContractDetailResponse"""
    loan: Optional[LoanDetail] = None
    notary: Optional[List[ParticipantDetail]] = None
    clients: Optional[List[ParticipantDetail]] = None
    investors: Optional[List[ParticipantDetail]] = None
    referents: Optional[List[ParticipantDetail]] = None
    witnesses: Optional[List[ParticipantDetail]] = None
    drive_path: Optional[DrivePathDetail] = None
    properties: Optional[List[PropertyDetail]] = None
    contract_id: Optional[str] = None
    description: Optional[str] = None
    contract_date: Optional[str] = None
    contract_type: Optional[str] = None
    client_company: Optional[CompanyDetail] = None
    contract_number: Optional[str] = None
    contract_type_id: Optional[int] = None
    investor_company: Optional[CompanyDetail] = None
    contract_end_date: Optional[str] = None
    paragraph_request: Optional[List[ParagraphRequestDetail]] = None


class ContractDetailResponse(BaseModel):
    """Schema para respuesta de detalle de contrato"""
    success: bool
    error: Optional[str] = None
    message: str
    data: Optional[ContractDetailData] = None


class ContractCompleteRequest(BaseModel):
    """Schema principal para crear contrato completo"""
    # Información básica del contrato
    contract_type: str = Field(..., description="Tipo de contrato")
    contract_type_id: int = Field(..., description="ID del tipo de contrato")

    # Datos financieros
    loan: Optional[ContractLoanCreate] = Field(None, description="Datos del préstamo")

    # Propiedades
    properties: Optional[List[PropertyCreate]] = Field(None, description="Lista de propiedades")

    # Participantes (mantenidos como Dict por flexibilidad)
    clients: Optional[List[Dict[str, Any]]] = Field(None, description="Lista de clientes")
    investors: Optional[List[Dict[str, Any]]] = Field(None, description="Lista de inversionistas")
    witnesses: Optional[List[Dict[str, Any]]] = Field(None, description="Lista de testigos")
    notaries: Optional[List[Dict[str, Any]]] = Field(None, description="Lista de notarios")
    referrers: Optional[List[Dict[str, Any]]] = Field(None, description="Lista de referentes")

    class Config:
        json_schema_extra = {
            "example": {
                "contract_type": "mortgage",
                "contract_type_id": 1,
                "loan": {
                    "amount": 20000.00,
                    "currency": "USD",
                    "interest_rate": 2.2,
                    "term_months": 12,
                    "loan_type": "hipotecario",
                    "loan_payments_details": {
                        "monthly_payment": 440.00,
                        "final_payment": 20440.00,
                        "discount_rate": 0.2,
                        "payment_qty_quotes": 11,
                        "payment_type": "mensual"
                    }
                },
                "properties": [
                    {
                        "property_type": "casa",
                        "cadastral_number": "406463901881",
                        "title_number": "4000277703",
                        "surface_area": 300.21,
                        "covered_area": 220.00,
                        "property_value": 20000.00,
                        "property_owner": "Juan Pérez",
                        "currency": "USD",
                        "property_description": "Casa hipotecada como garantía",
                        "address_line1": "Calle Altagracia No. 39",
                        "address_line2": "Apto 2B",
                        "city_id": 1
                    }
                ],
                "clients": [
                    {
                        "person": {
                            "first_name": "Rafael José",
                            "last_name": "Dolis",
                            "gender": "Masculino",
                            "nationality": "Dominicana",
                            "marital_status": "Soltero"
                        },
                        "person_document": {
                            "document_type": "Cédula",
                            "document_number": "138-0005267-5",
                            "issuing_country_id": "1"
                        },
                        "address": {
                            "address_line1": "Calle José Hazim Azar",
                            "city_id": "1"
                        }
                    }
                ]
            }
        }


# Schemas para operaciones específicas
class LoanCreateRequest(BaseModel):
    """Schema para crear solo loan"""
    contract_id: UUID
    loan_data: ContractLoanCreate


class PropertyCreateRequest(BaseModel):
    """Schema para crear solo properties"""
    contract_id: UUID
    properties_data: List[PropertyCreate]


class LoanPropertyCreateRequest(BaseModel):
    """Schema para crear loan y properties juntos"""
    contract_id: UUID
    loan_data: Optional[ContractLoanCreate] = None
    properties_data: Optional[List[PropertyCreate]] = None


# Schemas de respuesta
class ProcessedDataResponse(BaseModel):
    """Schema para datos procesados en la respuesta"""
    persons_summary: Dict[str, int]
    participants_count: int
    contract_type: str
    loan_amount: Optional[Decimal] = None
    properties_count: int
    document_generation: Dict[str, Any]
    loan_property_result: Optional[LoanPropertyResult] = None
    persons_detail: Dict[str, int]


# Existing schemas que ya tenías...
class UpdateResponse(BaseModel):
    success: bool
    message: str
    contract_id: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None


class UploadResponse(BaseModel):
    success: bool
    message: str
    filename: str
    size: Optional[int] = None
    contract_id: str


class ContractListResponse(BaseModel):
    success: bool
    contracts: List[Dict[str, Any]]
    total: int


class DeleteResponse(BaseModel):
    success: bool
    message: str


class SystemInfo(BaseModel):
    system: str
    version: str
    storage_type: str
    templates_dir: str
    contracts_dir: str
    templates_found: int
    contracts_generated: int
    template_files: List[str]
    google_drive: Dict[str, Any]
    max_file_size_mb: int
    allowed_extensions: List[str]
