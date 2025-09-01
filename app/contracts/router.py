# router_clean.py
from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request
from fastapi.responses import FileResponse
from typing import Dict, Any, Optional, List
from pathlib import Path
import os
import uuid
import json
from datetime import datetime, date


from app.auth.dependencies import DepCurrentUser
from .service import ContractService
from .services import ContractListService
from .schemas import *
from .loan_property_schemas import *
from app.database import DepDatabase, fetch_one, execute
from app.contracts.models import contract as contract_table, contract_participant as contract_participant_table
from app.contracts.loan_property_service import ContractLoanPropertyService
from app.contracts.participant_service import ParticipantService
from app.contracts.contract_creation_service import ContractCreationService
from app.person.service import PersonService
from app.person.schemas import PersonCompleteCreate, PersonDocumentCreate, PersonAddressCreate
from sqlalchemy import text as sql_text

load_dotenv()

router = APIRouter(prefix="/contracts", tags=["contracts"])

def get_contract_service() -> ContractService:
    """Dependency para obtener servicio de contratos"""
    use_google_drive = os.getenv("USE_GOOGLE_DRIVE", "false").lower() == "true"
    return ContractService(use_google_drive=use_google_drive)


def get_participant_service() -> ParticipantService:
    """Dependency para obtener servicio de participantes"""
    return ParticipantService()


def get_contract_creation_service() -> ContractCreationService:
    """Dependency para obtener servicio de creación de contratos"""
    return ContractCreationService()


