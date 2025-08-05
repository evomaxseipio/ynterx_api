# contract_service.py
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import HTTPException, UploadFile
from docxtpl import DocxTemplate
import json
import uuid
import shutil
import os
<<<<<<< HEAD
=======
import asyncio
from app.config import settings
from app.utils.email_services import send_email, load_email_template
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f


class ContractService:
    """Servicio completo de contratos con todas las funcionalidades"""

    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.doc', '.docx', '.pdf', '.xls', '.xlsx'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

<<<<<<< HEAD
    def __init__(self, use_google_drive: bool = False):
=======
    def __init__(self, use_google_drive: bool = True):
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
        self.use_google_drive = use_google_drive
        self.base_dir = Path(__file__).parent.parent
        self.template_dir = self.base_dir / "templates"
        self.contracts_dir = self.base_dir / "generated_contracts"
        self._ensure_directories()

        # Inicializar Google Drive si está habilitado
        if self.use_google_drive:
            self._init_google_drive()

    def _ensure_directories(self):
        """Crear directorios necesarios"""
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.contracts_dir.mkdir(parents=True, exist_ok=True)

    def _init_google_drive(self):
        """Inicializar servicio de Google Drive"""
        try:
            from .gdrive_service import GoogleDriveService
            self.gdrive_service = GoogleDriveService()
        except ImportError:
            raise HTTPException(500, "Google Drive no configurado correctamente")

    def _generate_contract_id(self, prefix: str = "contract") -> str:
        """Generar ID único para el contrato"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}_{timestamp}_{unique_id}"

    def _get_contract_folder(self, contract_id: str) -> Path:
        """Crear carpeta individual para el contrato"""
        folder = self.contracts_dir / contract_id
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "attachments").mkdir(parents=True, exist_ok=True)
        return folder

    def _save_metadata(self, folder: Path, contract_id: str, data: Dict[str, Any], version: int = 1):
        """Guardar metadatos del contrato"""
        metadata = {
            "contract_id": contract_id,
            "created_at": datetime.now().isoformat(),
            "modified_at": datetime.now().isoformat(),
            "original_data": data,
            "version": version,
            "storage_type": "google_drive" if self.use_google_drive else "local"
        }

        metadata_file = folder / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)


        # Actualizar en service.py el método _flatten_data

    def _flatten_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
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
<<<<<<< HEAD
            flattened.update({
                "loan_amount": f"{loan.get('amount', 0):,.2f}",
                "loan_amount_raw": loan.get('amount', 0),
                "loan_currency": loan.get("currency", "USD"),
=======
            
            # Importar función de conversión de números a texto
            from app.utils.number_to_text import numero_a_texto_con_monto, numero_a_texto_simple
            
            # Obtener monto y moneda
            loan_amount = loan.get('amount', 0)
            loan_currency = loan.get("currency", "USD")
            
            # Generar texto legal del monto (con formato numérico)
            loan_amount_text = numero_a_texto_con_monto(loan_amount, loan_currency)
            
            # Generar texto simple del monto (sin formato numérico)
            loan_amount_text_simple = numero_a_texto_simple(loan_amount, loan_currency)
            
            flattened.update({
                "loan_amount": f"{loan_amount:,.2f}",
                "loan_amount_raw": loan_amount,
                "loan_amount_text": loan_amount_text,
                "loan_amount_text_simple": loan_amount_text_simple,
                "loan_currency": loan_currency,
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
                "interest_rate": loan.get("interest_rate", ""),
                "loan_term_months": loan.get("term_months", ""),
                "start_date": loan.get("start_date", ""),
                "end_date": loan.get("end_date", ""),
                "loan_type": loan.get("loan_type", ""),
            })

            # Detalles de pagos
            if "loan_payments_details" in loan:
                payments = loan["loan_payments_details"]
<<<<<<< HEAD
                flattened.update({
                    "monthly_payment": f"{payments.get('monthly_payment', 0):,.2f}",
                    "monthly_payment_raw": payments.get('monthly_payment', 0),
                    "final_payment": f"{payments.get('final_payment', 0):,.2f}",
                    "final_payment_raw": payments.get('final_payment', 0),
=======
                
                # Generar texto legal para pagos mensuales y final
                monthly_payment_amount = payments.get('monthly_payment', 0)
                final_payment_amount = payments.get('final_payment', 0)
                
                monthly_payment_text = numero_a_texto_con_monto(monthly_payment_amount, loan_currency)
                final_payment_text = numero_a_texto_con_monto(final_payment_amount, loan_currency)
                
                flattened.update({
                    "monthly_payment": f"{monthly_payment_amount:,.2f}",
                    "monthly_payment_raw": monthly_payment_amount,
                    "monthly_payment_text": monthly_payment_text,
                    "final_payment": f"{final_payment_amount:,.2f}",
                    "final_payment_raw": final_payment_amount,
                    "final_payment_text": final_payment_text,
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
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
<<<<<<< HEAD
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
                "property_city": prop.get("city", ""),
                "property_postal_code": prop.get("postal_code", ""),
                "property_value": f"{prop.get('property_value', 0):,.2f}",
                "property_value_raw": prop.get('property_value', 0),
                "property_currency": prop.get("currency", "USD"),
                "property_description": prop.get("description", ""),
                "property_appraised_by": prop.get("appraised_by", ""),
                "property_appraised_at": prop.get("appraised_at", ""),
            })

            # Todas las propiedades para iteración
            flattened["all_properties"] = data["properties"]

        # ========================================
        # EMPRESAS
        # ========================================
        if "investor_company" in data:
            company = data["investor_company"]
            flattened.update({
                "investor_company_name": company.get("name", ""),
                "investor_company_rnc": company.get("rnc", ""),
                "investor_company_rm": company.get("rm", ""),
            })

        if "client_company" in data:
            company = data["client_company"]
            flattened.update({
                "client_company_name": company.get("name", ""),
                "client_company_rnc": company.get("rnc", ""),
                "client_company_rm": company.get("rm", ""),
            })

        # ========================================
        # CLIENTES (MEJORADO)
        # ========================================
        if "clients" in data and data["clients"]:
            clients_list = []

            for idx, client in enumerate(data["clients"]):
                person = client.get("person", {})
                document = client.get("person_document", {})
                address = client.get("address", {})

=======
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
                "property_description": prop.get("property_description", ""),
                "property_owner": prop.get("property_owner", ""),
            })

            # Todas las propiedades para iteración
            flattened["all_properties"] = data["properties"]

        # ========================================
        # EMPRESAS
        # ========================================
        if "investor_company" in data:
            company = data["investor_company"]
            flattened.update({
                "investor_company_name": company.get("name", ""),
                "investor_company_rnc": company.get("rnc", ""),
                "investor_company_rm": company.get("rm", ""),
            })

        if "client_company" in data:
            company = data["client_company"]
            flattened.update({
                "client_company_name": company.get("name", ""),
                "client_company_rnc": company.get("rnc", ""),
                "client_company_rm": company.get("rm", ""),
            })

        # ========================================
        # CLIENTES (MEJORADO)
        # ========================================
        if "clients" in data and data["clients"]:
            clients_list = []

            for idx, client in enumerate(data["clients"]):
                person = client.get("person", {})
                document = client.get("person_document", {})
                address = client.get("address", {})

                # Mascara por defecto para email y teléfono
                email = person.get("email", "") or "xxxxxx@xmail.com"
                phone = person.get("phone_number", "") or "(XXX) XXX-XXXX"

>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
                client_flat = {
                    "first_name": person.get("first_name", ""),
                    "last_name": person.get("last_name", ""),
                    "middle_name": person.get("middle_name", ""),
                    "full_name": f"{person.get('first_name', '')} {person.get('middle_name', '') or ''} {person.get('last_name', '')}".strip(),
                    "date_of_birth": person.get("date_of_birth", ""),
                    "gender": person.get("gender", ""),
                    "nationality": person.get("nationality", ""),
                    "marital_status": person.get("marital_status", ""),
<<<<<<< HEAD
                    "phone_number": person.get("phone_number", ""),
                    "email": person.get("email", ""),
=======
                    "phone_number": phone,
                    "email": email,
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
                    "document_type": document.get("document_type", ""),
                    "document_number": document.get("document_number", ""),
                    "issuing_country": document.get("issuing_country", ""),
                    "document_issue_date": document.get("document_issue_date", ""),
                    "document_expiry_date": document.get("document_expiry_date", ""),
                    "address_line1": address.get("address_line1", ""),
                    "address_line2": address.get("address_line2", ""),
                    "city": address.get("city", ""),
                    "postal_code": address.get("postal_code", ""),
                    "address_type": address.get("address_type", ""),
                    "is_principal": address.get("is_principal", False),
                }
                clients_list.append(client_flat)

            # Exponer lista completa
            flattened["clients"] = clients_list
            flattened["clients_count"] = len(clients_list)

            # Cliente principal (primero)
            if clients_list:
                main_client = clients_list[0]
                flattened.update({
                    "client_name": f"{main_client['first_name']} {main_client['last_name']}",
                    "client_full_name": main_client["full_name"],
                    "client_first_name": main_client["first_name"],
                    "client_last_name": main_client["last_name"],
                    "client_middle_name": main_client["middle_name"],
                    "client_date_of_birth": main_client["date_of_birth"],
                    "client_gender": main_client["gender"],
                    "client_nationality": main_client["nationality"],
                    "client_marital_status": main_client["marital_status"],
<<<<<<< HEAD
                    "client_phone": main_client["phone_number"],
                    "client_email": main_client["email"],
=======
                    "client_phone": main_client["phone_number"] or "(XXX) XXX-XXXX",
                    "client_email": main_client["email"] or "xxxxxx@xmail.com",
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
                    "client_document_type": main_client["document_type"],
                    "client_document_number": main_client["document_number"],
                    "client_issuing_country": main_client["issuing_country"],
                    "client_address": main_client["address_line1"],
                    "client_address2": main_client["address_line2"],
                    "client_city": main_client["city"],
                    "client_postal_code": main_client["postal_code"],
                })

        # ========================================
        # INVERSIONISTAS (MEJORADO)
        # ========================================
        if "investors" in data and data["investors"]:
            investors_list = []

            for idx, investor in enumerate(data["investors"]):
                person = investor.get("person", {})
                document = investor.get("person_document", {})
                address = investor.get("address", {})

<<<<<<< HEAD
=======
                # Mascara por defecto para email y teléfono
                email = person.get("email", "") or "xxxxxx@xmail.com"
                phone = person.get("phone_number", "") or "(XXX) XXX-XXXX"

>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
                investor_flat = {
                    "first_name": person.get("first_name", ""),
                    "last_name": person.get("last_name", ""),
                    "middle_name": person.get("middle_name", ""),
                    "full_name": f"{person.get('first_name', '')} {person.get('middle_name', '') or ''} {person.get('last_name', '')}".strip(),
                    "date_of_birth": person.get("date_of_birth", ""),
                    "gender": person.get("gender", ""),
                    "nationality": person.get("nationality", ""),
                    "marital_status": person.get("marital_status", ""),
<<<<<<< HEAD
                    "phone_number": person.get("phone_number", ""),
                    "email": person.get("email", ""),
=======
                    "phone_number": phone,
                    "email": email,
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
                    "document_type": document.get("document_type", ""),
                    "document_number": document.get("document_number", ""),
                    "address_line1": address.get("address_line1", ""),
                    "city": address.get("city", ""),
                }
                investors_list.append(investor_flat)

            flattened["investors"] = investors_list
            flattened["investors_count"] = len(investors_list)

            # Inversionista principal
            if investors_list:
                main_investor = investors_list[0]
                flattened.update({
                    "investor_name": f"{main_investor['first_name']} {main_investor['last_name']}",
                    "investor_full_name": main_investor["full_name"],
                    "investor_first_name": main_investor["first_name"],
                    "investor_last_name": main_investor["last_name"],
                    "investor_middle_name": main_investor["middle_name"],
                    "investor_document_number": main_investor["document_number"],
                    "investor_address": main_investor["address_line1"],
<<<<<<< HEAD
                    "investor_phone": main_investor["phone_number"],
                    "investor_email": main_investor["email"],
=======
                    "investor_phone": main_investor["phone_number"] or "(XXX) XXX-XXXX",
                    "investor_email": main_investor["email"] or "xxxxxx@xmail.com",
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
                })

        # ========================================
        # TESTIGOS
        # ========================================
        if "witnesses" in data and data["witnesses"]:
            witness = data["witnesses"][0]
            person = witness.get("person", {})
            document = witness.get("person_document", {})
            address = witness.get("address", {})

<<<<<<< HEAD
=======
            # Mascara por defecto para email y teléfono
            email = person.get("email", "") or "xxxxxx@xmail.com"
            phone = person.get("phone_number", "") or "(XXX) XXX-XXXX"

>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
            flattened.update({
                "witness_name": f"{person.get('first_name', '')} {person.get('last_name', '')}".strip(),
                "witness_full_name": f"{person.get('first_name', '')} {person.get('middle_name', '') or ''} {person.get('last_name', '')}".strip(),
                "witness_first_name": person.get("first_name", ""),
                "witness_last_name": person.get("last_name", ""),
                "witness_document_number": document.get("document_number", ""),
                "witness_address": address.get("address_line1", ""),
<<<<<<< HEAD
=======
                "witness_phone": phone,
                "witness_email": email,
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
            })

            flattened["witnesses"] = data["witnesses"]
            flattened["witnesses_count"] = len(data["witnesses"])

        # ========================================
        # NOTARIOS
        # ========================================
<<<<<<< HEAD
        if "notaries" in data and data["notaries"]:
            notary = data["notaries"][0]
            person = notary.get("person", {})
            notary_doc = notary.get("notary_document", {})
            address = notary.get("address", {})
=======
        # Manejar estructura antigua (notaries) y nueva (notary)
        notary_data = None
        if "notaries" in data and data["notaries"]:
            notary_data = data["notaries"][0]
            person = notary_data.get("person", {})
            notary_doc = notary_data.get("notary_document", {})
            address = notary_data.get("address", {})

            # Mascara por defecto para email y teléfono
            email = person.get("email", "") or "xxxxxx@xmail.com"
            phone = person.get("phone_number", "") or "(XXX) XXX-XXXX"
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f

            flattened.update({
                "notary_name": f"{person.get('first_name', '')} {person.get('last_name', '')}".strip(),
                "notary_full_name": f"{person.get('first_name', '')} {person.get('middle_name', '') or ''} {person.get('last_name', '')}".strip(),
                "notary_first_name": person.get("first_name", ""),
                "notary_last_name": person.get("last_name", ""),
                "notary_license_number": notary_doc.get("notary_number", ""),
                "notary_document_number": notary_doc.get("document_number", ""),
                "notary_address": address.get("address_line1", ""),
<<<<<<< HEAD
            })

            flattened["notaries"] = data["notaries"]
=======
                "notary_phone": phone,
                "notary_email": email,
            })

            flattened["notaries"] = data["notaries"]
        
        # Manejar estructura nueva (notary)
        elif "notary" in data and data["notary"]:
            notary_data = data["notary"][0]
            person = notary_data.get("person", {})
            documents = person.get("p_documents", [])
            addresses = person.get("p_addresses", [])
            additional_data = person.get("p_additional_data", {})
            
            # Obtener primer documento y dirección
            notary_doc = documents[0] if documents else {}
            address = addresses[0] if addresses else {}
            
            # Mascara por defecto para email y teléfono
            email = additional_data.get("professional_email", "") or "xxxxxx@xmail.com"
            phone = additional_data.get("professional_phone", "") or "(XXX) XXX-XXXX"

            flattened.update({
                "notary_name": f"{person.get('p_first_name', '')} {person.get('p_last_name', '')}".strip(),
                "notary_full_name": f"{person.get('p_first_name', '')} {person.get('p_middle_name', '') or ''} {person.get('p_last_name', '')}".strip(),
                "notary_first_name": person.get("p_first_name", ""),
                "notary_last_name": person.get("p_last_name", ""),
                "notary_license_number": additional_data.get("license_number", ""),
                "notary_document_number": notary_doc.get("document_number", ""),
                "notary_address": address.get("address_line1", ""),
                "notary_phone": phone,
                "notary_email": email,
            })

            flattened["notaries"] = data["notary"]
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f

        # ========================================
        # REFERENTES
        # ========================================
<<<<<<< HEAD
        if "referrers" in data and data["referrers"]:
            referrer = data["referrers"][0]
            person = referrer.get("person", {})
            document = referrer.get("person_document", {})
=======
        if "referents" in data and data["referents"]:
            referent = data["referents"][0]
            person = referent.get("person", {})
            document = referent.get("person_document", {})
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f

            flattened.update({
                "referrer_name": f"{person.get('first_name', '')} {person.get('last_name', '')}".strip(),
                "referrer_document_number": document.get("document_number", ""),
            })

<<<<<<< HEAD
            flattened["referrers"] = data["referrers"]
=======
            flattened["referents"] = data["referents"]
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f

        # ========================================
        # FECHAS Y METADATOS
        # ========================================
<<<<<<< HEAD
=======
        
        # Importar funciones de formateo de fechas
        from app.utils.date_formatter import formatear_fecha_legal, formatear_fecha_simple, parse_fecha_string
        
        # Procesar fechas del contrato si están disponibles
        contract_date_str = data.get("contract_date")
        contract_end_date_str = data.get("contract_end_date")
        
        if contract_date_str:
            contract_date_obj = parse_fecha_string(contract_date_str)
            
            # loan_start_date = contract_date (sin modificar)
            loan_start_date_text = formatear_fecha_legal(contract_date_obj)
            loan_start_date_simple = formatear_fecha_simple(contract_date_obj)
            
            # first_payment_date = contract_date + 1 mes
            from datetime import timedelta
            from dateutil.relativedelta import relativedelta
            
            first_payment_date_obj = contract_date_obj + relativedelta(months=1)
            first_payment_date_text = formatear_fecha_legal(first_payment_date_obj)
            first_payment_date_simple = formatear_fecha_simple(first_payment_date_obj)
        else:
            loan_start_date_text = "FECHA A DETERMINAR"
            loan_start_date_simple = "FECHA A DETERMINAR"
            first_payment_date_text = "FECHA A DETERMINAR"
            first_payment_date_simple = "FECHA A DETERMINAR"
        
        if contract_end_date_str:
            contract_end_date_obj = parse_fecha_string(contract_end_date_str)
            last_payment_date_text = formatear_fecha_legal(contract_end_date_obj)
            last_payment_date_simple = formatear_fecha_simple(contract_end_date_obj)
        else:
            last_payment_date_text = "FECHA A DETERMINAR"
            last_payment_date_simple = "FECHA A DETERMINAR"
        
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
        flattened.update({
            "current_date": datetime.now().strftime("%d de %B de %Y"),
            "current_year": datetime.now().year,
            "current_month": datetime.now().strftime("%B"),
            "current_day": datetime.now().day,
<<<<<<< HEAD
=======
            "loan_start_date_text": loan_start_date_text,
            "loan_start_date_simple": loan_start_date_simple,
            "first_payment_date_text": first_payment_date_text,
            "first_payment_date_simple": first_payment_date_simple,
            "last_payment_date_text": last_payment_date_text,
            "last_payment_date_simple": last_payment_date_simple,
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
        })

        # ========================================
        # DATOS DIRECTOS (para compatibilidad)
        # ========================================
        for key, value in data.items():
            if not isinstance(value, (dict, list)) and key not in flattened:
                flattened[key] = value

        return flattened


    def _select_template(self, data: Dict[str, Any]) -> Path:
        """Seleccionar plantilla apropiada"""
        # Determinar tipo de contrato
        if "loan" in data or data.get("contract_type") == "mortgage":
            template_name = "mortgage_template.docx"
        else:
            template_name = data.get("template_name", "default_template.docx")

        template_path = self.template_dir / template_name

        # Si no existe la plantilla específica, usar la primera disponible
        if not template_path.exists():
            available_templates = list(self.template_dir.glob("*.docx"))
            if not available_templates:
                raise HTTPException(404, "No se encontraron plantillas disponibles")
            template_path = available_templates[0]

        return template_path

<<<<<<< HEAD
    async def generate_contract(self, data: Dict[str, Any], connection=None) -> Dict[str, Any]:
=======
    async def generate_contract(self, data: Dict[str, Any], connection: Any = None) -> Dict[str, Any]:
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
        """Generar contrato completo"""

        # Ya no es necesario generar contract_id manualmente, el número de contrato viene de la base de datos
        # Elimina cualquier uso de _generate_contract_id y contract_type para nombres de carpeta o archivo
        contract_number = data.get("contract_number")
        if not contract_number:
            raise HTTPException(400, "El número de contrato es requerido para generar el contrato.")

        contract_id = f"contract_{contract_number}"
        contract_folder = self._get_contract_folder(contract_id)

        try:
            # Seleccionar plantilla
            template_path = self._select_template(data)

            # Procesar datos básicos
            processed_data = self._flatten_data(data)

            # Procesar párrafos de la base de datos si hay conexión
            if connection:
                try:
                    from .paragraphs import get_all_paragraphs_for_contract, get_paragraph_from_db, process_paragraph

                    # Si existe paragraph_request, usarlo para obtener los párrafos específicos
                    if "paragraph_request" in data:
                        paragraphs_result = {}
<<<<<<< HEAD
                        for req in data["paragraph_request"]:
                            person_role = req.get("person_role")
                            contract_type_db = req.get("contract_type")
                            section = req.get("section")
                            contract_services = req.get("contract_services", contract_type_db)
                            template = await get_paragraph_from_db(
                                connection,
                                person_role=person_role,
                                contract_type=contract_type_db,
                                section=section,
                                contract_services=contract_services
                            )
                            if template:
                                processed = process_paragraph(template, processed_data)
                                key = f"{person_role}_{contract_type_db}_{section}"
                                paragraphs_result[key] = processed
                        processed_data["paragraphs_result"] = paragraphs_result
                    else:
                        # Lógica anterior: inferir automáticamente
                        person_role = data.get("person_role")
                        if not person_role:
                            if "clients" in data and data["clients"]:
                                person_role = "cliente"
                            elif "investors" in data and data["investors"]:
                                person_role = "inversionista"
                            else:
                                person_role = "cliente"
                        contract_type_db = data.get("contract_type_db") or data.get("contract_type_person") or "juridica"
                        contract_services = data.get("contract_services") or contract_type_db or "mortgage"
                        db_paragraphs = await get_all_paragraphs_for_contract(
                            connection,
                            person_role,
                            contract_type_db,
                            contract_services,
                            processed_data
                        )
                        processed_data.update(db_paragraphs)
                        print(f"✅ Párrafos DB procesados para person_role={person_role}, contract_type={contract_type_db}, contract_services={contract_services}")
                        for key, value in db_paragraphs.items():
                            preview = value[:100] + "..." if len(value) > 100 else value
                            print(f"   📝 {key}: {preview}")

                except Exception as e:
                    print(f"⚠️ Error procesando párrafos de DB: {e}")
                    # Continuar sin párrafos de DB

            # Si se generaron párrafos específicos, insertarlos en el contexto para el Word
            if "paragraphs_result" in processed_data:
                # Mapeo automático para los más comunes
                for key, value in processed_data["paragraphs_result"].items():
                    if "client" in key and "identification" in key:
                        processed_data["client_paragraph"] = value
                    if "investor" in key and "identification" in key:
                        processed_data["investor_paragraph"] = value

=======
                        paragraph_errors = []

                        for req in data["paragraph_request"]:
                            try:
                                person_role = req.get("person_role")
                                contract_type_db = req.get("contract_type")
                                section = req.get("section")
                                contract_services = req.get("contract_services", contract_type_db)

                                template = await get_paragraph_from_db(
                                    connection,
                                    person_role=person_role,
                                    contract_type=contract_type_db,
                                    section=section,
                                    contract_services=contract_services
                                )

                                if template:
                                    processed = process_paragraph(template, processed_data)
                                    key = f"{person_role}_{contract_type_db}_{section}"
                                    paragraphs_result[key] = processed
                                else:
                                    # Si no se encuentra el párrafo, usar uno por defecto
                                    default_template = f"Párrafo por defecto para {person_role} - {section}"
                                    key = f"{person_role}_{contract_type_db}_{section}"
                                    paragraphs_result[key] = default_template
                                    paragraph_errors.append({
                                        "type": "missing_paragraph",
                                        "person_role": person_role,
                                        "contract_type": contract_type_db,
                                        "section": section,
                                        "message": f"No se encontró párrafo para {person_role} - {section}"
                                    })

                            except Exception as paragraph_error:
                                paragraph_errors.append({
                                    "type": "paragraph_error",
                                    "person_role": req.get("person_role"),
                                    "contract_type": req.get("contract_type"),
                                    "section": req.get("section"),
                                    "error": str(paragraph_error)
                                })
                                # Continuar con el siguiente párrafo
                                continue

                        processed_data["paragraphs_result"] = paragraphs_result
                        if paragraph_errors:
                            processed_data["paragraph_errors"] = paragraph_errors

                    else:
                        # Lógica anterior: inferir automáticamente
                        person_role = data.get("person_role")
                        if not person_role:
                            if "clients" in data and data["clients"]:
                                person_role = "client"
                            elif "investors" in data and data["investors"]:
                                person_role = "investor"
                            else:
                                person_role = "client"
                        contract_type_db = data.get("contract_type_db") or data.get("contract_type_person") or "juridica"
                        contract_services = data.get("contract_services") or data.get("contract_type", "mortgage")
                        
                        # Normalizar valores para asegurar compatibilidad con la base de datos
                        if person_role in ["cliente", "client"]:
                            person_role = "client"
                        elif person_role in ["inversionista", "investor"]:
                            person_role = "investor"
                        
                        if contract_type_db in ["juridica", "fisica_soltera", "fisica_casada"]:
                            contract_type_db = contract_type_db
                        else:
                            contract_type_db = "juridica"  # valor por defecto

                        print(f"🔍 Parámetros para párrafos: person_role={person_role}, contract_type_db={contract_type_db}, contract_services={contract_services}")

                        try:
                            # Obtener párrafos para cliente
                            client_paragraphs = await get_all_paragraphs_for_contract(
                                connection,
                                "client",
                                contract_type_db,
                                contract_services,
                                processed_data
                            )
                            
                            # Obtener párrafos para inversionista
                            investor_paragraphs = await get_all_paragraphs_for_contract(
                                connection,
                                "investor",
                                contract_type_db,
                                contract_services,
                                processed_data
                            )
                            
                            # Combinar párrafos
                            all_paragraphs = {**client_paragraphs, **investor_paragraphs}
                            processed_data.update(all_paragraphs)
                            
                            print(f"✅ Párrafos DB procesados para contract_type={contract_type_db}, contract_services={contract_services}")
                            print(f"   📝 Párrafos de cliente: {len(client_paragraphs)}")
                            print(f"   📝 Párrafos de inversionista: {len(investor_paragraphs)}")
                            for key, value in all_paragraphs.items():
                                preview = value[:100] + "..." if len(value) > 100 else value
                                print(f"   📝 {key}: {preview}")
                        except Exception as e:
                            print(f"⚠️ Error procesando párrafos automáticos: {e}")
                            # Continuar sin párrafos automáticos

                except Exception as e:
                    print(f"⚠️ Error general procesando párrafos de DB: {e}")
                    # Continuar sin párrafos de DB



            # Si se generaron párrafos específicos, insertarlos en el contexto para el Word
            # SOLO si no existen párrafos de la base de datos
            if "paragraphs_result" in processed_data:
                # Mapeo automático para los más comunes
                for key, value in processed_data["paragraphs_result"].items():
                    if "client" in key and "identification" in key and "client_paragraph" not in processed_data:
                        processed_data["client_paragraph"] = value
                        print(f"📝 Usando párrafo específico para cliente: {value[:50]}...")
                    if "investor" in key and "identification" in key and "investor_paragraph" not in processed_data:
                        processed_data["investor_paragraph"] = value
                        print(f"📝 Usando párrafo específico para inversionista: {value[:50]}...")

            # Mostrar qué párrafos se van a usar en el documento
            print("📋 Párrafos finales para el documento:")
            for key in ['client_paragraph', 'investor_paragraph', 'witness_paragraph', 'notary_paragraph']:
                if key in processed_data:
                    preview = processed_data[key][:100] + "..." if len(processed_data[key]) > 100 else processed_data[key]
                    print(f"   {key}: {preview}")
                else:
                    print(f"   {key}: NO ENCONTRADO")

            # Mostrar todas las variables que se van a pasar al template
            print("🔍 Variables que se pasan al template:")
            template_vars = ['client_paragraph', 'investor_paragraph', 'client_full_name', 'investor_full_name', 
                           'loan_amount', 'interest_rate', 'monthly_payment', 'final_payment']
            for var in template_vars:
                if var in processed_data:
                    value = processed_data[var]
                    if isinstance(value, str) and len(value) > 50:
                        preview = value[:50] + "..."
                    else:
                        preview = str(value)
                    print(f"   {var}: {preview}")
                else:
                    print(f"   {var}: NO ENCONTRADO")

>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
            # Generar documento
            doc = DocxTemplate(template_path)
            doc.render(processed_data)

            # Definir archivo de salida
            output_filename = f"{contract_id}.docx"
            output_path = contract_folder / output_filename
            doc.save(output_path)

            # Guardar metadatos
            self._save_metadata(contract_folder, contract_id, processed_data)

            # Respuesta base
            response = {
                "success": True,
                "message": "Contrato generado exitosamente",
                "contract_id": contract_id,
                "filename": output_filename,
                "path": str(output_path),
                "folder_path": str(contract_folder),
                "template_used": template_path.name,
                "processed_data": processed_data
            }

            # Si usa Google Drive, subir también allí
<<<<<<< HEAD
            if self.use_google_drive:
                try:
                    drive_result = await self.gdrive_service.upload_contract(
                        contract_id, output_path, processed_data
                    )
                    response.update(drive_result)
                except Exception as e:
                    # No fallar si Google Drive falla, solo advertir
                    response["drive_warning"] = f"Error subiendo a Google Drive: {str(e)}"

=======
            # print("🔄 use_google_drive:", self.use_google_drive)
            # print("📦 gdrive_service inicializado:", hasattr(self, 'gdrive_service'))



            if self.use_google_drive:
                try:
                    drive_result = self.gdrive_service.upload_contract(
                        contract_id, output_path, processed_data
                    )
                    response.update(drive_result)
                    # Enviar email a los destinatarios si hay enlace de Drive
                    if drive_result.get("drive_link"):
                        print(f"🔔 Enviando email a los destinatarios: {settings.CONTRACT_EMAIL_RECIPIENTS}")

                        # Obtener nombre del cliente para el email
                        client_name = "Cliente"
                        if "clients" in processed_data and processed_data["clients"]:
                            main_client = processed_data["clients"][0]
                            client_name = f"{main_client.get('first_name', '')} {main_client.get('last_name', '')}".strip()
                        elif "client_name" in processed_data:
                            client_name = processed_data["client_name"]

                        subject = f"📄 Su contrato está disponible - {contract_id}"

                        # Usar template HTML para el email
                        html_body = load_email_template(client_name, drive_result['drive_link'])

                        # Enviar a todos los destinatarios de forma asíncrona
                        email_tasks = []
                        for email in settings.CONTRACT_EMAIL_RECIPIENTS:
                            task = asyncio.create_task(
                                asyncio.to_thread(
                                    send_email,
                                    email,
                                    subject,
                                    text="Su contrato ha sido generado exitosamente y está disponible para revisión.",
                                    html_body=html_body,
                                    category="Contract Notification"
                                )
                            )
                            email_tasks.append(task)

                        # Esperar a que todos los emails se envíen
                        await asyncio.gather(*email_tasks, return_exceptions=True)
                        print(f"🔔 Email enviado a los destinatarios: {settings.CONTRACT_EMAIL_RECIPIENTS}")
                except Exception as e:
                    # No fallar si Google Drive falla, solo advertir
                    print(f"Error subiendo a Google Drive: {str(e)}")
                    response["drive_warning"] = f"Error subiendo a Google Drive: {str(e)}"

>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
            return response

        except Exception as e:
            # Limpiar en caso de error
            if contract_folder.exists():
                shutil.rmtree(contract_folder)
            raise HTTPException(400, f"Error generando contrato: {str(e)}")

    async def update_contract(self, contract_id: str, updates: Dict[str, Any], connection=None) -> Dict[str, Any]:
        """Modificar contrato existente"""
        contract_folder = self.contracts_dir / contract_id

        if not contract_folder.exists():
            raise HTTPException(404, "Contrato no encontrado")

        # Cargar metadatos existentes
        metadata_file = contract_folder / "metadata.json"
        if not metadata_file.exists():
            raise HTTPException(404, "Metadatos del contrato no encontrados")

        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # Combinar datos existentes con actualizaciones
        original_data = metadata["original_data"]
        updated_data = {**original_data, **updates}

        # Regenerar contrato
        template_path = self._select_template(updated_data)
        processed_data = self._flatten_data(updated_data)

        # Procesar párrafos de la base de datos si hay conexión
        if connection:
            try:
                from .paragraphs import get_all_paragraphs_for_contract

                person_role = updated_data.get("person_role")
                if not person_role:
                    if "clients" in updated_data and updated_data["clients"]:
                        person_role = "cliente"
                    elif "investors" in updated_data and updated_data["investors"]:
                        person_role = "inversionista"
                    else:
                        person_role = "cliente"
                contract_type_db = updated_data.get("contract_type_db") or updated_data.get("contract_type_person") or "juridica"
                contract_services = updated_data.get("contract_services") or updated_data.get("contract_type", "mortgage")

                db_paragraphs = await get_all_paragraphs_for_contract(
                    connection,
                    person_role,
                    contract_type_db,
                    contract_services,
                    processed_data
                )

                processed_data.update(db_paragraphs)
<<<<<<< HEAD
                print(f"✅ Párrafos DB actualizados para person_role={person_role}, contract_type={contract_type_db}, contract_services={contract_services}")
                for key, value in db_paragraphs.items():
                    preview = value[:100] + "..." if len(value) > 100 else value
                    print(f"   📝 {key}: {preview}")
=======
                # print(f"✅ Párrafos DB actualizados para person_role={person_role}, contract_type={contract_type_db}, contract_services={contract_services}")
                for key, value in db_paragraphs.items():
                    preview = value[:100] + "..." if len(value) > 100 else value
                    # print(f"   📝 {key}: {preview}")
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f

            except Exception as e:
                print(f"⚠️ Error procesando párrafos en update: {e}")

        doc = DocxTemplate(template_path)
        doc.render(processed_data)

        output_filename = f"{contract_id}.docx"
        output_path = contract_folder / output_filename
        doc.save(output_path)

        # Actualizar metadatos
        new_version = metadata["version"] + 1
        self._save_metadata(contract_folder, contract_id, processed_data, new_version)

        return {
            "success": True,
            "message": "Contrato actualizado exitosamente",
            "contract_id": contract_id,
            "version": new_version,
            "updated_fields": list(updates.keys())
        }

    async def upload_attachment(self, contract_id: str, file: UploadFile) -> Dict[str, Any]:
        """Subir archivo adjunto al contrato"""
        contract_folder = self.contracts_dir / contract_id

        if not contract_folder.exists():
            raise HTTPException(404, "Contrato no encontrado")

        # Validar archivo
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(400, f"Tipo de archivo no permitido: {file_extension}")

        # Verificar tamaño
        content = await file.read()
        if len(content) > self.MAX_FILE_SIZE:
            raise HTTPException(400, "Archivo demasiado grande (máximo 10MB)")

        # Guardar archivo
        attachments_folder = contract_folder / "attachments"
        file_path = attachments_folder / file.filename

        with open(file_path, 'wb') as f:
            f.write(content)

        return {
            "success": True,
            "message": "Archivo subido exitosamente",
            "filename": file.filename,
            "size": len(content),
            "path": str(file_path)
        }

    def list_contracts(self) -> Dict[str, Any]:
        """Listar todos los contratos"""
        contracts = []

        if not self.contracts_dir.exists():
            return {"contracts": [], "total": 0}

        for contract_folder in self.contracts_dir.iterdir():
            if contract_folder.is_dir():
                metadata_file = contract_folder / "metadata.json"
                contract_file = contract_folder / f"{contract_folder.name}.docx"

                if metadata_file.exists() and contract_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)

                    # Contar archivos adjuntos
                    attachments_folder = contract_folder / "attachments"
                    attachments_count = len(list(attachments_folder.glob("*"))) if attachments_folder.exists() else 0

                    contracts.append({
                        "contract_id": contract_folder.name,
                        "created_at": metadata.get("created_at"),
                        "modified_at": metadata.get("modified_at"),
                        "version": metadata.get("version", 1),
                        "size": contract_file.stat().st_size,
                        "attachments_count": attachments_count,
                        "storage_type": metadata.get("storage_type", "local")
                    })

        # Ordenar por fecha de creación
        contracts.sort(key=lambda x: x["created_at"], reverse=True)

        return {
            "contracts": contracts,
            "total": len(contracts)
        }
