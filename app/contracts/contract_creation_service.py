# contract_creation_service.py
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date
from uuid import UUID
from sqlalchemy import text, delete, select
from app.database import fetch_one, execute
from app.contracts.models import (
    contract as contract_table,
    contract_participant as contract_participant_table,
    contract_loan as contract_loan_table,
    contract_bank_account as contract_bank_account_table,
)
from app.contracts.participant_service import ParticipantService
from fastapi import Request

# person_type_id: 1 = client, 2 = investor
_COMPANY_ROLES = [("client_company", 1), ("investor_company", 2)]


def _allowed_company_identifiers(data: Dict[str, Any], role_key: str) -> Tuple[List[str], List[str]]:
    """RNCs y company_ids que el payload indica para un rol (client_company / investor_company)."""
    rncs: List[str] = []
    ids: List[str] = []
    raw = data.get(role_key)
    if not raw:
        return rncs, ids
    items = [raw] if isinstance(raw, dict) else (raw if isinstance(raw, list) else [])
    for c in items:
        if not isinstance(c, dict):
            continue
        rnc = (c.get("company_rnc") or "").strip()
        if rnc:
            rncs.append(rnc)
        cid = c.get("company_id")
        if cid is not None and str(cid).strip() and str(cid) != "0":
            ids.append(str(cid).strip())
    return rncs, ids