@router.post("/generate-complete", response_model=ContractResponse)
async def generate_contract_complete(
    data: Dict[str, Any],  # JSON complejo directo
    db: DepDatabase,
    request: Request,  # ✅ AGREGADO para acceder al pool asyncpg
    service: ContractService = Depends(get_contract_service),
    participant_service: ParticipantService = Depends(get_participant_service),
    contract_creation_service: ContractCreationService = Depends(get_contract_creation_service)
) -> Dict[str, Any]:
    """
    Generar contrato completo desde JSON estructurado con personas, propiedades y préstamo.

    Este endpoint maneja contratos complejos como hipotecas con:
    - Múltiples clientes, inversionistas, testigos, notarios, referentes
    - Propiedades con detalles completos
    - Información de préstamos
    - Generación automática de personas en la BD
    - Reutilización de personas existentes
    """

    # 1. PROCESAR TODAS LAS PERSONAS del JSON
    participants_for_contract, participant_errors, processed_persons_summary = await participant_service.process_all_participants(data, request)

    print(f"📊 Resumen procesamiento personas:")
    print(f"   Total: {processed_persons_summary['total']}")
    print(f"   Exitosos: {processed_persons_summary['successful']}")
    print(f"   Nuevas: {processed_persons_summary['successful'] - processed_persons_summary['existing'] - processed_persons_summary['reused']}")
    print(f"   Existentes: {processed_persons_summary['existing']}")
    print(f"   Reutilizadas: {processed_persons_summary['reused']}")
    print(f"   Errores: {processed_persons_summary['errors']}")
    
    print(f"📋 Participantes para contrato: {len(participants_for_contract)}")
    for p in participants_for_contract:
        print(f"  - {p['role']}: {p['person_id']} (Type: {p['person_role_id']})")

    # Validar que se procesaron personas mínimas
    if participant_errors and processed_persons_summary["successful"] == 0:
        raise HTTPException(400, detail={
            "message": "Error procesando todas las personas",
            "errors": participant_errors,
            "summary": processed_persons_summary
        })

    # 2. GENERAR CONTRACT_NUMBER usando función SQL
    contract_type_name = data.get("contract_type", "mortgage")
    contract_number = await contract_creation_service.generate_contract_number(contract_type_name, db)

    # 3. CREAR CONTRATO EN LA BASE DE DATOS
    contract_id = await contract_creation_service.create_contract_record(data, contract_number, db)

    # 4. REGISTRAR PARTICIPANTES EN contract_participant
    print(f"🔍 DEBUG: Insertando {len(participants_for_contract)} participantes en contract_participant")
    participant_db_errors = await contract_creation_service.register_contract_participants(contract_id, participants_for_contract, db)

    if participant_db_errors:
        print(f"⚠️ Errores insertando participantes: {len(participant_db_errors)} errores")
        for error in participant_db_errors:
            print(f"  - {error['role']}: {error['error']}")
    else:
        print(f"👥 Registrados {len(participants_for_contract)} participantes en BD exitosamente")

    # 5. CREAR RELACIONES CLIENTE-REFERIDOR
    print("🔗 LLEGANDO A LA SECCIÓN DE CLIENT_REFERRER")
    client_referrer_created, client_referrer_errors = await contract_creation_service.create_client_referrer_relationships(participants_for_contract, db)
    
    if client_referrer_created > 0:
        print(f"🔗 Creadas {client_referrer_created} relaciones cliente-referidor exitosamente")
    if client_referrer_errors:
        print(f"⚠️ Errores en relaciones cliente-referidor: {len(client_referrer_errors)} errores")
        for error in client_referrer_errors:
            print(f"  - {error['client_id']} ↔ {error['referrer_id']}: {error['error']}")
    else:
        print(f"🔗 No se crearon relaciones cliente-referidor (sin errores)")

    # 6. CREAR LOAN Y PROPERTIES
    loan_property_result = None
    loan_property_errors = []

    if data.get("loan") or data.get("properties"):
        try:
            loan_property_result = await ContractLoanPropertyService.create_contract_loan_and_properties(
                contract_id=contract_id,
                loan_data=data.get("loan"),
                properties_data=data.get("properties", []),
                connection=db,
                contract_context=data
            )

            if loan_property_result["overall_success"]:
                pass
            else:
                # Recolectar errores específicos
                if loan_property_result.get("loan_result") and not loan_property_result["loan_result"].get("success"):
                    loan_property_errors.append({
                        "type": "loan",
                        "error": loan_property_result["loan_result"].get("message", "Error desconocido en loan")
                    })

                if loan_property_result.get("bank_account_result") and not loan_property_result["bank_account_result"].get("success"):
                    loan_property_errors.append({
                        "type": "bank_account",
                        "error": loan_property_result["bank_account_result"].get("message", "Error desconocido en bank account")
                    })

                if loan_property_result.get("properties_result") and not loan_property_result["properties_result"].get("success"):
                    loan_property_errors.append({
                        "type": "properties",
                        "error": loan_property_result["properties_result"].get("message", "Error desconocido en properties")
                    })

        except Exception as e:
            loan_property_errors.append({
                "type": "general",
                "error": f"Error general procesando loan/properties: {str(e)}"
            })
            loan_property_result = {
                "overall_success": False,
                "message": f"Error general: {str(e)}"
            }

    # 7. GENERAR DOCUMENTO WORD usando tu servicio existente
    enhanced_data = data.copy()
    enhanced_data.update({
        "contract_id": str(contract_id),
        "contract_number": contract_number,
        "generated_at": datetime.now().isoformat(),
        "loan_property_result": loan_property_result
    })

    try:
        document_result = await service.generate_contract(enhanced_data, connection=db)
        await contract_creation_service.update_contract_with_document_info(contract_id, document_result, db)

    except Exception as e:
        document_result = {
            "success": False,
            "error": str(e),
            "message": f"Error generando documento: {str(e)}"
        }

    # 8. RESPUESTA FINAL
    # Determinar qué URLs usar: Google Drive si está disponible, sino rutas locales
    file_path = document_result.get("path", "")
    folder_path = document_result.get("folder_path", "")
    
    # Si Google Drive está habilitado y se subió exitosamente, usar URLs de Drive
    if document_result.get("drive_success") and document_result.get("drive_link"):
        file_path = document_result.get("drive_view_link", file_path)
        folder_path = document_result.get("drive_link", folder_path)
    
    return ContractResponse(
        success=True,
        message="Contrato completo generado exitosamente",
        contract_id=str(contract_id),
        contract_number=contract_number,
        filename=document_result.get("filename", f"{contract_number}.docx"),
        path=file_path,
        folder_path=folder_path,
        processed_data={
            "persons_summary": processed_persons_summary,
            "participants_count": len(participants_for_contract),
            "contract_type": data.get("contract_type", "unknown"),
            "loan_amount": data.get("loan", {}).get("amount"),
            "properties_count": len(data.get("properties", [])),
            "persons_detail": {
                "new_persons": processed_persons_summary['successful'] - processed_persons_summary['existing'] - processed_persons_summary['reused'],
                "existing_persons": processed_persons_summary['existing'],
                "reused_persons": processed_persons_summary['reused'],
                "total_successful": processed_persons_summary['successful']
            }
        },
        # Incluir información de Google Drive
        drive_success=document_result.get("drive_success"),
        drive_folder_id=document_result.get("drive_folder_id"),
        drive_file_id=document_result.get("drive_file_id"),
        drive_link=document_result.get("drive_link"),
        drive_view_link=document_result.get("drive_view_link"),
        warnings={
            "person_errors": participant_errors,
            "message": f"Se procesaron {processed_persons_summary['successful']} personas exitosamente ({processed_persons_summary['reused']} reutilizadas), {processed_persons_summary['errors']} errores reales"
        } if participant_errors else None
    )


