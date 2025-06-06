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
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
) -> list[dict]:
    """List all persons."""
    async with request.app.state.db_pool.acquire() as connection:
        query = """
            SELECT * FROM public.person
            WHERE ($3::boolean IS NULL OR is_active = $3::boolean)
            OFFSET $1 LIMIT $2;
        """
        persons = await connection.fetch(query, skip, limit, is_active)
        return [dict(person) for person in persons]


######################################################################################################
# Common Endpoints
######################################################################################################


@router.get("/genders", response_model=list[GenderResponse])
async def list_genders(
    _: DepCurrentUser,
    request: Request,
    is_active: bool | None = None,
) -> list[dict]:
    """List all genders."""
    async with request.app.state.db_pool.acquire() as connection:
        query = """
            SELECT * FROM gender
            WHERE ($1::boolean IS NULL OR is_active = $1::boolean)
        """
        genders = await connection.fetch(query, is_active)
    return [dict(gender) for gender in genders]


@router.get("/marital-statuses", response_model=list[MaritalStatusResponse])
async def list_marital_statuses(
    _: DepCurrentUser,
    request: Request,
    is_active: bool | None = None,
) -> list[dict]:
    """List all marital statuses."""
    async with request.app.state.db_pool.acquire() as connection:
        query = """
            SELECT * FROM marital_status
            WHERE ($1::boolean IS NULL OR is_active = $1::boolean)
        """
        marital_statuses = await connection.fetch(query, is_active)
    return [dict(marital_status) for marital_status in marital_statuses]


@router.get("/education-levels", response_model=list[EducationLevelResponse])
async def list_education_levels(
    _: DepCurrentUser,
    request: Request,
    is_active: bool | None = None,
) -> list[dict]:
    """List all education levels."""
    async with request.app.state.db_pool.acquire() as connection:
        query = """
            SELECT * FROM education_level
            WHERE ($1::boolean IS NULL OR is_active = $1::boolean)
        """
        education_levels = await connection.fetch(query, is_active)
    return [dict(education_level) for education_level in education_levels]


@router.get("/countries", response_model=list[CountryResponse])
async def list_countries(
    _: DepCurrentUser,
    request: Request,
    is_active: bool | None = None,
) -> list[dict]:
    """List all countries."""
    async with request.app.state.db_pool.acquire() as connection:
        query = """
            SELECT * FROM country
            WHERE ($1::boolean IS NULL OR is_active = $1::boolean)
        """
        countries = await connection.fetch(query, is_active)
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
    async with request.app.state.db_pool.acquire() as connection:
        query = "SELECT * FROM person WHERE person_id = $1"
        person = await connection.fetchrow(query, person_id)
        return dict(person) if person else None


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
