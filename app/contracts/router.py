# router_clean.py
from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request, status, Query
from fastapi.responses import FileResponse, JSONResponse
from typing import Dict, Any, Optional, List
from pathlib import Path
import os
import uuid
import json
from datetime import datetime, date


from app.auth.dependencies import DepCurrentUser
from app.exceptions import GenericHTTPException
from app.enums import ErrorCodeEnum
from .service import ContractService
from .services import ContractListService
from .schemas import *
from .loan_property_schemas import *
from app.database import DepDatabase, fetch_one, fetch_all, execute
from sqlalchemy import select, func
from app.contracts.models import contract as contract_table, contract_participant as contract_participant_table, contract_service
from app.contracts.loan_property_service import ContractLoanPropertyService
from app.contracts.participant_service import ParticipantService
from app.contracts.contract_creation_service import ContractCreationService
from app.person.service import PersonService
from app.person.schemas import PersonCompleteCreate, PersonDocumentCreate, PersonAddressCreate
from sqlalchemy import text as sql_text

load_dotenv()

router = APIRouter(prefix="/contracts", tags=["contracts"])

def get_contract_service() -> ContractService:
    """Dependency to get contract service"""
    use_google_drive = os.getenv("USE_GOOGLE_DRIVE", "false").lower() == "true"
    return ContractService(use_google_drive=use_google_drive)


def get_participant_service() -> ParticipantService:
    """Dependency to get participant service"""
    return ParticipantService()


def get_contract_creation_service() -> ContractCreationService:
    """Dependency to get contract creation service"""
    return ContractCreationService()


def validate_contract_data(data: Dict[str, Any]) -> None:
    """Validate that JSON has all required data to generate a contract"""
    missing_fields = []
    
    investors = data.get("investors") or []
    clients = data.get("clients") or []
    investor_company = data.get("investor_company", {})
    client_company = data.get("client_company", {})
    notaries = data.get("notaries") or data.get("notary") or []
    
    has_investor_person = investors and len(investors) > 0
    has_investor_company = investor_company and investor_company.get("company_name")
    
    if not has_investor_person and not has_investor_company:
        missing_fields.append("investors o investor_company: Se requiere al menos 1 inversionista (persona física o empresa)")
    
    has_client_person = clients and len(clients) > 0
    has_client_company = client_company and client_company.get("company_name")
    
    if not has_client_person and not has_client_company:
        missing_fields.append("clients o client_company: Se requiere al menos 1 cliente (persona física o empresa)")
    
    if not notaries or len(notaries) == 0:
        missing_fields.append("notaries: Se requiere al menos 1 notario")
    
    properties = data.get("properties") or []
    if not properties or len(properties) == 0:
        missing_fields.append("properties: Se requiere al menos 1 propiedad")
    
    if not data.get("paragraph_request"):
        missing_fields.append("paragraph_request: Se requiere la configuración de párrafos")
    
    if not data.get("loan"):
        missing_fields.append("loan: Se requiere información del préstamo")
    
    if missing_fields:
        raise GenericHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCodeEnum.VALIDATION_ERROR,
            message="Datos incompletos para generar el contrato",
            success=False,
            detail={
                "error_code": ErrorCodeEnum.VALIDATION_ERROR.value,
                "message": "Datos incompletos para generar el contrato",
                "success": False,
                "missing_fields": missing_fields
            }
        )


