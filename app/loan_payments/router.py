from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from app.auth.dependencies import get_current_user
from .service import LoanPaymentService
from .payment_image_service import PaymentImageService
from .schemas import *
from app.database import DepDatabase
from app.config import settings
from app.receipts.receipt_service import ReceiptService
from sqlalchemy import text

router = APIRouter(prefix="/loan-payments", tags=["loan-payments"])

def get_loan_payment_service(db: DepDatabase) -> LoanPaymentService:
    """Dependency para obtener servicio de pagos de préstamos"""
    return LoanPaymentService(db)


def get_payment_image_service() -> PaymentImageService:
    """Dependency para obtener servicio de imágenes de pagos"""
    contracts_dir = Path(settings.CONTRACTS_DIR)
    return PaymentImageService(contracts_dir, use_google_drive=True)


def get_receipt_service() -> ReceiptService:
    """Dependency para obtener servicio de recibos"""
    return ReceiptService()


async def _persist_payment_receipt_url(db: DepDatabase, transaction_ids: list, drive_link: str) -> None:
    """Guarda la URL del recibo en public.payment_transaction por transaction_id (UUID)."""
    if not transaction_ids or not drive_link:
        return
    try:
        print(f"[persist] payment_transaction: tx_count={len(transaction_ids)}")
        # Actualizar uno-a-uno para evitar problemas de tipos con arrays y asyncpg
        for tx_id in transaction_ids:
            await db.execute(
                text("UPDATE public.payment_transaction SET url_payment_receipt = :url WHERE transaction_id = :tx_id"),
                {"url": drive_link, "tx_id": str(tx_id)}
            )
        await db.commit()
        print("[persist] OK: url_payment_receipt actualizada en public.payment_transaction")
    except Exception as update_err:
        print(f"❌ [persist] ERROR actualizando public.payment_transaction.url_payment_receipt: {update_err}")


@router.post("/generate-schedule", response_model=GeneratePaymentScheduleResponse)
async def generate_payment_schedule(
    request: GeneratePaymentScheduleRequest,
    db: DepDatabase,
    service: LoanPaymentService = Depends(get_loan_payment_service),
    current_user: str = Depends(get_current_user)
):
    """
    Genera el cronograma de pagos para un préstamo
    
    Este endpoint llama a la función SQL sp_generate_loan_payment_schedule para crear
    el cronograma completo de pagos mensuales para un préstamo específico.
    """
    return await service.generate_payment_schedule(request)



