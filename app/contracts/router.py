from fastapi import APIRouter, HTTPException, Response, UploadFile, File, Depends
from typing import Optional, Union
from .schemas import (
    ContractData,
    ContractUpdateData,
    ContractResponse,
    ContractListResponse,
    TemplateListResponse,
    FileUploadResponse,
    MortgageContractData
)
from .gdrive_service import GoogleDriveContractService
from .service import ContractService  # Keep original service as fallback
import os
from app.config import settings

# Initialize router
router = APIRouter(prefix="/contracts", tags=["contracts"])

# Choose service based on configuration
USE_GOOGLE_DRIVE = settings.USE_GOOGLE_DRIVE

def get_contract_service():
    """Get the appropriate contract service based on configuration"""
    print("USE_GOOGLE_DRIVE:", settings.USE_GOOGLE_DRIVE)
    if USE_GOOGLE_DRIVE:
        return GoogleDriveContractService()
    else:
        return ContractService()


@router.post("/generate", response_model=ContractResponse)
async def generate_contract(
    contract_data: Union[ContractData, MortgageContractData],
    service = Depends(get_contract_service)
):
    """
    Generate contract from template
    Acepta tanto datos simples como estructura de hipoteca
    """
    try:
        # Convertir a diccionario
        data_dict = contract_data.model_dump()

        # Usar tu servicio existente (sin await si es síncrono)
        result = service.generate_contract(data_dict)

        return ContractResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating contract: {str(e)}")

# AGREGAR ESTE ENDPOINT A TU router.py PARA DEBUGGING

@router.post("/debug/mortgage-data")
async def debug_mortgage_data(
    contract_data: Union[ContractData, MortgageContractData],
    service = Depends(get_contract_service)
):
    """
    DEBUG: Ver exactamente qué datos se están procesando
    """
    try:
        data_dict = contract_data.model_dump()

        print("=== DEBUG MORTGAGE DATA ===")
        print(f"Received data keys: {list(data_dict.keys())}")
        print(f"Is mortgage data: {service._is_mortgage_data(data_dict)}")

        # Si es hipoteca, procesar y mostrar
        if service._is_mortgage_data(data_dict):
            print("Processing as mortgage...")
            flat_data = service._convert_mortgage_to_flat_data(data_dict)

            print(f"Processed {len(flat_data)} fields:")
            for key, value in list(flat_data.items())[:20]:  # Primeros 20 campos
                print(f"  {key}: {value}")

            return {
                "success": True,
                "message": "Debug mortgage data processing",
                "original_data_keys": list(data_dict.keys()),
                "is_mortgage": True,
                "processed_fields_count": len(flat_data),
                "processed_fields": flat_data
            }
        else:
            print("Processing as standard contract...")
            return {
                "success": True,
                "message": "Debug standard contract data",
                "original_data_keys": list(data_dict.keys()),
                "is_mortgage": False,
                "data": data_dict
            }

    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Debug error: {str(e)}")

# MODIFICAR TU MÉTODO generate_contract EN service.py
# Agregar más logging para ver qué está pasando