@router.post("/generate-complete", response_model=ContractResponse)
async def generate_contract_complete(
    data: Dict[str, Any],
    db: DepDatabase,
    request: Request,
    current_user: DepCurrentUser,
    service: ContractService = Depends(get_contract_service),
    participant_service: ParticipantService = Depends(get_participant_service),
    contract_creation_service: ContractCreationService = Depends(get_contract_creation_service)
) -> Dict[str, Any]:
    """
    Generate complete contract from structured JSON with persons, properties and loan.
    """
    
    validate_contract_data(data)

    participants_for_contract, participant_errors, processed_persons_summary = await participant_service.process_all_participants(data, request)

    if participant_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "No se puede generar el contrato: hay errores en el procesamiento de participantes. Corrija los datos e intente de nuevo.",
                "errors": participant_errors,
                "summary": processed_persons_summary
            }
        )

    contract_type_name = "CNT"
    contract_number = await contract_creation_service.generate_contract_number(contract_type_name, db)

    contract_id = await contract_creation_service.create_contract_record(data, contract_number, db, current_user)
    participant_db_errors = await contract_creation_service.register_contract_participants(contract_id, participants_for_contract, db)
    client_referrer_created, client_referrer_errors = await contract_creation_service.create_client_referrer_relationships(participants_for_contract, db)

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

            if not loan_property_result["overall_success"]:
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

    # Si falló loan o propiedades, no generar contrato: limpiar transacción abortada, borrar contrato y devolver error
    if loan_property_result is not None and not loan_property_result.get("overall_success", True):
        try:
            await db.rollback()
        except Exception:
            pass
        await contract_creation_service.delete_contract_cascade(contract_id, db)
        detail = {
            "message": "No se puede generar el contrato: hay errores en préstamo o propiedades. Corrija los datos e intente de nuevo.",
            "errors": loan_property_errors,
        }
        if loan_property_result.get("properties_result") and loan_property_result["properties_result"].get("errors"):
            detail["properties_errors"] = loan_property_result["properties_result"]["errors"]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

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

    file_path = document_result.get("path", "")
    folder_path = document_result.get("folder_path", "")
    
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
            "message": "Datos del contrato válidos",
            "summary": validation_summary,
            "total_participants": sum(validation_summary["participants_count"].values())
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Error de validación: {str(e)}",
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
    try:
        async with request.app.state.db_pool.acquire() as connection:
            result = await ContractListService.get_contracts(connection=connection)
            
            if not result.get("success", False):
                error_code = result.get("error", "UNKNOWN_ERROR")
                error_message = result.get("message", "Error al obtener contratos")
                status_code = 404 if error_code == "NO_DATA" else 500
                raise HTTPException(
                    status_code=status_code,
                    detail=f"{error_message} (Error: {error_code})"
                )
            
            return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado al recuperar contratos: {str(e)}"
        )


