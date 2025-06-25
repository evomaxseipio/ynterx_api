from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

class ContractData(BaseModel):
    """Schema for contract data to be inserted into template - EXTENDIDO PARA HIPOTECAS"""

    # === CAMPOS ORIGINALES (mantiene compatibilidad total) ===
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

    # === NUEVOS CAMPOS PARA HIPOTECAS ===
    # Loan/Préstamo
    loan_amount: Optional[str] = None
    loan_amount_words: Optional[str] = None
    loan_currency: Optional[str] = None
    interest_rate: Optional[str] = None
    interest_rate_words: Optional[str] = None
    term_months: Optional[str] = None
    monthly_payment: Optional[str] = None
    monthly_payment_words: Optional[str] = None
    final_payment: Optional[str] = None
    final_payment_words: Optional[str] = None
    payment_quotes: Optional[str] = None
    discount_rate: Optional[str] = None
    penalty_rate: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None

    # Investor/Inversionista (Primera Parte)
    investor_company_name: Optional[str] = None
    investor_rnc: Optional[str] = None
    investor_rm: Optional[str] = None
    investor_full_name: Optional[str] = None
    investor_first_name: Optional[str] = None
    investor_last_name: Optional[str] = None
    investor_nationality: Optional[str] = None
    investor_marital_status: Optional[str] = None
    investor_document_number: Optional[str] = None
    investor_address: Optional[str] = None
    investor_city: Optional[str] = None

    # Client/Cliente (Segunda Parte) - Campos adicionales
    client_full_name: Optional[str] = None
    client_first_name: Optional[str] = None
    client_last_name: Optional[str] = None
    client_nationality: Optional[str] = None
    client_marital_status: Optional[str] = None
    client_document_number: Optional[str] = None
    client_address: Optional[str] = None
    client_city: Optional[str] = None
    client_phone: Optional[str] = None
    client_email: Optional[str] = None

    # Property/Propiedad
    property_cadastral_number: Optional[str] = None
    property_title_number: Optional[str] = None
    property_surface_area: Optional[str] = None
    property_address: Optional[str] = None
    property_city: Optional[str] = None
    property_description: Optional[str] = None

    # Witness/Testigo
    witness_full_name: Optional[str] = None
    witness_document_number: Optional[str] = None
    witness_address: Optional[str] = None

    # Notary/Notario
    notary_full_name: Optional[str] = None
    notary_number: Optional[str] = None
    notary_document_number: Optional[str] = None

    # Contract specific
    contract_location: Optional[str] = None
    contract_year: Optional[str] = None
    authorized_lawyer: Optional[str] = None
    authorized_lawyer_cedula: Optional[str] = None

    # Additional data for complex structures (MANTIENE ORIGINAL)
    additional_data: Optional[Dict[str, Any]] = {}

    class Config:
        extra = "allow"  # Allows extra fields not defined in the model
        json_schema_extra = {
            "example": {
                # Ejemplo original
                "client_name": "John Doe",
                "contract_date": "2025-06-24",
                "amount": "15,000.00",
                "description": "Technology consulting services",
                "company_name": "Tech Solutions S.A.",
                # Ejemplo hipoteca
                "loan_amount": "20,000.00",
                "client_full_name": "Rafael José Dolis",
                "investor_full_name": "Miguel Angel Reyes",
                "property_cadastral_number": "406463901881"
            }
        }

class ContractUpdateData(BaseModel):
    """Schema for updating contract data"""
    client_name: Optional[str] = None
    contract_date: Optional[str] = None
    amount: Optional[str] = None
    description: Optional[str] = None
    company_name: Optional[str] = None
    company_tax_id: Optional[str] = None
    company_address: Optional[str] = None
    company_email: Optional[str] = None
    company_phone: Optional[str] = None
    contractor_name: Optional[str] = None
    contractor_email: Optional[str] = None
    contractor_phone: Optional[str] = None
    project: Optional[str] = None
    duration: Optional[str] = None
    work_mode: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    payment_method: Optional[str] = None
    payment_terms: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = {}

    class Config:
        extra = "allow"

class ContractResponse(BaseModel):
    """Schema for contract generation response"""
    success: bool
    message: str
    contract_id: Optional[str] = None
    filename: Optional[str] = None
    path: Optional[str] = None
    folder_path: Optional[str] = None
    # Google Drive specific fields
    drive_folder_id: Optional[str] = None
    drive_file_id: Optional[str] = None
    drive_link: Optional[str] = None
    metadata_file_id: Optional[str] = None
    processed_data: Optional[Dict[str, Any]] = None

