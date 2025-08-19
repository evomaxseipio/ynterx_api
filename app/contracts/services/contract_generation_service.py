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
        contract_folder = get_contract_folder(self.contracts_dir, contract_id)

        try:
            # Seleccionar plantilla
            template_path = self.template_service.select_template(data)

            # Procesar datos básicos
            processed_data = self.data_processor.flatten_data(data)

            # Procesar párrafos de la base de datos si hay conexión
            if connection:
                await self._process_paragraphs_from_db(connection, data, processed_data)

            # Generar documento
            doc_content = self.template_service.render_template(template_path, processed_data)

            # Guardar archivo
            output_filename = f"{contract_id}.docx"
            output_path = contract_folder / output_filename
            
            with open(output_path, 'wb') as f:
                f.write(doc_content)

            # Guardar metadatos
            storage_type = "google_drive" if self.use_google_drive else "local"
            self.metadata_service.save_contract_metadata(contract_id, processed_data, 1, storage_type)

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

            # Subir a Google Drive si está habilitado
            if self.use_google_drive:
                drive_result = self.gdrive_utils.upload_contract(contract_id, output_path, processed_data)
                response.update(drive_result)
                
                # Enviar email si hay enlace de Drive
                if drive_result.get("drive_link"):
                    await self._send_contract_email(contract_id, processed_data, drive_result['drive_link'])

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
        metadata = self.metadata_service.load_contract_metadata(contract_id)
        if not metadata:
            raise HTTPException(404, "Metadatos del contrato no encontrados")

        # Combinar datos existentes con actualizaciones
        original_data = metadata["original_data"]
        updated_data = {**original_data, **updates}

        # Regenerar contrato
        template_path = self.template_service.select_template(updated_data)
        processed_data = self.data_processor.flatten_data(updated_data)

        # Procesar párrafos de la base de datos si hay conexión
        if connection:
            await self._process_paragraphs_from_db(connection, updated_data, processed_data)

        # Renderizar plantilla
        doc_content = self.template_service.render_template(template_path, processed_data)

        # Guardar archivo actualizado
        output_filename = f"{contract_id}.docx"
        output_path = contract_folder / output_filename
        
        with open(output_path, 'wb') as f:
            f.write(doc_content)

        # Actualizar metadatos
        new_version = self.metadata_service.increment_version(contract_id)
        self.metadata_service.save_contract_metadata(contract_id, processed_data, new_version)

        return {
            "success": True,
            "message": "Contrato actualizado exitosamente",
            "contract_id": contract_id,
            "version": new_version,
            "updated_fields": list(updates.keys())
        }

    async def _process_paragraphs_from_db(self, connection: Any, data: Dict[str, Any], processed_data: Dict[str, Any]) -> None:
        """Procesar párrafos desde la base de datos"""
        try:
            from app.contracts.paragraphs import get_all_paragraphs_for_contract, get_paragraph_from_db, process_paragraph

            # Si existe paragraph_request, usarlo para obtener los párrafos específicos
            if "paragraph_request" in data:
                paragraphs_result = {}
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
            print(f"Error enviando email: {e}")