def generate_contract(self, data: dict[str, str]) -> dict[str, str]:
    """
    Generate contract from template with provided data
    MODIFICADO: Con debugging extensivo
    """
    try:
        print("=== GENERATE CONTRACT DEBUG ===")
        print(f"1. Input data keys: {list(data.keys())}")

        # Detectar si es contrato hipotecario
        is_mortgage = self._is_mortgage_data(data)
        print(f"2. Is mortgage: {is_mortgage}")

        if is_mortgage:
            print("3. Converting mortgage data to flat structure...")
            original_data = data.copy()  # Guardar original
            data = self._convert_mortgage_to_flat_data(data)
            print(f"4. Converted to {len(data)} flat fields")
            print(f"5. Sample converted fields:")
            for key, value in list(data.items())[:10]:
                print(f"   {key}: {value}")
            contract_id = self._generate_contract_id().replace("contract_", "mortgage_")
        else:
            print("3. Using standard contract data")
            contract_id = self._generate_contract_id()

        # Crear carpeta del contrato
        contract_folder = self._create_contract_folder(contract_id)
        print(f"6. Created folder: {contract_folder}")

        # Seleccionar template apropiado
        template_path = self._select_template_for_contract(data)
        print(f"7. Selected template: {template_path}")

        # Load template
        print("8. Loading template...")
        doc = DocxTemplate(template_path)

        # Clean data to avoid template issues
        print("9. Cleaning data for template...")
        cleaned_data = self._clean_data_for_template(data)
        print(f"10. Cleaned data has {len(cleaned_data)} fields")

        # LOG: Mostrar datos que van al template
        print("11. Data going to template:")
        for key, value in list(cleaned_data.items())[:15]:
            print(f"    {key}: {value}")

        # Render template with data
        print("12. Rendering template...")
        try:
            doc.render(cleaned_data)
            print("13. Template rendered successfully!")
        except Exception as e:
            print(f"❌ Template rendering error: {str(e)}")
            print(f"Available fields in data: {list(cleaned_data.keys())}")
            shutil.rmtree(contract_folder)
            raise HTTPException(
                status_code=400,
                detail=f"Error processing template. Available fields: {list(cleaned_data.keys())[:10]}... Error: {str(e)}"
            )

        # Generate filename and save
        filename = self._generate_filename(contract_id)
        output_path = contract_folder / filename
        doc.save(output_path)
        print(f"14. Saved contract: {output_path}")

        # Save metadata
        self._save_metadata(contract_folder, contract_id, cleaned_data)
        print("15. Metadata saved")

        return {
            "success": True,
            "message": "Contract generated successfully",
            "contract_id": contract_id,
            "filename": filename,
            "path": str(output_path),
            "folder_path": str(contract_folder),
            "processed_data": cleaned_data
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# VERIFICAR TU MÉTODO _is_mortgage_data
def _is_mortgage_data(self, data: dict[str, str]) -> bool:
    """
    Detecta automáticamente si los datos son de contrato hipotecario
    CON DEBUGGING
    """
    # Buscar campos característicos de estructura de hipoteca
    mortgage_indicators = ['loan', 'properties', 'clients', 'investors', 'witnesses', 'notaries']

    found_indicators = []
    for indicator in mortgage_indicators:
        if indicator in data:
            found_indicators.append(indicator)

    is_mortgage = len(found_indicators) >= 4

    print(f"DEBUG _is_mortgage_data:")
    print(f"  Found indicators: {found_indicators}")
    print(f"  Is mortgage: {is_mortgage}")

    return is_mortgage


# AGREGAR ENDPOINT PARA VALIDAR DATOS (opcional pero útil)
@router.post("/validate")
async def validate_contract_data(
    contract_data: Union[ContractData, MortgageContractData]
):
    """
    Validate contract data structure

    - Para contratos simples: valida campos básicos
    - Para hipotecas: procesa estructura compleja y muestra campos generados
    """
    try:
        data_dict = contract_data.model_dump()

        # Verificar si es hipoteca
        if 'loan' in data_dict and 'properties' in data_dict:
            # Es hipoteca - mostrar campos procesados
            from .service import ContractService
            service = ContractService()
            flat_data = service._convert_mortgage_to_flat_data(data_dict)

            return {
                "success": True,
                "message": "Mortgage contract data validated",
                "contract_type": "mortgage",
                "fields_processed": len(flat_data),
                "sample_fields": {k: v for k, v in list(flat_data.items())[:15]}
            }
        else:
            # Es contrato simple
            return {
                "success": True,
                "message": "Standard contract data validated",
                "contract_type": "standard",
                "fields_count": len(data_dict)
            }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid contract data: {str(e)}")




@router.post("/{contract_id}/upload")
async def upload_attachment(
    contract_id: str,
    file: UploadFile = File(...),
    service = Depends(get_contract_service)
):
    """
    Upload attachment file to contract folder in Google Drive or local storage
    """
    return service.upload_attachment(contract_id, file)

@router.get("/list")
async def list_contracts(
    service = Depends(get_contract_service)
):
    """
    List all generated contracts
    """
    return service.list_contracts()

@router.get("/{contract_id}/download")
async def download_contract(
    contract_id: str,
    service = Depends(get_contract_service)
):
    """
    Download the contract file
    """
    if USE_GOOGLE_DRIVE:
        file_content = service.download_contract(contract_id)
        filename = f"{contract_id}.docx"
    else:
        file_path = service.get_contract_file(contract_id)
        with open(file_path, "rb") as file:
            file_content = file.read()
        filename = file_path.name

    return Response(
        content=file_content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.get("/{contract_id}/drive-link")
async def get_drive_link(
    contract_id: str,
    service = Depends(get_contract_service)
):
    """
    Get Google Drive folder link for the contract (only works with Google Drive service)
    """
    if not USE_GOOGLE_DRIVE:
        raise HTTPException(
            status_code=400,
            detail="Google Drive integration is not enabled"
        )

    drive_link = service.get_drive_folder_link(contract_id)

    return {
        "success": True,
        "contract_id": contract_id,
        "drive_link": drive_link,
        "message": "Click the link to access the contract folder in Google Drive"
    }

@router.get("/drive/test-connection")
async def test_drive_connection():
    """
    Test Google Drive connection
    """
    if not USE_GOOGLE_DRIVE:
        return {
            "success": False,
            "message": "Google Drive integration is not enabled. Set USE_GOOGLE_DRIVE=true in environment variables."
        }

    service = GoogleDriveContractService()
    return service.test_drive_connection()

@router.get("/config/info")
async def get_config_info():
    """
    Get current configuration information
    """
    return {
        "use_google_drive": USE_GOOGLE_DRIVE,
        "storage_type": "Google Drive" if USE_GOOGLE_DRIVE else "Local Storage",
        "google_credentials_configured": bool(os.getenv('GOOGLE_CREDENTIALS_PATH')),
        "drive_folder_id": os.getenv('GOOGLE_DRIVE_FOLDER_ID', 'Not set (will be created automatically)')
    }

# Backward compatibility endpoints for local storage
@router.patch("/{contract_id}/update")
async def update_contract(
    contract_id: str,
    data: ContractUpdateData
):
    """
    Update existing contract (currently only supported with local storage)
    """
    if USE_GOOGLE_DRIVE:
        raise HTTPException(
            status_code=501,
            detail="Contract update is not yet implemented for Google Drive. Use local storage or regenerate the contract."
        )

    service = ContractService()
    context = data.dict(exclude_unset=True)
    if data.additional_data:
        context.update(data.additional_data)

    return service.update_contract(contract_id, context)

@router.get("/{contract_id}/attachments")
async def list_attachments(
    contract_id: str
):
    """
    List all attachments for a specific contract
    """
    if USE_GOOGLE_DRIVE:
        # For Google Drive, we need to implement this in the service
        raise HTTPException(
            status_code=501,
            detail="Attachment listing for Google Drive is not yet implemented. Check the Drive folder directly."
        )
    else:
        service = ContractService()
        return service.list_attachments(contract_id)

@router.get("/{contract_id}/details")
async def get_contract_details(
    contract_id: str
):
    """
    Get detailed information about a contract
    """
    if USE_GOOGLE_DRIVE:
        raise HTTPException(
            status_code=501,
            detail="Contract details for Google Drive is not yet implemented. Use the drive link to access files."
        )
    else:
        service = ContractService()
        return service.get_contract_details(contract_id)

@router.delete("/{contract_id}/delete")
async def delete_contract(
    contract_id: str
):
    """
    Delete contract and all its attachments
    """
    if USE_GOOGLE_DRIVE:
        raise HTTPException(
            status_code=501,
            detail="Contract deletion for Google Drive is not yet implemented. Delete manually from Drive."
        )
    else:
        service = ContractService()
        return service.delete_contract(contract_id)

@router.get("/templates")
async def list_templates(
    service = Depends(get_contract_service)
):
    """
    List all available templates
    """
    return service.list_templates()

@router.get("/test-template")
async def test_template(
    service = Depends(get_contract_service)
):
    """
    Test template with minimal data
    """
    return service.test_template()

@router.get("/example-data")
async def get_example_data(
    service = Depends(get_contract_service)
):
    """
    Get example data structure
    """
    return service.get_example_data()
