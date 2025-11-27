"""Service layer for partner-related operations."""

import json
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncConnection


class PartnerService:
    """Service class for partner operations."""

    @staticmethod
    async def get_partners(
        person_type_id: int = 2,
        search_term: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        connection: AsyncConnection | None = None,
    ) -> Dict[str, Any]:
        """
        Get partners using the stored procedure sp_get_partners_directory.
        
        Args:
            person_type_id: Person type ID (default: 2 for partners)
            search_term: Optional search term to filter partners
            limit: Maximum number of results to return (default: 20)
            offset: Number of results to skip (default: 0)
            connection: Database connection
            
        Returns:
            Dictionary with the result from the stored procedure
        """
        if not connection:
            raise ValueError("Connection is required")

        try:
            # Call the stored procedure with parameters
            query = "SELECT sp_get_partners_directory($1, $2, $3, $4)"
            result = await connection.fetchrow(
                query,
                person_type_id,
                search_term,
                limit,
                offset
            )

            if not result or not result[0]:
                raise ValueError("No se encontraron datos de partners")

            # Parse the JSON result from the stored procedure
            try:
                partners_data = result["sp_get_partners_directory"]
                return json.loads(partners_data)
            except (KeyError, json.JSONDecodeError) as e:
                raise ValueError(f"Error al procesar los datos de partners: {str(e)}")
        except ValueError:
            # Re-raise ValueError as-is (these are expected errors)
            raise
        except Exception as e:
            raise RuntimeError(f"Error inesperado al recuperar partners: {str(e)}")

