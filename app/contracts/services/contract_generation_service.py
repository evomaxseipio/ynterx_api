from typing import Dict, Any, Optional
from pathlib import Path
from fastapi import HTTPException
import asyncio
import shutil

from app.contracts.processors.contract_data_processor import ContractDataProcessor
from app.contracts.services.contract_template_service import ContractTemplateService
from app.contracts.services.contract_file_service import ContractFileService
from app.contracts.services.contract_metadata_service import ContractMetadataService
from app.contracts.utils.google_drive_utils import GoogleDriveUtils
from app.contracts.utils.file_handlers import get_contract_folder
from app.config import settings
from app.utils.email_services import send_email, load_email_template


class ContractGenerationService:
    """Servicio principal para generación de contratos"""
    
    def __init__(self, template_dir: Path, contracts_dir: Path, use_google_drive: bool = True):
        self.template_dir = template_dir
        self.contracts_dir = contracts_dir
        self.use_google_drive = use_google_drive
        
        # Inicializar servicios
        self.data_processor = ContractDataProcessor()
        self.template_service = ContractTemplateService(template_dir)
        self.file_service = ContractFileService(contracts_dir)
        self.metadata_service = ContractMetadataService(contracts_dir)
        self.gdrive_utils = GoogleDriveUtils(use_google_drive)
    
    async def generate_contract(self, data: Dict[str, Any], connection: Any = None) -> Dict[str, Any]:
        """Generar contrato completo"""
        contract_number = data.get("contract_number")
        if not contract_number:
            raise HTTPException(400, "El número de contrato es requerido para generar el contrato.")

        contract_id = f"contract_{contract_number}"
        
        # Solo crear carpeta local si NO se usa Google Drive
        if not self.use_google_drive:
            contract_folder = get_contract_folder(self.contracts_dir, contract_id)
        else:
            contract_folder = None

        try:
            # Seleccionar plantilla
            template_path = self.template_service.select_template(data)

            # Process basic data
            processed_data = self.data_processor.flatten_data(data)

            # Process paragraphs from database if connection exists
            if connection:
                await self._process_paragraphs_from_db(connection, data, processed_data)

            # Generar documento
            doc_content = self.template_service.render_template(template_path, processed_data)

            # Generar nombre descriptivo del archivo para la respuesta
            contract_number = contract_id.replace("contract_", "")
            descriptive_filename = f"{contract_number}.docx"

            # Respuesta base
            response = {
                "success": True,
                "message": "Contrato generado exitosamente",
                "contract_id": contract_id,
                "template_used": template_path.name,
                "processed_data": processed_data,
                "filename": descriptive_filename
            }

            # Si NO se usa Google Drive, guardar localmente
            if not self.use_google_drive:
                output_filename = f"{contract_id}.docx"
                output_path = contract_folder / output_filename
                
                with open(output_path, 'wb') as f:
                    f.write(doc_content)
                
                # Guardar metadatos localmente
                self.metadata_service.save_contract_metadata(contract_id, processed_data, 1, "local")
                
                response.update({
                    "filename": output_filename,
                    "path": str(output_path),
                    "folder_path": str(contract_folder)
                })
            else:
                # Si se usa Google Drive, NO guardar localmente
                response.update({
                    "filename": f"{contract_id}.docx",
                    "path": None,
                    "folder_path": None,
                    "storage_type": "google_drive_only"
                })

            # Upload to Google Drive if enabled
            if self.use_google_drive:
                # Crear archivo temporal solo para subir a Drive
                import tempfile
                import os

                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
                    temp_file.write(doc_content)
                    temp_file_path = temp_file.name

                try:
                    drive_result = self.gdrive_utils.upload_contract(contract_id, temp_file_path, processed_data)
                    response.update(drive_result)

                    # Si la subida a Drive fue exitosa, actualizar path y folder_path con las URLs de Drive
                    if drive_result.get("drive_success") and drive_result.get("drive_link"):
                        response["path"] = drive_result.get("drive_view_link")
                        response["folder_path"] = drive_result.get("drive_link")

                    # Enviar email si hay enlace de Drive
                    if drive_result.get("drive_link"):
                        await self._send_contract_email(contract_id, processed_data, drive_result['drive_link'])
                finally:
                    # Limpiar archivo temporal
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)

            return response

        except Exception as e:
            # Clean up on error (only if local folder was created)
            if contract_folder and contract_folder.exists():
                shutil.rmtree(contract_folder)
            raise HTTPException(400, f"Error generando contrato: {str(e)}")

    async def update_contract(self, contract_id: str, updates: Dict[str, Any], connection=None) -> Dict[str, Any]:
        """Modificar contrato existente"""
        
        # Solo buscar carpeta local si NO se usa Google Drive
        if not self.use_google_drive:
            contract_folder = self.contracts_dir / contract_id
            if not contract_folder.exists():
                raise HTTPException(404, "Contrato no encontrado")
        else:
            contract_folder = None

        # Cargar metadatos existentes (solo si no se usa Google Drive)
        metadata = None
        if not self.use_google_drive:
            metadata = self.metadata_service.load_contract_metadata(contract_id)
            if not metadata:
                raise HTTPException(404, "Metadatos del contrato no encontrados")

        # Combinar datos existentes con actualizaciones
        original_data = metadata["original_data"] if metadata else {}
        updated_data = {**original_data, **updates}

        # Regenerar contrato
        template_path = self.template_service.select_template(updated_data)
        processed_data = self.data_processor.flatten_data(updated_data)

        # Process paragraphs from database if connection exists
        if connection:
            await self._process_paragraphs_from_db(connection, updated_data, processed_data)

        # Renderizar plantilla
        doc_content = self.template_service.render_template(template_path, processed_data)

        # Respuesta base
        response = {
            "success": True,
            "message": "Contrato actualizado exitosamente",
            "contract_id": contract_id,
            "updated_fields": list(updates.keys()),
            "filename": f"{contract_id}.docx"
        }

        # Si NO se usa Google Drive, guardar localmente
        if not self.use_google_drive:
            # Generar nombre descriptivo del archivo
            contract_number = contract_id.replace("contract_", "")
            output_filename = f"{contract_number}.docx"
            
            # Guardar archivo localmente
            output_path = contract_folder / output_filename
            with open(output_path, 'wb') as f:
                f.write(doc_content)
                # Generar nombre descriptivo del archivo
                contract_number = contract_id.replace("contract_", "")
                output_filename = f"{contract_number}.docx"
                output_path = contract_folder / output_filename
                
                with open(output_path, 'wb') as f:
                    f.write(doc_content)

                # Actualizar metadatos
                new_version = self.metadata_service.increment_version(contract_id)
                self.metadata_service.save_contract_metadata(contract_id, processed_data, new_version)
                
                response.update({
                    "version": new_version,
                    "path": str(output_path),
                    "folder_path": str(contract_folder),
                    "filename": output_filename
                })
        else:
            # Si se usa Google Drive, NO guardar localmente
            response.update({
                "version": None,
                "path": None,
                "folder_path": None,
                "storage_type": "google_drive_only"
            })

        # Upload to Google Drive if enabled
        if self.use_google_drive:
            # Crear archivo temporal solo para subir a Drive
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
                temp_file.write(doc_content)
                temp_file_path = temp_file.name

            try:
                drive_result = self.gdrive_utils.upload_contract(contract_id, temp_file_path, processed_data)
                response.update(drive_result)

                # Si la subida a Drive fue exitosa, actualizar path y folder_path con las URLs de Drive
                if drive_result.get("drive_success") and drive_result.get("drive_link"):
                    response["path"] = drive_result.get("drive_view_link")
                    response["folder_path"] = drive_result.get("drive_link")
            finally:
                # Limpiar archivo temporal
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        return response

    async def _process_paragraphs_from_db(self, connection: Any, data: Dict[str, Any], processed_data: Dict[str, Any]) -> None:
        """Procesar párrafos desde la base de datos"""
        try:
            from app.contracts.paragraphs import get_all_paragraphs_for_contract, get_paragraph_from_db, process_paragraph

            # Si existe paragraph_request, usarlo para obtener los párrafos específicos
            if "paragraph_request" in data:
                paragraphs_result = {}
                paragraph_errors = []
                
                # Mapeo de secciones a variables de Word (igual que en get_all_paragraphs_for_contract)
                section_mapping = {
                    'identification': 'client_paragraph',  # Will be overwritten based on person_role
                    'investors': 'investor_paragraph',
                    'clients': 'client_paragraph',
                    'witnesses': 'witness_paragraph',
                    'notaries': 'notary_paragraph',
                    'guarantees': 'guarantee_paragraph',
                    'terms_conditions': 'terms_paragraph',
                    'payment_terms': 'payment_paragraph',
                    'legal_clauses': 'legal_paragraph',
                    'signatures': 'signature_paragraph'
                }

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
                            # Determine word_variable first to check if we need multiple clients logic
                            word_variable = section_mapping.get(section)
                            if section == 'identification':
                                # For identification, use person_role to determine the variable
                                word_variable = 'client_paragraph' if person_role == 'client' else 'investor_paragraph'
                            
                            # Handle multiple clients for client_paragraph
                            if word_variable == 'client_paragraph':
                                clients_count = processed_data.get('clients_count', 0)
                                has_multiple_clients = clients_count > 1 or 'client2_full_name' in processed_data
                                
                                if has_multiple_clients:
                                    from app.contracts.paragraphs import _process_multiple_clients_paragraph
                                    processed = _process_multiple_clients_paragraph(template, processed_data, clients_count)
                                else:
                                    processed = process_paragraph(template, processed_data)
                            else:
                                processed = process_paragraph(template, processed_data)
                            
                            if word_variable:
                                paragraphs_result[word_variable] = processed
                                # Also add directly to processed_data for template compatibility
                                processed_data[word_variable] = processed
                                print(f"✅ Párrafo procesado: {word_variable} (desde {person_role}_{contract_type_db}_{section})")
                            else:
                                # If no mapping, use original key
                                key = f"{person_role}_{contract_type_db}_{section}"
                                paragraphs_result[key] = processed
                        else:
                            # If paragraph not found, use default one
                            default_template = f"Párrafo por defecto para {person_role} - {section}"
                            word_variable = section_mapping.get(section)
                            if section == 'identification':
                                word_variable = 'client_paragraph' if person_role == 'client' else 'investor_paragraph'
                            
                            if word_variable:
                                paragraphs_result[word_variable] = default_template
                                processed_data[word_variable] = default_template
                            else:
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
                        continue

                processed_data["paragraphs_result"] = paragraphs_result
                if paragraph_errors:
                    processed_data["paragraph_errors"] = paragraph_errors

            else:
                # Previous logic: infer automatically
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

                try:
                    # Get paragraphs for client
                    client_paragraphs = await get_all_paragraphs_for_contract(
                        connection,
                        "client",
                        contract_type_db,
                        contract_services,
                        processed_data
                    )
                    
                    # Get paragraphs for investor
                    investor_paragraphs = await get_all_paragraphs_for_contract(
                        connection,
                        "investor",
                        contract_type_db,
                        contract_services,
                        processed_data
                    )
                    
                    # Combine paragraphs
                    all_paragraphs = {**client_paragraphs, **investor_paragraphs}
                    processed_data.update(all_paragraphs)
                    
                except Exception as e:
                    print(f"⚠️ Error procesando párrafos automáticos: {e}")

        except Exception as e:
            print(f"⚠️ Error general procesando párrafos de DB: {e}")

    async def _send_contract_email(self, contract_id: str, processed_data: Dict[str, Any], drive_link: str) -> None:
        """Enviar email con el contrato generado"""
        try:
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
            html_body = load_email_template(client_name, drive_link)

            # Send to all recipients asynchronously
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

            # Wait for all emails to be sent
            await asyncio.gather(*email_tasks, return_exceptions=True)
            print(f"🔔 Email enviado a los destinatarios: {settings.CONTRACT_EMAIL_RECIPIENTS}")
            
        except Exception as e:
            print(f"Error enviando email: {e}")
