from typing import Dict, Any, List
from app.contracts.utils.data_formatters import format_full_name


class ParticipantDataProcessor:
    """Procesador de datos de participantes del contrato"""
    
    def process_clients(self, clients_data: List[Dict]) -> Dict[str, Any]:
        """Procesar datos de clientes"""
        if not clients_data:
            return {}
        
        clients_list = []
        for idx, client in enumerate(clients_data):
            person = client.get("person", {})
            documents = person.get("p_documents", [])
            addresses = person.get("p_addresses", [])
            additional_data = person.get("p_additional_data", {})

            # Extraer email y teléfono de additional_data - NO asignar valores por defecto
            email = additional_data.get("email", "") or ""
            phone = additional_data.get("phone_number", "") or ""

            # Obtener el primer documento y dirección
            document = documents[0] if documents else {}
            address = addresses[0] if addresses else {}

            client_flat = {
                "first_name": person.get("p_first_name", ""),
                "last_name": person.get("p_last_name", ""),
                "middle_name": person.get("p_middle_name", ""),
                "full_name": format_full_name(
                    person.get("p_first_name", ""),
                    person.get("p_middle_name", ""),
                    person.get("p_last_name", "")
                ),
                "date_of_birth": person.get("p_date_of_birth", ""),
                "gender": person.get("p_gender", ""),
                "nationality": person.get("p_nationality_country", ""),
                "marital_status": person.get("p_marital_status", ""),
                "phone_number": phone,
                "email": email,
                "document_type": document.get("document_type", ""),
                "document_number": document.get("document_number", ""),
                "issuing_country": document.get("issuing_country_id", ""),
                "document_issue_date": document.get("document_issue_date", ""),
                "document_expiry_date": document.get("document_expiry_date", ""),
                "address_line1": address.get("address_line1", ""),
                "address_line2": address.get("address_line2", ""),
                "city": address.get("city_id", ""),
                "postal_code": address.get("postal_code", ""),
                "address_type": address.get("address_type", ""),
                "is_principal": address.get("is_principal", False),
            }
            clients_list.append(client_flat)

        result = {
            "clients": clients_list,
            "clients_count": len(clients_list)
        }

        # Cliente principal (primero) - Mantener compatibilidad
        if clients_list:
            main_client = clients_list[0]
            result.update({
                "client_name": f"{main_client['first_name']} {main_client['last_name']}",
                "client_full_name": main_client["full_name"],
                "client_first_name": main_client["first_name"],
                "client_last_name": main_client["last_name"],
                "client_middle_name": main_client["middle_name"],
                "client_date_of_birth": main_client["date_of_birth"],
                "client_gender": main_client["gender"],
                "client_nationality": main_client["nationality"],
                "client_marital_status": main_client["marital_status"],
                "client_phone": main_client["phone_number"] or "",
                "client_email": main_client["email"] or "",
                "client_document_type": main_client["document_type"],
                "client_document_number": main_client["document_number"],
                "client_issuing_country": main_client["issuing_country"],
                "client_address": main_client["address_line1"],
                "client_address2": main_client["address_line2"].upper() if main_client["address_line2"] else "",
                "client_city": main_client["city"],
                "client_postal_code": main_client["postal_code"],
            })

        # Generar variables múltiples para clientes (client1, client2, etc.)
        for idx, client in enumerate(clients_list, 1):
            client_num = idx
            result.update({
                f"client{client_num}_full_name": client["full_name"],
                f"client{client_num}_first_name": client["first_name"],
                f"client{client_num}_last_name": client["last_name"],
                f"client{client_num}_middle_name": client["middle_name"],
                f"client{client_num}_date_of_birth": client["date_of_birth"],
                f"client{client_num}_gender": client["gender"],
                f"client{client_num}_nationality": client["nationality"],
                f"client{client_num}_marital_status": client["marital_status"],
                f"client{client_num}_phone": client["phone_number"] or "",
                f"client{client_num}_email": client["email"] or "",
                f"client{client_num}_document_type": client["document_type"],
                f"client{client_num}_document_number": client["document_number"],
                f"client{client_num}_issuing_country": client["issuing_country"],
                f"client{client_num}_address": client["address_line1"],
                f"client{client_num}_address2": client["address_line2"].upper() if client["address_line2"] else "",
                f"client{client_num}_city": client["city"],
                f"client{client_num}_postal_code": client["postal_code"],
            })

        return result

    def process_investors(self, investors_data: List[Dict]) -> Dict[str, Any]:
        """Procesar datos de inversionistas"""
        if not investors_data:
            return {}
        
        investors_list = []
        for idx, investor in enumerate(investors_data):
            person = investor.get("person", {})
            documents = person.get("p_documents", [])
            addresses = person.get("p_addresses", [])
            additional_data = person.get("p_additional_data", {})

            # Extraer email y teléfono de additional_data - NO asignar valores por defecto
            email = additional_data.get("email", "") or ""
            phone = additional_data.get("phone_number", "") or ""

            # Obtener el primer documento y dirección
            document = documents[0] if documents else {}
            address = addresses[0] if addresses else {}

            investor_flat = {
                "first_name": person.get("p_first_name", ""),
                "last_name": person.get("p_last_name", ""),
                "middle_name": person.get("p_middle_name", ""),
                "full_name": format_full_name(
                    person.get("p_first_name", ""),
                    person.get("p_middle_name", ""),
                    person.get("p_last_name", "")
                ),
                "date_of_birth": person.get("p_date_of_birth", ""),
                "gender": person.get("p_gender", ""),
                "nationality": person.get("p_nationality_country", ""),
                "marital_status": person.get("p_marital_status", ""),
                "phone_number": phone,
                "email": email,
                "document_type": document.get("document_type", ""),
                "document_number": document.get("document_number", ""),
                "address_line1": address.get("address_line1", ""),
                "address_line2": address.get("address_line2", ""),
                "city": address.get("city_id", ""),
            }
            investors_list.append(investor_flat)

        result = {
            "investors": investors_list,
            "investors_count": len(investors_list)
        }

        # Inversionista principal - Mantener compatibilidad
        if investors_list:
            main_investor = investors_list[0]
            result.update({
                "investor_name": f"{main_investor['first_name']} {main_investor['last_name']}",
                "investor_full_name": main_investor["full_name"],
                "investor_first_name": main_investor["first_name"],
                "investor_last_name": main_investor["last_name"],
                "investor_middle_name": main_investor["middle_name"],
                "investor_document_number": main_investor["document_number"],
                "investor_address": main_investor["address_line1"],
                "investor_address2": main_investor["address_line2"].upper() if main_investor["address_line2"] else "",
                "investor_phone": main_investor["phone_number"] or "",
                "investor_email": main_investor["email"] or "",
            })

        # Generar variables múltiples para inversores (investor1, investor2, etc.)
        for idx, investor in enumerate(investors_list, 1):
            investor_num = idx
            result.update({
                f"investor{investor_num}_full_name": investor["full_name"],
                f"investor{investor_num}_first_name": investor["first_name"],
                f"investor{investor_num}_last_name": investor["last_name"],
                f"investor{investor_num}_middle_name": investor["middle_name"],
                f"investor{investor_num}_date_of_birth": investor["date_of_birth"],
                f"investor{investor_num}_gender": investor["gender"],
                f"investor{investor_num}_nationality": investor["nationality"],
                f"investor{investor_num}_marital_status": investor["marital_status"],
                f"investor{investor_num}_phone": investor["phone_number"] or "(XXX) XXX-XXXX",
                f"investor{investor_num}_email": investor["email"] or "xxxxxx@xmail.com",
                f"investor{investor_num}_document_type": investor["document_type"],
                f"investor{investor_num}_document_number": investor["document_number"],
                f"investor{investor_num}_address": investor["address_line1"],
                f"investor{investor_num}_address2": investor["address_line2"].upper() if investor["address_line2"] else "",
                f"investor{investor_num}_city": investor["city"],
            })

        return result

    def process_witnesses(self, witnesses_data: List[Dict]) -> Dict[str, Any]:
        """Procesar datos de testigos"""
        if not witnesses_data:
            return {}
        
        witness = witnesses_data[0]
        person = witness.get("person", {})
        documents = person.get("p_documents", [])
        addresses = person.get("p_addresses", [])
        additional_data = person.get("p_additional_data", {})

        # Extraer email y teléfono de additional_data - NO asignar valores por defecto
        email = additional_data.get("email", "") or ""
        phone = additional_data.get("phone_number", "") or ""

        # Obtener el primer documento y dirección
        document = documents[0] if documents else {}
        address = addresses[0] if addresses else {}

        result = {
            "witness_name": f"{person.get('p_first_name', '')} {person.get('p_last_name', '')}".strip(),
            "witness_full_name": format_full_name(
                person.get("p_first_name", ""),
                person.get("p_middle_name", ""),
                person.get("p_last_name", "")
            ),
            "witness_first_name": person.get("p_first_name", ""),
            "witness_last_name": person.get("p_last_name", ""),
            "witness_document_number": document.get("document_number", ""),
            "witness_address": address.get("address_line1", ""),
            "witness_address2": address.get("address_line2", "").upper() if address.get("address_line2") else "",
            "witness_phone": phone,
            "witness_email": email,
            "witnesses": witnesses_data,
            "witnesses_count": len(witnesses_data)
        }

        return result

    def process_notaries(self, notaries_data: List[Dict]) -> Dict[str, Any]:
        """Procesar datos de notarios"""
        if not notaries_data:
            return {}
        
        notary_data = notaries_data[0]
        person = notary_data.get("person", {})
        documents = person.get("p_documents", [])
        addresses = person.get("p_addresses", [])
        additional_data = person.get("p_additional_data", {})
        
        # Obtener primer documento y dirección
        notary_doc = documents[0] if documents else {}
        address = addresses[0] if addresses else {}
        
        # NO asignar valores por defecto para email y teléfono
        email = additional_data.get("professional_email", "") or ""
        phone = additional_data.get("professional_phone", "") or ""

        # Formatear nombres con función de limpieza de espacios dobles
        notary_name = f"{person.get('p_first_name', '')} {person.get('p_last_name', '')}".strip()
        notary_full_name = f"{person.get('p_first_name', '')} {person.get('p_middle_name', '') or ''} {person.get('p_last_name', '')}".strip()
        
        # Limpiar espacios dobles y convertir a mayúsculas para full_name
        notary_full_name = ' '.join(notary_full_name.split()).upper()

        result = {
            "notary_name": notary_name,
            "notary_full_name": notary_full_name,
            "notary_first_name": person.get("p_first_name", ""),
            "notary_last_name": person.get("p_last_name", ""),
            "notary_license_number": additional_data.get("license_number", ""),
            "notary_document_number": notary_doc.get("document_number", ""),
            "notary_address": address.get("address_line1", ""),
            "notary_phone": phone,
            "notary_email": email,
            "notaries": notaries_data
        }

        return result

    def process_referrers(self, referrers_data: List[Dict]) -> Dict[str, Any]:
        """Procesar datos de referentes"""
        if not referrers_data:
            return {}
        
        referent = referrers_data[0]
        person = referent.get("person", {})
        document = referent.get("person_document", {})

        result = {
            "referrer_name": f"{person.get('p_first_name', '')} {person.get('p_last_name', '')}".strip(),
            "referrer_document_number": document.get("document_number", ""),
            "referents": referrers_data
        }

        return result
