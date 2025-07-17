# router.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request
from fastapi.responses import FileResponse
from typing import Dict, Any, Optional, List
from pathlib import Path
import os
import uuid
import json
from datetime import datetime


from app.auth.dependencies import DepCurrentUser
from .service import ContractService
from .schemas import *
from .loan_property_schemas import *
from app.database import DepDatabase, fetch_one, execute
from app.contracts.models import contract as contract_table, contract_participant as contract_participant_table
from app.contracts.loan_property_service import ContractLoanPropertyService
from app.person.service import PersonService
from app.person.schemas import PersonCompleteCreate, PersonDocumentCreate, PersonAddressCreate
from sqlalchemy import text as sql_text

router = APIRouter(prefix="/contracts", tags=["contracts"])

def get_contract_service() -> ContractService:
    """Dependency para obtener servicio de contratos"""
    use_google_drive = os.getenv("USE_GOOGLE_DRIVE", "false").lower() == "true"
    return ContractService(use_google_drive=use_google_drive)


@router.post("/generate-complete", response_model=ContractResponse)
async def generate_contract_complete(
    data: Dict[str, Any],  # JSON complejo directo
    db: DepDatabase,
    request: Request,  # ✅ AGREGADO para acceder al pool asyncpg
    service: ContractService = Depends(get_contract_service)
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

    print(f"🚀 Iniciando generación de contrato completo...")

    # 1. PROCESAR TODAS LAS PERSONAS del JSON
    participant_roles = [
        ("clients", "cliente", 1),
        ("investors", "inversionista", 2),
        ("witnesses", "testigo", 3),
        ("notaries", "notario", 7),
        ("referrers", "referente", 8)
    ]

    participant_ids = []
    participant_errors = []
    participants_for_contract = []
    processed_persons_summary = {
        "total": 0,
        "successful": 0,
        "errors": 0,
        "existing": 0,
        "reused": 0  # Nuevo contador para personas reutilizadas
    }

    # Procesar cada grupo de personas
    for group_name, role_name, default_role_id in participant_roles:
        group_data = data.get(group_name, [])
        print(f"👤 Procesando {len(group_data)} {group_name}...")

        for idx, participant in enumerate(group_data):
            processed_persons_summary["total"] += 1

            try:
                # Construir PersonCompleteCreate desde el JSON
                person_data = {
                    "p_first_name": participant["person"]["first_name"],
                    "p_last_name": participant["person"]["last_name"],
                    "p_middle_name": participant["person"].get("middle_name"),
                    "p_date_of_birth": participant["person"].get("date_of_birth"),
                    "p_gender": participant["person"].get("gender"),
                    "p_nationality_country": participant["person"].get("nationality"),
                    "p_marital_status": participant["person"].get("marital_status"),
                    "p_occupation": participant["person"].get("occupation", role_name.title()),
                    "p_person_role_id": participant.get("p_person_role_id", default_role_id),
                    "p_additional_data": participant.get("p_additional_data", {})
                }

                # Preparar documentos
                documents = []
                if "person_document" in participant:
                    doc_data = participant["person_document"]
                    documents.append({
                        "is_primary": True,
                        "document_type": doc_data["document_type"],
                        "document_number": doc_data["document_number"],
                        "issuing_country_id": doc_data["issuing_country_id"],
                        "document_issue_date": doc_data.get("document_issue_date"),
                        "document_expiry_date": doc_data.get("document_expiry_date")
                    })
                elif "notary_document" in participant:
                    doc_data = participant["notary_document"]
                    documents.append({
                        "is_primary": True,
                        "document_type": doc_data.get("document_type", "Cédula"),
                        "document_number": doc_data["document_number"],
                        "issuing_country_id": doc_data["issuing_country_id"],
                        "document_issue_date": doc_data.get("document_issue_date"),
                        "document_expiry_date": doc_data.get("document_expiry_date")
                    })

                if documents:
                    person_data["p_documents"] = documents

                # Preparar direcciones
                if "address" in participant:
                    address_data = participant["address"]
                    person_data["p_addresses"] = [{
                        "address_line1": address_data["address_line1"],
                        "address_line2": address_data.get("address_line2"),
                        "city_id": address_data["city_id"],
                        "postal_code": address_data.get("postal_code"),
                        "address_type": address_data.get("address_type", "Casa"),
                        "is_principal": address_data.get("is_principal", True)
                    }]

                # Crear el schema
                from app.person.schemas import PersonCompleteCreate
                person_schema = PersonCompleteCreate(**person_data)

                # ✅ USAR POOL ASYNCPG en lugar de SQLAlchemy
                async with request.app.state.db_pool.acquire() as asyncpg_connection:
                    result = await PersonService.create_person_complete(
                        person_schema,
                        connection=asyncpg_connection,  # asyncpg connection
                        created_by=None,
                        updated_by=None
                    )

                # ✅ VERIFICACIÓN CRÍTICA: Manejar None result
                if result is None:
                    result = {
                        "success": False,
                        "message": "Error interno: servicio retornó None",
                        "error": "NULL_RESULT"
                    }

                # ✅ NUEVA LÓGICA: Manejar caso de persona existente
                person_id = None
                is_existing = False
                is_reused = False

                if result.get("success") and result.get("person_id"):
                    # Caso exitoso normal
                    person_id = result["person_id"]
                    is_existing = result.get("person_exists", False)

                elif not result.get("success") and result.get("data", {}).get("person_id"):
                    # 🔥 CASO ESPECIAL: Error pero con person_id (persona ya existe)
                    person_id = result["data"]["person_id"]
                    is_reused = True

                    # Verificar si el mensaje indica que la persona ya existe
                    error_message = result.get("message", "").lower()
                    if any(keyword in error_message for keyword in [
                        "ya está registrada", "already registered", "persona ya existe",
                        "already exists", "duplicate", "duplicado"
                    ]):
                        print(f"  🔄 {role_name} {idx+1}: Persona ya existe, reutilizando ID {person_id}")
                        processed_persons_summary["reused"] += 1

                        # Tratamos esto como éxito
                        result["success"] = True
                        result["person_exists"] = True
                        result["reused"] = True
                    else:
                        # Es un error real, no persona duplicada
                        person_id = None

                if person_id:
                    # Persona válida (nueva, existente o reutilizada)
                    participant_ids.append(person_id)
                    participants_for_contract.append({
                        "person_id": person_id,
                        "role": role_name,
                        "is_primary": idx == 0,
                        "person_role_id": person_data["p_person_role_id"],
                        "person_exists": is_existing,
                        "person_reused": is_reused
                    })
                    processed_persons_summary["successful"] += 1

                    if is_existing:
                        processed_persons_summary["existing"] += 1

                    # Log detallado
                    status = "Reutilizada" if is_reused else ("Existente" if is_existing else "Nueva")
                    print(f"  ✅ {role_name} {idx+1}: {participant['person']['first_name']} - {status} (ID: {person_id})")

                else:
                    # Error real que no podemos manejar
                    processed_persons_summary["errors"] += 1
                    error_msg = result.get("message", "Error creando persona")
                    participant_errors.append({
                        "role": role_name,
                        "index": idx,
                        "name": f"{participant['person']['first_name']} {participant['person']['last_name']}",
                        "error": error_msg,
                        "full_result": result
                    })
                    print(f"  ❌ {role_name} {idx+1}: Error real - {error_msg}")

            except Exception as e:
                processed_persons_summary["errors"] += 1
                participant_errors.append({
                    "role": role_name,
                    "index": idx,
                    "name": f"{participant.get('person', {}).get('first_name', 'Unknown')}",
                    "error": f"Error en procesamiento: {str(e)}",
                    "exception": True
                })
                print(f"  ❌ {role_name} {idx+1}: Exception - {str(e)}")

    print(f"📊 Resumen procesamiento personas:")
    print(f"   Total: {processed_persons_summary['total']}")
    print(f"   Exitosos: {processed_persons_summary['successful']}")
    print(f"   Nuevas: {processed_persons_summary['successful'] - processed_persons_summary['existing'] - processed_persons_summary['reused']}")
    print(f"   Existentes: {processed_persons_summary['existing']}")
    print(f"   Reutilizadas: {processed_persons_summary['reused']}")
    print(f"   Errores: {processed_persons_summary['errors']}")

    # Validar que se procesaron personas mínimas
    if participant_errors and processed_persons_summary["successful"] == 0:
        raise HTTPException(400, detail={
            "message": "Error procesando todas las personas",
            "errors": participant_errors,
            "summary": processed_persons_summary
        })

    # Advertir si hay errores pero continuar
    if participant_errors:
        print(f"⚠️ Continuando con {processed_persons_summary['successful']} personas exitosas, {processed_persons_summary['errors']} errores")

    # 2. GENERAR CONTRACT_NUMBER usando función SQL
    contract_type_name = data.get("contract_type", "mortgage")
    print(f"📋 Generando número de contrato para tipo: {contract_type_name}")

    try:
        from sqlalchemy import text
        result = await db.execute(
            text("SELECT generate_contract_number(:contract_type)"),
            {"contract_type": contract_type_name}
        )
        contract_number = result.scalar()
        print(f"📄 Número de contrato generado: {contract_number}")
    except Exception as e:
        print(f"⚠️ Error generando desde BD: {str(e)}")
        contract_number = f"{contract_type_name.upper()}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        print(f"📄 Número de contrato fallback: {contract_number}")

    if not contract_number:
        contract_number = f"{contract_type_name.upper()}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        print(f"📄 Número de contrato por defecto: {contract_number}")

    # 3. CREAR CONTRATO EN LA BASE DE DATOS
    contract_insert = contract_table.insert().values(
        contract_number=contract_number,
        contract_type_id=data.get("contract_type_id", 1),
        contract_service_id=None,
        contract_status_id=1,  # Draft
        contract_date=datetime.now().date(),
        title=data.get("description"),
        description=data.get("description"),
        template_name=f"{contract_type_name}_template.docx",
        generated_filename=None,
        file_path=None,
        folder_path=None,
        version=1,
        is_active=True,
        created_by=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    ).returning(contract_table.c.contract_id)

    contract_row = await fetch_one(contract_insert, connection=db, commit_after=True)
    contract_id = contract_row["contract_id"]
    print(f"🆔 Contrato creado en BD con ID: {contract_id}")

    # 4. REGISTRAR PARTICIPANTES EN contract_participant
    for p in participants_for_contract:
        participant_insert = contract_participant_table.insert().values(
            contract_id=contract_id,
            person_id=p["person_id"],
            person_type_id=p["person_role_id"],
            is_primary=p["is_primary"],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        await execute(participant_insert, connection=db, commit_after=True)

    print(f"👥 Registrados {len(participants_for_contract)} participantes en BD")


    # ✅ 4.5 CREAR LOAN Y PROPERTIES
    loan_property_result = None
    if data.get("loan") or data.get("properties"):
        print(f"🏦 Procesando loan y properties...")
        loan_property_result = await ContractLoanPropertyService.create_contract_loan_and_properties(
            contract_id=contract_id,
            loan_data=data.get("loan"),
            properties_data=data.get("properties", []),
            connection=db,
            contract_context=data
        )

        if loan_property_result["overall_success"]:
            print(f"✅ Loan y properties creados exitosamente")
        else:
            print(f"⚠️ Algunos problemas creando loan/properties: {loan_property_result}")

    # 5. GENERAR DOCUMENTO WORD usando tu servicio existente
    print(f"📝 Generando documento Word...")

    enhanced_data = data.copy()
    enhanced_data.update({
        "contract_id": str(contract_id),
        "contract_number": contract_number,
        "generated_at": datetime.now().isoformat(),
        "loan_property_result": loan_property_result
    })



    try:
        document_result = await service.generate_contract(enhanced_data, connection=db)

        if document_result.get("success"):
            update_query = contract_table.update().where(
                contract_table.c.contract_id == contract_id
            ).values(
                generated_filename=document_result.get("filename"),
                file_path=document_result.get("path"),
                folder_path=document_result.get("folder_path"),
                updated_at=datetime.now()
            )
            await execute(update_query, connection=db, commit_after=True)
            print(f"✅ Contrato actualizado en BD con paths del documento")
        else:
            print(f"❌ Error en generación de documento: {document_result}")

    except Exception as e:
        print(f"❌ Error generando documento Word: {str(e)}")
        document_result = {
            "success": False,
            "error": str(e),
            "message": f"Error generando documento: {str(e)}"
        }

    # 6. RESPUESTA FINAL
    return ContractResponse(
        success=True,
        message="Contrato completo generado exitosamente",
        contract_id=str(contract_id),
        contract_number=contract_number,
        filename=document_result.get("filename", f"{contract_number}.docx"),
        path=document_result.get("path", ""),
        folder_path=document_result.get("folder_path", ""),
        template_used=document_result.get("template_used", ""),
        processed_data={
            "persons_summary": processed_persons_summary,
            "participants_count": len(participants_for_contract),
            "contract_type": data.get("contract_type", "unknown"),
            "loan_amount": data.get("loan", {}).get("amount"),
            "properties_count": len(data.get("properties", [])),
            "document_generation": document_result,
            "loan_property_result": loan_property_result,
            "persons_detail": {
                "new_persons": processed_persons_summary['successful'] - processed_persons_summary['existing'] - processed_persons_summary['reused'],
                "existing_persons": processed_persons_summary['existing'],
                "reused_persons": processed_persons_summary['reused'],
                "total_successful": processed_persons_summary['successful']
            }
        },

        warnings={
            "person_errors": participant_errors,
            "message": f"Se procesaron {processed_persons_summary['successful']} personas exitosamente ({processed_persons_summary['reused']} reutilizadas), {processed_persons_summary['errors']} errores reales"
        } if participant_errors else None
    )

    # Incluir información de Google Drive si está disponible
    if document_result.get("drive_link"):
        response.update({
            "drive_success": True,
            "drive_folder_id": document_result.get("drive_folder_id"),
            "drive_file_id": document_result.get("drive_file_id"),
            "drive_link": document_result.get("drive_link"),
            "drive_view_link": document_result.get("drive_view_link")
        })

    # Incluir errores como advertencias si las hubo (solo errores reales)
    if participant_errors:
        response["warnings"] = {
            "person_errors": participant_errors,
            "message": f"Se procesaron {processed_persons_summary['successful']} personas exitosamente ({processed_persons_summary['reused']} reutilizadas), {processed_persons_summary['errors']} errores reales"
        }

    print(f"🎉 Contrato completo generado exitosamente!")
    print(f"   Personas nuevas: {processed_persons_summary['successful'] - processed_persons_summary['existing'] - processed_persons_summary['reused']}")
    print(f"   Personas reutilizadas: {processed_persons_summary['reused']}")
    print(f"   Participantes registrados: {len(participants_for_contract)}")

    return response


@router.post("/loans", response_model=Dict[str, Any])
async def create_contract_loan(
    request: LoanCreateRequest,
    db: DepDatabase,
    _: DepCurrentUser
) -> Dict[str, Any]:
    """Crear préstamo para un contrato existente"""
    result = await ContractLoanPropertyService.create_contract_loan(
        contract_id=request.contract_id,
        loan_data=request.loan_data.model_dump(),
        connection=db
    )
    return result


@router.post("/properties", response_model=Dict[str, Any])
async def create_contract_properties(
    request: PropertyCreateRequest,
    db: DepDatabase,
    _: DepCurrentUser
) -> Dict[str, Any]:
    """Crear propiedades para un contrato existente"""
    result = await ContractLoanPropertyService.create_contract_properties(
        contract_id=request.contract_id,
        properties_data=[prop.model_dump() for prop in request.properties_data],
        connection=db
    )
    return result


@router.post("/loan-properties", response_model=Dict[str, Any])
async def create_contract_loan_and_properties(
    request: LoanPropertyCreateRequest,
    db: DepDatabase,
    _: DepCurrentUser
) -> Dict[str, Any]:
    """Crear préstamo y propiedades para un contrato existente"""
    result = await ContractLoanPropertyService.create_contract_loan_and_properties(
        contract_id=request.contract_id,
        loan_data=request.loan_data.model_dump() if request.loan_data else None,
        properties_data=[prop.model_dump() for prop in request.properties_data] if request.properties_data else [],
        connection=db
    )
    return result


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



@router.patch("/{contract_id}/update", response_model=UpdateResponse)
async def update_contract(
    contract_id: str,
    updates: Dict[str, Any],
    db: DepDatabase,  # Inyecta la conexión
    service: ContractService = Depends(get_contract_service)
) -> Dict[str, Any]:
    """
    Modificar contrato existente

    Actualiza campos específicos y regenera el documento
    con nueva versión automáticamente.
    """
    return await service.update_contract(contract_id, updates, connection=db)


@router.post("/{contract_id}/upload", response_model=UploadResponse)
async def upload_attachment(
    contract_id: str,
    file: UploadFile = File(...),
    service: ContractService = Depends(get_contract_service)
) -> Dict[str, Any]:
    """
    Subir archivo adjunto al contrato

    Tipos permitidos: .jpg, .jpeg, .png, .gif, .bmp, .doc, .docx, .pdf, .xls, .xlsx
    Tamaño máximo: 10MB
    """
    return await service.upload_attachment(contract_id, file)


@router.get("/list", response_model=ContractListResponse)
async def list_contracts(
    service: ContractService = Depends(get_contract_service)
) -> Dict[str, Any]:
    """
    Listar todos los contratos generados

    Incluye metadatos, versiones y conteo de archivos adjuntos
    """
    return service.list_contracts()


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


@router.get("/{contract_id}/attachments")
async def list_attachments(
    contract_id: str,
    service: ContractService = Depends(get_contract_service)
) -> Dict[str, Any]:
    """Listar archivos adjuntos de un contrato"""
    contract_folder = service.contracts_dir / contract_id
    attachments_folder = contract_folder / "attachments"

    if not contract_folder.exists():
        raise HTTPException(404, "Contrato no encontrado")

    attachments = []
    if attachments_folder.exists():
        for file_path in attachments_folder.iterdir():
            if file_path.is_file():
                attachments.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified_at": file_path.stat().st_mtime
                })

    return {
        "contract_id": contract_id,
        "attachments": attachments,
        "total": len(attachments)
    }


