from uuid import UUID

from fastapi import APIRouter, Request, HTTPException, Query, Depends
from typing import List, Optional

from app.auth.dependencies import DepCurrentUser
from app.database import DepDatabase
from app.person.schemas import (
    CountryResponse,
    EducationLevelResponse,
    GenderResponse,
    MaritalStatusResponse,
    PersonCreate,
    PersonSchema,
    PersonUpdate,
    PersonCompleteCreate,
    PersonCompleteResponse,
    ReferrerCreate,
    ReferrerUpdate,
    ReferrerResponse,
)
from app.person.service import (
    CountryService,
    EducationLevelService,
    GenderService,
    MaritalStatusService,
    PersonService,
    PersonDocumentService,
    PersonAddressService,
)
from app.person.services import ReferrerService

router = APIRouter(prefix="/persons", tags=["persons"])

######################################################################################################
# Person List and Search Endpoints
######################################################################################################


@router.get("", response_model=dict)
async def list_persons(
    _: DepCurrentUser,
    request: Request,
    search_term: Optional[str] = Query(None, description="Buscar por nombre, apellido, cédula, etc."),
    limit: int = Query(20, ge=1, le=100, description="Número de registros por página"),
    offset: int = Query(0, ge=0, description="Número de registros a saltar"),
) -> dict:
    """List all persons with pagination using stored procedure."""
    async with request.app.state.db_pool.acquire() as connection:
        return await PersonService.list_persons(
            connection=connection,
            search_term=search_term,
            limit=limit,
            offset=offset
        )


@router.get("/search", response_model=list[PersonSchema])
async def search_persons(
    _: DepCurrentUser,
    request: Request,
    q: str = Query(..., description="Search term for name or document number"),
    skip: int = 0,
    limit: int = 50,
) -> list[dict]:
    """Search persons by name or document number."""
    if len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Search term must be at least 2 characters")

    async with request.app.state.db_pool.acquire() as connection:
        return await PersonService.search_persons(
            connection=connection,
            search_term=q.strip(),
            skip=skip,
            limit=limit
        )


######################################################################################################
# Reference Data Endpoints (para dropdowns y selects)
######################################################################################################


@router.get("/genders", response_model=list[GenderResponse])
async def list_genders(
    _: DepCurrentUser,
    request: Request,
    is_active: bool | None = None,
) -> list[dict]:
    """List all genders from lookup table."""
    async with request.app.state.db_pool.acquire() as connection:
        return await GenderService.list_genders(
            connection=connection,
            is_active=is_active
        )


@router.get("/genders/used", response_model=list[str])
async def list_used_genders(
    _: DepCurrentUser,
    request: Request,
) -> list[str]:
    """List distinct genders actually used in person records."""
    async with request.app.state.db_pool.acquire() as connection:
        return await GenderService.get_distinct_genders_from_persons(connection)


@router.get("/marital-statuses", response_model=list[MaritalStatusResponse])
async def list_marital_statuses(
    _: DepCurrentUser,
    request: Request,
    is_active: bool | None = None,
) -> list[dict]:
    """List all marital statuses from lookup table."""
    async with request.app.state.db_pool.acquire() as connection:
        return await MaritalStatusService.list_marital_statuses(
            connection=connection,
            is_active=is_active
        )


@router.get("/marital-statuses/used", response_model=list[str])
async def list_used_marital_statuses(
    _: DepCurrentUser,
    request: Request,
) -> list[str]:
    """List distinct marital statuses actually used in person records."""
    async with request.app.state.db_pool.acquire() as connection:
        return await MaritalStatusService.get_distinct_marital_statuses_from_persons(connection)


@router.get("/education-levels", response_model=list[EducationLevelResponse])
async def list_education_levels(
    _: DepCurrentUser,
    request: Request,
    is_active: bool | None = None,
) -> list[dict]:
    """List all education levels."""
    async with request.app.state.db_pool.acquire() as connection:
        return await EducationLevelService.list_education_levels(
            connection=connection,
            is_active=is_active
        )


@router.get("/countries", response_model=list[CountryResponse])
async def list_countries(
    _: DepCurrentUser,
    request: Request,
    is_active: bool | None = None,
) -> list[dict]:
    """List all countries from lookup table."""
    async with request.app.state.db_pool.acquire() as connection:
        return await CountryService.list_countries(
            connection=connection,
            is_active=is_active
        )


@router.get("/countries/used", response_model=list[str])
async def list_used_countries(
    _: DepCurrentUser,
    request: Request,
) -> list[str]:
    """List distinct nationality countries actually used in person records."""
    async with request.app.state.db_pool.acquire() as connection:
        return await CountryService.get_distinct_countries_from_persons(connection)


######################################################################################################
# Person CRUD Endpoints
######################################################################################################


@router.post("", response_model=PersonSchema)
async def create_person(
    person_data: PersonCreate,
    db: DepDatabase,
    current_user: DepCurrentUser,
) -> dict:
    """Create a new person with basic information."""
    return await PersonService.create_person(
        person_data,
        connection=db,
        created_by=current_user,
    )


