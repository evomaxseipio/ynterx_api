from typing import Dict, Any, Optional, List
from pathlib import Path
from fastapi import HTTPException, UploadFile
import shutil
from app.contracts.utils.file_handlers import (
    get_contract_folder, 
    get_contract_file_path, 
    get_attachments_folder,
    count_attachments,
    get_file_size
)


class ContractFileService:
    """Servicio para manejo de archivos de contratos"""
    
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.doc', '.docx', '.pdf', '.xls', '.xlsx'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self, contracts_dir: Path):
        self.contracts_dir = contracts_dir
    
    def save_contract_file(self, contract_id: str, content: bytes) -> str:
        """Guardar archivo del contrato"""
        contract_folder = get_contract_folder(self.contracts_dir, contract_id)
        file_path = get_contract_file_path(contract_folder, contract_id)
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return str(file_path)
    
    def get_contract_file(self, contract_id: str) -> Optional[bytes]:
        """Obtener contenido del archivo del contrato"""
        contract_folder = self.contracts_dir / contract_id
        file_path = get_contract_file_path(contract_folder, contract_id)
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'rb') as f:
            return f.read()
    
    def delete_contract_files(self, contract_id: str) -> bool:
        """Eliminar todos los archivos del contrato"""
        contract_folder = self.contracts_dir / contract_id
        
        if not contract_folder.exists():
            return False
        
        try:
            shutil.rmtree(contract_folder)
            return True
        except Exception as e:
            print(f"Error eliminando archivos del contrato {contract_id}: {e}")
            return False
    
    async def upload_attachment(self, contract_id: str, file: UploadFile) -> Dict[str, Any]:
        """Subir archivo adjunto al contrato"""
        contract_folder = self.contracts_dir / contract_id

        if not contract_folder.exists():
            raise HTTPException(404, "Contrato no encontrado")

        # Validar archivo
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(400, f"Tipo de archivo no permitido: {file_extension}")

        # Verificar tamaño
        content = await file.read()
        if len(content) > self.MAX_FILE_SIZE:
            raise HTTPException(400, "Archivo demasiado grande (máximo 10MB)")

        # Guardar archivo
        attachments_folder = get_attachments_folder(contract_folder)
        file_path = attachments_folder / file.filename

        with open(file_path, 'wb') as f:
            f.write(content)

        return {
            "success": True,
            "message": "Archivo subido exitosamente",
            "filename": file.filename,
            "size": len(content),
            "path": str(file_path)
        }
    
    def get_contract_info(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Obtener información del archivo del contrato"""
        contract_folder = self.contracts_dir / contract_id
        file_path = get_contract_file_path(contract_folder, contract_id)
        
        if not file_path.exists():
            return None
        
        return {
            "contract_id": contract_id,
            "file_path": str(file_path),
            "file_size": get_file_size(file_path),
            "attachments_count": count_attachments(contract_folder),
            "exists": True
        }
    
    def list_attachments(self, contract_id: str) -> List[Dict[str, Any]]:
        """Listar archivos adjuntos del contrato"""
        contract_folder = self.contracts_dir / contract_id
        attachments_folder = get_attachments_folder(contract_folder)
        
        if not attachments_folder.exists():
            return []
        
        attachments = []
        for file_path in attachments_folder.iterdir():
            if file_path.is_file():
                attachments.append({
                    "filename": file_path.name,
                    "size": get_file_size(file_path),
                    "path": str(file_path)
                })
        
        return attachments
