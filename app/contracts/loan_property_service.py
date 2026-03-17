# app/contracts/loan_property_service.py
"""
Servicio para manejar la creación de loans y properties en contratos
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncConnection

from app.database import fetch_one, execute
from app.contracts.models import contract_loan, contract_property, property_table, contract_bank_account


class ContractLoanPropertyService:

    @staticmethod
    def _normalize_city_id(value: Any) -> Optional[int]:
        """Convierte city_id a int si es numérico; si es string tipo 'CITY-SDE' retorna None."""
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.isdigit():
                return int(stripped)
            # Códigos como "CITY-SDE" no son convertibles; permitir null para no romper el flujo
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

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
            
            # Obtener las fechas del contrato para el cronograma de pagos
            try:
                from app.contracts.models import contract
                from sqlalchemy import select
                
                # Consultar las fechas del contrato
                contract_query = select(contract.c.contract_date, contract.c.start_date, contract.c.end_date).where(
                    contract.c.contract_id == contract_id
                )
                contract_result = await fetch_one(contract_query, connection=connection)
                
                if contract_result:
                    contract_date = contract_result.get("contract_date")
                    start_date = contract_result.get("start_date") or contract_date
                    end_date = contract_result.get("end_date")
                    
                    print(f"📅 Fechas del contrato: contract_date={contract_date}, start_date={start_date}, end_date={end_date}")
                else:
                    print("⚠️ No se encontraron fechas del contrato, usando fechas por defecto")
                    contract_date = date.today()
                    start_date = date.today()
                    end_date = date.today()
                
            except Exception as e:
                print(f"⚠️ Error obteniendo fechas del contrato: {str(e)}, usando fechas por defecto")
                contract_date = date.today()
                start_date = date.today()
                end_date = date.today()
            
            # Generar automáticamente el cronograma de pagos
            try:
                from app.loan_payments.service import LoanPaymentService
                from app.loan_payments.schemas import GeneratePaymentScheduleRequest
                from decimal import Decimal
                from datetime import date
                
                loan_payment_service = LoanPaymentService(connection)
                
                payment_request = GeneratePaymentScheduleRequest(
                    contract_loan_id=loan_id,
                    monthly_quotes=loan_data.get("term_months", 12),
                    monthly_amount=Decimal(str(loan_data.get("loan_payments_details", {}).get("monthly_payment", 0))),
                    interest_amount=Decimal(str(loan_data.get("loan_payments_details", {}).get("monthly_payment", 0))),
                    start_date=start_date,
                    end_date=end_date,
                    last_payment_date=end_date,
                    last_principal=Decimal(str(loan_data.get("loan_payments_details", {}).get("final_payment", 0))),
                    last_interest=Decimal("0")
                )
                
                await loan_payment_service.generate_payment_schedule(payment_request)
                print(f"✅ Cronograma de pagos generado para loan_id: {loan_id}")
                
            except Exception as e:
                print(f"⚠️ Error generando pagos: {str(e)}")

            return {
                "success": True,
                "message": "Loan created successfully with payment schedule",
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
                        "city_id": ContractLoanPropertyService._normalize_city_id(prop_data.get("city_id")),
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

            # Crear bank account si hay datos de cuenta bancaria en el loan (siempre que exista bank_account)
            if "bank_account" in loan_data and loan_data["bank_account"]:
                bank_account_result = await ContractLoanPropertyService._create_bank_account_record(
                    contract_id,
                    loan_data["bank_account"],
                    connection,
                    contract_context or {}
                )
                results["bank_account_result"] = bank_account_result

        # Crear properties
        if properties_data:
            properties_result = await ContractLoanPropertyService.create_contract_properties(
                contract_id, properties_data, connection
            )
            results["properties_result"] = properties_result
            # print(f"🏠 Properties: {'✅' if properties_result['success'] else '❌'} {properties_result['message']}")

        # Determinar éxito general (incluir bank_account si se envió)
        loan_ok = not loan_data or (results["loan_result"] and results["loan_result"]["success"])
        bank_ok = (
            "bank_account" not in (loan_data or {})
            or not (loan_data or {}).get("bank_account")
            or (results.get("bank_account_result") and results["bank_account_result"].get("success"))
        )
        properties_ok = not properties_data or (results["properties_result"] and results["properties_result"]["success"])

        results["overall_success"] = loan_ok and bank_ok and properties_ok

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

        # Prioridad 1: Empresa del cliente (payload usa company_name)
        client_company = contract_context.get("client_company") or {}
        if client_company.get("company_name") or client_company.get("name"):
            holder_name = client_company.get("company_name") or client_company.get("name", "")

        # Prioridad 2: Empresa del inversionista (payload usa company_name)
        elif contract_context.get("investor_company"):
            inv_company = contract_context["investor_company"]
            if inv_company.get("company_name") or inv_company.get("name"):
                holder_name = inv_company.get("company_name") or inv_company.get("name", "")

        # Prioridad 3: Primer cliente (puede estar en participants.clients; person usa p_first_name/p_last_name)
        else:
            clients = contract_context.get("clients") or (contract_context.get("participants") or {}).get("clients") or []
            if clients:
                client = clients[0]
                person = client.get("person", {})
                first_name = person.get("p_first_name") or person.get("first_name", "")
                last_name = person.get("p_last_name") or person.get("last_name", "")
                holder_name = f"{first_name} {last_name}".strip() or holder_name

        try:
            # Aceptar tanto nombres largos (bank_account_*) como cortos (account_*, currency) del payload
            account_number = (
                bank_account_data.get("bank_account_number")
                or bank_account_data.get("account_number")
                or ""
            )
            account_currency = (
                bank_account_data.get("bank_account_currency")
                or bank_account_data.get("currency")
                or "USD"
            )
            bank_name = bank_account_data.get("bank_name") or ""

            # Normalizar account_type para el constraint (corriente, ahorros, inversion, other)
            account_type_raw = (
                bank_account_data.get("bank_account_type")
                or bank_account_data.get("account_type")
                or "corriente"
            )
            if account_type_raw:
                account_type_raw = str(account_type_raw).strip().lower()
            account_type_mapping = {
                "ahorros": "ahorros",
                "corriente": "corriente",
                "inversion": "inversion",
                "other": "other",
                "savings": "ahorros",
                "checking": "corriente",
                "investment": "inversion",
            }
            account_type = account_type_mapping.get(account_type_raw, "corriente")

            # Insert usando la misma capa que create_contract_loan (commit_after=True)
            bank_insert = contract_bank_account.insert().values(
                contract_id=contract_id,
                client_person_id=None,
                holder_name=holder_name,
                bank_name=bank_name,
                account_number=account_number,
                account_type=account_type,
                bank_code=bank_account_data.get("bank_code"),
                swift_code=bank_account_data.get("swift_code"),
                iban=bank_account_data.get("iban"),
                currency=account_currency,
            ).returning(contract_bank_account.c.bank_account_id)

            bank_result = await fetch_one(bank_insert, connection=connection, commit_after=True)

            if bank_result and bank_result.get("bank_account_id") is not None:
                return {
                    "success": True,
                    "bank_account_id": bank_result["bank_account_id"],
                    "holder_name": holder_name,
                    "bank_name": bank_name,
                    "account_number": account_number,
                    "account_type": account_type,
                    "currency": account_currency,
                }
            return {
                "success": False,
                "message": "No se pudo crear el registro de cuenta bancaria",
                "bank_account_id": None,
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error creando cuenta bancaria: {str(e)}",
                "bank_account_id": None,
            }
