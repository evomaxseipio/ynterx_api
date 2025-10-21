from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from app.contracts.utils.file_handlers import save_metadata, load_metadata


class ContractMetadataService:
    """Servicio para manejo de metadatos de contratos"""
    
    def __init__(self, contracts_dir: Path):
        self.contracts_dir = contracts_dir
    
    def save_contract_metadata(self, contract_id: str, data: Dict[str, Any], version: int = 1, storage_type: str = "local") -> None:
        """Guardar metadatos del contrato"""
        contract_folder = self.contracts_dir / contract_id
        contract_folder.mkdir(parents=True, exist_ok=True)
        
        # Modificar el tipo de almacenamiento si se especifica
        metadata_data = data.copy()
        if storage_type != "local":
            metadata_data["storage_type"] = storage_type
        
        save_metadata(contract_folder, contract_id, metadata_data, version)
    
    def load_contract_metadata(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Cargar metadatos del contrato"""
        contract_folder = self.contracts_dir / contract_id
        
        try:
            return load_metadata(contract_folder)
        except FileNotFoundError:
            return None
    
    def update_contract_metadata(self, contract_id: str, updates: Dict[str, Any]) -> bool:
        """Actualizar metadatos del contrato"""
        contract_folder = self.contracts_dir / contract_id
        
        try:
            # Cargar metadatos existentes
            metadata = load_metadata(contract_folder)
            
            # Actualizar
            metadata.update(updates)
            metadata["modified_at"] = datetime.now().isoformat()
            
            # Guardar actualizado
            save_metadata(contract_folder, contract_id, metadata, metadata.get("version", 1))
            
            return True
        except Exception as e:
            print(f"Error actualizando metadatos del contrato {contract_id}: {e}")
            return False
    
    def increment_version(self, contract_id: str) -> Optional[int]:
        """Incrementar versión del contrato"""
        contract_folder = self.contracts_dir / contract_id
        
        try:
            metadata = load_metadata(contract_folder)
            new_version = metadata.get("version", 1) + 1
            metadata["version"] = new_version
            metadata["modified_at"] = datetime.now().isoformat()
            
            save_metadata(contract_folder, contract_id, metadata, new_version)
            
            return new_version
        except Exception as e:
            print(f"Error incrementando versión del contrato {contract_id}: {e}")
            return None
    
    def get_contract_version(self, contract_id: str) -> int:
        """Obtener versión actual del contrato"""
        metadata = self.load_contract_metadata(contract_id)
        return metadata.get("version", 1) if metadata else 1
    
    def contract_exists(self, contract_id: str) -> bool:
        """Verificar si existe un contrato"""
        contract_folder = self.contracts_dir / contract_id
        metadata_file = contract_folder / "metadata.json"
        return metadata_file.exists()
