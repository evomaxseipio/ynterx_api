from typing import Dict, Any
from .receipt_schemas import ReceiptResponse
from .receipt_generator import ReceiptGenerator
from pathlib import Path
import tempfile
import os
from datetime import datetime


class ReceiptService:
    """Servicio simple para generar recibos"""
    
    def __init__(self):
        self.generator = ReceiptGenerator()
    
    async def generate_receipt_from_payment(self, payment_data: Dict[str, Any], db=None) -> ReceiptResponse:
        """
        Genera recibo a partir de datos de pago y lo sube a Google Drive
        
        Args:
            payment_data: Datos de la respuesta del auto-payment
            db: Conexión a la base de datos para Google Drive
            
        Returns:
            Recibo generado con imagen base64 y link de Google Drive
        """
        try:
            # Extraer datos necesarios
            payment_info = payment_data.get("data", payment_data)
            contract_loan_id = payment_info.get("contract_loan_id")
            
            # Generar imagen del recibo
            image_bytes = self.generator.generate_receipt(payment_info)
            image_base64 = self.generator.image_to_base64(image_bytes)
            
            # Generar ID único
            receipt_id = self.generator.generate_receipt_id()
            filename = f"receipt_{receipt_id}.png"
            
            # Subir a Google Drive si tenemos conexión a BD
            drive_link = None
            if db and contract_loan_id:
                try:
                    drive_result = await self._upload_receipt_to_drive(
                        contract_loan_id, receipt_id, image_bytes, db
                    )
                    if drive_result.get("drive_success"):
                        drive_link = drive_result.get("drive_view_link")
                except Exception:
                    pass
            
            return ReceiptResponse(
                success=True,
                message="Recibo generado exitosamente",
                receipt_id=receipt_id,
                image_base64=image_base64,
                drive_link=drive_link,
                filename=filename
            )
        except Exception as e:
            return ReceiptResponse(
                success=False,
                message=f"Error generando recibo: {str(e)}",
                receipt_id="",
                image_base64="",
                drive_link=None,
                filename=""
            )
    
    async def _upload_receipt_to_drive(self, contract_loan_id: int, receipt_id: str, image_bytes: bytes, db) -> Dict[str, Any]:
        """Sube el recibo a Google Drive en la carpeta payments del contrato"""
        try:
            # Importar el servicio de imágenes aquí para evitar importación circular
            from app.loan_payments.payment_image_service import PaymentImageService
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(image_bytes)
                temp_file_path = temp_file.name
            
            try:
                # Inicializar servicio de imágenes
                contracts_dir = Path("contracts")
                image_service = PaymentImageService(contracts_dir, use_google_drive=True)
                
                # Crear un objeto similar a UploadFile para el servicio de imágenes
                class MockUploadFile:
                    def __init__(self, content: bytes, filename: str):
                        self.content = content
                        self.filename = filename
                        self.content_type = 'image/png'
                        self.size = len(content)
                    
                    async def read(self):
                        return self.content
                
                mock_file = MockUploadFile(image_bytes, f"receipt_{receipt_id}.png")
                
                # Usar el servicio de imágenes para subir al Drive
                result = await image_service.upload_payment_image(
                    str(contract_loan_id),
                    f"receipt_{receipt_id}",
                    mock_file,
                    db,
                    file_bytes=image_bytes
                )
                
                return result
                
            finally:
                # Limpiar archivo temporal
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            return {
                "drive_success": False,
                "drive_error": str(e)
            }
    