# ✅ Endpoint para validar datos antes de crear
@router.post("/validate-complete", response_model=Dict[str, Any])
async def validate_contract_complete(
    data: ContractCompleteRequest,
    _: DepCurrentUser
) -> Dict[str, Any]:
    """
    Validar datos de contrato completo sin crear el registro.
    Útil para validación frontend antes de envío.
    """
    try:
        # Si llegamos aquí, la validación de Pydantic pasó
        validation_summary = {
            "contract_type": data.contract_type,
            "has_loan": data.loan is not None,
            "has_properties": data.properties is not None and len(data.properties) > 0,
            "participants_count": {
                "clients": len(data.clients) if data.clients else 0,
                "investors": len(data.investors) if data.investors else 0,
                "witnesses": len(data.witnesses) if data.witnesses else 0,
                "notaries": len(data.notaries) if data.notaries else 0,
                "referrers": len(data.referrers) if data.referrers else 0
            }
        }

        return {
            "valid": True,
            "message": "Contract data is valid",
            "summary": validation_summary,
            "total_participants": sum(validation_summary["participants_count"].values())
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Validation error: {str(e)}",
            "errors": [str(e)]
        }


@router.get("/list", response_model=ContractListResponse)
async def list_contracts(
    _: DepCurrentUser,
    request: Request,
) -> Dict[str, Any]:
    """
    Listar todos los contratos generados desde la base de datos

    Incluye metadatos, versiones y conteo de archivos adjuntos
    """
    async with request.app.state.db_pool.acquire() as connection:
        result = await ContractListService.get_contracts(connection=connection)
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=404 if result.get("error") == "NO_DATA" else 500,
                detail=result.get("message", "Error al obtener contratos")
            )
        
        return result
@router.get("/{contract_id}/download")
async def download_contract(
    contract_id: str,
    service: ContractService = Depends(get_contract_service)
) -> FileResponse:
    """Descargar archivo de contrato"""
    contract_folder = service.contracts_dir / contract_id
    contract_file = contract_folder / f"{contract_id}.docx"

    if not contract_file.exists():
        raise HTTPException(404, "Contrato no encontrado")

    return FileResponse(
        path=contract_file,
        filename=f"{contract_id}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@router.patch("/{contract_id}/update", response_model=UpdateResponse)
async def update_contract(
    contract_id: str,
    updates: Dict[str, Any],
    db: DepDatabase,
    service: ContractService = Depends(get_contract_service),
    contract_creation_service: ContractCreationService = Depends(get_contract_creation_service)
) -> Dict[str, Any]:
    """
    Modificar contrato existente

    Actualiza campos específicos y regenera el documento
    con nueva versión automáticamente.
    """
    try:
        # Actualizar contrato usando el servicio
        document_result = await service.update_contract(contract_id, updates, connection=db)
        
        # Actualizar información en la base de datos con URLs de Google Drive
        await contract_creation_service.update_contract_with_document_info(contract_id, document_result, db)
        
        return document_result
    except Exception as e:
        raise HTTPException(500, f"Error actualizando contrato: {str(e)}")


@router.delete("/{contract_id}", response_model=DeleteResponse)
async def delete_contract(
    contract_id: str,
    service: ContractService = Depends(get_contract_service)
) -> Dict[str, Any]:
    """
    Eliminar contrato y todos sus archivos

    CUIDADO: Esta acción no se puede deshacer
    """
    contract_folder = service.contracts_dir / contract_id

    if not contract_folder.exists():
        raise HTTPException(404, "Contrato no encontrado")

    # Eliminar carpeta completa
    import shutil
    shutil.rmtree(contract_folder)

    return {
        "success": True,
        "message": f"Contrato {contract_id} eliminado completamente"
    }
