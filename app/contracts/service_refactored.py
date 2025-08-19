from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import HTTPException, UploadFile
import os

from app.contracts.services.contract_list_service import ContractListService
from app.contracts.services.contract_generation_service import ContractGenerationService
from app.contracts.services.contract_file_service import ContractFileService
from app.contracts.services.contract_template_service import ContractTemplateService
from app.contracts.services.contract_metadata_service import ContractMetadataService
from app.contracts.utils.file_handlers import ensure_directories


class ContractService:
    """Servicio completo de contratos refactorizado con todas las funcionalidades"""

    def __init__(self, use_google_drive: bool = True):
        self.use_google_drive = use_google_drive
        self.base_dir = Path(__file__).parent.parent
        self.template_dir = self.base_dir / "templates"
        self.contracts_dir = self.base_dir / "generated_contracts"
        
        # Crear directorios necesarios
        ensure_directories(self.base_dir, self.template_dir, self.contracts_dir)
        
        # Inicializar servicios especializados
        self.list_service = ContractListService(self.contracts_dir)
        self.generation_service = ContractGenerationService(
            self.template_dir, 
            self.contracts_dir, 
            use_google_drive
        )
        self.file_service = ContractFileService(self.contracts_dir)
        self.template_service = ContractTemplateService(self.template_dir)
        self.metadata_service = ContractMetadataService(self.contracts_dir)

    async def list_contracts(self, db=None) -> Dict[str, Any]:
        """Listar todos los contratos"""
        return await self.list_service.list_contracts(db)

    async def generate_contract(self, data: Dict[str, Any], connection: Any = None) -> Dict[str, Any]:
        """Generar contrato completo"""
        return await self.generation_service.generate_contract(data, connection)

    async def update_contract(self, contract_id: str, updates: Dict[str, Any], connection=None) -> Dict[str, Any]:
        """Modificar contrato existente"""
        return await self.generation_service.update_contract(contract_id, updates, connection)

    async def upload_attachment(self, contract_id: str, file: UploadFile) -> Dict[str, Any]:
        """Subir archivo adjunto al contrato"""
        return await self.file_service.upload_attachment(contract_id, file)

    def get_contract_file(self, contract_id: str) -> Optional[bytes]:
        """Obtener contenido del archivo del contrato"""
        return self.file_service.get_contract_file(contract_id)

    def delete_contract_files(self, contract_id: str) -> bool:
        """Eliminar todos los archivos del contrato"""
        return self.file_service.delete_contract_files(contract_id)

    def get_contract_info(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Obtener información del archivo del contrato"""
        return self.file_service.get_contract_info(contract_id)

    def list_attachments(self, contract_id: str) -> list:
        """Listar archivos adjuntos del contrato"""
        return self.file_service.list_attachments(contract_id)

    def get_available_templates(self) -> list:
        """Obtener lista de plantillas disponibles"""
        return self.template_service.get_available_templates()

    def validate_template_data(self, data: Dict[str, Any]) -> list:
        """Validar datos para la plantilla"""
        return self.template_service.validate_template_data(data)

    def get_contract_metadata(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Obtener metadatos del contrato"""
        return self.metadata_service.load_contract_metadata(contract_id)

    def update_contract_metadata(self, contract_id: str, updates: Dict[str, Any]) -> bool:
        """Actualizar metadatos del contrato"""
        return self.metadata_service.update_contract_metadata(contract_id, updates)

    def get_contract_version(self, contract_id: str) -> int:
        """Obtener versión actual del contrato"""
        return self.metadata_service.get_contract_version(contract_id)

    def contract_exists(self, contract_id: str) -> bool:
        """Verificar si existe un contrato"""
        return self.metadata_service.contract_exists(contract_id)

    # Métodos de compatibilidad con el servicio original
    def _generate_contract_id(self, prefix: str = "contract") -> str:
        """Generar ID único para el contrato (método de compatibilidad)"""
        from datetime import datetime
        import uuid
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}_{timestamp}_{unique_id}"

    def _get_contract_folder(self, contract_id: str) -> Path:
        """Crear carpeta individual para el contrato (método de compatibilidad)"""
        from app.contracts.utils.file_handlers import get_contract_folder
        return get_contract_folder(self.contracts_dir, contract_id)

    def _save_metadata(self, folder: Path, contract_id: str, data: Dict[str, Any], version: int = 1):
        """Guardar metadatos del contrato (método de compatibilidad)"""
        from app.contracts.utils.file_handlers import save_metadata
        save_metadata(folder, contract_id, data, version)

    def _flatten_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Aplanar estructura JSON compleja (método de compatibilidad)"""
        from app.contracts.processors.contract_data_processor import ContractDataProcessor
        processor = ContractDataProcessor()
        return processor.flatten_data(data)

    def _select_template(self, data: Dict[str, Any]) -> Path:
        """Seleccionar plantilla apropiada (método de compatibilidad)"""
        return self.template_service.select_template(data)
