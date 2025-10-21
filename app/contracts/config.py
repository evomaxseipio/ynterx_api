# config.py
import os
from pathlib import Path
from typing import Optional


class ContractConfig:
    """Configuración centralizada del sistema de contratos"""


    # Configuración de Google Drive
    USE_GOOGLE_DRIVE: bool = os.getenv("USE_GOOGLE_DRIVE", "false").lower() == "true"
    GOOGLE_CREDENTIALS_PATH: Optional[str] = os.getenv("GOOGLE_CREDENTIALS_PATH")
    GOOGLE_DRIVE_FOLDER_ID: Optional[str] = os.getenv("GOOGLE_DRIVE_FOLDER_ID")


    # Configuración de archivos
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB por defecto
    ALLOWED_EXTENSIONS: set = {
        ext.strip() for ext in os.getenv(
            "ALLOWED_EXTENSIONS",
            ".jpg,.jpeg,.png,.gif,.bmp,.doc,.docx,.pdf,.xls,.xlsx"
        ).split(",")
    }

    # Configuración de directorios
    BASE_DIR: Path = Path(__file__).parent.parent
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    CONTRACTS_DIR: Path = BASE_DIR / "generated_contracts"

    # Configuración de plantillas
    DEFAULT_TEMPLATE: str = "default_template.docx"
    MORTGAGE_TEMPLATE: str = "mortgage_template.docx"



    @classmethod
    def validate_config(cls) -> dict:
        """Validar configuración y retornar estado"""
        issues = []

        # Validar Google Drive si está habilitado
        if cls.USE_GOOGLE_DRIVE:
            if not cls.GOOGLE_CREDENTIALS_PATH:
                issues.append("GOOGLE_CREDENTIALS_PATH not set")
            elif not Path(cls.GOOGLE_CREDENTIALS_PATH).exists():
                issues.append(f"Credentials file not found: {cls.GOOGLE_CREDENTIALS_PATH}")

        # Validar directorios
        if not cls.TEMPLATES_DIR.exists():
            issues.append(f"Templates directory not found: {cls.TEMPLATES_DIR}")

        # Validar que exista al menos una plantilla
        templates = list(cls.TEMPLATES_DIR.glob("*.docx")) if cls.TEMPLATES_DIR.exists() else []
        if not templates:
            issues.append("No Word templates found in templates directory")



        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "google_drive_enabled": cls.USE_GOOGLE_DRIVE,
            "templates_found": len(templates),
            "max_file_size_mb": cls.MAX_FILE_SIZE // (1024 * 1024)
        }

    @classmethod
    def get_info(cls) -> dict:
        """Obtener información completa de configuración"""
        validation = cls.validate_config()

        return {
            "google_drive": {
                "enabled": cls.USE_GOOGLE_DRIVE,
                "credentials_path": cls.GOOGLE_CREDENTIALS_PATH,
                "main_folder_id": cls.GOOGLE_DRIVE_FOLDER_ID
            },
            "directories": {
                "base": str(cls.BASE_DIR),
                "templates": str(cls.TEMPLATES_DIR),
                "contracts": str(cls.CONTRACTS_DIR)
            },
            "files": {
                "max_size_bytes": cls.MAX_FILE_SIZE,
                "max_size_mb": cls.MAX_FILE_SIZE // (1024 * 1024),
                "allowed_extensions": list(cls.ALLOWED_EXTENSIONS)
            },
            "templates": {
                "default": cls.DEFAULT_TEMPLATE,
                "mortgage": cls.MORTGAGE_TEMPLATE
            },
            "validation": validation
        }
