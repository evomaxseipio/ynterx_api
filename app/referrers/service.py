"""Service layer for referrer-related operations."""

import json
from uuid import UUID
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncConnection


class ReferrerService:
    """Service class for referrer operations."""

    @staticmethod
    async def get_referrers(
        referrer_id: Optional[UUID] = None,
        connection: AsyncConnection | None = None,
    ) -> Dict[str, Any]:
        """
        Get referrers using the stored procedure sp_get_referrers.
        
        Args:
            referrer_id: Optional UUID to get a specific referrer
            connection: Database connection
            
        Returns:
            Dictionary with the result from the stored procedure
        """
        if not connection:
            raise ValueError("Connection is required")

        try:
            # Prepare the query based on whether we want all referrers or a specific one
            if referrer_id:
                query = "SELECT sp_get_referrers($1)"
                result = await connection.fetchrow(query, referrer_id)
            else:
                query = "SELECT sp_get_referrers()"
                result = await connection.fetchrow(query)

            if not result or not result[0]:
                return {
                    "success": False,
                    "error": "NO_DATA",
                    "message": "No se encontraron datos de referentes",
                    "data": None
                }

            # Parse the JSON result from the stored procedure
            try:
                referrers_data = result["sp_get_referrers"]
                return json.loads(referrers_data)
            except (KeyError, json.JSONDecodeError) as e:
                return {
                    "success": False,
                    "error": "PARSE_ERROR",
                    "message": f"Error al procesar los datos de referentes: {str(e)}",
                    "data": None
                }
        except Exception as e:
            return {
                "success": False,
                "error": "DATABASE_ERROR",
                "message": f"Error inesperado al recuperar referentes: {str(e)}",
                "data": None
            } 