@router.post("/complete", response_model=PersonCompleteResponse)
async def create_person_complete(
    person_data: PersonCompleteCreate,
    request: Request,
    current_user: DepCurrentUser,
) -> PersonCompleteResponse:
    """
    Create a complete person with documents and addresses using stored procedure.

    This endpoint allows creating a person with all related information in a single operation:
    - Basic person information
    - Documents (cédula, passport, etc.)
    - Addresses (home, work, etc.)

    Example request body:
    ```json
    {
        "p_first_name": "Maximiliano",
        "p_last_name": "Martins",
        "p_middle_name": "Seipio",
        "p_date_of_birth": "1976-05-18",
        "p_gender": "Masculino",
        "p_nationality_country": "República Dominicana",
        "p_marital_status": "Soltero",
        "p_occupation": "Ingeniero de Software",
        "p_documents": [
            {
                "is_primary": true,
                "document_type": "Cédula",
                "document_number": "023-0093859-0",
                "issuing_country_id": "1",
                "document_issue_date": "2018-05-18",
                "document_expiry_date": "2028-05-18"
            }
        ],
        "p_addresses": [
            {
                "address_line1": "Calle Duarte #456",
                "address_line2": "Edificio Los Prados, Apt 3B",
                "city_id": "1",
                "postal_code": "10210",
                "address_type": "Casa",
                "is_principal": true
            }
        ],
        "p_person_role_id": 1,
        "p_additional_data": {
            "license_number": "NT-239872",
            "issuing_entity": "Suprema Corte de Justicia",
            "issue_date": "2020-05-15",
            "expiration_date": "2030-05-14",
            "jurisdiction": "Distrito Nacional",
            "office_name": "Oficina Jurídica Pérez & Asociados",
            "professional_email": "notario.perez@oficina.com",
            "professional_phone": "809-555-1234",
            "notes": "Especializado en contratos civiles y notariales"
        }
    }
    ```
    """
    async with request.app.state.db_pool.acquire() as connection:
        try:
            # Llamar al servicio
            result = await PersonService.create_person_complete(
                person_data,
                connection=connection,
                created_by=current_user,
                updated_by=current_user
            )

            print(f"DEBUG SERVICE RESULT: {result}")

            # El servicio siempre devuelve un dict con la estructura correcta
            # Solo necesitamos crear la respuesta
            if result.get("success", False):
                # Caso exitoso
                response = PersonCompleteResponse(
                    success=result["success"],
                    message=result["message"],
                    person_id=result.get("person_id"),
                    data=result.get("data"),
                    errors=result.get("errors"),
                    person_exists=result.get("person_exists"),
                    status_code=result.get("status_code"),
                    timestamp=result.get("timestamp"),
                    error_details=result.get("error_details")
                )
                return response
            else:
                # Error del stored procedure - devolver como respuesta, no como excepción
                response = PersonCompleteResponse(
                    success=result["success"],
                    message=result["message"],
                    person_id=result.get("person_id"),
                    data=result.get("data"),
                    errors=result.get("errors"),
                    person_exists=result.get("person_exists"),
                    status_code=result.get("status_code"),
                    timestamp=result.get("timestamp"),
                    error_details=result.get("error_details")
                )
                return response

        except Exception as e:
            print(f"ERROR in router create_person_complete: {str(e)}")
            # Error de ejecución - crear respuesta estructurada
            error_response = PersonCompleteResponse(
                success=False,
                message=f"Router error: {str(e)}",
                person_id=None,
                data=None,
                errors=[str(e)],
                person_exists=False,
                status_code=500,
                timestamp=None,
                error_details={"router_error": str(e)}
            )
            return error_response


@router.get("/{person_id}", response_model=PersonSchema)
async def get_person(
    _: DepCurrentUser,
    person_id: UUID,
    request: Request,
) -> dict:
    """Get a person by ID."""
    async with request.app.state.db_pool.acquire() as connection:
        query = "SELECT * FROM person WHERE person_id = $1"
        person = await connection.fetchrow(query, person_id)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        return dict(person)


@router.get("/{person_id}/complete")
async def get_person_complete(
    _: DepCurrentUser,
    person_id: UUID,
    request: Request,
) -> dict:
    """Get a person with all related documents and addresses."""
    async with request.app.state.db_pool.acquire() as connection:
        # Obtener datos básicos de la persona
        query = "SELECT * FROM person WHERE person_id = $1"
        person = await connection.fetchrow(query, person_id)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")

        # Obtener documentos
        documents = await PersonDocumentService.get_documents_by_person(
            person_id, connection
        )

        # Obtener direcciones
        addresses = await PersonAddressService.get_addresses_by_person(
            person_id, connection
        )

        return {
            "person": dict(person),
            "documents": documents,
            "addresses": addresses
        }


