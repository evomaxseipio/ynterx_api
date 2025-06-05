"""Service layer for person-related operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection

from app.database import execute, fetch_all, fetch_one
from app.person.models import (
    country,
    education_level,
    gender,
    marital_status,
    person,
)
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
        )

        result = await execute(query, connection=connection, commit_after=True)
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

        if updated_by:
            values["updated_by"] = updated_by

        query = (
            person.update()
            .where(person.c.person_id == person_id)
            .values(**values)
            .returning(*person.c)
        )
        return await fetch_one(query, connection=connection)

    @staticmethod
    async def delete_person(
        person_id: UUID,
        connection: AsyncConnection | None = None,
    ) -> dict | None:
        """Delete a person."""
        query = (
            person.delete()
            .where(person.c.person_id == person_id)
            .returning(*person.c)
        )
        return await fetch_one(query, connection=connection)

    @staticmethod
    async def list_persons(
        connection: AsyncConnection | None = None,
    ) -> list[dict]:
        """List all persons."""
        query = select(person)
        return await fetch_all(query, connection=connection)


class GenderService:
    @staticmethod
    async def list_genders(
        connection: AsyncConnection | None = None,
    ) -> list[dict]:
        """List all genders."""
        query = select(gender).where(gender.c.is_active)
        return await fetch_all(query, connection=connection)


class MaritalStatusService:
    @staticmethod
    async def list_marital_statuses(
        connection: AsyncConnection | None = None,
    ) -> list[dict]:
        """List all marital statuses."""
        query = select(marital_status).where(marital_status.c.is_active)
        return await fetch_all(query, connection=connection)


class EducationLevelService:
    @staticmethod
    async def list_education_levels(
        connection: AsyncConnection | None = None,
    ) -> list[dict]:
        """List all education levels."""
        query = select(education_level).where(education_level.c.is_active)
        return await fetch_all(query, connection=connection)


class CountryService:
    @staticmethod
    async def list_countries(
        connection: AsyncConnection | None = None,
    ) -> list[dict]:
        """List all countries."""
        query = select(country).where(country.c.is_active)
        return await fetch_all(query, connection=connection)