class ContractCreationService:
    """Servicio para manejar la creación de contratos en la base de datos"""

    async def get_contract_type_id_by_name(self, type_name: str, db) -> Optional[int]:
        """Buscar contract_type_id en public.contract_type usando type_name"""
        try:
            query = text("""
                SELECT contract_type_id 
                FROM public.contract_type 
                WHERE type_name = :type_name
                LIMIT 1
            """)
            result = await db.execute(query, {"type_name": type_name})
            row = result.fetchone()
            if row:
                contract_type_id = row[0]
                print(f"✅ Encontrado contract_type_id: {contract_type_id} para type_name: '{type_name}'")
                return contract_type_id
            print(f"⚠️  No se encontró contract_type_id para type_name: '{type_name}'")
            return None
        except Exception as e:
            print(f"❌ Error buscando contract_type_id para type_name '{type_name}': {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    async def generate_contract_number(self, contract_type_name: str, db) -> str:
        """Generar número de contrato usando función SQL"""
        try:
            result = await db.execute(
                text("SELECT generate_contract_number(:contract_type)"),
                {"contract_type": contract_type_name}
            )
            contract_number = result.scalar()
            return contract_number
        except Exception as e:
            # Fallback si falla la función SQL
            contract_number = f"{contract_type_name.upper()}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            return contract_number

    def parse_contract_date(self, date_str: str) -> date:
        """Convertir fecha del formato DD/MM/YYYY a objeto date"""
        if not date_str:
            return datetime.now().date()
        try:
            day, month, year = date_str.split('/')
            return date(int(year), int(month), int(day))
        except (ValueError, AttributeError):
            return datetime.now().date()

    async def create_contract_record(
        self, 
        data: Dict[str, Any], 
        contract_number: str, 
        db,
        current_user: str = None
    ) -> str:
        """Crear registro de contrato en la base de datos"""
        
        # Procesar fechas del contrato
        contract_start_date = self.parse_contract_date(data.get("contract_date"))
        contract_end_date = self.parse_contract_date(data.get("contract_end_date"))
        
        contract_type_name = data.get("contract_type", "mortgage")
        
        # Procesar paragraph_request para obtener contract_type_id_client e contract_type_id_investor
        contract_type_id_client = None
        contract_type_id_investor = None
        
        paragraph_request = data.get("paragraph_request", [])
        print(f"📝 Procesando paragraph_request: {len(paragraph_request)} elementos")
        
        if isinstance(paragraph_request, list):
            # Buscar el primer elemento con person_role="client" y el primero con person_role="investor"
            client_found = False
            investor_found = False
            
            for req in paragraph_request:
                if not isinstance(req, dict):
                    continue
                    
                person_role = req.get("person_role", "").lower()
                contract_type_from_req = req.get("contract_type")
                
                print(f"   - Procesando: person_role={person_role}, contract_type={contract_type_from_req}")
                
                # Buscar contract_type_id en public.contract_type usando type_name
                if contract_type_from_req:
                    contract_type_id = await self.get_contract_type_id_by_name(contract_type_from_req, db)
                    
                    if contract_type_id:
                        if person_role == "client" and not client_found:
                            contract_type_id_client = contract_type_id
                            client_found = True
                            print(f"   ✅ Asignado contract_type_id_client = {contract_type_id}")
                        elif person_role == "investor" and not investor_found:
                            contract_type_id_investor = contract_type_id
                            investor_found = True
                            print(f"   ✅ Asignado contract_type_id_investor = {contract_type_id}")
                        
                        # Si ya encontramos ambos, podemos salir del loop
                        if client_found and investor_found:
                            break
        
        print(f"📊 Resultado final:")
        print(f"   - contract_type_id_client: {contract_type_id_client}")
        print(f"   - contract_type_id_investor: {contract_type_id_investor}")
        
        # Obtener contract_service_id del contract_type_id del JSON raíz
        contract_service_id = data.get("contract_type_id")
        
        print(f"📝 Valores para inserción:")
        print(f"   - contract_service_id: {contract_service_id}")
        print(f"   - contract_type_id_client: {contract_type_id_client}")
        print(f"   - contract_type_id_investor: {contract_type_id_investor}")
        
        try:
            contract_insert = contract_table.insert().values(
                contract_number=contract_number,
                contract_service_id=contract_service_id,
                contract_type_id_client=contract_type_id_client,
                contract_type_id_investor=contract_type_id_investor,
                contract_date=contract_start_date,
                start_date=contract_start_date,
                end_date=contract_end_date,
                title=data.get("description"),
                description=data.get("description"),
                template_name=f"{contract_type_name}_template.docx",
                generated_filename=None,
                file_path=None,
                folder_path=None,
                version=1,
                is_active=True,
                created_by=current_user,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ).returning(contract_table.c.contract_id)

            contract_row = await fetch_one(contract_insert, connection=db, commit_after=True)
            contract_id = contract_row["contract_id"]
            
            print(f"✅ Contrato creado exitosamente con ID: {contract_id}")
            return contract_id
        except Exception as e:
            print(f"❌ Error al crear contrato: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    async def register_contract_participants(
        self, 
        contract_id: str, 
        participants_for_contract: List[Dict[str, Any]], 
        db
    ) -> List[Dict[str, Any]]:
        """Registrar participantes en la tabla contract_participant"""
        
        participant_errors = []
        
        for p in participants_for_contract:
            try:
                # Para empresas: person_id = None, company_id = p["company_id"]
                # Para personas: person_id = p["person_id"], company_id = None
                participant_insert = contract_participant_table.insert().values(
                    contract_id=contract_id,
                    person_id=p.get("person_id"),  # None para empresas
                    company_id=p.get("company_id"),  # None para personas
                    person_type_id=p["person_role_id"],
                    is_primary=p["is_primary"],
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
                await execute(participant_insert, connection=db, commit_after=True)
                
            except Exception as e:
                error_msg = f"Error insertando {p['role']}: {str(e)}"
                participant_errors.append({
                    "role": p['role'],
                    "person_id": p.get("person_id"),
                    "company_id": p.get("company_id"),
                    "error": str(e)
                })

        return participant_errors

    async def create_client_referrer_relationships(
        self, 
        participants_for_contract: List[Dict[str, Any]], 
        db
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """Crear relaciones cliente-referidor"""
        
        client_referrer_errors = []
        client_referrer_created = 0
        
        # Obtener IDs de clientes y referidores del contrato
        client_ids = []
        referrer_ids = []
        
        for p in participants_for_contract:
            if p.get("person_role_id") == 1:  # Cliente
                client_ids.append(p["person_id"])
            elif p.get("person_role_id") == 8:  # Referidor
                referrer_ids.append(p["person_id"])
        
        if client_ids and referrer_ids:
            # Obtener client_id de la tabla client basado en person_id
            for client_person_id in client_ids:
                try:
                    # Buscar el client_id correspondiente al person_id
                    client_query = text("""
                        SELECT client_id FROM client 
                        WHERE person_id = :person_id AND is_active = true
                    """)
                    client_result = await db.execute(client_query, {"person_id": client_person_id})
                    client_row = client_result.fetchone()
                    
                    if client_row:
                        client_id = client_row["client_id"]
                        
                        for referrer_person_id in referrer_ids:
                            try:
                                # Verificar que el referidor existe en la tabla referrer
                                referrer_check_query = text("""
                                    SELECT referrer_id FROM referrer 
                                    WHERE person_id = :person_id AND is_active = true
                                """)
                                referrer_check_result = await db.execute(referrer_check_query, {"person_id": referrer_person_id})
                                referrer_check_row = referrer_check_result.fetchone()
                                
                                if referrer_check_row:
                                    # Crear relación usando client_id y person_id
                                    insert_query = text("""
                                        INSERT INTO client_referrer 
                                        (client_id, referrer_id, relation_date, is_active, created_at, updated_at)
                                        VALUES (:client_id, :referrer_id, :relation_date, :is_active, :created_at, :updated_at)
                                        ON CONFLICT (client_id, referrer_id, is_active) DO NOTHING
                                        RETURNING client_referrer_id
                                    """)
                                    
                                    result = await db.execute(insert_query, {
                                        "client_id": client_id,
                                        "referrer_id": referrer_person_id,
                                        "relation_date": datetime.now(),
                                        "is_active": True,
                                        "created_at": datetime.now(),
                                        "updated_at": datetime.now()
                                    })
                                    
                                    await db.commit()
                                    
                                    if result.rowcount > 0:
                                        client_referrer_created += 1
                                        
                            except Exception as e:
                                client_referrer_errors.append({
                                    "client_id": str(client_id),
                                    "referrer_id": str(referrer_person_id),
                                    "error": str(e)
                                })
                                
                except Exception as e:
                    # Error buscando client_id
                    pass

        return client_referrer_created, client_referrer_errors

    async def delete_contract_cascade(self, contract_id: str | UUID, db) -> None:
        """
        Elimina el contrato y, por CASCADE en BD, sus participantes, loan y propiedades.
        Usar para rollback cuando falla loan o properties después de crear el contrato.
        """
        uid = UUID(str(contract_id)) if isinstance(contract_id, str) else contract_id
        await execute(
            delete(contract_table).where(contract_table.c.contract_id == uid),
            connection=db,
            commit_after=True,
        )

    async def update_contract_with_document_info(
        self,
        contract_id: str,
        document_result: Dict[str, Any],
        db
    ) -> None:
        """Actualizar contrato con información del documento generado"""

        if document_result.get("success"):
            # Determinar qué URLs usar: Google Drive si está disponible, sino rutas locales
            file_path = document_result.get("path")  # Ruta local por defecto
            folder_path = document_result.get("folder_path")  # Ruta local por defecto

            # Si Google Drive está habilitado y se subió exitosamente, usar URLs de Drive
            if document_result.get("drive_success") and document_result.get("drive_link"):
                file_path = document_result.get("drive_view_link", file_path)
                folder_path = document_result.get("drive_link", folder_path)

            # Generar nombre descriptivo - Convertir UUID a string
            contract_id_str = str(contract_id)
            contract_number = contract_id_str.replace("contract_", "")
            descriptive_filename = document_result.get("filename", f"{contract_number}.docx")

            update_query = contract_table.update().where(
                contract_table.c.contract_id == contract_id
            ).values(
                generated_filename=descriptive_filename,
                file_path=file_path,
                folder_path=folder_path,
                updated_at=datetime.now()
            )

            await db.execute(update_query)
            await db.commit()

    async def update_contract_data_in_db(
        self,
        contract_id: str,
        updates: Dict[str, Any],
        db,
    ) -> None:
        """
        Persiste en la base de datos los datos actualizados del contrato y del préstamo.
        Actualiza contract (description, end_date, title) y contract_loan (montos, tasa, plazo, etc.).
        """
        uid = UUID(contract_id) if isinstance(contract_id, str) else contract_id

        # 1. Actualizar tabla contract (description, end_date, title)
        contract_values = {}
        if updates.get("description") is not None:
            contract_values["description"] = updates["description"]
        if updates.get("contract_end_date") is not None:
            contract_values["end_date"] = self.parse_contract_date(updates["contract_end_date"])
        if updates.get("title") is not None:
            contract_values["title"] = updates["title"]
        if contract_values:
            contract_values["updated_at"] = datetime.now()
            update_contract = contract_table.update().where(
                contract_table.c.contract_id == uid
            ).values(**contract_values)
            await db.execute(update_contract)
            await db.commit()

        # 2. Actualizar contract_loan si viene loan en updates
        loan_data = updates.get("loan")
        if not loan_data or not isinstance(loan_data, dict):
            return

        def _to_decimal(v) -> Optional[Decimal]:
            if v is None:
                return None
            if isinstance(v, (Decimal, int, float)):
                return Decimal(str(v))
            if isinstance(v, str) and v.strip():
                try:
                    return Decimal(v)
                except Exception:
                    return None
            return None

        def _to_int(v) -> Optional[int]:
            if v is None:
                return None
            if isinstance(v, int):
                return v
            if isinstance(v, (float, Decimal)):
                return int(v)
            if isinstance(v, str) and v.strip():
                try:
                    return int(float(v))
                except Exception:
                    return None
            return None

        loan_values = {}
        if "amount" in loan_data:
            loan_values["loan_amount"] = _to_decimal(loan_data["amount"])
        if "interest_rate" in loan_data:
            loan_values["interest_rate"] = _to_decimal(loan_data["interest_rate"])
        if "term_months" in loan_data:
            loan_values["term_months"] = _to_int(loan_data["term_months"])
        if "loan_type" in loan_data and loan_data["loan_type"]:
            loan_values["loan_type"] = loan_data["loan_type"]
        details = loan_data.get("loan_payments_details") or {}
        if "monthly_payment" in details:
            loan_values["monthly_payment"] = _to_decimal(details["monthly_payment"])
        if "final_payment" in details:
            loan_values["final_payment"] = _to_decimal(details["final_payment"])
        if "discount_rate" in details:
            loan_values["discount_rate"] = _to_decimal(details["discount_rate"])
        if "payment_qty_quotes" in details:
            loan_values["payment_qty_quotes"] = _to_int(details["payment_qty_quotes"])
        if "payment_type" in details and details["payment_type"]:
            loan_values["payment_type"] = details["payment_type"]
        if "currency" in loan_data and loan_data["currency"]:
            loan_values["currency"] = loan_data["currency"]

        if loan_values:
            loan_values["updated_at"] = datetime.now()
            update_loan = contract_loan_table.update().where(
                contract_loan_table.c.contract_id == uid
            ).values(**loan_values)
            await db.execute(update_loan)
            await db.commit()

        # 3. Actualizar/insertar contract_bank_account si viene bank_account en loan
        bank_data = loan_data.get("bank_account")
        if bank_data and isinstance(bank_data, dict):
            account_type_raw = (
                bank_data.get("bank_account_type")
                or bank_data.get("account_type")
                or "corriente"
            )
            account_type_mapping = {
                "ahorros": "ahorros",
                "corriente": "corriente",
                "inversion": "inversion",
                "other": "other",
                "savings": "ahorros",
                "checking": "corriente",
                "investment": "inversion",
            }
            account_type = account_type_mapping.get(
                str(account_type_raw).strip().lower(), "corriente"
            )
            account_number = (
                bank_data.get("bank_account_number")
                or bank_data.get("account_number")
                or ""
            )
            account_currency = (
                bank_data.get("bank_account_currency")
                or bank_data.get("currency")
                or "USD"
            )
            bank_name = bank_data.get("bank_name") or ""

            cursor = await db.execute(
                select(contract_bank_account_table.c.bank_account_id).where(
                    contract_bank_account_table.c.contract_id == uid
                )
            )
            existing_row = cursor.first()

            if existing_row is not None:
                await db.execute(
                    contract_bank_account_table.update().where(
                        contract_bank_account_table.c.contract_id == uid
                    ).values(
                        bank_name=bank_name,
                        account_number=account_number,
                        account_type=account_type,
                        currency=account_currency,
                        bank_code=bank_data.get("bank_code"),
                        swift_code=bank_data.get("swift_code"),
                        iban=bank_data.get("iban"),
                    )
                )
            else:
                await db.execute(
                    contract_bank_account_table.insert().values(
                        contract_id=uid,
                        client_person_id=None,
                        holder_name="",
                        bank_name=bank_name,
                        account_number=account_number,
                        account_type=account_type,
                        currency=account_currency,
                        bank_code=bank_data.get("bank_code"),
                        swift_code=bank_data.get("swift_code"),
                        iban=bank_data.get("iban"),
                    )
                )
            await db.commit()

    async def upsert_contract_participants_from_payload(
        self,
        contract_id: str,
        data: Dict[str, Any],
        db,
        request: Request,
        participant_service: ParticipantService | None = None,
    ) -> None:
        """
        En update, crea (si aplica) personas/empresas nuevas desde el payload y
        asegura que estén asociadas al contrato en `contract_participant`.

        - Reusa `ParticipantService.process_all_participants` (personas + empresas).
        - Evita duplicar filas en `contract_participant`.
        """
        uid = UUID(contract_id) if isinstance(contract_id, str) else contract_id
        ps = participant_service or ParticipantService()

        # Aceptar payload tipo detail: `participants` anidado
        participants = data.get("participants")
        if isinstance(participants, dict):
            for key, value in participants.items():
                if data.get(key) in (None, [], {}, ""):
                    data[key] = value

        # Eliminar del contrato las compañías que ya no vienen en el payload (por RNC o company_id)
        for role_key, person_type_id in _COMPANY_ROLES:
            rncs, ids = _allowed_company_identifiers(data, role_key)
            delete_sql = text("""
                DELETE FROM contract_participant cp
                USING company c
                WHERE cp.contract_id = :uid
                  AND cp.person_type_id = :person_type_id
                  AND cp.company_id IS NOT NULL
                  AND c.company_id = cp.company_id
                  AND NOT (c.company_rnc = ANY(:rncs) OR c.company_id::text = ANY(:ids))
            """)
            await db.execute(
                delete_sql,
                {
                    "uid": uid,
                    "person_type_id": person_type_id,
                    "rncs": rncs,
                    "ids": ids,
                },
            )

        participants_for_contract, participant_errors, _summary = await ps.process_all_participants(data, request)

        # Si hay errores, no abortar el update completo: solo no insertamos esos participantes.
        # (Los errores ya están capturados por ParticipantService.)
        for p in participants_for_contract:
            person_id = p.get("person_id")
            company_id = p.get("company_id")
            person_type_id = p.get("person_role_id")
            is_primary = bool(p.get("is_primary"))

            # Normalizar UUIDs
            person_uuid = None
            if person_id:
                person_uuid = UUID(str(person_id))
            company_uuid = None
            if company_id:
                company_uuid = UUID(str(company_id))

            # Construir condición de existencia
            where_clauses = [contract_participant_table.c.contract_id == uid]
            if person_uuid is not None:
                where_clauses.append(contract_participant_table.c.person_id == person_uuid)
            elif company_uuid is not None:
                where_clauses.append(contract_participant_table.c.company_id == company_uuid)
            else:
                continue
            if person_type_id is not None:
                where_clauses.append(contract_participant_table.c.person_type_id == person_type_id)

            exists_cursor = await db.execute(
                select(contract_participant_table.c.contract_participant_id).where(*where_clauses).limit(1)
            )
            exists_row = exists_cursor.first()
            if exists_row is not None:
                continue

            participant_insert = contract_participant_table.insert().values(
                contract_id=uid,
                person_id=person_uuid,
                company_id=company_uuid,
                person_type_id=person_type_id,
                is_primary=is_primary,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            await db.execute(participant_insert)

        await db.commit()
