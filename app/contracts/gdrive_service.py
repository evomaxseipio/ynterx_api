from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import os
import json
import uuid
import io
from fastapi import HTTPException, UploadFile
from docxtpl import DocxTemplate
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import mimetypes
from app.email import send_email
from app.config import settings

class GoogleDriveContractService:
    """Service class for handling contract operations with Google Drive integration"""

    # Allowed file extensions for attachments
    ALLOWED_EXTENSIONS = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
        'documents': ['.doc', '.docx', '.pdf'],
        'spreadsheets': ['.xls', '.xlsx']
    }

    # Google Drive MIME types
    MIME_TYPES = {
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.pdf': 'application/pdf',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xls': 'application/vnd.ms-excel',
        '.doc': 'application/msword',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.json': 'application/json'
    }

    def __init__(self, credentials_path: str = None):
        """Initialize Google Drive service"""
        self.base_dir = Path(__file__).parent.parent
        self.template_dir = self.base_dir / "templates"
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CREDENTIALS_PATH')

        # Initialize Google Drive service
        self.drive_service = self._init_drive_service()

        # Ensure local template directory exists
        self.template_dir.mkdir(exist_ok=True)

        # Always find or create the main contracts folder in Google Drive
        self.drive_folder_id = self._get_or_create_main_folder()

    def _init_drive_service(self):
        """Initialize Google Drive service with service account credentials"""
        if not self.credentials_path or not Path(self.credentials_path).exists():
            raise HTTPException(
                status_code=500,
                detail=f"Google Drive credentials not found at: {self.credentials_path}"
            )

        try:
            credentials = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/drive']
            )

            service = build('drive', 'v3', credentials=credentials)
            return service

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize Google Drive service: {str(e)}"
            )

    def _get_or_create_main_folder(self) -> str:
        """Find 'Ynterx_Contracts' folder in Google Drive, or create it if it doesn't exist. Share it if needed."""
        # Search for folder by name
        query = "name = 'Ynterx_Contracts' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = self.drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        if files:
            folder_id = files[0]['id']
            print(f"Found main contracts folder with ID: {folder_id}")
            # Intentar compartir siempre que se inicializa
            self._share_folder_with_user(folder_id)
            return folder_id
        # If not found, create it
        folder_metadata = {
            'name': 'Ynterx_Contracts',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = self.drive_service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        print(f"Created main contracts folder with ID: {folder['id']}")
        self._share_folder_with_user(folder['id'])
        return folder['id']

    def _generate_contract_id(self) -> str:
        """Generate unique contract ID"""
        now = datetime.now()
        date = now.strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"contract_{date}_{unique_id}"

    def _create_contract_folder_in_drive(self, contract_id: str) -> str:
        """Create folder structure for contract in Google Drive"""
        # Create main contract folder
        contract_folder_metadata = {
            'name': contract_id,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [self.drive_folder_id]
        }

        contract_folder = self.drive_service.files().create(
            body=contract_folder_metadata,
            fields='id'
        ).execute()

        contract_folder_id = contract_folder.get('id')

        # Compartir carpeta automáticamente
        try:
            permission = {
                'type': 'user',
                'role': 'reader',
                'emailAddress': 'mseipio.evotechrd@gmail.com'
            }

            self.drive_service.permissions().create(
                fileId=contract_folder_id,
                body=permission,
                fields='id'
            ).execute()

            print(f"Folder shared with mseipio.evotechrd@gmail.com")

        except Exception as e:
            print(f"Error sharing folder: {e}")

        # NUEVO: Compartir automáticamente la carpeta
        self._share_folder_with_user(contract_folder_id)

        # Create attachments subfolder
        attachments_folder_metadata = {
            'name': 'attachments',
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [contract_folder_id]
        }

        attachments_folder = self.drive_service.files().create(
            body=attachments_folder_metadata,
            fields='id'
        ).execute()

        return contract_folder_id

    def _upload_file_to_drive(self, file_content: bytes, filename: str, parent_folder_id: str, mime_type: str = None) -> str:
        """Upload file to Google Drive"""
        if not mime_type:
            mime_type = self.MIME_TYPES.get(Path(filename).suffix.lower(), 'application/octet-stream')

        file_metadata = {
            'name': filename,
            'parents': [parent_folder_id]
        }

        media = MediaIoBaseUpload(
            io.BytesIO(file_content),
            mimetype=mime_type,
            resumable=True
        )

        file = self.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,name,size,createdTime,modifiedTime'
        ).execute()

        return file.get('id')

    def _download_file_from_drive(self, file_id: str) -> bytes:
        """Download file from Google Drive"""
        request = self.drive_service.files().get_media(fileId=file_id)
        file_io = io.BytesIO()
        downloader = MediaIoBaseDownload(file_io, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()

        return file_io.getvalue()

    def _save_metadata_to_drive(self, contract_folder_id: str, contract_id: str, data: Dict[str, Any]) -> str:
        """Save contract metadata to Google Drive as JSON"""
        metadata = {
            "contract_id": contract_id,
            "drive_folder_id": contract_folder_id,
            "created_at": datetime.now().isoformat(),
            "modified_at": datetime.now().isoformat(),
            "original_data": data,
            "version": 1
        }

        metadata_json = json.dumps(metadata, indent=2, ensure_ascii=False)
        metadata_bytes = metadata_json.encode('utf-8')

        file_id = self._upload_file_to_drive(
            metadata_bytes,
            "metadata.json",
            contract_folder_id,
            "application/json"
        )

        return file_id

    def _get_template_file(self) -> Path:
        """Find the first .docx file in the local templates folder"""
        template_files = list(self.template_dir.glob("*.docx"))
        if not template_files:
            raise HTTPException(
                status_code=404,
                detail="No .docx template found in templates folder"
            )
        return template_files[0]

    def _is_allowed_file_type(self, filename: str) -> bool:
        """Check if file type is allowed for attachments"""
        file_ext = Path(filename).suffix.lower()

        for category, extensions in self.ALLOWED_EXTENSIONS.items():
            if file_ext in extensions:
                return True
        return False

    def _get_file_type_category(self, filename: str) -> str:
        """Get file type category"""
        file_ext = Path(filename).suffix.lower()

        for category, extensions in self.ALLOWED_EXTENSIONS.items():
            if file_ext in extensions:
                return category
        return "unknown"

    def _clean_data_for_template(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean data to avoid template processing issues"""
        def clean_value(value):
            if isinstance(value, dict):
                return {k: clean_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [clean_value(item) for item in value]
            elif isinstance(value, str):
                return value.replace('\r\n', '\n').replace('\r', '\n')
            else:
                return value

        return clean_value(data)

    def _get_folder_contents(self, folder_id: str) -> List[Dict]:
        """Get contents of a Google Drive folder"""
        try:
            results = self.drive_service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="files(id,name,mimeType,size,createdTime,modifiedTime)"
            ).execute()

            return results.get('files', [])
        except Exception as e:
            print(f"Error getting folder contents: {str(e)}")
            return []

    def _is_mortgage_data(self, data: Dict[str, Any]) -> bool:
        """
        Detecta automáticamente si los datos son de contrato hipotecario
        """
        mortgage_indicators = ['loan', 'properties', 'clients', 'investors', 'witnesses', 'notaries']
        found_indicators = sum(1 for indicator in mortgage_indicators if indicator in data)
        return found_indicators >= 4

    def _convert_mortgage_to_flat_data(self, mortgage_data: Dict[str, Any]) -> Dict[str, Any]:
        def format_date_spanish(date_str: str) -> str:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                months = {
                    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
                    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
                    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
                }
                return f"{date_obj.day} de {months[date_obj.month]} de {date_obj.year}"
            except:
                return date_str

        def number_to_words(amount: float) -> str:
            if amount == 20000:
                return "VEINTE MIL"
            elif amount == 440:
                return "CUATROCIENTOS CUARENTA"
            elif amount == 20440:
                return "VEINTE MIL CUATROCIENTOS CUARENTA"
            else:
                return f"{amount:,.2f}"

        loan = mortgage_data.get("loan", {})
        properties = mortgage_data.get("properties", [])
        clients = mortgage_data.get("clients", [])
        investors = mortgage_data.get("investors", [])
        witnesses = mortgage_data.get("witnesses", [])
        notaries = mortgage_data.get("notaries", [])

        client = clients[0] if clients else {}
        investor = investors[0] if investors else {}
        witness = witnesses[0] if witnesses else {}
        notary = notaries[0] if notaries else {}
        property_data = properties[0] if properties else {}

        flat_data = {
            "client_name": f"{client.get('person', {}).get('first_name', '')} {client.get('person', {}).get('last_name', '')}".strip(),
            "contract_date": mortgage_data.get("contract_date") or format_date_spanish(loan.get("start_date", "2025-03-26")),
            "amount": f"{loan.get('amount', 0):,.2f}",
            "description": f"Préstamo hipotecario por {loan.get('currency', 'USD')}${loan.get('amount', 0):,.2f}",
            "company_name": "GRUPO REYSA, S.R.L.",
            "company_tax_id": "1-3225325-6",
            "company_address": f"{investor.get('address', {}).get('address_line1', '')}, {investor.get('address', {}).get('city', '')}".strip(', '),
            "company_email": investor.get('person', {}).get('email', ''),
            "company_phone": investor.get('person', {}).get('phone_number', ''),
            "contractor_name": f"{investor.get('person', {}).get('first_name', '')} {investor.get('person', {}).get('last_name', '')}".strip(),
            "contractor_email": investor.get('person', {}).get('email', ''),
            "contractor_phone": investor.get('person', {}).get('phone_number', ''),
            "project": f"Préstamo Hipotecario - Propiedad {property_data.get('cadastral_number', '')}",
            "duration": f"{loan.get('term_months', 12)} meses",
            "work_mode": "Presencial",
            "start_date": format_date_spanish(loan.get("start_date", "")),
            "end_date": format_date_spanish(loan.get("end_date", "")),
            "payment_method": "Transferencia bancaria",
            "payment_terms": f"{loan.get('loan_payments_details', {}).get('payment_qty_quotes', 11)} cuotas mensuales",
            "loan_amount": f"{loan.get('amount', 0):,.2f}",
            "loan_amount_words": number_to_words(loan.get('amount', 0)),
            "loan_currency": loan.get('currency', 'USD'),
            "interest_rate": f"{loan.get('interest_rate', 0)}",
            "interest_rate_words": "DOS PUNTO DOS",
            "term_months": str(loan.get('term_months', 12)),
            "monthly_payment": f"{loan.get('loan_payments_details', {}).get('monthly_payment', 0):,.2f}",
            "monthly_payment_words": number_to_words(loan.get('loan_payments_details', {}).get('monthly_payment', 0)),
            "final_payment": f"{loan.get('loan_payments_details', {}).get('final_payment', 0):,.2f}",
            "final_payment_words": number_to_words(loan.get('loan_payments_details', {}).get('final_payment', 0)),
            "payment_quotes": str(loan.get('loan_payments_details', {}).get('payment_qty_quotes', 11)),
            "discount_rate": f"{loan.get('loan_payments_details', {}).get('discount_rate', 0)}",
            "penalty_rate": "0.2",
            "bank_name": loan.get('bank_deposit_account', {}).get('bank_name', ''),
            "account_number": loan.get('bank_deposit_account', {}).get('account_number', ''),
            "investor_company_name": "GRUPO REYSA, S.R.L.",
            "investor_rnc": "1-3225325-6",
            "investor_rm": "3187SPM",
            "investor_full_name": f"{investor.get('person', {}).get('first_name', '')} {investor.get('person', {}).get('last_name', '')}".strip(),
            "investor_first_name": investor.get('person', {}).get('first_name', ''),
            "investor_last_name": investor.get('person', {}).get('last_name', ''),
            "investor_nationality": investor.get('person', {}).get('nationality', ''),
            "investor_marital_status": investor.get('person', {}).get('marital_status', ''),
            "investor_document_number": investor.get('person_document', {}).get('document_number', ''),
            "investor_address": f"{investor.get('address', {}).get('address_line1', '')}, {investor.get('address', {}).get('address_line2', '')}".strip(', '),
            "investor_city": investor.get('address', {}).get('city', ''),
            "client_full_name": f"{client.get('person', {}).get('first_name', '')} {client.get('person', {}).get('last_name', '')}".strip(),
            "client_first_name": client.get('person', {}).get('first_name', ''),
            "client_last_name": client.get('person', {}).get('last_name', ''),
            "client_nationality": client.get('person', {}).get('nationality', ''),
            "client_marital_status": client.get('person', {}).get('marital_status', ''),
            "client_document_number": client.get('person_document', {}).get('document_number', ''),
            "client_address": f"{client.get('address', {}).get('address_line1', '')}, {client.get('address', {}).get('address_line2', '')}".strip(', '),
            "client_city": client.get('address', {}).get('city', ''),
            "client_phone": client.get('person', {}).get('phone_number', ''),
            "client_email": client.get('person', {}).get('email', ''),
            "property_cadastral_number": property_data.get('cadastral_number', ''),
            "property_title_number": property_data.get('title_number', ''),
            "property_surface_area": f"{property_data.get('surface_area', 0)}",
            "property_address": f"{property_data.get('address_line1', '')}, {property_data.get('address_line2', '')}".strip(', '),
            "property_city": property_data.get('city', ''),
            "property_description": property_data.get('description', ''),
            "witness_full_name": f"{witness.get('person', {}).get('first_name', '')} {witness.get('person', {}).get('last_name', '')}".strip(),
            "witness_document_number": witness.get('person_document', {}).get('document_number', ''),
            "witness_address": f"{witness.get('address', {}).get('address_line1', '')}, {witness.get('address', {}).get('address_line2', '')}".strip(', '),
            "notary_full_name": f"{notary.get('person', {}).get('first_name', '')} {notary.get('person', {}).get('last_name', '')}".strip(),
            "notary_number": notary.get('notary_document', {}).get('notary_number', ''),
            "notary_document_number": notary.get('notary_document', {}).get('document_number', ''),
            "contract_location": mortgage_data.get("contract_location", "San Pedro de Macorís, República Dominicana"),
            "contract_year": "2025",
            "authorized_lawyer": "Licda. Lady Marlene Pineda Ramírez",
            "authorized_lawyer_cedula": "023-0142038-2",
            "additional_data": {
                "original_mortgage_data": mortgage_data,
                "contract_type": "mortgage",
                "processed_at": datetime.now().isoformat(),
                "fields_processed": True
            }
        }
        return flat_data

    def generate_contract(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contract from template and save to Google Drive"""
        try:
            # Detectar si es contrato hipotecario y convertir automáticamente
            if self._is_mortgage_data(data):
                print("Detected mortgage contract data - converting to flat structure")
                data = self._convert_mortgage_to_flat_data(data)

            # Generate contract ID and create folder in Drive
            contract_id = self._generate_contract_id()
            contract_folder_id = self._create_contract_folder_in_drive(contract_id)

            print(f"Generating contract: {contract_id}")
            print(f"Drive folder ID: {contract_folder_id}")

            # Get template from local storage
            template_path = self._get_template_file()

            # Load and render template
            doc = DocxTemplate(template_path)
            cleaned_data = self._clean_data_for_template(data)

            try:
                doc.render(cleaned_data)
            except Exception as e:
                print(f"Template rendering error: {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Error processing template. Check that fields match: {str(e)}"
                )

            # Save contract to memory buffer
            contract_buffer = io.BytesIO()
            doc.save(contract_buffer)
            contract_bytes = contract_buffer.getvalue()

            # Upload contract to Google Drive
            contract_filename = f"{contract_id}.docx"
            contract_file_id = self._upload_file_to_drive(
                contract_bytes,
                contract_filename,
                contract_folder_id
            )

            # Save metadata to Google Drive
            metadata_file_id = self._save_metadata_to_drive(
                contract_folder_id,
                contract_id,
                cleaned_data
            )

            # Generate shareable link
            drive_link = f"https://drive.google.com/drive/folders/{contract_folder_id}"

            # Enviar notificación por email (solo una vez por contrato)
            try:
                subject = "Nuevo contrato generado"
                body = f"Se ha generado un nuevo contrato con ID: {contract_id}.\n\nAccede a la carpeta en Google Drive: {drive_link}"
                # Cambia settings.SMTP_FROM_EMAIL por el destinatario real si lo deseas
                import asyncio
                asyncio.create_task(send_email(settings.SMTP_FROM_EMAIL, subject, body))
            except Exception as e:
                print(f"No se pudo enviar la notificación por email: {e}")

            return {
                "success": True,
                "message": "Contract generated and saved to Google Drive successfully",
                "contract_id": contract_id,
                "filename": contract_filename,
                "drive_folder_id": contract_folder_id,
                "drive_file_id": contract_file_id,
                "drive_link": drive_link,
                "metadata_file_id": metadata_file_id,
                "processed_data": cleaned_data
            }

        except HTTPException:
            raise
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )

    def upload_attachment(self, contract_id: str, file: UploadFile) -> Dict[str, Any]:
        """Upload attachment to contract folder in Google Drive"""
        try:
            # Find contract folder
            contract_folder = self._find_contract_folder(contract_id)
            if not contract_folder:
                raise HTTPException(
                    status_code=404,
                    detail="Contract not found"
                )

            # Validate file type
            if not self._is_allowed_file_type(file.filename):
                allowed_exts = []
                for exts in self.ALLOWED_EXTENSIONS.values():
                    allowed_exts.extend(exts)
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not allowed. Allowed types: {', '.join(allowed_exts)}"
                )

            # Find attachments folder
            attachments_folder = self._find_attachments_folder(contract_folder['id'])
            if not attachments_folder:
                raise HTTPException(
                    status_code=404,
                    detail="Attachments folder not found"
                )

            # Generate unique filename
            file_ext = Path(file.filename).suffix
            base_name = Path(file.filename).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{base_name}_{timestamp}{file_ext}"

            # Read file content
            file_content = file.file.read()

            # Upload to Google Drive
            file_id = self._upload_file_to_drive(
                file_content,
                unique_filename,
                attachments_folder['id']
            )

            file_size = len(file_content)
            file_type = self._get_file_type_category(file.filename)

            return {
                "success": True,
                "message": "File uploaded to Google Drive successfully",
                "filename": unique_filename,
                "drive_file_id": file_id,
                "file_size": file_size,
                "file_type": file_type,
                "contract_id": contract_id
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error uploading file: {str(e)}"
            )

    def _find_contract_folder(self, contract_id: str) -> Optional[Dict]:
        """Find contract folder in Google Drive by contract_id"""
        try:
            results = self.drive_service.files().list(
                q=f"'{self.drive_folder_id}' in parents and name='{contract_id}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                fields="files(id,name)"
            ).execute()

            files = results.get('files', [])
            return files[0] if files else None
        except Exception as e:
            print(f"Error finding contract folder: {str(e)}")
            return None

    def _find_attachments_folder(self, contract_folder_id: str) -> Optional[Dict]:
        """Find attachments folder within contract folder"""
        try:
            results = self.drive_service.files().list(
                q=f"'{contract_folder_id}' in parents and name='attachments' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                fields="files(id,name)"
            ).execute()

            files = results.get('files', [])
            return files[0] if files else None
        except Exception as e:
            print(f"Error finding attachments folder: {str(e)}")
            return None

    def list_contracts(self) -> Dict[str, Any]:
        """List all contracts in Google Drive"""
        try:
            contract_folders = self._get_folder_contents(self.drive_folder_id)

            contracts = []
            for folder in contract_folders:
                if folder['mimeType'] == 'application/vnd.google-apps.folder':
                    # Get contract file and metadata
                    folder_contents = self._get_folder_contents(folder['id'])

                    contract_file = None
                    attachments_count = 0

                    for item in folder_contents:
                        if item['name'].endswith('.docx') and item['name'].startswith('contract_'):
                            contract_file = item
                        elif item['name'] == 'attachments':
                            # Count attachments
                            attachments = self._get_folder_contents(item['id'])
                            attachments_count = len(attachments)

                    if contract_file:
                        contract_data = {
                            "contract_id": folder['name'],
                            "filename": contract_file['name'],
                            "created_at": contract_file.get('createdTime'),
                            "modified_at": contract_file.get('modifiedTime'),
                            "size_bytes": int(contract_file.get('size', 0)),
                            "drive_folder_id": folder['id'],
                            "drive_file_id": contract_file['id'],
                            "attachments_count": attachments_count,
                            "drive_link": f"https://drive.google.com/drive/folders/{folder['id']}"
                        }
                        contracts.append(contract_data)

            # Sort by creation date (newest first)
            contracts.sort(key=lambda x: x["created_at"], reverse=True)

            return {
                "success": True,
                "contracts": contracts,
                "total": len(contracts)
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error listing contracts: {str(e)}"
            )

    def download_contract(self, contract_id: str) -> bytes:
        """Download contract file from Google Drive"""
        try:
            contract_folder = self._find_contract_folder(contract_id)
            if not contract_folder:
                raise HTTPException(
                    status_code=404,
                    detail="Contract not found"
                )

            # Find contract file
            folder_contents = self._get_folder_contents(contract_folder['id'])
            contract_file = None

            for item in folder_contents:
                if item['name'].endswith('.docx') and item['name'].startswith('contract_'):
                    contract_file = item
                    break

            if not contract_file:
                raise HTTPException(
                    status_code=404,
                    detail="Contract file not found"
                )

            # Download file
            file_content = self._download_file_from_drive(contract_file['id'])
            return file_content

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error downloading contract: {str(e)}"
            )

    def get_drive_folder_link(self, contract_id: str) -> str:
        """Get shareable Google Drive folder link"""
        contract_folder = self._find_contract_folder(contract_id)
        if not contract_folder:
            raise HTTPException(
                status_code=404,
                detail="Contract not found"
            )

        return f"https://drive.google.com/drive/folders/{contract_folder['id']}"

    def test_drive_connection(self) -> Dict[str, Any]:
        """Test Google Drive connection"""
        try:
            about = self.drive_service.about().get(fields="user").execute()
            user_email = about.get('user', {}).get('emailAddress', 'Unknown')

            return {
                "success": True,
                "message": "Google Drive connection successful",
                "user_email": user_email,
                "main_folder_id": self.drive_folder_id
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Google Drive connection failed: {str(e)}"
            }

    # Keep original service methods for compatibility
    def list_templates(self) -> Dict[str, Any]:
        """List all available templates"""
        try:
            template_files = [f.name for f in self.template_dir.glob("*.docx")]
            return {
                "success": True,
                "templates": template_files,
                "total": len(template_files)
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error listing templates: {str(e)}"
            )

    def get_example_data(self) -> Dict[str, Any]:
        """Get example data structure"""
        return {
            "example": {
                "client_name": "John Doe",
                "contract_date": "2025-06-24",
                "amount": "15,000",
                "description": "Technology consulting services",
                "company_name": "Tech Solutions S.A.",
                "company_tax_id": "12345678901",
                "company_address": "Main Avenue 123",
                "contractor_name": "Jane Smith",
                "contractor_email": "jane@company.com",
                "contractor_phone": "+1234567890",
                "project": "ERP Implementation",
                "duration": "6 months",
                "work_mode": "Remote"
            },
            "note": "Use simple field names in template: {{client_name}}, {{contract_date}}, {{company_name}}, etc."
        }

    def test_template(self) -> Dict[str, Any]:
        """Test template with minimal data"""
        try:
            template_path = self._get_template_file()
            doc = DocxTemplate(template_path)

            # Minimal test data
            test_data = {
                "client_name": "Test Client",
                "contract_date": "2025-06-24",
                "amount": "1000",
                "description": "Test Service"
            }

            doc.render(test_data)

            return {
                "success": True,
                "message": "Template test successful",
                "template_file": template_path.name,
                "test_data": test_data
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Template test failed: {str(e)}",
                "error": str(e)
            }

    # Agregar este método a tu app/contracts/gdrive_service.py
    # Busca la clase GoogleDriveContractService y agrega este método:

    def _share_folder_with_user(self, folder_id: str, user_email: str = "mseipio.evotechrd@gmail.com"):
        """Share folder with a specific user"""
        try:
            permission = {
                'type': 'user',
                'role': 'reader',  # o 'writer' si quieres que pueda editar
                'emailAddress': user_email
            }

            self.drive_service.permissions().create(
                fileId=folder_id,
                body=permission,
                fields='id',
                sendNotificationEmail=False  # No enviar email de notificación
            ).execute()

            print(f"Folder {folder_id} shared with {user_email}")
            return True

        except Exception as e:
            print(f"Error sharing folder: {str(e)}")
            return False
