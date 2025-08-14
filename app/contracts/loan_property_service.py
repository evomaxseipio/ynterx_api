# app/contracts/loan_property_service.py
"""
Servicio para manejar la creación de loans y properties en contratos
"""

from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import text as sql_text  # ← AGREGAR ESTE IMPORT

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
                    print(f"🔍 Procesando propiedad {idx+1}: {prop_data}")
                    print(f"📝 Campo 'description' recibido: '{prop_data.get('description', 'NO ENCONTRADO')}'")
                    # 1. Crear la propiedad en la tabla property
                    # Preparar valores para insertar
                    insert_values = {
                        "property_type": prop_data.get("property_type"),
                        "cadastral_number": prop_data.get("cadastral_number"),
                        "title_number": prop_data.get("title_number"),
                        "surface_area": prop_data.get("surface_area"),
                        "covered_area": prop_data.get("covered_area"),
                        "property_value": prop_data.get("property_value"),
                        "property_owner": prop_data.get("owner_name"),
                        "owner_civil_status": prop_data.get("owner_civil_status"),
                        "owner_document_number": prop_data.get("owner_document_number"),
                        "owner_nationality": prop_data.get("owner_nationality"),
                        "currency": prop_data.get("currency", "USD"),
                        "property_description": prop_data.get("description"),
                        "address_line1": prop_data.get("address_line1"),
                        "address_line2": prop_data.get("address_line2"),
                        "city_id": int(prop_data.get("city_id")) if prop_data.get("city_id") else None,
                        "postal_code": prop_data.get("postal_code"),
                        "image_path": prop_data.get("image_path"),
                        "is_active": True,
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                    
                    print(f"📝 Valores a insertar: {insert_values}")
                    print(f"🎯 Campo 'property_description' a insertar: '{insert_values.get('property_description', 'VACÍO')}'")
                    
                    property_insert = property_table.insert().values(**insert_values).returning(property_table.c.property_id)

                    property_result = await fetch_one(property_insert, connection=connection, commit_after=True)
                    property_id = property_result["property_id"]
                    print(f"✅ Propiedad insertada con ID: {property_id}")

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
                    print(f"✅ Relación contract_property creada para property_id: {property_id}")

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
                    # Continuar con la siguiente propiedad en lugar de abortar
                    continue

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
                    "message": "No properties were created",
                    "property_ids": [],
                    "properties": [],
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
        connection: AsyncConnection,
        contract_context: Dict[str, Any] = None  # ← AGREGAR ESTE PARÁMETRO
    ) -> Dict[str, Any]:
        """
        Crear tanto loan como properties para un contrato (método conveniente)
        """
        # print(f"🏦 Procesando loan y properties para contrato {contract_id}")

        results = {
            "contract_id": str(contract_id),
            "loan_result": None,
            "properties_result": None,
            "bank_account_result": None,  # ← AGREGAR ESTA LÍNEA
            "overall_success": False
        }

        # Crear loan
        if loan_data:
            loan_result = await ContractLoanPropertyService.create_contract_loan(
                contract_id, loan_data, connection
            )
            results["loan_result"] = loan_result
            # print(f"🏦 Loan: {'✅' if loan_result['success'] else '❌'} {loan_result['message']}")

            # ← AGREGAR ESTA SECCIÓN COMPLETA
            # Crear bank account si hay datos de cuenta bancaria en el loan
            if "bank_account" in loan_data and contract_context:
                bank_account_result = await ContractLoanPropertyService._create_bank_account_record(
                    contract_id, loan_data["bank_account"], connection, contract_context
                )
                results["bank_account_result"] = bank_account_result
                # print(f"🏦 Bank Account: {'✅' if bank_account_result['success'] else '❌'} {bank_account_result.get('message', 'Created')}")

        # Crear properties
        if properties_data:
            properties_result = await ContractLoanPropertyService.create_contract_properties(
                contract_id, properties_data, connection
            )
            results["properties_result"] = properties_result
            # print(f"🏠 Properties: {'✅' if properties_result['success'] else '❌'} {properties_result['message']}")

        # Determinar éxito general
        loan_ok = not loan_data or (results["loan_result"] and results["loan_result"]["success"])
        properties_ok = not properties_data or (results["properties_result"] and results["properties_result"]["success"])

        results["overall_success"] = loan_ok and properties_ok

        return results

    # ← AGREGAR ESTE MÉTODO COMPLETO AL FINAL DE LA CLASE
    @staticmethod
    async def _create_bank_account_record(
        contract_id: UUID,
        bank_account_data: Dict[str, Any],
        connection: AsyncConnection,
        contract_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crear registro de cuenta bancaria en contract_bank_account"""

        # print(f"🏦 Iniciando creación de bank account para contrato {contract_id}")
        # print(f"🔍 Bank account data: {bank_account_data}")
        # print(f"🔍 Contract context keys: {list(contract_context.keys()) if contract_context else 'None'}")

        # Obtener holder_name
        holder_name = "Titular no especificado"

        # Prioridad 1: Empresa del cliente
        if "client_company" in contract_context and contract_context["client_company"].get("name"):
            holder_name = contract_context["client_company"]["name"]
            # print(f"🏢 Usando client_company: {holder_name}")

        # Prioridad 2: Empresa del inversionista
        elif "investor_company" in contract_context and contract_context["investor_company"].get("name"):
            holder_name = contract_context["investor_company"]["name"]
            # print(f"🏢 Usando investor_company: {holder_name}")

        # Prioridad 3: Primer cliente
        elif "clients" in contract_context and contract_context["clients"]:
            client = contract_context["clients"][0]
            person = client.get("person", {})
            first_name = person.get("first_name", "")
            last_name = person.get("last_name", "")
            holder_name = f"{first_name} {last_name}".strip()
            # print(f"👤 Usando primer cliente: {holder_name}")

        try:
            # Normalizar account_type para evitar errores de constraint
            account_type = bank_account_data.get("bank_account_type", "corriente")
            if account_type:
                # Limpiar espacios y normalizar valores
                account_type = account_type.strip().lower()
                # Mapear valores comunes a los permitidos
                account_type_mapping = {
                    "ahorros": "ahorros",
                    "corriente": "corriente",
                    "inversion": "inversion",
                    "savings": "ahorros",
                    "checking": "corriente",
                    "investment": "inversion"
                }
                account_type = account_type_mapping.get(account_type, "corriente")

            # print(f"🔍 Parámetros para INSERT: holder_name={holder_name}, bank_name={bank_account_data.get('bank_name', '')}, account_type={account_type}")

            # Usar connection.execute() directamente como en el router
            result = await connection.execute(
                sql_text("""
                    INSERT INTO contract_bank_account (
                        contract_id, client_person_id, holder_name, bank_name, account_number,
                        account_type, bank_code, swift_code, iban, currency, created_at
                    ) VALUES (
                        :contract_id, :client_person_id, :holder_name, :bank_name, :account_number,
                        :account_type, :bank_code, :swift_code, :iban, :currency, NOW()
                    ) RETURNING bank_account_id
                """),
                {
                    "contract_id": contract_id,
                    "client_person_id": None,
                    "holder_name": holder_name,
                    "bank_name": bank_account_data.get("bank_name", ""),
                    "account_number": bank_account_data.get("bank_account_number", ""),
                    "account_type": account_type,
                    "bank_code": bank_account_data.get("bank_code"),
                    "swift_code": bank_account_data.get("swift_code"),
                    "iban": bank_account_data.get("iban"),
                    "currency": bank_account_data.get("bank_account_currency", "USD")
                }
            )

            # Obtener el resultado
            bank_result = result.fetchone()

            # Commit manualmente
            await connection.commit()

            # print(f"🔍 Bank result: {bank_result}")

            # Convertir a dict si es necesario
            if bank_result:
                bank_account_id = bank_result[0] if hasattr(bank_result, '__getitem__') else bank_result.bank_account_id

                # print(f"✅ Bank Account creado con ID: {bank_account_id}")
                return {
                    "success": True,
                    "bank_account_id": bank_account_id,
                    "holder_name": holder_name,
                    "bank_name": bank_account_data.get("bank_name", ""),
                    "account_number": bank_account_data.get("bank_account_number", ""),
                    "account_type": account_type,
                    "currency": bank_account_data.get("bank_account_currency", "USD")
                }
            else:
                # print(f"❌ No se pudo crear bank account")
                return {
                    "success": False,
                    "message": "No se pudo crear el bank account",
                    "bank_account_id": None
                }

        except Exception as e:
            print(f"❌ Error creando bank account: {str(e)}")
            return {
                "success": False,
                "message": f"Error creating bank account: {str(e)}",
                "bank_account_id": None
            }
