from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class ReceiptData(BaseModel):
    """Datos básicos para generar recibo"""
    contract_loan_id: int
    client_name: str
    client_id: str
    contract_number: str
    payment_date: str
    total_paid: Decimal
    payment_method: str
    reference: Optional[str] = None


class ReceiptResponse(BaseModel):
    """Respuesta simple del recibo generado"""
    success: bool
    message: str
    receipt_id: str
    image_base64: str
    drive_link: Optional[str] = None
    filename: str