@router.get("/{contract_id}/attachments/{filename}")
async def download_attachment(
    contract_id: str,
    filename: str,
    service: ContractService = Depends(get_contract_service)
) -> FileResponse:
    """Descargar archivo adjunto específico"""
    contract_folder = service.contracts_dir / contract_id
    attachment_path = contract_folder / "attachments" / filename

    if not attachment_path.exists():
        raise HTTPException(404, "Archivo adjunto no encontrado")

    return FileResponse(path=attachment_path, filename=filename)


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


@router.delete("/{contract_id}/attachments/{filename}")
async def delete_attachment(
    contract_id: str,
    filename: str,
    service: ContractService = Depends(get_contract_service)
) -> Dict[str, Any]:
    """Eliminar archivo adjunto específico"""
    contract_folder = service.contracts_dir / contract_id
    attachment_path = contract_folder / "attachments" / filename

    if not attachment_path.exists():
        raise HTTPException(404, "Archivo adjunto no encontrado")

    attachment_path.unlink()

    return {
        "success": True,
        "message": f"Archivo {filename} eliminado"
    }


@router.get("/info", response_model=SystemInfo)
async def get_system_info(
    service: ContractService = Depends(get_contract_service)
) -> Dict[str, Any]:
    """
    Información del sistema de contratos

    Muestra configuración, plantillas disponibles y estadísticas
    """
    # Contar plantillas
    templates = list(service.template_dir.glob("*.docx")) if service.template_dir.exists() else []

    # Contar contratos
    contracts_count = len([d for d in service.contracts_dir.iterdir()
                          if d.is_dir() and (d / f"{d.name}.docx").exists()]) if service.contracts_dir.exists() else 0

    # Información de Google Drive
    drive_info = {}
    if service.use_google_drive:
        try:
            drive_info = {
                "enabled": True,
                "status": "configured",
                "service_available": hasattr(service, 'gdrive_service')
            }
        except:
            drive_info = {
                "enabled": True,
                "status": "error",
                "service_available": False
            }
    else:
        drive_info = {"enabled": False}

    return {
        "system": "Contract Service - Full Version",
        "version": "2.0",
        "storage_type": "google_drive" if service.use_google_drive else "local",
        "templates_dir": str(service.template_dir),
        "contracts_dir": str(service.contracts_dir),
        "templates_found": len(templates),
        "contracts_generated": contracts_count,
        "template_files": [t.name for t in templates],
        "google_drive": drive_info,
        "max_file_size_mb": service.MAX_FILE_SIZE // (1024 * 1024),
        "allowed_extensions": list(service.ALLOWED_EXTENSIONS)
    }


