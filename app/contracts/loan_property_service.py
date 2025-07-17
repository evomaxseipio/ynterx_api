
# app/contracts/loan_property_service.py
"""
Servicio para manejar la creación de loans y properties en contratos
"""

from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncConnection

from app.database import fetch_one, execute
from app.contracts.models import contract_loan, contract_property, property_table


class ContractLoanPropertyService:

    @staticmethod
    async def create_contract_loan(
        contract_id: UUID,
        loan_data: Dict[str, Any],
        connection: AsyncConnection
    ) -> Dict[str, Any]:
        """
        Crear registro de préstamo para un contrato
        """
        try:
            if not loan_data:
                return {"success": True, "message": "No loan data provided", "loan_id": None}

            loan_insert = contract_loan.insert().values(
                contract_id=contract_id,
                loan_amount=loan_data.get("amount"),
                currency=loan_data.get("currency", "USD"),
                interest_rate=loan_data.get("interest_rate"),
                term_months=loan_data.get("term_months"),
                loan_type=loan_data.get("loan_type"),
                monthly_payment=loan_data.get("loan_payments_details", {}).get("monthly_payment"),
                final_payment=loan_data.get("loan_payments_details", {}).get("final_payment"),
                discount_rate=loan_data.get("loan_payments_details", {}).get("discount_rate"),
                payment_qty_quotes=loan_data.get("loan_payments_details", {}).get("payment_qty_quotes"),
                payment_type=loan_data.get("loan_payments_details", {}).get("payment_type"),
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ).returning(contract_loan.c.contract_loan_id)

            result = await fetch_one(loan_insert, connection=connection, commit_after=True)
            loan_id = result["contract_loan_id"]

            print(f"✅ Loan creado con ID: {loan_id}")
            return {
                "success": True,
                "message": "Loan created successfully",
                "loan_id": loan_id
            }

        except Exception as e:
            print(f"❌ Error creando loan: {str(e)}")
            return {
                "success": False,
                "message": f"Error creating loan: {str(e)}",
                "loan_id": None
            }

    @staticmethod
    async def create_contract_properties(
        contract_id: UUID,
        properties_data: List[Dict[str, Any]],
        connection: AsyncConnection
    ) -> Dict[str, Any]:
        """
        Crear propiedades y relacionarlas con el contrato
        """
        try:
            if not properties_data:
                return {"success": True, "message": "No properties data provided", "property_ids": []}

            created_properties = []
            property_errors = []

            for idx, prop_data in enumerate(properties_data):
                try:
                    # 1. Crear la propiedad en la tabla property
                    property_insert = property_table.insert().values(
                        property_type=prop_data.get("property_type"),
                        cadastral_number=prop_data.get("cadastral_number"),
                        title_number=prop_data.get("title_number"),
                        surface_area=prop_data.get("surface_area"),
                        covered_area=prop_data.get("covered_area"),
                        property_value=prop_data.get("property_value"),
                        currency=prop_data.get("currency", "USD"),
                        description=prop_data.get("description"),
                        address_line1=prop_data.get("address_line1"),
                        address_line2=prop_data.get("address_line2"),
                        city_id=prop_data.get("city_id"),  # Puede ser None si no se mapea
                        postal_code=prop_data.get("postal_code"),
                        is_active=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    ).returning(property_table.c.property_id)

                    property_result = await fetch_one(property_insert, connection=connection, commit_after=True)
                    property_id = property_result["property_id"]

                    # 2. Relacionar la propiedad con el contrato
                    contract_property_insert = contract_property.insert().values(
                        contract_id=contract_id,
                        property_id=property_id,
                        property_role=prop_data.get("property_role", "garantia"),
                        is_primary=idx == 0,  # Primera propiedad es primary
                        notes=prop_data.get("notes"),
                        is_active=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )

                    await execute(contract_property_insert, connection=connection, commit_after=True)

                    created_properties.append({
                        "property_id": property_id,
                        "cadastral_number": prop_data.get("cadastral_number"),
                        "title_number": prop_data.get("title_number"),
                        "is_primary": idx == 0
                    })

                    print(f"✅ Propiedad {idx+1} creada con ID: {property_id}")

                except Exception as prop_error:
                    property_errors.append({
                        "index": idx,
                        "cadastral_number": prop_data.get("cadastral_number", "Unknown"),
                        "error": str(prop_error)
                    })
                    print(f"❌ Error creando propiedad {idx+1}: {str(prop_error)}")

            # Resultado final
            if created_properties:
                return {
                    "success": True,
                    "message": f"Created {len(created_properties)} properties successfully",
                    "property_ids": [p["property_id"] for p in created_properties],
                    "properties": created_properties,
                    "errors": property_errors if property_errors else None
                }
            else:
                return {
                    "success": False,
                    "message": "No properties could be created",
                    "property_ids": [],
                    "errors": property_errors
                }

        except Exception as e:
            print(f"❌ Error general creando properties: {str(e)}")
            return {
                "success": False,
                "message": f"Error creating properties: {str(e)}",
                "property_ids": []
            }

    @staticmethod
    async def create_contract_loan_and_properties(
        contract_id: UUID,
        loan_data: Dict[str, Any],
        properties_data: List[Dict[str, Any]],
        connection: AsyncConnection
    ) -> Dict[str, Any]:
        """
        Crear tanto loan como properties para un contrato (método conveniente)
        """
        print(f"🏦 Procesando loan y properties para contrato {contract_id}")

        results = {
            "contract_id": str(contract_id),
            "loan_result": None,
            "properties_result": None,
            "overall_success": False
        }

        # Crear loan
        if loan_data:
            loan_result = await ContractLoanPropertyService.create_contract_loan(
                contract_id, loan_data, connection
            )
            results["loan_result"] = loan_result
            print(f"🏦 Loan: {'✅' if loan_result['success'] else '❌'} {loan_result['message']}")

        # Crear properties
        if properties_data:
            properties_result = await ContractLoanPropertyService.create_contract_properties(
                contract_id, properties_data, connection
            )
            results["properties_result"] = properties_result
            print(f"🏠 Properties: {'✅' if properties_result['success'] else '❌'} {properties_result['message']}")

        # Determinar éxito general
        loan_ok = not loan_data or (results["loan_result"] and results["loan_result"]["success"])
        properties_ok = not properties_data or (results["properties_result"] and results["properties_result"]["success"])

        results["overall_success"] = loan_ok and properties_ok

        return results