@router.post("/register-payment")
async def register_payment_with_image(
    db: DepDatabase,
    contract_loan_id: int = Form(...),
    amount: float = Form(...),
    payment_method: str = Form("Cash"),
    reference: Optional[str] = Form(None),
    transaction_date: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    url_payment_receipt: Optional[str] = Form(None),
    image_file: Optional[UploadFile] = File(default=None),
    image_service: PaymentImageService = Depends(get_payment_image_service),
    service: LoanPaymentService = Depends(get_loan_payment_service),
    receipt_service: ReceiptService = Depends(get_receipt_service),
    current_user: str = Depends(get_current_user),
):
    """
    Endpoint atómico para registrar un pago y subir la imagen del voucher
    - Recibe todos los datos y el archivo por multipart/form-data
    - Sube el archivo a la carpeta del contrato (Drive o local)
    - Si ocurre un error, hace rollback y elimina el archivo
    - Retorna metadata de la transacción y del archivo
    """
    payment_image_url = None
    uploaded_filename = None
    file_remove_func = None  # función para limpiar si la DB falla

    # 1. Procesar el archivo si existe (y es realmente un archivo subido)
    if image_file and hasattr(image_file, 'filename') and image_file.filename and image_file.filename.strip():
        try:
            # Valida tipo y tamaño (ejemplo: solo jpg/png/pdf y <= 8MB)
            allowed_types = {"image/jpeg", "image/png", "application/pdf"}
            max_size = 8 * 1024 * 1024
            
            # Verificar que el archivo tenga contenido
            contents = await image_file.read()
            if not contents or len(contents) == 0:
                raise HTTPException(400, "El archivo está vacío")
            
            # Verificar tipo de contenido
            if not image_file.content_type or image_file.content_type not in allowed_types:
                raise HTTPException(400, f"Tipo de archivo no permitido: {image_file.content_type}")
            
            # Verificar tamaño
            if len(contents) > max_size:
                raise HTTPException(400, "El archivo excede el tamaño máximo de 8MB")
            
            # Subida atómica: solo sube después de validar
            result = await image_service.upload_payment_image(
                str(contract_loan_id), reference, image_file, db, file_bytes=contents
            )
            payment_image_url = result.get("drive_view_link") or result.get("local_path")
            uploaded_filename = result.get("filename")
            # Prepara función de limpieza
            if result.get("remove_func"):
                file_remove_func = result["remove_func"]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Error al procesar la imagen: {e}")
    
    # 2. Registrar el pago usando la misma lógica que auto-payment
    try:
        # Convertir transaction_date si se proporciona
        tx_date = None
        if transaction_date:
            try:
                tx_date = datetime.fromisoformat(transaction_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Formato de fecha inválido. Use formato ISO (YYYY-MM-DDTHH:MM:SS)"
                )

        # Usar el mismo método que auto-payment para obtener datos completos
        result = await service.register_auto_payment(
            contract_loan_id=contract_loan_id,
            amount=amount,
            payment_method=payment_method,
            reference=reference,
            transaction_date=tx_date,
            notes=notes,
            url_bank_receipt=payment_image_url,
            url_payment_receipt=url_payment_receipt
        )

        if not result.get("success", False):
            # Limpiar archivo antes de lanzar la excepción
            if file_remove_func:
                try:
                    await file_remove_func()
                except Exception as cleanup_error:
                    print(f"Error al eliminar archivo luego de falla DB: {cleanup_error}")

            status_code = result.get("status_code", 500)

            # Manejar error como dict o string
            error_info = result.get("error", {})
            if isinstance(error_info, dict):
                error_detail = {
                    "error_code": error_info.get("code", "UNKNOWN_ERROR"),
                    "message": error_info.get("message", "Error al procesar el pago"),
                    "success": False
                }
            else:
                error_detail = {
                    "error_code": "UNKNOWN_ERROR",
                    "message": str(error_info) if error_info else "Error al procesar el pago",
                    "success": False
                }

            raise HTTPException(status_code=status_code, detail=error_detail)

    except HTTPException as http_exc:
        # Limpiar archivo si hay HTTPException
        if file_remove_func:
            try:
                await file_remove_func()
            except Exception as cleanup_error:
                print(f"Error al eliminar archivo luego de HTTPException: {cleanup_error}")
        # Re-lanzar la excepción original
        raise http_exc
    except Exception as e:
        # Limpiar archivo si hay otra excepción
        if file_remove_func:
            try:
                await file_remove_func()
            except Exception as cleanup_error:
                print(f"Error al eliminar archivo luego de Exception: {cleanup_error}")
        raise HTTPException(500, f"Error al registrar el pago: {e}")
    
    # 3. Generar recibo automáticamente si el pago fue exitoso
    receipt_result = None
    try:
        # Usar la respuesta del procedimiento para generar el recibo
        # El servicio de recibos espera los datos completos como en auto-payment
        receipt_result = await receipt_service.generate_receipt_from_payment(result, db)
        
        # Agregar información del recibo a la respuesta
        if receipt_result.success:
            result["receipt"] = {
                "receipt_id": receipt_result.receipt_id,
                "image_base64": receipt_result.image_base64,
                "drive_link": receipt_result.drive_link,
                "filename": receipt_result.filename
            }
            if receipt_result.drive_link:
                result["data"]["url_payment_receipt"] = receipt_result.drive_link
                transaction_ids = [t["transaction_id"] for t in result["data"].get("transactions", [])]
                print(f"[register-payment] tx_ids={transaction_ids}, drive_link={receipt_result.drive_link}")
                await _persist_payment_receipt_url(db, transaction_ids, receipt_result.drive_link)
                
    except Exception as e:
        print(f"⚠️ Error generando recibo: {e}")
        # No fallar el pago si falla la generación del recibo
    
    # 4. Retornar respuesta enriquecida
    return {
        "success": True,
        "status_code": 200,
        "message": "Pago registrado correctamente",
        "data": result["data"] if result.get("data") else result,
        # "transaction_result": result,
        "voucher_url": payment_image_url,
        "voucher_filename": uploaded_filename,
        "receipt": receipt_result.dict() if receipt_result else None,
        "error": None
    }



