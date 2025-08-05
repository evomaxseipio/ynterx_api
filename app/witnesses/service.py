"""Service layer for witness-related operations."""

import json
from uuid import UUID
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncConnection


class WitnessService:
    """Service class for witness operations."""

    @staticmethod
    async def get_witnesses(
        witness_id: Optional[UUID] = None,
        connection: AsyncConnection | None = None,
    ) -> Dict[str, Any]:
        """
        Get witnesses using the stored procedure sp_get_witnesses.
        
        Args:
            witness_id: Optional UUID to get a specific witness
            connection: Database connection
            
        Returns:
            Dictionary with the result from the stored procedure
        """
        if not connection:
            raise ValueError("Connection is required")

        try:
            # Prepare the query based on whether we want all witnesses or a specific one
            if witness_id:
                query = "SELECT sp_get_witnesses($1)"
                result = await connection.fetchrow(query, witness_id)
            else:
                query = "SELECT sp_get_witnesses()"
                result = await connection.fetchrow(query)

            if not result or not result[0]:
                return {
                    "success": False,
                    "error": "NO_DATA",
                    "message": "No se encontraron datos de testigos",
                    "data": None
                }

            # Parse the JSON result from the stored procedure
            try:
                witnesses_data = result["sp_get_witnesses"]
                return json.loads(witnesses_data)
            except (KeyError, json.JSONDecodeError) as e:
                return {
                    "success": False,
                    "error": "PARSE_ERROR",
                    "message": f"Error al procesar los datos de testigos: {str(e)}",
                    "data": None
                }
        except Exception as e:
            return {
                "success": False,
                "error": "DATABASE_ERROR",
                "message": f"Error inesperado al recuperar testigos: {str(e)}",
                "data": None
            } 