@router.get("/services", response_model=ContractServiceListResponse)
async def list_contract_services(
    _: DepCurrentUser,
    db: DepDatabase,
    is_active: Optional[bool] = Query(None, description="Filtrar por activos (true) o inactivos (false); si no se envía, devuelve todos"),
    limit: int = Query(default=20, ge=1, le=100, description="Máximo de registros por página"),
    offset: int = Query(default=0, ge=0, description="Registros a saltar"),
) -> ContractServiceListResponse:
    """
    Listar tipos de servicio / préstamo desde contract_service (paginado).

    Respuesta estándar: success, error, message, data, pagination.
    """
    base_filter = select(contract_service)
    if is_active is not None:
        base_filter = base_filter.where(contract_service.c.is_active == is_active)
    count_query = select(func.count().label("total")).select_from(contract_service)
    if is_active is not None:
        count_query = count_query.where(contract_service.c.is_active == is_active)
    total_row = await fetch_one(count_query, connection=db)
    total = int(total_row["total"]) if total_row and total_row.get("total") is not None else 0
    query = base_filter.limit(limit).offset(offset)
    rows = await fetch_all(query, connection=db)
    data = [ContractServiceItem(**r) for r in rows]
    page = (offset // limit) + 1 if limit else 1
    pagination = ContractServicePaginationSchema(total=total, per_page=limit, page=page, offset=offset)
    return ContractServiceListResponse(
        success=True,
        error=None,
        message="Tipos de servicio obtenidos correctamente",
        data=data,
        pagination=pagination,
    )


@router.get("/{contract_id}/detail", response_model=ContractDetailResponse)
async def get_contract_detail(
    contract_id: str,
    _: DepCurrentUser,
    request: Request,
) -> Dict[str, Any]:
    """
    Obtener detalle completo de un contrato por UUID o número de contrato
    
    Acepta tanto UUID como número de contrato. Si el parámetro es un UUID válido,
    lo busca por UUID. Si no, lo trata como número de contrato.
    
    Devuelve toda la información del contrato incluyendo:
    - Datos básicos del contrato
    - Participantes (personas, documentos, direcciones)
    - Información del préstamo
    - Propiedades asociadas
    - Cuentas bancarias
    """
    try:
        async with request.app.state.db_pool.acquire() as connection:
            try:
                try:
                    uuid.UUID(contract_id)
                    query = "SELECT fn_get_contract_detail($1)"
                    result = await connection.fetchval(query, contract_id)
                except ValueError:
                    query = "SELECT fn_get_contract_detail($1, $2)"
                    result = await connection.fetchval(query, None, contract_id)
                
                if result:
                    if isinstance(result, str):
                        try:
                            result = json.loads(result)
                        except json.JSONDecodeError as json_err:
                            raise HTTPException(
                                status_code=500,
                                detail=f"Error al parsear respuesta JSON de la BD: {str(json_err)}. Respuesta: {result[:200] if len(str(result)) > 200 else result}"
                            )
                    elif not isinstance(result, dict):
                        raise HTTPException(
                            status_code=500,
                            detail=f"Tipo de resultado inesperado de la BD: {type(result)}. Se esperaba dict o string JSON."
                        )
                    
                    if not result.get("success", False):
                        error_code = result.get("error", "UNKNOWN_ERROR")
                        error_message = result.get("message", "Error al obtener detalle del contrato")
                        error_details = result.get("details", None)
                        
                        error_detail_message = error_message
                        if error_details:
                            error_detail_message = f"{error_message}. Detalles: {error_details}"
                        
                        if error_code == "CONTRACT_NOT_FOUND":
                            status_code = 404
                        elif error_code == "DATABASE_ERROR":
                            status_code = 500
                        else:
                            status_code = 500
                        
                        raise HTTPException(
                            status_code=status_code,
                            detail=error_detail_message
                        )
                    
                    def normalize_data_types(obj, parent_key=""):
                        """Normalize data types: convert strings to numbers for numeric fields, numbers to strings for string fields"""
                        numeric_fields = {
                            "amount", "interest_rate", "term_months", "discount_rate", 
                            "monthly_payment", "final_payment", "payment_qty_quotes",
                            "total_paid", "loan_amount", "net_earnings", "total_earning",
                            "total_pending", "total_payments", "total_amount_due", 
                            "progress_percentage", "total_pending_interest", "contract_loan_id",
                            "payments_made", "surface_area", "covered_area", "property_value",
                            "contract_type_id", "company_id", "participation_percentage",
                            "p_person_role_id"
                        }
                        
                        string_fields = {
                            "postal_code", "title_number", "cadastral_number", "document_number",
                            "issuing_country_id"
                        }
                        
                        if isinstance(obj, str):
                            if parent_key in numeric_fields:
                                try:
                                    if '.' in obj:
                                        return float(obj)
                                    elif obj.isdigit() or (obj.startswith('-') and obj[1:].isdigit()):
                                        return int(obj)
                                except (ValueError, TypeError):
                                    pass
                            return obj
                        elif isinstance(obj, (int, float)):
                            if parent_key in string_fields:
                                return str(obj)
                            elif parent_key not in numeric_fields:
                                return obj
                            return obj
                        elif isinstance(obj, dict):
                            return {k: normalize_data_types(v, k) for k, v in obj.items()}
                        elif isinstance(obj, list):
                            return [normalize_data_types(item, parent_key) for item in obj]
                        return obj
                    
                    def normalize_participant_structure(data_obj):
                        """Flatten person.person nested structure if exists"""
                        if isinstance(data_obj, dict):
                            if "participants" in data_obj:
                                participants = data_obj["participants"]
                                for role_key in ["clients", "investors", "witnesses", "notaries", "referents", "notary"]:
                                    if role_key in participants and isinstance(participants[role_key], list):
                                        for p in participants[role_key]:
                                            if isinstance(p, dict):
                                                person = p.get("person")
                                                if person and isinstance(person, dict) and "person" in person:
                                                    nested_person = person.pop("person")
                                                    person.update(nested_person)
                            return {k: normalize_participant_structure(v) if isinstance(v, (dict, list)) else v 
                                   for k, v in data_obj.items()}
                        elif isinstance(data_obj, list):
                            return [normalize_participant_structure(item) if isinstance(item, (dict, list)) else item 
                                   for item in data_obj]
                        return data_obj
                    
                    if result.get("data"):
                        result["data"] = normalize_participant_structure(result["data"])
                        result["data"] = normalize_data_types(result["data"])
                        # Si la función de BD no devuelve contract_end_date, rellenar desde contract.end_date
                        if result["data"].get("contract_end_date") is None:
                            try:
                                row = await connection.fetchrow(
                                    "SELECT end_date FROM contract WHERE contract_id = $1",
                                    uuid.UUID(contract_id),
                                )
                                if row and row.get("end_date") is not None:
                                    result["data"]["contract_end_date"] = row["end_date"].strftime("%d/%m/%Y")
                            except (ValueError, TypeError, Exception):
                                pass

                        # Si la función de BD no devuelve bank_account en loan, rellenar desde contract_bank_account
                        try:
                            loan_obj = result["data"].get("loan") or {}
                            if loan_obj.get("bank_account") is None:
                                ba_row = await connection.fetchrow(
                                    """SELECT bank_name, account_number, account_type, currency,
                                              bank_code, swift_code, iban, holder_name
                                       FROM contract_bank_account
                                       WHERE contract_id = $1
                                       ORDER BY bank_account_id DESC LIMIT 1""",
                                    uuid.UUID(contract_id),
                                )
                                if ba_row:
                                    loan_obj["bank_account"] = {
                                        "bank_name": ba_row["bank_name"],
                                        "bank_account_number": ba_row["account_number"],
                                        "bank_account_type": ba_row["account_type"],
                                        "bank_account_currency": ba_row["currency"],
                                    }
                                    result["data"]["loan"] = loan_obj
                        except Exception:
                            pass
                    
                    from app.contracts.schemas import ContractDetailResponse
                    from decimal import Decimal
                    
                    validated_response = ContractDetailResponse(**result)
                    
                    def convert_decimals_to_float(obj):
                        """Convert Decimal to float recursively for JSON serialization"""
                        if isinstance(obj, Decimal):
                            return float(obj)
                        elif isinstance(obj, dict):
                            return {k: convert_decimals_to_float(v) for k, v in obj.items()}
                        elif isinstance(obj, list):
                            return [convert_decimals_to_float(item) for item in obj]
                        return obj
                    
                    result_dict = validated_response.model_dump(mode='python')
                    result_dict = convert_decimals_to_float(result_dict)
                    
                    return result_dict
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="No se pudo obtener respuesta de la función de BD (resultado None)"
                    )
                    
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error inesperado al recuperar el detalle del contrato: {str(e)}"
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error de conexión a la base de datos: {str(e)}"
        )
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