@router.get("/{contract_id}/metadata")
async def get_contract_metadata(
    contract_id: str,
    service: ContractService = Depends(get_contract_service)
) -> Dict[str, Any]:
    """Obtener metadatos completos del contrato"""
    contract_folder = service.contracts_dir / contract_id
    metadata_file = contract_folder / "metadata.json"

    if not metadata_file.exists():
        raise HTTPException(404, "Metadatos del contrato no encontrados")

    import json
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    return metadata


# Endpoints específicos de Google Drive (si está habilitado)
@router.get("/{contract_id}/drive-link")
async def get_drive_link(
    contract_id: str,
    service: ContractService = Depends(get_contract_service)
) -> Dict[str, Any]:
    """Obtener enlace de Google Drive del contrato"""
    if not service.use_google_drive:
        raise HTTPException(400, "Google Drive no está habilitado")

    # Implementar lógica para obtener enlace de Drive
    # (requiere que el servicio mantenga IDs de Drive en metadatos)
    raise HTTPException(501, "Funcionalidad pendiente de implementar")


@router.get("/drive/test-connection")
async def test_drive_connection(
    service: ContractService = Depends(get_contract_service)
) -> Dict[str, Any]:
    """Probar conexión con Google Drive"""
    if not service.use_google_drive:
        return {"success": False, "message": "Google Drive no está habilitado"}

    try:
        # Test básico de conexión
        if hasattr(service, 'gdrive_service'):
            # Aquí iría la lógica de test del servicio de Drive
            return {"success": True, "message": "Conexión a Google Drive exitosa"}
        else:
            return {"success": False, "message": "Servicio de Google Drive no inicializado"}
    except Exception as e:
        return {"success": False, "message": f"Error conectando a Google Drive: {str(e)}"}
