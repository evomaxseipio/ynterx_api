from uuid import UUID

from fastapi import APIRouter, Request

from app.auth.dependencies import DepCurrentUser
from app.database import DepDatabase
from app.person.schemas import (
    CountryResponse,
    EducationLevelResponse,
    GenderResponse,
    MaritalStatusResponse,
    PersonCreate,
    PersonResponse,
    PersonUpdate,
)
from app.person.service import PersonService

router = APIRouter(prefix="/persons", tags=["persons"])

######################################################################################################
# Person Endpoints
######################################################################################################


@router.get("", response_model=list[PersonResponse])
async def list_persons(
    _: DepCurrentUser,
    request: Request,
) -> list[dict]:
    """List all persons."""
    pool = request.app.state.db_pool
    async with pool.acquire() as connection:
        return await PersonService.list_persons(connection=connection)


######################################################################################################
# Common Endpoints
######################################################################################################


@router.get("/genders", response_model=list[GenderResponse])
async def list_genders(
    _: DepCurrentUser,
    request: Request,
) -> list[dict]:
    """List all genders."""
    query = "SELECT * FROM gender WHERE is_active = true"
    pool = request.app.state.db_pool
    async with pool.acquire() as connection:
        genders = await connection.fetch(query)
    return [dict(gender) for gender in genders]


@router.get("/marital-statuses", response_model=list[MaritalStatusResponse])
async def list_marital_statuses(
    _: DepCurrentUser,
    request: Request,
) -> list[dict]:
    """List all marital statuses."""
    query = "SELECT * FROM marital_status WHERE is_active = true"
    pool = request.app.state.db_pool
    async with pool.acquire() as connection:
        marital_statuses = await connection.fetch(query)
    return [dict(marital_status) for marital_status in marital_statuses]


@router.get("/education-levels", response_model=list[EducationLevelResponse])
async def list_education_levels(
    _: DepCurrentUser,
    request: Request,
) -> list[dict]:
    """List all education levels."""
    query = "SELECT * FROM education_level WHERE is_active = true"
    pool = request.app.state.db_pool
    async with pool.acquire() as connection:
        education_levels = await connection.fetch(query)
    return [dict(education_level) for education_level in education_levels]


@router.get("/countries", response_model=list[CountryResponse])
async def list_countries(
    _: DepCurrentUser,
    request: Request,
) -> list[dict]:
    """List all countries."""
    query = "SELECT * FROM country WHERE is_active = true"
    pool = request.app.state.db_pool
    async with pool.acquire() as connection:
        countries = await connection.fetch(query)
    return [dict(country) for country in countries]


######################################################################################################
# Person Endpoints
######################################################################################################


@router.post("", response_model=PersonResponse)
async def create_person(
    person_data: PersonCreate,
    db: DepDatabase,
    current_user: DepCurrentUser,
) -> dict:
    """Create a new person."""
    return await PersonService.create_person(
        person_data,
        connection=db,
        created_by=current_user,
    )


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(
    _: DepCurrentUser,
    person_id: UUID,
    request: Request,
) -> dict | None:
    """Get a person by ID."""
    pool = request.app.state.db_pool
    async with pool.acquire() as connection:
        return await PersonService.get_person(person_id, connection=connection)


@router.put("/{person_id}", response_model=PersonResponse)
async def update_person(
    person_id: UUID,
    person_data: PersonUpdate,
    db: DepDatabase,
    current_user: DepCurrentUser,
) -> dict | None:
    """Update a person."""
    return await PersonService.update_person(
        person_id,
        person_data,
        connection=db,
        updated_by=current_user,
    )


@router.delete("/{person_id}", response_model=PersonResponse)
async def delete_person(
    person_id: UUID,
    db: DepDatabase,
    current_user: DepCurrentUser,
) -> dict | None:
    """Delete a person."""
    return await PersonService.delete_person(
        person_id,
        connection=db,
        deleted_by=current_user,
    )
