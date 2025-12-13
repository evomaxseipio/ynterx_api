"""Service layer for contract list operations."""

import json
from uuid import UUID
from typing import Optional, Dict, Any
import asyncpg


class ContractListService:
    """Service class for contract list operations."""

    @staticmethod
    async def get_contracts(
        contract_id: Optional[str] = None,
        connection: asyncpg.Connection | None = None,
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
                contracts_data = await connection.fetchval(query, contract_id)
            else:
                query = "SELECT sp_get_dashboard_contracts_full()"
                contracts_data = await connection.fetchval(query)

            if not contracts_data:
                return {
                    "success": True,
                    "contracts": [],
                    "total": 0
                }

            # Parse the JSON result from the stored procedure
            try:
                
                parsed_data = json.loads(contracts_data)
                
                # Asegurar que parsed_data no sea None
                if parsed_data is None:
                    return {
                        "success": True,
                        "contracts": [],
                        "total": 0
                    }
                
                # Asegurar que la respuesta tenga la estructura correcta
                if isinstance(parsed_data, dict) and "data" in parsed_data:
                    contracts_list = parsed_data.get("data") or []
                    # Asegurar que contracts_list sea siempre una lista
                    if not isinstance(contracts_list, list):
                        contracts_list = []
                    return {
                        "success": parsed_data.get("success", True),
                        "contracts": contracts_list,
                        "total": len(contracts_list)
                    }
                elif isinstance(parsed_data, dict) and "contracts" in parsed_data:
                    contracts_list = parsed_data.get("contracts") or []
                    if not isinstance(contracts_list, list):
                        contracts_list = []
                    return {
                        "success": parsed_data.get("success", True),
                        "contracts": contracts_list,
                        "total": len(contracts_list)
                    }
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
            import traceback
            error_trace = traceback.format_exc()
            error_msg = f"Error inesperado al recuperar contratos: {str(e)}"
            # Log del error completo para debugging (en producción esto iría a un logger)
            print(f"ERROR en get_contracts: {error_msg}")
            print(f"Traceback: {error_trace}")
            return {
                "success": False,
                "contracts": [],
                "total": 0,
                "error": "DATABASE_ERROR",
                "message": error_msg
            }


