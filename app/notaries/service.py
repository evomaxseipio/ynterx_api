"""Service layer for notary-related operations."""

import json
from uuid import UUID
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncConnection


class NotaryService:
    """Service class for notary operations."""

    @staticmethod
    async def get_notaries(
        notary_id: Optional[UUID] = None,
        connection: AsyncConnection | None = None,
    ) -> Dict[str, Any]:
        """
        Get notaries using the stored procedure sp_get_notaries.
        
        Args:
            notary_id: Optional UUID to get a specific notary
            connection: Database connection
            
        Returns:
            Dictionary with the result from the stored procedure
        """
        if not connection:
            raise ValueError("Connection is required")

        try:
            # Prepare the query based on whether we want all notaries or a specific one
            if notary_id:
                query = "SELECT sp_get_notaries($1)"
                result = await connection.fetchrow(query, notary_id)
            else:
                query = "SELECT sp_get_notaries()"
                result = await connection.fetchrow(query)

            if not result or not result[0]:
                return {
                    "success": False,
                    "error": "NO_DATA",
                    "message": "No se encontraron datos de notarios",
                    "data": None
                }

            # Parse the JSON result from the stored procedure
            try:
                notaries_data = result["sp_get_notaries"]
                return json.loads(notaries_data)
            except (KeyError, json.JSONDecodeError) as e:
                return {
                    "success": False,
                    "error": "PARSE_ERROR",
                    "message": f"Error al procesar los datos de notarios: {str(e)}",
                    "data": None
                }
        except Exception as e:
            return {
                "success": False,
                "error": "DATABASE_ERROR",
                "message": f"Error inesperado al recuperar notarios: {str(e)}",
                "data": None
            } 