class ContractListItem(BaseModel):
    """Schema for contract list item"""
    contract_id: str
    filename: str
    created_at: str
    modified_at: Optional[str] = None
    size_bytes: int
    folder_path: Optional[str] = None
    attachments_count: int
    # Google Drive specific fields
    drive_folder_id: Optional[str] = None
    drive_file_id: Optional[str] = None
    drive_link: Optional[str] = None

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

class FileUploadResponse(BaseModel):
    """Schema for file upload response"""
    success: bool
    message: str
    filename: str
    file_path: Optional[str] = None
    file_size: int
    file_type: str
    contract_id: str
    # Google Drive specific fields
    drive_file_id: Optional[str] = None

class AttachmentListItem(BaseModel):
    """Schema for attachment list item"""
    filename: str
    file_size: int
    file_type: str
    uploaded_at: str
    file_path: Optional[str] = None
    drive_file_id: Optional[str] = None

class AttachmentListResponse(BaseModel):
    """Schema for attachment list response"""
    success: bool
    contract_id: str
    attachments: List[AttachmentListItem]
    total: int

class ContractDetailsResponse(BaseModel):
    """Schema for contract details with attachments"""
    success: bool
    contract_id: str
    filename: str
    created_at: str
    modified_at: Optional[str] = None
    size_bytes: int
    folder_path: Optional[str] = None
    attachments: List[AttachmentListItem]
    original_data: Optional[Dict[str, Any]] = None
    # Google Drive specific fields
    drive_folder_id: Optional[str] = None
    drive_link: Optional[str] = None


# === NUEVOS MODELOS PARA RECIBIR DATOS COMPLEJOS DE HIPOTECA ===
# Estos serán convertidos automáticamente a ContractData plano

class PersonDocument(BaseModel):
    document_type: str
    document_number: str
    issuing_country: str
    document_issue_date: str
    document_expiry_date: str

class NotaryDocument(BaseModel):
    notary_number: str
    document_type: str
    document_number: str
    issuing_country: str
    document_issue_date: str
    document_expiry_date: str

class Address(BaseModel):
    address_line1: str
    address_line2: Optional[str] = ""
    city: str
    postal_code: str
    address_type: str = "Residencial"

class Person(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = ""
    date_of_birth: str
    gender: str
    nationality: str
    marital_status: str
    phone_number: Optional[str] = ""
    email: Optional[str] = ""

class Client(BaseModel):
    person: Person
    person_document: PersonDocument
    address: Address

class Investor(BaseModel):
    person: Person
    person_document: PersonDocument
    address: Address

class Witness(BaseModel):
    person: Person
    person_document: PersonDocument
    address: Address

class Notary(BaseModel):
    person: Person
    notary_document: NotaryDocument
    address: Address

class BankDepositAccount(BaseModel):
    account_number: str
    account_type: str
    bank_name: str

class LoanPaymentDetails(BaseModel):
    monthly_payment: float
    final_payment: float
    discount_rate: float
    payment_qty_quotes: int
    payment_qty_months: int
    payment_type: str = "mensual"

class Loan(BaseModel):
    amount: float
    currency: str = "USD"
    interest_rate: float
    term_months: int
    start_date: str
    end_date: str
    loan_type: str = "hipotecario"
    bank_deposit_account: BankDepositAccount
    loan_payments_details: LoanPaymentDetails

class PropertyOwner(BaseModel):
    person_id: str
    ownership_percentage: float
    is_main_owner: bool = False

class Property(BaseModel):
    property_type: str
    cadastral_number: str
    title_number: str
    surface_area: float
    covered_area: float
    address_line1: str
    address_line2: Optional[str] = ""
    city: str
    postal_code: str
    current_use: str = "residencial"
    property_value: float
    currency: str = "USD"
    appraised_by: str
    appraised_at: str
    description: str
    owners: List[PropertyOwner]

class MortgageContractData(BaseModel):
    """Estructura compleja para contratos hipotecarios - será convertida automáticamente"""
    loan: Loan
    properties: List[Property]
    clients: List[Client]
    investors: List[Investor]
    witnesses: List[Witness]
    notaries: List[Notary]
    contract_date: Optional[str] = None
    contract_location: Optional[str] = "San Pedro de Macorís, República Dominicana"
