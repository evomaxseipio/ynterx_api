from typing import Dict, Any, List
from datetime import datetime
from app.contracts.utils.data_formatters import format_dates, format_loan_amounts, format_payment_amounts
from app.contracts.processors.participant_data_processor import ParticipantDataProcessor


class ContractDataProcessor:
    """Procesador principal de datos del contrato"""
    
    def __init__(self):
        self.participant_processor = ParticipantDataProcessor()
    
    def flatten_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Aplanar estructura JSON compleja para plantilla Word - Mejorado para contratos hipotecarios"""
        flattened = {}

        # ========================================
        # INFORMACIÓN BÁSICA DEL CONTRATO
        # ========================================
        flattened.update({
            "contract_type": data.get("contract_type", ""),
            "contract_date": data.get("contract_date", datetime.now().strftime("%d de %B de %Y")),
            "description": data.get("description", ""),
            "contract_number": data.get("contract_number", ""),
            "generated_at": data.get("generated_at", datetime.now().isoformat()),
        })

        # ========================================
        # PRÉSTAMO/LOAN
        # ========================================
        if "loan" in data and data["loan"]:
            loan = data["loan"]
            
            # Obtener monto y moneda
            loan_amount = loan.get('amount', 0)
            loan_currency = loan.get("currency", "USD")
            
            # Formatear montos del préstamo
            loan_formatted = format_loan_amounts(loan_amount, loan_currency)
            flattened.update(loan_formatted)
            
            flattened.update({
                "interest_rate": loan.get("interest_rate", ""),
                "loan_term_months": loan.get("term_months", ""),
                "start_date": loan.get("start_date", ""),
                "end_date": loan.get("end_date", ""),
                "loan_type": loan.get("loan_type", ""),
            })

            # Detalles de pagos
            if "loan_payments_details" in loan:
                payments = loan["loan_payments_details"]
                
                # Formatear montos de pago
                monthly_payment_amount = payments.get('monthly_payment', 0)
                final_payment_amount = payments.get('final_payment', 0)
                
                payment_formatted = format_payment_amounts(monthly_payment_amount, final_payment_amount, loan_currency)
                flattened.update(payment_formatted)
                
                flattened.update({
                    "discount_rate": payments.get("discount_rate", ""),
                    "payment_qty_quotes": payments.get("payment_qty_quotes", ""),
                    "payment_qty_months": payments.get("payment_qty_months", ""),
                    "payment_type": payments.get("payment_type", ""),
                })

            # Cuenta bancaria
            if "bank_deposit_account" in loan:
                bank = loan["bank_deposit_account"]
                flattened.update({
                    "bank_account_number": bank.get("account_number", ""),
                    "bank_account_type": bank.get("account_type", ""),
                    "bank_name": bank.get("bank_name", ""),
                })

        # ========================================
        # CUENTA BANCARIA DE LA BASE DE DATOS (NUEVO)
        # ========================================
        if "loan_property_result" in data and data["loan_property_result"]:
            bank_result = data["loan_property_result"].get("bank_account_result")
            if bank_result and bank_result.get("success"):
                flattened.update({
                    "bank_holder_name": bank_result.get("holder_name", ""),
                    "bank_name": bank_result.get("bank_name", ""),
                    "bank_account_number": bank_result.get("account_number", ""),
                    "bank_account_type": bank_result.get("account_type", ""),
                    "bank_currency": bank_result.get("currency", "USD"),
                    "bank_account_id": bank_result.get("bank_account_id", ""),
                })

        # ========================================
        # PROPIEDADES
        # ========================================
        if "properties" in data and data["properties"]:
            # Primera propiedad como principal
            prop = data["properties"][0]
            flattened.update({
                "property_type": prop.get("property_type", ""),
                "property_cadastral": prop.get("cadastral_number", ""),
                "property_title": prop.get("title_number", ""),
                "property_surface_area": prop.get("surface_area", ""),
                "property_covered_area": prop.get("covered_area", ""),
                "property_address": prop.get("address_line1", ""),
                "property_address2": prop.get("address_line2", ""),
                "property_value": f"{prop.get('property_value', 0):,.2f}",
                "property_value_raw": prop.get('property_value', 0),
                "property_currency": prop.get("currency", "USD"),
                "property_description": prop.get("description", ""),
                "property_owner": prop.get("property_owner", ""),
            })

            # Todas las propiedades para iteración
            flattened["all_properties"] = data["properties"]

        # ========================================
        # EMPRESAS (MEJORADO)
        # ========================================
        if "investor_company" in data:
            company = data["investor_company"]
            company_address = company.get("company_address", {})
            company_managers = company.get("company_manager", [])
            main_manager = next((m for m in company_managers if m.get("is_main_manager")), company_managers[0] if company_managers else {})
            
            flattened.update({
                "investor_company_name": company.get("company_name", ""),
                "investor_company_rnc": company.get("company_rnc", ""),
                "investor_company_mercantil_number": company.get("company_mercantil_number", ""),
                "investor_company_phone": company.get("company_phone", ""),
                "investor_company_email": company.get("company_email", ""),
                "investor_company_type": company.get("company_type", ""),
                "investor_company_address": company_address.get("address_line1", ""),
                "investor_company_address2": company_address.get("address_line2", ""),
                "investor_company_city": company_address.get("city", ""),
                "investor_company_postal_code": company_address.get("postal_code", ""),
                "investor_company_address_type": company_address.get("address_type", ""),
                "investor_manager_name": main_manager.get("name", ""),
                "investor_manager_position": main_manager.get("position", ""),
                "investor_manager_document_number": main_manager.get("document_number", ""),
                "investor_manager_nationality": main_manager.get("nationality", ""),
                "investor_manager_marital_status": main_manager.get("marital_status", ""),
                "investor_manager_address": main_manager.get("address", ""),
            })

        if "client_company" in data:
            company = data["client_company"]
            company_address = company.get("company_address", {})
            company_managers = company.get("company_manager", [])
            main_manager = next((m for m in company_managers if m.get("is_main_manager")), company_managers[0] if company_managers else {})
            
            flattened.update({
                "client_company_name": company.get("company_name", ""),
                "client_company_rnc": company.get("company_rnc", ""),
                "client_company_mercantil_number": company.get("company_mercantil_number", ""),
                "client_company_phone": company.get("company_phone", ""),
                "client_company_email": company.get("company_email", ""),
                "client_company_type": company.get("company_type", ""),
                "client_company_address": company_address.get("address_line1", ""),
                "client_company_address2": company_address.get("address_line2", ""),
                "client_company_city": company_address.get("city", ""),
                "client_company_postal_code": company_address.get("postal_code", ""),
                "client_company_address_type": company_address.get("address_type", ""),
                "client_manager_name": main_manager.get("name", ""),
                "client_manager_position": main_manager.get("position", ""),
                "client_manager_document_number": main_manager.get("document_number", ""),
                "client_manager_nationality": main_manager.get("nationality", ""),
                "client_manager_marital_status": main_manager.get("marital_status", ""),
                "client_manager_address": main_manager.get("address", ""),
            })

        # ========================================
        # PARTICIPANTES (CLIENTES, INVERSIONISTAS, ETC.)
        # ========================================
        # Procesar clientes
        if "clients" in data and data["clients"]:
            clients_result = self.participant_processor.process_clients(data["clients"])
            flattened.update(clients_result)

        # Procesar inversionistas
        if "investors" in data and data["investors"]:
            investors_result = self.participant_processor.process_investors(data["investors"])
            flattened.update(investors_result)

        # Procesar testigos
        if "witnesses" in data and data["witnesses"]:
            witnesses_result = self.participant_processor.process_witnesses(data["witnesses"])
            flattened.update(witnesses_result)

        # Procesar notarios
        if "notaries" in data and data["notaries"]:
            notaries_result = self.participant_processor.process_notaries(data["notaries"])
            flattened.update(notaries_result)
        elif "notary" in data and data["notary"]:
            notaries_result = self.participant_processor.process_notaries(data["notary"])
            flattened.update(notaries_result)

        # Procesar referentes
        if "referents" in data and data["referents"]:
            referrers_result = self.participant_processor.process_referrers(data["referents"])
            flattened.update(referrers_result)

        # ========================================
        # FECHAS Y METADATOS
        # ========================================
        contract_date_str = data.get("contract_date")
        contract_end_date_str = data.get("contract_end_date")
        
        dates_formatted = format_dates(contract_date_str, contract_end_date_str)
        flattened.update(dates_formatted)

        # ========================================
        # DATOS DIRECTOS (para compatibilidad)
        # ========================================
        for key, value in data.items():
            if not isinstance(value, (dict, list)) and key not in flattened:
                flattened[key] = value

        # ========================================
        # ASIGNACIÓN DE NOMBRES PARA COMPATIBILIDAD
        # ========================================
        # Si no existe client_full_name, usar client_manager_name
        if "client_full_name" not in flattened or not flattened["client_full_name"]:
            if "client_manager_name" in flattened and flattened["client_manager_name"]:
                flattened["client_full_name"] = flattened["client_manager_name"]
        
        # Si no existe investor_full_name, usar investor_manager_name
        if "investor_full_name" not in flattened or not flattened["investor_full_name"]:
            if "investor_manager_name" in flattened and flattened["investor_manager_name"]:
                flattened["investor_full_name"] = flattened["investor_manager_name"]

        return flattened
