# contract_creation_service.py
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date
from sqlalchemy import text
from app.database import fetch_one, execute
from app.contracts.models import contract as contract_table, contract_participant as contract_participant_table


class ContractCreationService:
    """Servicio para manejar la creación de contratos en la base de datos"""

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
        db
    ) -> str:
        """Crear registro de contrato en la base de datos"""
        
        # Procesar fechas del contrato
        contract_start_date = self.parse_contract_date(data.get("contract_date"))
        contract_end_date = self.parse_contract_date(data.get("contract_end_date"))
        
        contract_type_name = data.get("contract_type", "mortgage")
        
        contract_insert = contract_table.insert().values(
            contract_number=contract_number,
            contract_type_id=data.get("contract_type_id", 1),
            contract_service_id=None,
            contract_status_id=1,  # Draft
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
            created_by=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ).returning(contract_table.c.contract_id)

        contract_row = await fetch_one(contract_insert, connection=db, commit_after=True)
        contract_id = contract_row["contract_id"]
        
        return contract_id

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
                # Usar URL de Google Drive para el archivo (drive_view_link)
                file_path = document_result.get("drive_view_link", file_path)
                # Usar URL de Google Drive para la carpeta (drive_link)
                folder_path = document_result.get("drive_link", folder_path)
                print(f"✅ URLs de Google Drive almacenadas en BD:")
                print(f"   - file_path: {file_path}")
                print(f"   - folder_path: {folder_path}")
            else:
                print(f"📁 Rutas locales almacenadas en BD:")
                print(f"   - file_path: {file_path}")
                print(f"   - folder_path: {folder_path}")
            
            # Generar nombre descriptivo como fallback
            contract_number = contract_id.replace("contract_", "")
            descriptive_filename = document_result.get("filename", f"{contract_number}.docx")
            
            update_query = contract_table.update().where(
                contract_table.c.contract_id == contract_id
            ).values(
                generated_filename=descriptive_filename,
                file_path=file_path,
                folder_path=folder_path,
                updated_at=datetime.now()
            )
            await execute(update_query, connection=db, commit_after=True)

