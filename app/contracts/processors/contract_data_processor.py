from typing import Dict, Any, List
from datetime import datetime
from app.contracts.utils.data_formatters import format_dates, format_loan_amounts, format_payment_amounts
from app.contracts.processors.participant_data_processor import ParticipantDataProcessor


class ContractDataProcessor:
    """Main contract data processor"""
    
    def __init__(self):
        self.participant_processor = ParticipantDataProcessor()
    
    def flatten_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten complex JSON structure for Word template"""
        flattened = {}

        # Basic contract information
        flattened.update({
            "contract_type": data.get("contract_type", ""),
            "contract_date": data.get("contract_date", datetime.now().strftime("%d de %B de %Y")),
            "description": data.get("description", ""),
            "contract_number": data.get("contract_number", ""),
            "generated_at": data.get("generated_at", datetime.now().isoformat()),
        })

        # Loan information
        if "loan" in data and data["loan"]:
            loan = data["loan"]
            loan_amount = loan.get('amount', 0)
            loan_currency = loan.get("currency", "USD")
            
            loan_formatted = format_loan_amounts(loan_amount, loan_currency)
            flattened.update(loan_formatted)
            
            flattened.update({
                "interest_rate": loan.get("interest_rate", ""),
                "loan_term_months": loan.get("term_months", ""),
                "start_date": loan.get("start_date", ""),
                "end_date": loan.get("end_date", ""),
                "loan_type": loan.get("loan_type", ""),
            })

            if "loan_payments_details" in loan:
                payments = loan["loan_payments_details"]
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

            if "bank_deposit_account" in loan:
                bank = loan["bank_deposit_account"]
                flattened.update({
                    "bank_account_number": bank.get("account_number", ""),
                    "bank_account_type": bank.get("account_type", ""),
                    "bank_name": bank.get("bank_name", ""),
                })

        # Bank account from database
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

        # Properties
        if "properties" in data and data["properties"]:
            properties = data["properties"]
            prop = properties[0]
            
            flattened.update({
                "property_type": prop.get("property_type", ""),
                "property_cadastral": prop.get("cadastral_number", ""),
                "property_surface_area": prop.get("surface_area", ""),
                "property_covered_area": prop.get("covered_area", ""),
                "property_address": prop.get("address_line1", ""),
                "property_address2": prop.get("address_line2", ""),
                "property_value": f"{prop.get('property_value', 0):,.2f}",
                "property_value_raw": prop.get('property_value', 0),
                "property_currency": prop.get("currency", "USD"),
                "property_owner": prop.get("property_owner", ""),
            })
            
            # Format property_title based on number of properties
            if len(properties) == 1:
                title = prop.get("title_number", "")
                if title:
                    title = title.strip()
                    if not title.endswith('.'):
                        title = title + "."
                flattened["property_title"] = title
            else:
                # Multiple properties: join titles with commas, last one with " y " before period
                titles = []
                for p in properties:
                    title = p.get("title_number", "")
                    if title:
                        titles.append(title.strip())
                
                if titles:
                    if len(titles) == 1:
                        flattened["property_title"] = titles[0] + "."
                    else:
                        # Join all but last with commas, last with " y " before period
                        formatted_titles = ", ".join(titles[:-1]) + " y " + titles[-1] + "."
                        flattened["property_title"] = formatted_titles
                else:
                    flattened["property_title"] = ""
            
            # Format property_description based on number of properties
            if len(properties) == 1:
                description = prop.get("description", "")
                if description and not description.rstrip().endswith('.'):
                    description = description.rstrip() + "."
                flattened["property_description"] = description
            else:
                # Multiple properties: prefix with A., B., C., etc. on separate lines
                # Each property with hanging indent (subsequent lines aligned with text after prefix)
                # Last property ends with ".", others end with "; y"
                descriptions = []
                for idx, p in enumerate(properties):
                    letter = chr(65 + idx)
                    description = p.get("description", "")
                    if description:
                        description = description.strip()
                        # Remove any existing punctuation at the end
                        description = description.rstrip('.;')
                        
                        # Last property ends with ".", others end with "; y"
                        if idx == len(properties) - 1:
                            description = description + "."
                        else:
                            description = description + "; y"
                        
                        descriptions.append(f"{letter}. {description}")
                
                # Join with blank line between properties (\r\n\r\n) for Word compatibility
                flattened["property_description"] = "\r\n\r\n".join(descriptions)
            
            flattened["all_properties"] = properties

        # Companies
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

        # Participants (clients, investors, witnesses, notaries, referrers)
        if "clients" in data and data["clients"]:
            clients_result = self.participant_processor.process_clients(data["clients"])
            flattened.update(clients_result)

        if "investors" in data and data["investors"]:
            investors_result = self.participant_processor.process_investors(data["investors"])
            flattened.update(investors_result)

        if "witnesses" in data and data["witnesses"]:
            witnesses_result = self.participant_processor.process_witnesses(data["witnesses"])
            flattened.update(witnesses_result)

        if "notaries" in data and data["notaries"]:
            notaries_result = self.participant_processor.process_notaries(data["notaries"])
            flattened.update(notaries_result)
        elif "notary" in data and data["notary"]:
            notaries_result = self.participant_processor.process_notaries(data["notary"])
            flattened.update(notaries_result)

        if "referents" in data and data["referents"]:
            referrers_result = self.participant_processor.process_referrers(data["referents"])
            flattened.update(referrers_result)

        # Dates and metadata
        contract_date_str = data.get("contract_date")
        contract_end_date_str = data.get("contract_end_date")
        dates_formatted = format_dates(contract_date_str, contract_end_date_str)
        flattened.update(dates_formatted)

        # Direct data mapping (for compatibility)
        for key, value in data.items():
            if not isinstance(value, (dict, list)) and key not in flattened:
                flattened[key] = value

        # Name fallbacks for compatibility
        if "client_full_name" not in flattened or not flattened["client_full_name"]:
            if "client_manager_name" in flattened and flattened["client_manager_name"]:
                flattened["client_full_name"] = flattened["client_manager_name"]
        
        if "investor_full_name" not in flattened or not flattened["investor_full_name"]:
            if "investor_manager_name" in flattened and flattened["investor_manager_name"]:
                flattened["investor_full_name"] = flattened["investor_manager_name"]

        return flattened