@router.put("/{person_id}", response_model=PersonSchema)
async def update_person(
    person_id: UUID,
    person_data: PersonUpdate,
    db: DepDatabase,
    current_user: DepCurrentUser,
) -> dict:
    """Update a person's basic information."""
    updated_person = await PersonService.update_person(
        person_id,
        person_data,
        connection=db,
        updated_by=current_user,
    )
    if not updated_person:
        raise HTTPException(status_code=404, detail="Person not found")
    return updated_person


@router.delete("/{person_id}", response_model=PersonSchema)
async def delete_person(
    person_id: UUID,
    db: DepDatabase,
    current_user: DepCurrentUser,
) -> dict:
    """Soft delete a person (sets is_active = false)."""
    deleted_person = await PersonService.delete_person(
        person_id,
        connection=db,
        deleted_by=current_user,
    )
    if not deleted_person:
        raise HTTPException(status_code=404, detail="Person not found")
    return deleted_person


######################################################################################################
# Utility Endpoints
######################################################################################################


@router.post("/validate-data")
async def validate_person_data(
    person_data: PersonCompleteCreate,
    _: DepCurrentUser,
) -> dict:
    """
    Validate person data without creating the record.
    Useful for frontend validation before submission.
    """
    try:
        # Si llegamos aquí, la validación de Pydantic pasó
        return {
            "valid": True,
            "message": "Person data is valid",
            "data": person_data.model_dump()
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Validation error: {str(e)}",
            "errors": [str(e)]
        }


@router.get("/stats/summary")
async def get_persons_stats(
    _: DepCurrentUser,
    request: Request,
) -> dict:
    """Get summary statistics about persons in the database."""
    async with request.app.state.db_pool.acquire() as connection:
        # Total de personas
        total_query = "SELECT COUNT(*) as total FROM person WHERE is_active = true"
        total_result = await connection.fetchrow(total_query)

        # Por género
        gender_query = """
            SELECT gender, COUNT(*) as count
            FROM person
            WHERE is_active = true AND gender IS NOT NULL
            GROUP BY gender
            ORDER BY count DESC
        """
        gender_result = await connection.fetch(gender_query)

        # Por estado civil
        marital_query = """
            SELECT marital_status, COUNT(*) as count
            FROM person
            WHERE is_active = true AND marital_status IS NOT NULL
            GROUP BY marital_status
            ORDER BY count DESC
        """
        marital_result = await connection.fetch(marital_query)

        # Registros recientes (últimos 30 días)
        recent_query = """
            SELECT COUNT(*) as recent_count
            FROM person
            WHERE is_active = true
            AND created_at >= CURRENT_DATE - INTERVAL '30 days'
        """
        recent_result = await connection.fetchrow(recent_query)

        return {
            "total_persons": total_result['total'],
            "recent_additions_30_days": recent_result['recent_count'],
            "by_gender": [dict(row) for row in gender_result],
            "by_marital_status": [dict(row) for row in marital_result]
        }


router_referrers = APIRouter(prefix="/referrers", tags=["referrers"])


@router_referrers.post("", response_model=dict)
async def create_or_update_referrer(
    referrer_data: ReferrerCreate,
    db: DepDatabase,
    current_user: DepCurrentUser,
) -> dict:
    """Crear o actualizar un referente"""
    result = await ReferrerService.create_or_update_referrer(referrer_data, connection=db)
    
    if not result["success"]:
        raise HTTPException(400, result["message"])
    
    return result


@router_referrers.get("/{person_id}", response_model=Optional[ReferrerResponse])
async def get_referrer_by_person_id(
    person_id: UUID,
    db: DepDatabase,
    current_user: DepCurrentUser,
) -> Optional[dict]:
    """Obtener referente por person_id"""
    referrer = await ReferrerService.get_referrer_by_person_id(person_id, connection=db)
    
    if not referrer:
        raise HTTPException(404, "Referente no encontrado")
    
    return referrer


@router_referrers.get("/id/{referrer_id}", response_model=Optional[ReferrerResponse])
async def get_referrer_by_id(
    referrer_id: UUID,
    db: DepDatabase,
    current_user: DepCurrentUser,
) -> Optional[dict]:
    """Obtener referente por referrer_id"""
    referrer = await ReferrerService.get_referrer_by_id(referrer_id, connection=db)
    
    if not referrer:
        raise HTTPException(404, "Referente no encontrado")
    
    return referrer


@router_referrers.get("", response_model=List[ReferrerResponse])
async def list_referrers(
    db: DepDatabase,
    current_user: DepCurrentUser,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> List[dict]:
    """Listar todos los referentes activos"""
    return await ReferrerService.list_referrers(connection=db, limit=limit, offset=offset)


@router_referrers.post("/{person_id}/increment-count", response_model=dict)
async def increment_referred_clients_count(
    person_id: UUID,
    db: DepDatabase,
    current_user: DepCurrentUser,
) -> dict:
    """Incrementar el contador de clientes referidos"""
    result = await ReferrerService.increment_referred_clients_count(person_id, connection=db)
    
    if not result["success"]:
        raise HTTPException(400, result["message"])
    
    return result
