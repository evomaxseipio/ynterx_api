"""Service layer for person-related operations."""

import json
from uuid import UUID
from typing import Dict, Any
from datetime import datetime, date

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
<<<<<<< HEAD
        if person_data.p_additional_data and person_data.p_additional_data:
=======
        if person_data.p_additional_data:
            # Validar que p_email y p_phone_number estén en additional_data
            if 'email' not in person_data.p_additional_data or 'phone_number' not in person_data.p_additional_data:
                return {
                    "success": False,
                    "message": "Los campos 'email' y 'phone_number' son requeridos en additional_data",
                    "errors": ["Campos email y phone_number faltantes en additional_data"],
                    "status_code": 400,
                    "person_id": None,
                    "data": None,
                    "person_exists": False,
                    "timestamp": None,
                    "error_details": None
                }
            
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
            # Convertir fechas en additional_data si existen
            additional_data = person_data.p_additional_data.copy()
            for key, value in additional_data.items():
                if isinstance(value, (date, datetime)):
                    additional_data[key] = value.isoformat()
                elif key in ['issue_date', 'expiration_date'] and isinstance(value, str):
                    # Mantener las fechas como string si ya vienen en formato string
                    pass
            additional_data_json = json.dumps(additional_data)

        try:
            if not connection:
                raise ValueError("Connection is required")

            print('DEBUG: Iniciando stored procedure...')

            # Usar asyncpg directamente sin SQLAlchemy text()
            query_string = """
                SELECT sp_insert_person_complete(
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14
                ) as result
            """

            # Ejecutar directamente con asyncpg
            row = await connection.fetchrow(
                query_string,
                person_data.p_first_name,
                person_data.p_last_name,
                person_data.p_middle_name,
                person_data.p_date_of_birth,
                person_data.p_gender,
                person_data.p_nationality_country,
                person_data.p_marital_status,
                person_data.p_occupation,
                documents_json,
                addresses_json,
                additional_data_json,
                person_data.p_person_role_id,
                str(created_by) if created_by else None,
                str(updated_by) if updated_by else None
            )
            print('DEBUG: Stored procedure executed successfully')


            if row and row[0]:
                print('DEBUG STORED PROCEDURE RAW RESULT:', row[0])

                # Parsear resultado del stored procedure
                if isinstance(row[0], str):
                    stored_proc_result = json.loads(row[0])
                else:
                    stored_proc_result = row[0]

                print('DEBUG PARSED RESULT:', stored_proc_result)

                # Procesar respuesta exitosa
                if stored_proc_result.get('success', False):
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
                        "timestamp": stored_proc_result.get('timestamp'),
                        "errors": None,
                        "error_details": None
                    }
                else:
                    # Error del stored procedure
                    message = stored_proc_result.get('message') or 'Unknown error from stored procedure'
                    errors = stored_proc_result.get('errors') or []

                    # Asegurar que todos los elementos de errors sean strings válidos
                    clean_errors = []
                    if isinstance(errors, list):
                        for error in errors:
                            if error is not None and str(error).strip():
                                clean_errors.append(str(error))

                    # Si no hay errores válidos, usar el mensaje como error
                    if not clean_errors:
                        clean_errors = [message]

                    return {
                        "success": False,
                        "message": message,
                        "errors": clean_errors,
                        "status_code": stored_proc_result.get('status_code', 500),
                        "error_details": stored_proc_result.get('error_details'),
                        "person_id": None,
                        "data": stored_proc_result.get('data'),
                        "person_exists": stored_proc_result.get('person_exists', False),
                        "timestamp": stored_proc_result.get('timestamp')
                    }
            else:
                return {
                    "success": False,
                    "message": "No result returned from stored procedure",
                    "errors": ["Stored procedure returned empty result"],
                    "status_code": 500,
                    "person_id": None,
                    "data": None,
                    "person_exists": False,
                    "timestamp": None,
                    "error_details": None
                }

        except json.JSONDecodeError as e:
            print(f"JSON DECODE ERROR: {str(e)}")
            return {
                "success": False,
                "message": f"Error parsing stored procedure result: {str(e)}",
                "errors": [f"JSON decode error: {str(e)}"],
                "status_code": 500,
                "person_id": None,
                "data": None,
                "person_exists": False,
                "timestamp": None,
                "error_details": None
            }
        except Exception as e:
            print(f"ERROR in create_person_complete: {str(e)}")
            return {
                "success": False,
                "message": f"Error executing stored procedure: {str(e)}",
                "errors": [str(e)],
                "status_code": 500,
                "person_id": None,
                "data": None,
                "person_exists": False,
                "timestamp": None,
                "error_details": None
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
        """Soft delete a person (sets is_active = false)."""
        query = (
            person.update()
            .where(person.c.person_id == person_id)
            .values(is_active=False)
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
