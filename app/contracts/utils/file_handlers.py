from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime


def ensure_directories(base_dir: Path, template_dir: Path, contracts_dir: Path = None) -> None:
    """Crear directorios necesarios"""
    template_dir.mkdir(parents=True, exist_ok=True)
    
    # Solo crear directorio de contratos si se especifica
    if contracts_dir:
        contracts_dir.mkdir(parents=True, exist_ok=True)


def get_contract_folder(contracts_dir: Path, contract_id: str) -> Path:
    """Crear carpeta individual para el contrato"""
    folder = contracts_dir / contract_id
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "attachments").mkdir(parents=True, exist_ok=True)
    return folder


def save_metadata(folder: Path, contract_id: str, data: Dict[str, Any], version: int = 1) -> None:
    """Guardar metadatos del contrato"""
    metadata = {
        "contract_id": contract_id,
        "created_at": datetime.now().isoformat(),
        "modified_at": datetime.now().isoformat(),
        "original_data": data,
        "version": version,
        "storage_type": "local"  # Se puede cambiar dinámicamente
    }

    metadata_file = folder / "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)


def load_metadata(folder: Path) -> Dict[str, Any]:
    """Cargar metadatos del contrato"""
    metadata_file = folder / "metadata.json"
    if not metadata_file.exists():
        raise FileNotFoundError("Metadatos del contrato no encontrados")
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_contract_file_path(contract_folder: Path, contract_id: str) -> Path:
    """Obtener la ruta del archivo del contrato con nombre descriptivo"""
    contract_number = contract_id.replace("contract_", "")
    return contract_folder / f"{contract_number}.docx"


def get_attachments_folder(contract_folder: Path) -> Path:
    """Obtener la carpeta de archivos adjuntos"""
    return contract_folder / "attachments"


def count_attachments(contract_folder: Path) -> int:
    """Contar archivos adjuntos del contrato"""
    attachments_folder = get_attachments_folder(contract_folder)
    return len(list(attachments_folder.glob("*"))) if attachments_folder.exists() else 0


def get_file_size(file_path: Path) -> int:
    """Obtener tamaño del archivo en bytes"""
    return file_path.stat().st_size if file_path.exists() else 0
