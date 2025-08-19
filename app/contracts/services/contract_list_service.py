"""Service layer for contract list operations."""

import json
from uuid import UUID
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncConnection


class ContractListService:
    """Service class for contract list operations."""

    @staticmethod
    async def get_contracts(
        contract_id: Optional[str] = None,
        connection: AsyncConnection | None = None,
    ) -> Dict[str, Any]:

        """
        Get contracts using the stored procedure sp_get_dashboard_contracts_full.
        
        Args:
            contract_id: Optional contract ID to get a specific contract
            connection: Database connection
            
        Returns:
            Dictionary with the result from the stored procedure
        """
        if not connection:
            raise ValueError("Connection is required")

        try:
            # Prepare the query based on whether we want all contracts or a specific one
            if contract_id:
                query = "SELECT sp_get_dashboard_contracts_full($1)"
                result = await connection.fetchrow(query, contract_id)
            else:
                query = "SELECT sp_get_dashboard_contracts_full()"
                result = await connection.fetchrow(query)

            if not result or not result[0]:
                return {
                    "success": True,
                    "contracts": [],
                    "total": 0
                }

            # Parse the JSON result from the stored procedure
            try:
                contracts_data = result["sp_get_dashboard_contracts_full"]
                parsed_data = json.loads(contracts_data)
                
                # Asegurar que la respuesta tenga la estructura correcta
                if isinstance(parsed_data, dict) and "data" in parsed_data:
                    contracts_list = parsed_data.get("data", [])
                    return {
                        "success": parsed_data.get("success", True),
                        "contracts": contracts_list,
                        "total": len(contracts_list)
                    }
                elif isinstance(parsed_data, dict) and "contracts" in parsed_data:
                    return parsed_data
                else:
                    # Si la función devuelve una estructura diferente, adaptarla
                    return {
                        "success": True,
                        "contracts": parsed_data if isinstance(parsed_data, list) else [],
                        "total": len(parsed_data) if isinstance(parsed_data, list) else 0
                    }
            except (KeyError, json.JSONDecodeError) as e:
                return {
                    "success": False,
                    "contracts": [],
                    "total": 0,
                    "error": "PARSE_ERROR",
                    "message": f"Error al procesar los datos de contratos: {str(e)}"
                }
        except Exception as e:
            return {
                "success": False,
                "contracts": [],
                "total": 0,
                "error": "DATABASE_ERROR",
                "message": f"Error inesperado al recuperar contratos: {str(e)}"
            }


