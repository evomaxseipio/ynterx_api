from typing import Dict, Any, Optional, List, Union
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal

# ========================================
# Request Models
# ========================================

class GeneratePaymentScheduleRequest(BaseModel):
    """Request model for generating payment schedule"""
    contract_loan_id: int = Field(..., description="ID del préstamo del contrato")
    monthly_quotes: int = Field(..., description="Número de cuotas mensuales")
    monthly_amount: Decimal = Field(..., description="Monto mensual del capital")
    interest_amount: Decimal = Field(..., description="Monto del interés mensual")
    start_date: date = Field(..., description="Fecha de inicio del préstamo")
    end_date: date = Field(..., description="Fecha de finalización del préstamo")
    last_payment_date: date = Field(..., description="Fecha del último pago")
    last_principal: Decimal = Field(..., description="Monto del capital del último pago")
    last_interest: Decimal = Field(..., description="Monto del interés del último pago")

# ========================================
# Response Models
# ========================================

class GeneratePaymentScheduleResponse(BaseModel):
    """Response model for payment schedule generation"""
    success: bool
    message: str
    contract_loan_id: int
    total_payments_generated: int
    schedule_summary: Optional[Dict[str, Any]] = None


class RegisterPaymentTransactionRequest(BaseModel):
    """Request model for registering payment transaction"""
    contract_loan_id: int
    amount: float
    payment_method: str = "Cash"
    reference: Optional[str] = None
    transaction_date: Optional[str] = None
    url_bank_receipt: Optional[str] = None
    url_payment_receipt: Optional[str] = None
    notes: Optional[str] = None
    payment_image_url: Optional[str] = None  # URL de la imagen subida
    image_file: Optional[Any] = None  # Campo para recibir el archivo de imagen


class RegisterPaymentTransactionResponse(BaseModel):
    """Response model for payment transaction registration"""
    success: bool
    message: str
    transaction_id: Optional[int] = None


class LoanSummaryResponse(BaseModel):
    """Response model for loan summary from vw_loan_summary"""
    contract_loan_id: Optional[int] = None
    contract_id: Optional[str] = None
    loan_amount: Optional[float] = None
    total_payments: Optional[int] = None
    total_paid: Optional[float] = None
    total_pending: Optional[float] = None
    total_overdue: Optional[float] = None
    next_payment_date: Optional[str] = None
    next_payment_amount: Optional[float] = None
    loan_status: Optional[str] = None


class PaymentScheduleResponse(BaseModel):
    """Response model for payment schedule from sp_get_payment_schedule"""
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    message: Optional[str] = None


class AutoPaymentRequest(BaseModel):
    """Request model for automatic payment registration"""
    contract_loan_id: int = Field(..., description="ID del préstamo del contrato")
    amount: float = Field(..., gt=0, description="Monto del pago (debe ser mayor que 0)")
    payment_method: str = Field(default="Cash", description="Método de pago")
    reference: Optional[str] = Field(None, description="Número de referencia del pago")
    transaction_date: Optional[str] = Field(None, description="Fecha de la transacción (ISO format)")
    notes: Optional[str] = Field(None, description="Notas adicionales del pago")
    url_bank_receipt: Optional[str] = Field(None, description="URL del recibo del banco")
    url_payment_receipt: Optional[str] = Field(None, description="URL del recibo de la transacción")
    payment_image_url: Optional[str] = Field(None, description="URL de la imagen del voucher subida")
    image_file: Optional[Any] = Field(None, description="Archivo de imagen del voucher")

class AutoPaymentResponse(BaseModel):
    """Response model for automatic payment registration"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None
    receipt: Optional[Dict[str, Any]] = None  # Información del recibo generado


class SpecificPaymentRequest(BaseModel):
    """Request model for specific payment registration"""
    contract_loan_id: int = Field(..., description="ID del préstamo del contrato")
    payment_ids: List[str] = Field(..., description="Lista de UUIDs de las cuotas a pagar")
    amount: float = Field(..., gt=0, description="Monto exacto del pago (debe coincidir con la suma de las cuotas)")
    payment_method: str = Field(default="Cash", description="Método de pago")
    reference: Optional[str] = Field(None, description="Número de referencia del pago")
    transaction_date: Optional[str] = Field(None, description="Fecha de la transacción (ISO format)")
    notes: Optional[str] = Field(None, description="Notas adicionales del pago")
    url_bank_receipt: Optional[str] = Field(None, description="URL del recibo del banco")
    url_payment_receipt: Optional[str] = Field(None, description="URL del recibo de la transacción")
    payment_image_url: Optional[str] = Field(None, description="URL de la imagen del voucher subida")
    image_file: Optional[Any] = Field(None, description="Archivo de imagen del voucher")

class SpecificPaymentResponse(BaseModel):
    """Response model for specific payment registration"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class PaymentImageUploadRequest(BaseModel):
    """Request model for payment image upload"""
    contract_id: str = Field(..., description="ID del contrato")
    reference: str = Field(..., description="Referencia del pago (usado como nombre del archivo)")


class PaymentImageUploadResponse(BaseModel):
    """Response model for payment image upload"""
    success: bool
    message: str
    filename: Optional[str] = None
    local_path: Optional[str] = None
    drive_success: Optional[bool] = None
    drive_view_link: Optional[str] = None
    drive_error: Optional[str] = None
