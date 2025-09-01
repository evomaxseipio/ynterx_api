import os
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import HTTPException, UploadFile
import mimetypes
from sqlalchemy import select, text

try:
    from app.contracts.gdrive_service import GoogleDriveService
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from app.contracts.models import contract, contract_loan
from app.database import fetch_one


class PaymentImageService:
    """Servicio para manejar imágenes de vouchers de pagos"""
    
    def __init__(self, contracts_dir: Path, use_google_drive: bool = True):
        self.contracts_dir = contracts_dir
        self.use_google_drive = use_google_drive and GOOGLE_AVAILABLE
        self.gdrive_service = None
        
        if self.use_google_drive:
            try:
                self.gdrive_service = GoogleDriveService()
            except Exception as e:
                print(f"Google Drive no disponible: {e}")
                self.use_google_drive = False
    
    async def _get_contract_folder_path(self, contract_loan_id: int, db) -> str:
        """Obtener folder_path del contrato desde la base de datos"""
        print(f"🔍 Buscando folder_path para contract_loan_id: {contract_loan_id}")
        
        # Buscar contract_id usando contract_loan_id
        query = select(contract_loan.c.contract_id).where(
            contract_loan.c.contract_loan_id == contract_loan_id
        )
        loan_result = await fetch_one(query, connection=db)
        
        if not loan_result:
            raise HTTPException(404, f"Contract loan con ID {contract_loan_id} no encontrado")
        
        contract_id = loan_result["contract_id"]
        print(f"📋 Encontrado contract_id: {contract_id}")
        
        # Buscar folder_path del contrato
        contract_query = select(contract.c.folder_path).where(
            contract.c.contract_id == contract_id
        )
        contract_result = await fetch_one(contract_query, connection=db)
        
        if not contract_result or not contract_result["folder_path"]:
            raise HTTPException(404, f"Folder path no encontrado para contract_id {contract_id}")
        
        folder_path = contract_result["folder_path"]
        print(f"📁 Folder path encontrado: {folder_path}")
        
        return folder_path
    
    def _create_payments_folder(self, contract_folder_path: str, contract_loan_id: str = None) -> Path:
        """Crear carpeta payments en el contrato"""
        print(f"🏗️ Creando carpeta payments para: {contract_folder_path}")
        
        # Si es una URL de Google Drive, extraer el folder_id para usar en Google Drive
        if contract_folder_path.startswith('http'):
            folder_id = contract_folder_path.split('/')[-1]
            print(f"🌐 Folder ID extraído de URL: {folder_id}")
            
            # Para almacenamiento local, usar la carpeta del contrato
            if contract_loan_id:
                contract_path = self.contracts_dir / str(contract_loan_id) / "payments"
                contract_path.mkdir(parents=True, exist_ok=True)
                print(f"📂 URL detectada, usando carpeta local del contrato: {contract_path}")
                return contract_path
            else:
                # Fallback: usar carpeta general
                contract_path = self.contracts_dir / "payments"
                contract_path.mkdir(parents=True, exist_ok=True)
                print(f"📂 URL detectada, usando carpeta general: {contract_path}")
                return contract_path
        else:
            # Usar la ruta local del contrato
            contract_path = Path(contract_folder_path)
            payments_folder = contract_path / "payments"
            payments_folder.mkdir(parents=True, exist_ok=True)
            print(f"📂 Ruta local, usando carpeta: {payments_folder}")
            return payments_folder
    
    def _validate_image(self, file: UploadFile) -> None:
        """Validar archivo de imagen"""
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        
        if file.content_type not in allowed_types:
            raise HTTPException(400, f"Tipo de archivo no permitido. Solo se permiten: {', '.join(allowed_types)}")
        
        # Verificar tamaño (máximo 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if hasattr(file, 'size') and file.size > max_size:
            raise HTTPException(400, "Archivo demasiado grande. Máximo 10MB")
    
    def _get_file_extension(self, content_type: str) -> str:
        """Obtener extensión del archivo basado en content_type"""
        if content_type == 'image/jpeg' or content_type == 'image/jpg':
            return '.jpg'
        elif content_type == 'image/png':
            return '.png'
        elif content_type == 'image/gif':
            return '.gif'
        return '.jpg'  # Por defecto
    
    async def upload_payment_image(self, contract_loan_id: str, reference: str, image_file: UploadFile, db, file_bytes: bytes = None) -> Dict[str, Any]:
        """Subir imagen de voucher de pago"""
        try:
            # Validar imagen
            self._validate_image(image_file)
            
            # Obtener folder_path del contrato desde la base de datos
            contract_folder_path = await self._get_contract_folder_path(int(contract_loan_id), db)
            payments_folder = self._create_payments_folder(contract_folder_path, contract_loan_id)
            
            print(f"💾 Carpeta final seleccionada: {payments_folder}")
            
            # Generar nombre del archivo
            file_extension = self._get_file_extension(image_file.content_type)
            filename = f"{reference}{file_extension}"
            file_path = payments_folder / filename
            
            # Leer contenido del archivo solo si no se proporciona file_bytes
            if file_bytes is None:
                content = await image_file.read()
            else:
                content = file_bytes
            
            # Guardar archivo local
            with open(file_path, 'wb') as f:
                f.write(content)
            
            result = {
                "success": True,
                "message": "Imagen subida exitosamente",
                "filename": filename,
                "local_path": str(file_path),
                "size": len(content),
                "reference": reference
            }
            
            # Subir a Google Drive si está disponible
            if self.use_google_drive and self.gdrive_service:
                try:
                    # Obtener contract_id para usar en Google Drive
                    query = select(contract_loan.c.contract_id).where(
                        contract_loan.c.contract_loan_id == int(contract_loan_id)
                    )
                    loan_result = await fetch_one(query, connection=db)
                    contract_id = loan_result["contract_id"]
                    
                    # Extraer folder_id de la URL de Google Drive
                    if contract_folder_path.startswith('http'):
                        folder_id = contract_folder_path.split('/')[-1]
                        print(f"🌐 Usando folder_id de URL: {folder_id}")
                        drive_result = await self._upload_to_google_drive_with_folder_id(folder_id, file_path, filename)
                    else:
                        drive_result = await self._upload_to_google_drive(contract_id, file_path, filename)
                    
                    result.update(drive_result)
                except Exception as e:
                    result["drive_error"] = str(e)
                    result["drive_success"] = False
            
            return result
            
        except Exception as e:
            raise HTTPException(500, f"Error subiendo imagen: {str(e)}")
    
    async def _upload_to_google_drive(self, contract_id: str, file_path: Path, filename: str) -> Dict[str, Any]:
        """Subir imagen a Google Drive"""
        try:
            print(f"🌐 Subiendo a Google Drive para contract_id: {contract_id}")
            
            # Buscar carpeta del contrato en Google Drive usando el contract_id
            query = f"name='{contract_id}' and mimeType='application/vnd.google-apps.folder'"
            if self.gdrive_service.main_folder_id:
                query += f" and parents='{self.gdrive_service.main_folder_id}'"
            
            results = self.gdrive_service.service.files().list(
                q=query, 
                fields='files(id)', 
                supportsAllDrives=True, 
                includeItemsFromAllDrives=True
            ).execute()
            
            folders = results.get('files', [])
            if not folders:
                # Crear carpeta del contrato si no existe
                contract_folder_id = self.gdrive_service._create_contract_folder(contract_id)
            else:
                contract_folder_id = folders[0]['id']
            
            # Crear carpeta payments si no existe
            payments_query = f"name='payments' and mimeType='application/vnd.google-apps.folder' and parents='{contract_folder_id}'"
            payments_results = self.gdrive_service.service.files().list(
                q=payments_query, 
                fields='files(id)', 
                supportsAllDrives=True, 
                includeItemsFromAllDrives=True
            ).execute()
            
            payments_folders = payments_results.get('files', [])
            if not payments_folders:
                # Crear carpeta payments
                payments_metadata = {
                    'name': 'payments',
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [contract_folder_id]
                }
                payments_folder = self.gdrive_service.service.files().create(
                    body=payments_metadata, 
                    fields='id', 
                    supportsAllDrives=True
                ).execute()
                payments_folder_id = payments_folder.get('id')
            else:
                payments_folder_id = payments_folders[0]['id']
            
            # Subir archivo
            upload_result = self.gdrive_service._upload_file(file_path, payments_folder_id, filename)
            
            return {
                "drive_success": True,
                "drive_file_id": upload_result['file_id'],
                "drive_view_link": upload_result['web_view_link'],
                "drive_download_link": upload_result['download_link']
            }
            
        except Exception as e:
            return {
                "drive_success": False,
                "drive_error": str(e)
            }
    
    async def _upload_to_google_drive_with_folder_id(self, folder_id: str, file_path: Path, filename: str) -> Dict[str, Any]:
        """Subir imagen a Google Drive usando folder_id específico del contrato"""
        try:
            print(f"🌐 Subiendo a Google Drive usando folder_id del contrato: {folder_id}")
            
            # Crear carpeta payments dentro del contrato si no existe
            payments_query = f"name='payments' and mimeType='application/vnd.google-apps.folder' and parents='{folder_id}'"
            payments_results = self.gdrive_service.service.files().list(
                q=payments_query, 
                fields='files(id)', 
                supportsAllDrives=True, 
                includeItemsFromAllDrives=True
            ).execute()
            
            payments_folders = payments_results.get('files', [])
            if not payments_folders:
                # Crear carpeta payments dentro del contrato
                payments_metadata = {
                    'name': 'payments',
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [folder_id]
                }
                payments_folder = self.gdrive_service.service.files().create(
                    body=payments_metadata, 
                    fields='id', 
                    supportsAllDrives=True
                ).execute()
                payments_folder_id = payments_folder.get('id')
                print(f"📁 Carpeta payments creada dentro del contrato en Google Drive: {payments_folder_id}")
            else:
                payments_folder_id = payments_folders[0]['id']
                print(f"📁 Carpeta payments encontrada dentro del contrato en Google Drive: {payments_folder_id}")
            
            # Subir archivo a la carpeta payments del contrato
            upload_result = self.gdrive_service._upload_file(file_path, payments_folder_id, filename)
            print(f"✅ Archivo subido a la carpeta payments del contrato: {filename}")
            
            return {
                "drive_success": True,
                "drive_file_id": upload_result['file_id'],
                "drive_view_link": upload_result['web_view_link'],
                "drive_download_link": upload_result['download_link']
            }
            
        except Exception as e:
            print(f"❌ Error subiendo a Google Drive: {str(e)}")
            return {
                "drive_success": False,
                "drive_error": str(e)
            }
    
    async def upload_payment_image_direct(self, contract_id: str, reference: str, image_file: UploadFile, db, file_bytes: bytes = None) -> Dict[str, Any]:
        """Subir imagen de voucher de pago usando contract_id directamente"""
        try:
            # Validar imagen
            self._validate_image(image_file)
            
            # Obtener folder_path del contrato directamente usando contract_id
            contract_query = select(contract.c.folder_path).where(
                contract.c.contract_id == contract_id
            )
            contract_result = await fetch_one(contract_query, connection=db)
            
            if not contract_result or not contract_result["folder_path"]:
                raise HTTPException(404, f"Folder path no encontrado para contract_id {contract_id}")
            
            contract_folder_path = contract_result["folder_path"]
            print(f"📁 Folder path encontrado directamente: {contract_folder_path}")
            
            # Crear carpeta local usando contract_id
            payments_folder = self._create_payments_folder_direct(contract_folder_path, contract_id)
            
            print(f"💾 Carpeta final seleccionada: {payments_folder}")
            
            # Generar nombre del archivo
            file_extension = self._get_file_extension(image_file.content_type)
            filename = f"{reference}{file_extension}"
            file_path = payments_folder / filename
            
            # Leer contenido del archivo solo si no se proporciona file_bytes
            if file_bytes is None:
                content = await image_file.read()
            else:
                content = file_bytes
            
            # Guardar archivo local
            with open(file_path, 'wb') as f:
                f.write(content)
            
            result = {
                "success": True,
                "message": "Imagen subida exitosamente",
                "filename": filename,
                "local_path": str(file_path),
                "size": len(content),
                "reference": reference
            }
            
            # Subir a Google Drive si está disponible
            if self.use_google_drive and self.gdrive_service:
                try:
                    # Extraer folder_id de la URL de Google Drive
                    if contract_folder_path.startswith('http'):
                        folder_id = contract_folder_path.split('/')[-1]
                        print(f"🌐 Usando folder_id de URL: {folder_id}")
                        drive_result = await self._upload_to_google_drive_with_folder_id(folder_id, file_path, filename)
                    else:
                        drive_result = await self._upload_to_google_drive(contract_id, file_path, filename)
                    
                    result.update(drive_result)
                except Exception as e:
                    result["drive_error"] = str(e)
                    result["drive_success"] = False
            
            return result
            
        except Exception as e:
            raise HTTPException(500, f"Error subiendo imagen: {str(e)}")
    
    def _create_payments_folder_direct(self, contract_folder_path: str, contract_id: str) -> Path:
        """Crear carpeta payments usando contract_id directamente"""
        print(f"🏗️ Creando carpeta payments para contract_id: {contract_id}")
        
        # Si es una URL de Google Drive, usar la carpeta específica del contrato
        if contract_folder_path.startswith('http'):
            # Usar la carpeta específica del contrato: contracts/contract_id/payments/
            contract_path = self.contracts_dir / contract_id / "payments"
            contract_path.mkdir(parents=True, exist_ok=True)
            print(f"📂 URL detectada, usando carpeta específica del contrato: {contract_path}")
            return contract_path
        else:
            # Usar la ruta local del contrato
            contract_path = Path(contract_folder_path)
            payments_folder = contract_path / "payments"
            payments_folder.mkdir(parents=True, exist_ok=True)
            print(f"📂 Ruta local, usando carpeta: {payments_folder}")
            return payments_folder
