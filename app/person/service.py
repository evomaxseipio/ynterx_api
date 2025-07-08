"""Service layer for person-related operations."""

import json
from uuid import UUID
from typing import Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection

from app.database import fetch_one
from app.person.models import person
from app.person.schemas import PersonCreate, PersonUpdate, PersonCompleteCreate


class PersonService:
    @staticmethod
    async def create_person(
        person_data: PersonCreate,
        created_by: str | None = None,
        connection: AsyncConnection | None = None,
    ) -> dict:
        """Create a new person using the simplified structure."""
        query = person.insert().values(
            first_name=person_data.first_name,
            last_name=person_data.last_name,
            middle_name=person_data.middle_name,
            date_of_birth=person_data.date_of_birth,
            gender=person_data.gender,  # Directo, no ID
            nationality_country=person_data.nationality_country,  # Directo, no ID
            marital_status=person_data.marital_status,  # Directo, no ID
            occupation=person_data.occupation,  # Nuevo campo
            is_active=person_data.is_active,
        ).returning(person)

        result = await fetch_one(query, connection=connection, commit_after=True)
        return result

    @staticmethod
    async def create_person_complete(
        person_data: PersonCompleteCreate,
        connection: AsyncConnection | None = None,
        created_by: UUID | None = None,
        updated_by: UUID | None = None,
    ) -> Dict[str, Any]:
        """Create a complete person using stored procedure with validation."""

        # Preparar documentos como JSON
        documents_json = None
        if person_data.p_documents:
            documents_list = []
            for doc in person_data.p_documents:
                doc_dict = {
                    "is_primary": doc.is_primary,
                    "document_type": doc.document_type,
                    "document_number": doc.document_number,
                    "issuing_country_id": doc.issuing_country_id,
                    "document_issue_date": doc.document_issue_date.isoformat() if doc.document_issue_date else None,
                    "document_expiry_date": doc.document_expiry_date.isoformat() if doc.document_expiry_date else None
                }
                documents_list.append(doc_dict)
            documents_json = json.dumps(documents_list)

        # Preparar direcciones como JSON
        addresses_json = None
        if person_data.p_addresses:
            addresses_list = []
            for addr in person_data.p_addresses:
                addr_dict = {
                    "address_line1": addr.address_line1,
                    "address_line2": addr.address_line2,
                    "city_id": addr.city_id,
                    "postal_code": addr.postal_code,
                    "address_type": addr.address_type,
                    "is_principal": addr.is_principal
                }
                addresses_list.append(addr_dict)
            addresses_json = json.dumps(addresses_list)

        # Preparar datos adicionales como JSON
        additional_data_json = None
        if person_data.p_additional_data:
            additional_data_json = json.dumps(person_data.p_additional_data)

        # Preparar fecha de nacimiento
        date_of_birth = person_data.p_date_of_birth

        # Llamar al stored procedure con los nuevos parámetros
        query = """
            SELECT sp_insert_person_complete(
                $1::VARCHAR,      -- p_first_name
                $2::VARCHAR,      -- p_last_name
                $3::VARCHAR,      -- p_middle_name
                $4::DATE,         -- p_date_of_birth
                $5::VARCHAR,      -- p_gender
                $6::VARCHAR,      -- p_nationality_country
                $7::VARCHAR,      -- p_marital_status
                $8::VARCHAR,      -- p_occupation
                $9::JSONB,        -- p_documents
                $10::JSONB,       -- p_addresses
                $11::JSONB,       -- p_additional_data
                $12::INTEGER,     -- p_person_role_id
                $13::UUID,        -- p_created_by
                $14::UUID         -- p_updated_by
            ) as result
        """

        try:
            if connection:
                # Usar la conexión existente
                print('DEBUG PARAMS SP JSON:', json.dumps({
                    'p_first_name': person_data.p_first_name,
                    'p_last_name': person_data.p_last_name,
                    'p_middle_name': person_data.p_middle_name,
                    'p_date_of_birth': date_of_birth,
                    'p_gender': person_data.p_gender,
                    'p_nationality_country': person_data.p_nationality_country,
                    'p_marital_status': person_data.p_marital_status,
                    'p_occupation': person_data.p_occupation,
                    'p_documents': documents_json,
                    'p_addresses': addresses_json,
                    'p_additional_data': additional_data_json,
                    'p_person_role_id': person_data.p_person_role_id,
                    'p_created_by': str(created_by) if created_by else None,
                    'p_updated_by': str(updated_by) if updated_by else None
                }, default=str, ensure_ascii=False, indent=2))
                result = await connection.fetchrow(
                    query,
                    person_data.p_first_name,
                    person_data.p_last_name,
                    person_data.p_middle_name,
                    date_of_birth,
                    person_data.p_gender,
                    person_data.p_nationality_country,
                    person_data.p_marital_status,
                    person_data.p_occupation,
                    documents_json,
                    addresses_json,
                    additional_data_json,
                    person_data.p_person_role_id,
                    created_by,
                    updated_by
                )
            else:
                # Este caso no debería ocurrir en la práctica
                raise ValueError("Connection is required")

            if result and result['result']:
                print('DEBUG STORED PROCEDURE RAW RESULT:', result['result'])
                stored_proc_result = json.loads(result['result'])

                # Tu stored procedure devuelve una estructura más rica
                # Adaptarla para compatibilidad con el schema de respuesta
                if stored_proc_result.get('success', False):
                    # Extraer person_id del stored procedure
                    person_id = None
                    if 'data' in stored_proc_result and stored_proc_result['data']:
                        person_id = stored_proc_result['data'].get('person_id')

                    return {
                        "success": True,
                        "message": stored_proc_result.get('message') or 'Person processed successfully',
                        "person_id": person_id,
                        "data": stored_proc_result.get('data'),
                        "person_exists": stored_proc_result.get('person_exists', False),
                        "status_code": stored_proc_result.get('status_code', 200),
                        "timestamp": stored_proc_result.get('timestamp')
                    }
                else:
                    # Error del stored procedure
                    message = stored_proc_result.get('message') or 'Unknown error from stored procedure'
                    errors = stored_proc_result.get('errors')
                    if not errors:
                        errors = [message]
                    else:
                        errors = [e or message for e in errors]
                    return {
                        "success": False,
                        "message": message,
                        "errors": errors,
                        "status_code": stored_proc_result.get('status_code', 500),
                        "error_details": stored_proc_result.get('error')
                    }
            else:
                return {
                    "success": False,
                    "message": "No result returned from stored procedure",
                    "errors": ["Stored procedure returned empty result"]
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error executing stored procedure: {str(e)}",
                "errors": [str(e)]
            }

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
        """Get a person by user ID - Note: user_id field doesn't exist in new structure"""
        # Este método podría necesitar ser removido o adaptado según tu nueva estructura
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
            ORDER BY created_at DESC
            OFFSET $1 LIMIT $2;
        """
        persons = await connection.fetch(query, skip, limit, is_active)
        return [dict(person) for person in persons]

    @staticmethod
    async def search_persons(
        connection,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict]:
        """Search persons by name, document number, etc."""
        query = """
            SELECT DISTINCT p.* FROM public.person p
            LEFT JOIN person_document pd ON p.person_id = pd.person_id
            WHERE (
                LOWER(p.first_name || ' ' || p.last_name) LIKE LOWER($1)
                OR LOWER(p.first_name) LIKE LOWER($1)
                OR LOWER(p.last_name) LIKE LOWER($1)
                OR LOWER(COALESCE(p.middle_name, '')) LIKE LOWER($1)
                OR pd.document_number LIKE $1
            )
            AND p.is_active = true
            ORDER BY p.created_at DESC
            OFFSET $2 LIMIT $3;
        """
        search_pattern = f"%{search_term}%"
        persons = await connection.fetch(query, search_pattern, skip, limit)
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
            ORDER BY gender_name
        """
        genders = await connection.fetch(query, is_active)
        return [dict(gender) for gender in genders]

    @staticmethod
    async def get_distinct_genders_from_persons(connection) -> list[str]:
        """Get distinct genders from person table."""
        query = """
            SELECT DISTINCT gender
            FROM person
            WHERE gender IS NOT NULL
            AND is_active = true
            ORDER BY gender
        """
        result = await connection.fetch(query)
        return [row['gender'] for row in result]


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
            ORDER BY marital_status_name
        """
        statuses = await connection.fetch(query, is_active)
        return [dict(status) for status in statuses]

    @staticmethod
    async def get_distinct_marital_statuses_from_persons(connection) -> list[str]:
        """Get distinct marital statuses from person table."""
        query = """
            SELECT DISTINCT marital_status
            FROM person
            WHERE marital_status IS NOT NULL
            AND is_active = true
            ORDER BY marital_status
        """
        result = await connection.fetch(query)
        return [row['marital_status'] for row in result]


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
            ORDER BY education_level_name
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
            ORDER BY country_name
        """
        countries = await connection.fetch(query, is_active)
        return [dict(country) for country in countries]

    @staticmethod
    async def get_distinct_countries_from_persons(connection) -> list[str]:
        """Get distinct nationality countries from person table."""
        query = """
            SELECT DISTINCT nationality_country
            FROM person
            WHERE nationality_country IS NOT NULL
            AND is_active = true
            ORDER BY nationality_country
        """
        result = await connection.fetch(query)
        return [row['nationality_country'] for row in result]


class PersonDocumentService:
    @staticmethod
    async def get_documents_by_person(
        person_id: UUID,
        connection,
    ) -> list[dict]:
        """Get all documents for a person."""
        query = """
            SELECT * FROM person_document
            WHERE person_id = $1 AND is_active = true
            ORDER BY is_primary DESC, created_at ASC
        """
        documents = await connection.fetch(query, person_id)
        return [dict(doc) for doc in documents]


class PersonAddressService:
    @staticmethod
    async def get_addresses_by_person(
        person_id: UUID,
        connection,
    ) -> list[dict]:
        """Get all addresses for a person."""
        query = """
            SELECT a.*, c.city_name, co.country_name
            FROM address a
            LEFT JOIN city c ON a.city_id = c.city_id
            LEFT JOIN country co ON c.country_id = co.country_id
            WHERE a.person_id = $1 AND a.is_active = true
            ORDER BY a.is_principal DESC, a.created_at ASC
        """
        addresses = await connection.fetch(query, person_id)
        return [dict(addr) for addr in addresses]
