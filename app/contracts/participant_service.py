# participant_service.py
from typing import Dict, Any, List, Tuple, Optional
from fastapi import Request
from app.person.service import PersonService
from app.person.schemas import PersonCompleteCreate
from sqlalchemy import text
from datetime import datetime
import asyncio


class ParticipantService:
    """Servicio para manejar el procesamiento de participantes en contratos"""
    
    def __init__(self):
        self.participant_roles = [
            ("clients", "cliente", 1),
            ("investors", "inversionista", 2),
            ("witnesses", "testigo", 3),
            ("notaries", "notario", 7),
            ("notary", "notario", 7),
            ("referents", "referidor", 8)
        ]

    async def process_all_participants(
        self, 
        data: Dict[str, Any], 
        request: Request
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, int]]:
        """
        Procesar todas las personas del JSON de contrato
        
        Returns:
            Tuple[participants_for_contract, participant_errors, processed_persons_summary]
        """
        participant_ids = []
        participant_errors = []
        participants_for_contract = []
        processed_persons_summary = {
            "total": 0,
            "successful": 0,
            "errors": 0,
            "existing": 0,
            "reused": 0
        }

        # Procesar cada grupo de personas
        for group_name, role_name, default_role_id in self.participant_roles:
            group_data = data.get(group_name, [])

            for idx, participant in enumerate(group_data):
                processed_persons_summary["total"] += 1

                try:
                    # Procesar persona individual
                    result = await self._process_single_participant(
                        participant, group_name, role_name, default_role_id, idx, request
                    )
                    
                    # Manejar resultado
                    person_id, is_existing, is_reused = self._handle_participant_result(
                        result, role_name, default_role_id, idx, participant
                    )
                    
                    if person_id:
                        participant_ids.append(person_id)
                        participants_for_contract.append({
                            "person_id": person_id,
                            "role": role_name,
                            "is_primary": idx == 0,
                            "person_role_id": default_role_id,
                            "person_exists": is_existing,
                            "person_reused": is_reused
                        })
                        processed_persons_summary["successful"] += 1

                        if is_existing:
                            processed_persons_summary["existing"] += 1
                        if is_reused:
                            processed_persons_summary["reused"] += 1

                    else:
                        processed_persons_summary["errors"] += 1
                        error_msg = result.get("message", "Error creando persona")
                        participant_errors.append({
                            "role": role_name,
                            "index": idx,
                            "name": f"{participant['person']['p_first_name']} {participant['person']['p_last_name']}",
                            "error": error_msg,
                            "full_result": result
                        })

                except Exception as e:
                    processed_persons_summary["errors"] += 1
                    participant_errors.append({
                        "role": role_name,
                        "index": idx,
                        "name": f"{participant.get('person', {}).get('p_first_name', 'Unknown')}",
                        "error": f"Error en procesamiento: {str(e)}",
                        "exception": True
                    })

        # Procesar empresas (client_company e investor_company)
        companies_to_process = [
            ("client_company", 1),  # client_company -> rol 1
            ("investor_company", 2)  # investor_company -> rol 2
        ]
        
        for company_key, role_id in companies_to_process:
            company_data = data.get(company_key, {})
            if company_data and company_data.get("company_rnc"):  # Solo si hay datos de empresa
                try:
                    # Validar/insertar empresa y obtener company_id
                    company_id = await self._process_company(company_data, request)
                    
                    if company_id:
                        participants_for_contract.append({
                            "person_id": None,  # Empresa, no persona
                            "company_id": company_id,
                            "role": company_key,
                            "is_primary": True,
                            "person_role_id": role_id,
                            "person_exists": False,
                            "person_reused": False
                        })
                        processed_persons_summary["successful"] += 1
                    else:
                        processed_persons_summary["errors"] += 1
                        participant_errors.append({
                            "role": company_key,
                            "index": 0,
                            "name": company_data.get("company_name", "Unknown Company"),
                            "error": "Error procesando empresa",
                            "exception": True
                        })
                except Exception as e:
                    processed_persons_summary["errors"] += 1
                    participant_errors.append({
                        "role": company_key,
                        "index": 0,
                        "name": company_data.get("company_name", "Unknown Company"),
                        "error": f"Error en procesamiento: {str(e)}",
                        "exception": True
                    })

        return participants_for_contract, participant_errors, processed_persons_summary

    async def _process_single_participant(
        self, 
        participant: Dict[str, Any], 
        group_name: str, 
        role_name: str, 
        default_role_id: int, 
        idx: int, 
        request: Request
    ) -> Dict[str, Any]:
        """Procesar una persona individual"""
        
        # Preparar datos de persona según el tipo de grupo
        person_data = self._prepare_person_data(participant, group_name, role_name, default_role_id)
        
        # Crear schema
        person_schema = PersonCompleteCreate(**person_data)

        # Usar pool asyncpg
        async with request.app.state.db_pool.acquire() as asyncpg_connection:
            result = await PersonService.create_person_complete(
                person_schema,
                connection=asyncpg_connection,
                created_by=None,
                updated_by=None
            )
            
            # Debug para inversionistas
            if group_name == "investors":
                print(f"🔍 DEBUG INVESTOR {idx+1}: {participant['person']['p_first_name']} {participant['person']['p_last_name']}")
                print(f"   - Result: {result}")
                print(f"   - Success: {result.get('success') if result else 'None'}")
                print(f"   - Person ID: {result.get('person_id') if result else 'None'}")
                print(f"   - Message: {result.get('message') if result else 'None'}")

        return result

    def _prepare_person_data(
        self, 
        participant: Dict[str, Any], 
        group_name: str, 
        role_name: str, 
        default_role_id: int
    ) -> Dict[str, Any]:
        """Preparar datos de persona según el tipo de grupo"""
        
        if group_name == "notary" and "person" in participant:
            # Estructura para notarios: notary[0].person
            person_info = participant["person"]
            documents = person_info.get("p_documents", [])
            addresses = person_info.get("p_addresses", [])
            additional_data = person_info.get("p_additional_data", {})
            
            person_data = {
                "p_first_name": person_info.get("p_first_name", ""),
                "p_last_name": person_info.get("p_last_name", ""),
                "p_middle_name": person_info.get("p_middle_name", ""),
                "p_date_of_birth": person_info.get("p_date_of_birth"),
                "p_gender": person_info.get("p_gender", ""),
                "p_nationality_country": person_info.get("p_nationality_country", ""),
                "p_marital_status": person_info.get("p_marital_status", ""),
                "p_occupation": person_info.get("p_occupation", "Notario"),
                "p_person_role_id": person_info.get("p_person_role_id", default_role_id),
                "p_additional_data": additional_data
            }
            
            # Usar documentos y direcciones directamente
            if documents:
                person_data["p_documents"] = documents
            if addresses:
                person_data["p_addresses"] = addresses
        elif group_name == "referents":
            # Estructura para referentes: referents[0].person
            person_info = participant["person"]
            documents = person_info.get("documents", [])
            addresses = person_info.get("addresses", [])
            additional_data = person_info.get("additional_data", {})
            
            person_data = {
                    "p_first_name": person_info.get("first_name", ""),
                    "p_last_name": person_info.get("last_name", ""),
                    "p_middle_name": person_info.get("middle_name", ""),
                    "p_date_of_birth": person_info.get("date_of_birth"),
                    "p_gender": person_info.get("gender", ""),
                    "p_nationality_country": person_info.get("nationality_country", ""),
                    "p_marital_status": person_info.get("marital_status", ""),
                    "p_occupation": person_info.get("occupation", "Referente"),
                    "p_person_role_id": person_info.get("person_role_id", default_role_id),
                    "p_additional_data": additional_data
                }
            
            # Usar documentos y direcciones directamente
            if documents:
                person_data["p_documents"] = documents
            if addresses:
                person_data["p_addresses"] = addresses
        else:
            # Estructura estándar para otros participantes
            person_info = participant["person"]
            documents = person_info.get("p_documents", [])
            addresses = person_info.get("p_addresses", [])
            additional_data = person_info.get("p_additional_data", {})
            
            person_data = {
                "p_first_name": person_info.get("p_first_name", ""),
                "p_last_name": person_info.get("p_last_name", ""),
                "p_middle_name": person_info.get("p_middle_name", ""),
                "p_date_of_birth": person_info.get("p_date_of_birth"),
                "p_gender": person_info.get("p_gender", ""),
                "p_nationality_country": person_info.get("p_nationality_country", ""),
                "p_marital_status": person_info.get("p_marital_status", ""),
                "p_occupation": person_info.get("p_occupation", role_name.title()),
                "p_person_role_id": person_info.get("p_person_role_id", default_role_id),
                "p_additional_data": additional_data
            }
            
            # Usar documentos y direcciones directamente
            if documents:
                person_data["p_documents"] = documents
            if addresses:
                person_data["p_addresses"] = addresses

        # Preparar documentos si no están ya incluidos
        if "p_documents" not in person_data:
            documents = self._prepare_documents(participant, group_name)
            if documents:
                person_data["p_documents"] = documents

        # Preparar direcciones si no están ya incluidas
        if group_name not in ["notary", "referents"] or "p_addresses" not in person_data:
            addresses = self._prepare_addresses(participant)
            if addresses:
                person_data["p_addresses"] = addresses

        return person_data

    def _prepare_documents(self, participant: Dict[str, Any], group_name: str) -> List[Dict[str, Any]]:
        """Preparar documentos según la estructura del participante"""
        documents = []
        
        if "p_documents" in participant["person"]:
            # Usar documentos directamente del objeto person con formato p_
            documents = participant["person"]["p_documents"]
        elif "documents" in participant["person"]:
            # Usar documentos directamente del objeto person (formato antiguo)
            for doc_data in participant["person"]["documents"]:
                documents.append({
                    "is_primary": doc_data.get("is_primary", True),
                    "document_type": doc_data["document_type"],
                    "document_number": doc_data["document_number"],
                    "issuing_country_id": doc_data["issuing_country_id"],
                    "document_issue_date": doc_data.get("document_issue_date"),
                    "document_expiry_date": doc_data.get("document_expiry_date")
                })
        elif "person_document" in participant:
            doc_data = participant["person_document"]
            documents.append({
                "is_primary": True,
                "document_type": doc_data["document_type"],
                "document_number": doc_data["document_number"],
                "issuing_country_id": doc_data["issuing_country_id"],
                "document_issue_date": doc_data.get("document_issue_date"),
                "document_expiry_date": doc_data.get("document_expiry_date")
            })
        elif "notary_document" in participant:
            doc_data = participant["notary_document"]
            documents.append({
                "is_primary": True,
                "document_type": doc_data.get("document_type", "Cédula"),
                "document_number": doc_data["document_number"],
                "issuing_country_id": doc_data["issuing_country_id"],
                "document_issue_date": doc_data.get("document_issue_date"),
                "document_expiry_date": doc_data.get("document_expiry_date")
            })
        
        return documents

    def _prepare_addresses(self, participant: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Preparar direcciones según la estructura del participante"""
        addresses = []
        
        if "addresses" in participant["person"]:
            # Usar direcciones directamente del objeto person
            for address_data in participant["person"]["addresses"]:
                addresses.append({
                    "address_line1": address_data["address_line1"],
                    "address_line2": address_data.get("address_line2"),
                    "city_id": address_data["city_id"],
                    "postal_code": address_data.get("postal_code"),
                    "address_type": address_data.get("address_type", "Casa"),
                    "is_principal": address_data.get("is_principal", True)
                })
        elif "address" in participant:
            address_data = participant["address"]
            addresses.append({
                "address_line1": address_data["address_line1"],
                "address_line2": address_data.get("address_line2"),
                "city_id": address_data["city_id"],
                "postal_code": address_data.get("postal_code"),
                "address_type": address_data.get("address_type", "Casa"),
                "is_principal": address_data.get("is_principal", True)
            })
        
        return addresses

    def _handle_participant_result(
        self, 
        result: Dict[str, Any], 
        role_name: str, 
        default_role_id: int, 
        idx: int, 
        participant: Dict[str, Any]
    ) -> Tuple[Optional[str], bool, bool]:
        """Manejar el resultado del procesamiento de una persona"""
        
        # Verificación crítica: manejar None result
        if result is None:
            result = {
                "success": False,
                "message": "Error interno: servicio retornó None",
                "error": "NULL_RESULT"
            }

        person_id = None
        is_existing = False
        is_reused = False

        if result.get("success") and result.get("person_id"):
            # Caso exitoso normal
            person_id = result["person_id"]
            is_existing = result.get("person_exists", False)

        elif not result.get("success") and result.get("data", {}).get("person_id"):
            # Caso especial: Error pero con person_id (persona ya existe)
            person_id = result["data"]["person_id"]
            is_reused = True

            # Verificar si el mensaje indica que la persona ya existe
            error_message = result.get("message", "").lower()
            if any(keyword in error_message for keyword in [
                "ya está registrada", "already registered", "persona ya existe",
                "already exists", "duplicate", "duplicado"
            ]):
                # Tratamos esto como éxito
                result["success"] = True
                result["person_exists"] = True
                result["reused"] = True
            else:
                # Es un error real, no persona duplicada
                person_id = None

        if person_id:
            # Log detallado
            status = "Reutilizada" if is_reused else ("Existente" if is_existing else "Nueva")
            
            # Debug para inversionistas
            if "investors" in participant.get("person", {}).get("p_first_name", ""):
                print(f"   ✅ INVESTOR AGREGADO: {participant['person']['p_first_name']} - {status} (ID: {person_id})")

        return person_id, is_existing, is_reused

    async def _process_company(self, company_data: Dict[str, Any], request: Request) -> Optional[int]:
        """Procesar empresa: validar si existe o insertar nueva"""
        try:
            async with request.app.state.db_pool.acquire() as conn:
                # Verificar si empresa ya existe por RNC
                rnc = company_data.get("company_rnc")
                if not rnc:
                    return None
                
                # Buscar empresa existente
                query = "SELECT company_id FROM company WHERE company_rnc = $1 AND is_active = true"
                existing = await conn.fetchrow(query, rnc)
                
                if existing:
                    return existing["company_id"]
                
                # Insertar nueva empresa
                insert_query = """
                    INSERT INTO company (
                        company_name, company_rnc, mercantil_registry, nationality,
                        email, phone, website, company_type, company_description,
                        is_active, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    RETURNING company_id
                """
                
                result = await conn.fetchrow(insert_query,
                    company_data.get("company_name", ""),
                    rnc,
                    company_data.get("company_mercantil_number", ""),
                    company_data.get("nationality", "Dominicana"),
                    company_data.get("company_email", ""),
                    company_data.get("company_phone", ""),
                    company_data.get("website", ""),
                    company_data.get("company_type", ""),
                    company_data.get("company_description", ""),
                    True,
                    datetime.now(),
                    datetime.now()
                )
                
                return result["company_id"] if result else None
                
        except Exception as e:
            print(f"Error procesando empresa: {str(e)}")
            return None

