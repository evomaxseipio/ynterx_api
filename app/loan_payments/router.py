from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.auth.dependencies import DepCurrentUser
from .service import LoanPaymentService
from .schemas import *
from app.database import DepDatabase

router = APIRouter(prefix="/loan-payments", tags=["loan-payments"])

def get_loan_payment_service(db: DepDatabase) -> LoanPaymentService:
    """Dependency para obtener servicio de pagos de préstamos"""
    return LoanPaymentService(db)


@router.post("/generate-schedule", response_model=GeneratePaymentScheduleResponse)
async def generate_payment_schedule(
    request: GeneratePaymentScheduleRequest,
    db: DepDatabase,
    current_user: DepCurrentUser,
    service: LoanPaymentService = Depends(get_loan_payment_service)
):
    """
    Genera el cronograma de pagos para un préstamo
    
    Este endpoint llama a la función SQL sp_generate_loan_payment_schedule para crear
    el cronograma completo de pagos mensuales para un préstamo específico.
    """
    return await service.generate_payment_schedule(request)


@router.post("/register-transaction")
async def register_payment_transaction(
    request: RegisterPaymentTransactionRequest,
    db: DepDatabase,
    current_user: DepCurrentUser,
    service: LoanPaymentService = Depends(get_loan_payment_service)
):
    """
    Registra una transacción de pago para un préstamo
    """
    return await service.register_payment_transaction(request)


@router.get("/schedule", response_model=PaymentScheduleResponse)
async def get_payment_schedule(
    db: DepDatabase,
    current_user: DepCurrentUser,
    service: LoanPaymentService = Depends(get_loan_payment_service),
    contract_id: Optional[str] = None
):
    """
    Obtiene el cronograma de pagos de un contrato
    
    Args:
        contract_id: ID del contrato (opcional). Si no se proporciona, devuelve todos los cronogramas.
    
    Returns:
        Cronograma de pagos del contrato usando la función SQL sp_get_payment_schedule
    """
    result = await service.get_payment_schedule(contract_id=contract_id)
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=404 if result.get("error") == "NO_DATA" else 500,
            detail=result.get("message", "Error al obtener el cronograma de pagos")
        )
    
    return result


@router.post("/auto-payment", response_model=AutoPaymentResponse)
async def register_auto_payment(
    request: AutoPaymentRequest,
    db: DepDatabase,
    current_user: DepCurrentUser,
    service: LoanPaymentService = Depends(get_loan_payment_service)
):
    """
    Registra un pago automático para un préstamo
    
    Este endpoint usa la función SQL sp_register_payment_transaction para:
    - Aplicar el pago automáticamente a las cuotas pendientes en orden cronológico
    - Crear transacciones para cada pago aplicado
    - Manejar pagos adelantados si el monto excede las cuotas pendientes
    - Actualizar el estado de los pagos (pending -> partial -> paid)
    
    Args:
        request: Datos del pago automático
        
    Returns:
        Resumen del pago procesado con detalles de transacciones y actualizaciones
    """
    # Convertir transaction_date si se proporciona
    transaction_date = None
    if request.transaction_date:
        try:
            transaction_date = datetime.fromisoformat(request.transaction_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Formato de fecha inválido. Use formato ISO (YYYY-MM-DDTHH:MM:SS)"
            )
    
    result = await service.register_auto_payment(
        contract_loan_id=request.contract_loan_id,
        amount=request.amount,
        payment_method=request.payment_method,
        reference=request.reference,
        transaction_date=transaction_date,
        notes=request.notes
    )
    
    if not result.get("success", False):
        status_code = result.get("status_code", 500)
        error_detail = result.get("error", {}).get("message", "Error al procesar el pago")
        raise HTTPException(status_code=status_code, detail=error_detail)
    
    return result


@router.post("/specific-payment", response_model=SpecificPaymentResponse)
async def register_specific_payments(
    request: SpecificPaymentRequest,
    db: DepDatabase,
    current_user: DepCurrentUser,
    service: LoanPaymentService = Depends(get_loan_payment_service)
):
    """
    Registra pagos específicos para cuotas seleccionadas
    
    Este endpoint usa la función SQL sp_register_specific_payments para:
    - Pagar exactamente las cuotas especificadas por ID
    - Validar que el monto coincida exactamente con la suma de las cuotas
    - Crear transacciones para cada cuota pagada
    - Actualizar el estado de las cuotas a 'paid'
    
    Args:
        request: Datos del pago específico con lista de cuotas
        
    Returns:
        Resumen del pago procesado con detalles de transacciones y actualizaciones
    """
    # Convertir transaction_date si se proporciona
    transaction_date = None
    if request.transaction_date:
        try:
            transaction_date = datetime.fromisoformat(request.transaction_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Formato de fecha inválido. Use formato ISO (YYYY-MM-DDTHH:MM:SS)"
            )
    
    result = await service.register_specific_payments(
        contract_loan_id=request.contract_loan_id,
        payment_ids=request.payment_ids,
        amount=request.amount,
        payment_method=request.payment_method,
        reference=request.reference,
        transaction_date=transaction_date,
        notes=request.notes
    )
    
    # Retornar directamente el resultado sin lanzar excepciones
    return result