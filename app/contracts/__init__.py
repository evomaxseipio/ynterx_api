# __init__.py
"""
Sistema Completo de Contratos para Ynterx API (v3.0.0 - Refactorizado)

Características principales:
✅ Generación de contratos desde plantillas Word (.docx)
✅ Almacenamiento local con carpetas organizadas por contrato
✅ Integración opcional con Google Drive
✅ Subida de archivos adjuntos con validación
✅ Modificación de contratos existentes con versionado
✅ API REST completa con 15+ endpoints
✅ Soporte para estructuras complejas (hipotecas, préstamos, etc.)
✅ Metadatos automáticos y historial de cambios
✅ Descarga de contratos y archivos adjuntos
✅ Sistema de configuración flexible
✅ Arquitectura modular y escalable (REFACTORIZADO)
✅ Servicios especializados por responsabilidad
✅ Procesadores de datos separados
✅ Utilidades reutilizables
✅ Validadores robustos
✅ Base de datos integrada para listado de contratos

Tipos de contratos soportados:
- Contratos simples (campos directos)
- Hipotecas (estructura compleja con clientes, inversionistas, propiedades)
- Préstamos personales
- Cualquier tipo personalizado

Plantillas soportadas:
- Sintaxis docxtpl: {{variable_name}}
- Campos planos para máxima compatibilidad
- Detección automática de tipo de contrato
- Plantillas específicas por tipo (mortgage_template.docx, etc.)

Archivos adjuntos permitidos:
- Imágenes: .jpg, .jpeg, .png, .gif, .bmp
- Documentos: .doc, .docx, .pdf
- Hojas de cálculo: .xls, .xlsx
- Tamaño máximo: 10MB por archivo

Google Drive (opcional):
- Almacenamiento automático en carpetas organizadas
- Enlaces compartibles públicos
- Sincronización bidireccional
- Service Account authentication
- Carpeta principal: Ynterx_Contracts/

Estructura de carpetas:
├── templates/              # Plantillas Word
├── generated_contracts/    # Contratos locales
│   ├── contract_20250114_143025_abc123/
│   │   ├── contract_20250114_143025_abc123.docx
│   │   ├── metadata.json
│   │   └── attachments/
│   │       ├── documento1.pdf
│   │       └── imagen1.jpg
│   └── mortgage_20250114_150000_def456/
└── .env                   # Variables de entorno
"""

from .service import ContractService
from .router import router
from .schemas import *
from .config import ContractConfig
from .paragraphs import (
    get_paragraph_from_db,
    process_paragraph,
    get_all_paragraphs_for_contract,
    get_investor_paragraph,
    get_client_paragraph,
    get_witness_paragraph,
    get_notary_paragraph
)

# Importar nuevos servicios refactorizados
from .services import (
    ContractListService,
    ContractGenerationService,
    ContractFileService,
    ContractTemplateService,
    ContractMetadataService
)

# Importar procesadores
from .processors import (
    ContractDataProcessor,
    ParticipantDataProcessor
)

# Importar utilidades
from .utils import (
    format_full_name,
    format_dates,
    ensure_directories,
    get_contract_folder,
    GoogleDriveUtils
)

# Importar validadores
from .validators import (
    ContractValidator,
    DataValidator
)

# Importación condicional de Google Drive
try:
    from .gdrive_service import GoogleDriveService
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GoogleDriveService = None
    GOOGLE_DRIVE_AVAILABLE = False

__version__ = "3.0.0"
__author__ = "Ynterx Development Team"

__all__ = [
    # Servicio principal
    "ContractService",

    # Router FastAPI
    "router",

    # Configuración
    "ContractConfig",

    # Funciones de párrafos desde DB
    "get_paragraph_from_db",
    "process_paragraph",
    "get_all_paragraphs_for_contract",
    "get_investor_paragraph",
    "get_client_paragraph",
    "get_witness_paragraph",
    "get_notary_paragraph",

    # Servicios refactorizados
    "ContractListService",
    "ContractGenerationService",
    "ContractFileService",
    "ContractTemplateService",
    "ContractMetadataService",

    # Procesadores
    "ContractDataProcessor",
    "ParticipantDataProcessor",

    # Utilidades
    "format_full_name",
    "format_dates",
    "ensure_directories",
    "get_contract_folder",
    "GoogleDriveUtils",

    # Validadores
    "ContractValidator",
    "DataValidator",

    # Schemas principales
    "ContractData",
    "ContractResponse",
    "UpdateResponse",
    "UploadResponse",
    "DeleteResponse",
    "ContractListResponse",
    "SystemInfo",

    # Schemas de estructura compleja
    "Loan",
    "Property",
    "Client",
    "Investor",
    "Witness",
    "Notary",

    # Google Drive (si está disponible)
    "GoogleDriveService",
    "GOOGLE_DRIVE_AVAILABLE",

    # Metadatos
    "__version__",
    "__author__"
]

def get_system_status() -> dict:
    """Obtener estado completo del sistema"""
    config_info = ContractConfig.get_info()

    return {
        "system": "Ynterx Contract System",
        "version": __version__,
        "status": "operational",
        "google_drive_available": GOOGLE_DRIVE_AVAILABLE,
        "configuration": config_info,
        "endpoints_available": [
            "POST /contracts/generate",
            "PATCH /contracts/{id}/update",
            "POST /contracts/{id}/upload",
            "GET /contracts/list",
            "GET /contracts/{id}/download",
            "GET /contracts/{id}/attachments",
            "GET /contracts/{id}/attachments/{filename}",
            "DELETE /contracts/{id}",
            "DELETE /contracts/{id}/attachments/{filename}",
            "GET /contracts/info",
            "GET /contracts/{id}/metadata",
            "GET /contracts/drive/test-connection",
            "GET /contracts/{id}/drive-link"
        ]
    }

# Configuración inicial automática
def setup_directories():
    """Crear directorios necesarios al importar el módulo"""
    ContractConfig.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    ContractConfig.CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)

# Ejecutar setup al importar
setup_directories()