@router.post("/register-transaction-with-image")
async def register_payment_transaction(
    request: RegisterPaymentTransactionRequest,
    db: DepDatabase,
    service: LoanPaymentService = Depends(get_loan_payment_service),
    image_service: PaymentImageService = Depends(get_payment_image_service),
    current_user: str = Depends(get_current_user)
):
    """
    Registra una transacción de pago para un préstamo
    
    Si se proporciona una imagen en request.payment_image_url, se subirá automáticamente
    a la carpeta payments del contrato.
    """
    # Si hay una imagen para subir, procesarla
    if hasattr(request, 'image_file') and request.image_file:
        try:
            contract_id = str(request.contract_loan_id)
            image_result = await image_service.upload_payment_image(contract_id, request.reference, request.image_file, db)
            
            if image_result.get("success"):
                # Usar URL de Google Drive si está disponible, sino URL local
                if image_result.get("drive_success") and image_result.get("drive_view_link"):
                    request.payment_image_url = image_result.get("drive_view_link")
                else:
                    request.payment_image_url = image_result.get("local_path")
        except Exception as e:
            print(f"Error subiendo imagen: {e}")
    
    return await service.register_payment_transaction(request)


@router.get("/schedule", response_model=PaymentScheduleResponse)
async def get_payment_schedule(
    db: DepDatabase,
    service: LoanPaymentService = Depends(get_loan_payment_service),
    current_user: str = Depends(get_current_user),
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
    service: LoanPaymentService = Depends(get_loan_payment_service),
    image_service: PaymentImageService = Depends(get_payment_image_service),
    receipt_service: ReceiptService = Depends(get_receipt_service),
    current_user: str = Depends(get_current_user)
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
    
    # Procesar imagen si se proporciona
    url_bank_receipt = request.url_bank_receipt
    if hasattr(request, 'image_file') and request.image_file:
        try:
            contract_id = str(request.contract_loan_id)
            image_result = await image_service.upload_payment_image(contract_id, request.reference, request.image_file, db)
            
            if image_result.get("success"):
                # Usar URL de Google Drive si está disponible, sino URL local
                if image_result.get("drive_success") and image_result.get("drive_view_link"):
                    url_bank_receipt = image_result.get("drive_view_link")
                else:
                    url_bank_receipt = image_result.get("local_path")
        except Exception as e:
            print(f"Error subiendo imagen: {e}")
    
    result = await service.register_auto_payment(
        contract_loan_id=request.contract_loan_id,
        amount=request.amount,
        payment_method=request.payment_method,
        reference=request.reference,
        transaction_date=transaction_date,
        notes=request.notes,
        url_bank_receipt=url_bank_receipt,
        url_payment_receipt=request.url_payment_receipt
    )
    
    if not result.get("success", False):
        status_code = result.get("status_code", 500)
        error_detail = result.get("error", {}).get("message", "Error al procesar el pago")
        raise HTTPException(status_code=status_code, detail=error_detail)
    
    # Generar recibo automáticamente si el pago fue exitoso
    try:
        receipt_result = await receipt_service.generate_receipt_from_payment(result, db)
        
        # Agregar información del recibo a la respuesta
        if receipt_result.success:
            result["receipt"] = {
                "receipt_id": receipt_result.receipt_id,
                "image_base64": receipt_result.image_base64,
                "drive_link": receipt_result.drive_link,
                "filename": receipt_result.filename
            }
            # También agregar la URL del recibo al campo url_payment_receipt
            if receipt_result.drive_link:
                result["data"]["url_payment_receipt"] = receipt_result.drive_link
                transaction_ids = [t["transaction_id"] for t in result["data"].get("transactions", [])]
                print(f"[auto-payment] tx_ids={transaction_ids}, drive_link={receipt_result.drive_link}")
                await _persist_payment_receipt_url(db, transaction_ids, receipt_result.drive_link)

            ## Add status code and message
            result["status_code"] = 200
            result["message"] = "Pago registrado correctamente"
    except Exception as e:
        # Error handling for receipt generation
        pass
    
    return result


@router.post("/specific-payment", response_model=SpecificPaymentResponse)
async def register_specific_payments(
    request: SpecificPaymentRequest,
    db: DepDatabase,
    service: LoanPaymentService = Depends(get_loan_payment_service),
    image_service: PaymentImageService = Depends(get_payment_image_service),
    current_user: str = Depends(get_current_user)
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
    
    # Procesar imagen si se proporciona
    url_bank_receipt = request.url_bank_receipt
    if hasattr(request, 'image_file') and request.image_file:
        try:
            contract_id = str(request.contract_loan_id)
            image_result = await image_service.upload_payment_image(contract_id, request.reference, request.image_file, db)
            
            if image_result.get("success"):
                # Usar URL de Google Drive si está disponible, sino URL local
                if image_result.get("drive_success") and image_result.get("drive_view_link"):
                    url_bank_receipt = image_result.get("drive_view_link")
                else:
                    url_bank_receipt = image_result.get("local_path")
        except Exception as e:
            print(f"Error subiendo imagen: {e}")
    
    result = await service.register_specific_payments(
        contract_loan_id=request.contract_loan_id,
        payment_ids=request.payment_ids,
        amount=request.amount,
        payment_method=request.payment_method,
        reference=request.reference,
        transaction_date=transaction_date,
        notes=request.notes,
        url_bank_receipt=url_bank_receipt,
        url_payment_receipt=request.url_payment_receipt
    )
    
    # Retornar directamente el resultado sin lanzar excepciones
    return result


@router.post("/upload-payment-image", response_model=PaymentImageUploadResponse)
async def upload_payment_image(
    db: DepDatabase,
    contract_id: str = Form(..., description="ID del contrato (UUID)"),
    reference: str = Form(..., description="Referencia del pago (usado como nombre del archivo)"),
    image_file: UploadFile = File(..., description="Imagen del voucher de pago"),
    image_service: PaymentImageService = Depends(get_payment_image_service),
    current_user: str = Depends(get_current_user)
):
    """
    Subir imagen de voucher de pago a la carpeta payments del contrato
    
    Este endpoint:
    - Valida que la imagen sea de tipo permitido (JPEG, PNG, GIF)
    - Usa el contract_id directamente (UUID)
    - Crea la carpeta payments si no existe
    - Guarda la imagen localmente con el nombre basado en la referencia
    - Sube la imagen a Google Drive si está disponible
    - Devuelve las URLs tanto locales como de Google Drive
    
    Args:
        contract_id: ID del contrato (UUID)
        reference: Referencia del pago (usado como nombre del archivo)
        image_file: Archivo de imagen del voucher
        
    Returns:
        Información del archivo subido con URLs locales y de Google Drive
    """
    return await image_service.upload_payment_image_direct(contract_id, reference, image_file, db)


