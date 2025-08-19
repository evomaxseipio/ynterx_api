from typing import Dict, Any, Optional
from pathlib import Path
from fastapi import HTTPException


class GoogleDriveUtils:
    """Utilidades para integración con Google Drive"""
    
    def __init__(self, use_google_drive: bool = True):
        self.use_google_drive = use_google_drive
        self.gdrive_service = None
        
        if self.use_google_drive:
            self._init_google_drive()
    
    def _init_google_drive(self):
        """Inicializar servicio de Google Drive"""
        try:
            from app.contracts.gdrive_service import GoogleDriveService
            self.gdrive_service = GoogleDriveService()
        except ImportError:
            raise HTTPException(500, "Google Drive no configurado correctamente")
    
    def upload_contract(self, contract_id: str, file_path: Path, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Subir contrato a Google Drive"""
        if not self.use_google_drive or not self.gdrive_service:
            return {"drive_link": None, "drive_warning": "Google Drive no disponible"}
        
        try:
            return self.gdrive_service.upload_contract(contract_id, file_path, metadata)
        except Exception as e:
            return {"drive_link": None, "drive_warning": f"Error subiendo a Google Drive: {str(e)}"}
    
    def is_available(self) -> bool:
        """Verificar si Google Drive está disponible"""
        return self.use_google_drive and self.gdrive_service is not None