@router.patch("/{contract_id}/update", response_model=UpdateResponse, response_model_exclude_none=True)
async def update_contract(
    contract_id: str,
    updates: Dict[str, Any],
    db: DepDatabase,
    request: Request,
    service: ContractService = Depends(get_contract_service),
    participant_service: ParticipantService = Depends(get_participant_service),
    contract_creation_service: ContractCreationService = Depends(get_contract_creation_service)
) -> Dict[str, Any]:
    """
    Modificar contrato existente

    Actualiza campos específicos y regenera el documento
    con nueva versión automáticamente.
    Acepta contract_id como UUID (desde detalle) o como identificador de carpeta (contract_CNT-XXX).
    Si el body tiene clave "data" (respuesta de GET detail), se usa body["data"] como datos a actualizar.
    """
    # Si el body es la respuesta de detalle ({ "success", "data", ... }), usar data
    if "data" in updates and isinstance(updates.get("data"), dict):
        updates = updates["data"]

    # Normalizar estructura de participantes para compatibilidad:
    # - El GET detail devuelve `participants` anidado.
    # - El generador y ParticipantService esperan `clients`, `investors`, etc. en raíz.
    participants = updates.get("participants")
    if isinstance(participants, dict):
        for key, value in participants.items():
            # Solo copiar si no existe en raíz o está vacío
            if updates.get(key) in (None, [], {}, ""):
                updates[key] = value
    folder_id = contract_id
    try:
        uuid.UUID(contract_id)
    except ValueError:
        # No es UUID: asumir que ya es folder_id (ej. contract_CNT-000001-2026)
        pass
    else:
        # Es UUID: resolver contract_number desde la BD para obtener folder_id (carpeta/metadatos)
        row = await fetch_one(
            select(contract_table.c.contract_number).where(contract_table.c.contract_id == uuid.UUID(contract_id)),
            connection=db,
        )
        if row and row.get("contract_number"):
            folder_id = f"contract_{row['contract_number']}"
    try:
        document_result = await service.update_contract(folder_id, updates, connection=db)
        await contract_creation_service.update_contract_with_document_info(contract_id, document_result, db)
        await contract_creation_service.update_contract_data_in_db(contract_id, updates, db)
        # Persistir participantes (personas nuevas y empresas) en BD y vincularlos al contrato
        await contract_creation_service.upsert_contract_participants_from_payload(
            contract_id=contract_id,
            data=updates,
            db=db,
            request=request,
            participant_service=participant_service,
        )
        return {
            "success": document_result.get("success", True),
            "message": document_result.get("message", "Contrato actualizado exitosamente"),
            "contract_id": document_result.get("contract_id"),
        }
    except HTTPException:
        raise
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

    import shutil
    shutil.rmtree(contract_folder)

    return {
        "success": True,
        "message": f"Contrato {contract_id} eliminado completamente"
    }
