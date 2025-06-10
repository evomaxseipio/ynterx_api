"""Service layer for person-related operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection

from app.database import fetch_one
from app.person.models import person
from app.person.schemas import PersonCreate, PersonUpdate


class PersonService:
    @staticmethod
    async def create_person(
        person_data: PersonCreate,
        created_by: str | None = None,
        connection: AsyncConnection | None = None,
    ) -> dict:
        """Create a new person."""
        query = person.insert().values(
            first_name=person_data.first_name,
            last_name=person_data.last_name,
            middle_name=person_data.middle_name,
            date_of_birth=person_data.date_of_birth,
            gender_id=person_data.gender_id,
            nationality_country_id=person_data.nationality_country_id,
            marital_status_id=person_data.marital_status_id,
            education_level_id=person_data.education_level_id,
            is_active=person_data.is_active,
        ).returning(person)

        result = await fetch_one(query, connection=connection, commit_after=True)
        return result

    @staticmethod
    async def get_person(
        person_id: UUID,
        connection: AsyncConnection | None = None,
    ) -> dict | None:
        """Get a person by ID."""
        query = select(person).where(person.c.person_id == person_id)
        return await fetch_one(query, connection=connection)

    @staticmethod
    async def get_person_by_user_id(
        user_id: UUID,
        connection: AsyncConnection | None = None,
    ) -> dict | None:
        """Get a person by user ID."""
        query = select(person).where(person.c.user_id == user_id)
        return await fetch_one(query, connection=connection)

    @staticmethod
    async def update_person(
        person_id: UUID,
        person_data: PersonUpdate,
        updated_by: UUID | None = None,
        connection: AsyncConnection | None = None,
    ) -> dict | None:
        """Update a person."""
        values = person_data.model_dump(exclude_unset=True)
        if not values:
            return await PersonService.get_person(person_id, connection=connection)

        query = (
            person.update()
            .where(person.c.person_id == person_id)
            .values(**values)
            .returning(*person.c)
        )
        return await fetch_one(query, connection=connection, commit_after=True)

    @staticmethod
    async def delete_person(
        person_id: UUID,
        connection: AsyncConnection | None = None,
        deleted_by: UUID | None = None,
    ) -> dict | None:
        """Delete a person."""
        query = (
            person.delete()
            .where(person.c.person_id == person_id)
            .returning(*person.c)
        )
        return await fetch_one(query, connection=connection, commit_after=True)

    @staticmethod
    async def list_persons(
        connection,
        skip: int = 0,
        limit: int = 100,
        is_active: bool | None = None,
    ) -> list[dict]:
        """List all persons with pagination and active filter."""
        query = """
            SELECT * FROM public.person
            WHERE ($3::boolean IS NULL OR is_active = $3::boolean)
            OFFSET $1 LIMIT $2;
        """
        persons = await connection.fetch(query, skip, limit, is_active)
        return [dict(person) for person in persons]


class GenderService:
    @staticmethod
    async def list_genders(
        connection,
        is_active: bool | None = None,
    ) -> list[dict]:
        """List all genders."""
        query = """
            SELECT * FROM gender
            WHERE ($1::boolean IS NULL OR is_active = $1::boolean)
        """
        genders = await connection.fetch(query, is_active)
        return [dict(gender) for gender in genders]


class MaritalStatusService:
    @staticmethod
    async def list_marital_statuses(
        connection,
        is_active: bool | None = None,
    ) -> list[dict]:
        """List all marital statuses."""
        query = """
            SELECT * FROM marital_status
            WHERE ($1::boolean IS NULL OR is_active = $1::boolean)
        """
        statuses = await connection.fetch(query, is_active)
        return [dict(status) for status in statuses]


class EducationLevelService:
    @staticmethod
    async def list_education_levels(
        connection,
        is_active: bool | None = None,
    ) -> list[dict]:
        """List all education levels."""
        query = """
            SELECT * FROM education_level
            WHERE ($1::boolean IS NULL OR is_active = $1::boolean)
        """
        levels = await connection.fetch(query, is_active)
        return [dict(level) for level in levels]


class CountryService:
    @staticmethod
    async def list_countries(
        connection,
        is_active: bool | None = None,
    ) -> list[dict]:
        """List all countries."""
        query = """
            SELECT * FROM country
            WHERE ($1::boolean IS NULL OR is_active = $1::boolean)
        """
        countries = await connection.fetch(query, is_active)
        return [dict(country) for country in countries]
