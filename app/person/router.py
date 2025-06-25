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
    PersonSchema,
    PersonUpdate,
)
from app.person.service import (
    CountryService,
    EducationLevelService,
    GenderService,
    MaritalStatusService,
    PersonService,
)

router = APIRouter(prefix="/persons", tags=["persons"])

######################################################################################################
# Person Endpoints
######################################################################################################


@router.get("", response_model=list[PersonSchema])
async def list_persons(
    _: DepCurrentUser,
    request: Request,
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
) -> list[dict]:
    """List all persons."""
    async with request.app.state.db_pool.acquire() as connection:
        return await PersonService.list_persons(
            connection=connection,
            skip=skip,
            limit=limit,
            is_active=is_active
        )


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
        return await GenderService.list_genders(
            connection=connection,
            is_active=is_active
        )


@router.get("/marital-statuses", response_model=list[MaritalStatusResponse])
async def list_marital_statuses(
    _: DepCurrentUser,
    request: Request,
    is_active: bool | None = None,
) -> list[dict]:
    """List all marital statuses."""
    async with request.app.state.db_pool.acquire() as connection:
        return await MaritalStatusService.list_marital_statuses(
            connection=connection,
            is_active=is_active
        )


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
    """List all countries."""
    async with request.app.state.db_pool.acquire() as connection:
        return await CountryService.list_countries(
            connection=connection,
            is_active=is_active
        )


######################################################################################################
# Person Endpoints
######################################################################################################


@router.post("", response_model=PersonSchema)
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


@router.get("/{person_id}", response_model=PersonSchema)
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


@router.put("/{person_id}", response_model=PersonSchema)
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


@router.delete("/{person_id}", response_model=PersonSchema)
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
