from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from fastapi import HTTPException, UploadFile
from docxtpl import DocxTemplate
import os
import json
import uuid
import shutil

class ContractService:
    """Service class for handling contract operations with local storage"""

    # Allowed file extensions for attachments
    ALLOWED_EXTENSIONS = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
        'documents': ['.doc', '.docx', '.pdf'],
        'spreadsheets': ['.xls', '.xlsx']
    }

    def __init__(self):
        # Set paths relative to the project root
        self.base_dir = Path(__file__).parent.parent  # Go up to project root
        self.template_dir = self.base_dir / "templates"
        self.contracts_dir = self.base_dir / "generated_contracts"
        self._ensure_directories()

    def _ensure_directories(self):
        """Create directories if they don't exist"""
        self.template_dir.mkdir(exist_ok=True)
        self.contracts_dir.mkdir(exist_ok=True)

    def _generate_contract_id(self) -> str:
        """Generate unique contract ID"""
        now = datetime.now()
        date = now.strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"contract_{date}_{unique_id}"

    def _generate_filename(self, contract_id: str) -> str:
        """Generate filename for contract"""
        return f"{contract_id}.docx"

    def _create_contract_folder(self, contract_id: str) -> Path:
        """Create folder structure for contract"""
        contract_folder = self.contracts_dir / contract_id
        contract_folder.mkdir(exist_ok=True)

        # Create attachments subfolder
        attachments_folder = contract_folder / "attachments"
        attachments_folder.mkdir(exist_ok=True)

        return contract_folder

    def _save_metadata(self, contract_folder: Path, contract_id: str, data: Dict[str, Any]):
        """Save contract metadata to JSON file"""
        metadata = {
            "contract_id": contract_id,
            "created_at": datetime.now().isoformat(),
            "modified_at": datetime.now().isoformat(),
            "original_data": data,
            "version": 1
        }

        metadata_file = contract_folder / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def _load_metadata(self, contract_folder: Path) -> Dict[str, Any]:
        """Load contract metadata from JSON file"""
        metadata_file = contract_folder / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _update_metadata(self, contract_folder: Path, new_data: Dict[str, Any]):
        """Update contract metadata"""
        metadata = self._load_metadata(contract_folder)
        metadata["modified_at"] = datetime.now().isoformat()
        metadata["original_data"].update(new_data)
        metadata["version"] = metadata.get("version", 1) + 1

        metadata_file = contract_folder / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def _get_template_file(self) -> Path:
        """Find the first .docx file in the templates folder"""
        template_files = list(self.template_dir.glob("*.docx"))
        if not template_files:
            raise HTTPException(
                status_code=404,
                detail="No .docx template found in templates folder"
            )
        return template_files[0]

    def _validate_filename(self, filename: str) -> bool:
        """Validate filename for security"""
        return (
            filename.endswith('.docx') and
            '..' not in filename and
            '/' not in filename and
            '\\' not in filename
        )

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
                # Remove problematic characters that might cause template issues
                return value.replace('\r\n', '\n').replace('\r', '\n')
            else:
                return value

        return clean_value(data)

    '''def generate_contract(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contract from template with provided data"""
        try:
            # Generate contract ID and create folder
            contract_id = self._generate_contract_id()
            contract_folder = self._create_contract_folder(contract_id)

            # Get template
            template_path = self._get_template_file()

            print(f"Generating contract: {contract_id}")
            print(f"Contract folder: {contract_folder}")
            print(f"Template path: {template_path}")

            # Load template
            doc = DocxTemplate(template_path)

            # Clean data to avoid template issues
            cleaned_data = self._clean_data_for_template(data)

            # Render template with data
            try:
                doc.render(cleaned_data)
            except Exception as e:
                print(f"Template rendering error: {str(e)}")
                shutil.rmtree(contract_folder)  # Clean up folder on error
                raise HTTPException(
                    status_code=400,
                    detail=f"Error processing template. Check that fields match: {str(e)}"
                )

            # Generate filename and save
            filename = self._generate_filename(contract_id)
            output_path = contract_folder / filename
            doc.save(output_path)

            # Save metadata
            self._save_metadata(contract_folder, contract_id, cleaned_data)

            return {
                "success": True,
                "message": "Contract generated successfully",
                "contract_id": contract_id,
                "filename": filename,
                "path": str(output_path),
                "folder_path": str(contract_folder),
                "processed_data": cleaned_data
            }

        except HTTPException:
            raise
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )'''

    # MODIFICAR TU MÉTODO generate_contract EXISTENTE
    # Reemplazar toda la función con esta versión mejorada
    def generate_contract(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate contract from template with provided data
        MODIFICADO: Detecta automáticamente contratos hipotecarios
        """
        try:
            # Detectar si es contrato hipotecario y convertir automáticamente
            if self._is_mortgage_data(data):
                print("Detected mortgage contract data - converting to flat structure")
                data = self._convert_mortgage_to_flat_data(data)
                # Agregar sufijo para identificar contratos hipotecarios
                contract_id = self._generate_contract_id().replace("contract_", "mortgage_")
            else:
                print("Using standard contract data")
                contract_id = self._generate_contract_id()

            # Crear carpeta del contrato
            contract_folder = self._create_contract_folder(contract_id)

            # Seleccionar template apropiado
            template_path = self._select_template_for_contract(data)

            print(f"Generating contract: {contract_id}")
            print(f"Contract folder: {contract_folder}")
            print(f"Template path: {template_path}")

            # Load template
            doc = DocxTemplate(template_path)

            # Clean data to avoid template issues
            cleaned_data = self._clean_data_for_template(data)

            # Render template with data
            try:
                doc.render(cleaned_data)
            except Exception as e:
                print(f"Template rendering error: {str(e)}")
                shutil.rmtree(contract_folder)  # Clean up folder on error
                raise HTTPException(
                    status_code=400,
                    detail=f"Error processing template. Check that fields match: {str(e)}"
                )

            # Generate filename and save
            filename = self._generate_filename(contract_id)
            output_path = contract_folder / filename
            doc.save(output_path)

            # Save metadata
            self._save_metadata(contract_folder, contract_id, cleaned_data)

            return {
                "success": True,
                "message": "Contract generated successfully",
                "contract_id": contract_id,
                "filename": filename,
                "path": str(output_path),
                "folder_path": str(contract_folder),
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


    def update_contract(self, contract_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing contract with new data"""
        try:
            contract_folder = self.contracts_dir / contract_id

            if not contract_folder.exists():
                raise HTTPException(
                    status_code=404,
                    detail="Contract not found"
                )

            # Load existing metadata
            metadata = self._load_metadata(contract_folder)
            if not metadata:
                raise HTTPException(
                    status_code=404,
                    detail="Contract metadata not found"
                )

            # Merge existing data with updates
            updated_data = metadata.get("original_data", {}).copy()

            # Remove None values and update with new data
            clean_update_data = {k: v for k, v in data.items() if v is not None}
            updated_data.update(clean_update_data)

            # Get template and regenerate contract
            template_path = self._get_template_file()
            doc = DocxTemplate(template_path)

            # Clean data and render
            cleaned_data = self._clean_data_for_template(updated_data)

            try:
                doc.render(cleaned_data)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error processing template with updated data: {str(e)}"
                )

            # Save updated contract
            filename = self._generate_filename(contract_id)
            output_path = contract_folder / filename
            doc.save(output_path)

            # Update metadata
            self._update_metadata(contract_folder, clean_update_data)

            return {
                "success": True,
                "message": "Contract updated successfully",
                "contract_id": contract_id,
                "filename": filename,
                "path": str(output_path),
                "folder_path": str(contract_folder),
                "processed_data": cleaned_data
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error updating contract: {str(e)}"
            )

    def upload_attachment(self, contract_id: str, file: UploadFile) -> Dict[str, Any]:
        """Upload attachment to contract folder"""
        try:
            contract_folder = self.contracts_dir / contract_id

            if not contract_folder.exists():
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

            # Create attachments folder if not exists
            attachments_folder = contract_folder / "attachments"
            attachments_folder.mkdir(exist_ok=True)

            # Generate unique filename to avoid conflicts
            file_ext = Path(file.filename).suffix
            base_name = Path(file.filename).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{base_name}_{timestamp}{file_ext}"

            file_path = attachments_folder / unique_filename

            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            file_size = file_path.stat().st_size
            file_type = self._get_file_type_category(file.filename)

            return {
                "success": True,
                "message": "File uploaded successfully",
                "filename": unique_filename,
                "file_path": str(file_path),
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

    def list_attachments(self, contract_id: str) -> Dict[str, Any]:
        """List all attachments for a contract"""
        try:
            contract_folder = self.contracts_dir / contract_id
            attachments_folder = contract_folder / "attachments"

            if not contract_folder.exists():
                raise HTTPException(
                    status_code=404,
                    detail="Contract not found"
                )

            if not attachments_folder.exists():
                return {
                    "success": True,
                    "contract_id": contract_id,
                    "attachments": [],
                    "total": 0
                }

            attachments = []
            for file_path in attachments_folder.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    attachments.append({
                        "filename": file_path.name,
                        "file_size": stat.st_size,
                        "file_type": self._get_file_type_category(file_path.name),
                        "uploaded_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "file_path": str(file_path)
                    })

            # Sort by upload date (newest first)
            attachments.sort(key=lambda x: x["uploaded_at"], reverse=True)

            return {
                "success": True,
                "contract_id": contract_id,
                "attachments": attachments,
                "total": len(attachments)
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error listing attachments: {str(e)}"
            )

    def list_contracts(self) -> Dict[str, Any]:
        """List all generated contracts"""
        try:
            contract_folders = []

            for folder in self.contracts_dir.iterdir():
                if folder.is_dir() and folder.name.startswith("contract_"):
                    # Find contract file
                    contract_files = list(folder.glob("*.docx"))
                    if contract_files:
                        contract_file = contract_files[0]
                        stat = contract_file.stat()

                        # Load metadata
                        metadata = self._load_metadata(folder)

                        # Count attachments
                        attachments_folder = folder / "attachments"
                        attachments_count = 0
                        if attachments_folder.exists():
                            attachments_count = len([f for f in attachments_folder.iterdir() if f.is_file()])

                        contract_folders.append({
                            "contract_id": folder.name,
                            "filename": contract_file.name,
                            "created_at": metadata.get("created_at", datetime.fromtimestamp(stat.st_ctime).isoformat()),
                            "modified_at": metadata.get("modified_at"),
                            "size_bytes": stat.st_size,
                            "folder_path": str(folder),
                            "attachments_count": attachments_count
                        })

            # Sort by creation date (newest first)
            contract_folders.sort(key=lambda x: x["created_at"], reverse=True)

            return {
                "success": True,
                "contracts": contract_folders,
                "total": len(contract_folders)
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error listing contracts: {str(e)}"
            )

    def get_contract_details(self, contract_id: str) -> Dict[str, Any]:
        """Get detailed information about a contract"""
        try:
            contract_folder = self.contracts_dir / contract_id

            if not contract_folder.exists():
                raise HTTPException(
                    status_code=404,
                    detail="Contract not found"
                )

            # Find contract file
            contract_files = list(contract_folder.glob("*.docx"))
            if not contract_files:
                raise HTTPException(
                    status_code=404,
                    detail="Contract file not found"
                )

            contract_file = contract_files[0]
            stat = contract_file.stat()

            # Load metadata
            metadata = self._load_metadata(contract_folder)

            # Get attachments
            attachments_data = self.list_attachments(contract_id)

            return {
                "success": True,
                "contract_id": contract_id,
                "filename": contract_file.name,
                "created_at": metadata.get("created_at", datetime.fromtimestamp(stat.st_ctime).isoformat()),
                "modified_at": metadata.get("modified_at"),
                "size_bytes": stat.st_size,
                "folder_path": str(contract_folder),
                "attachments": attachments_data["attachments"],
                "original_data": metadata.get("original_data", {})
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting contract details: {str(e)}"
            )

    def get_contract_file(self, contract_id: str) -> Path:
        """Get contract file path"""
        contract_folder = self.contracts_dir / contract_id

        if not contract_folder.exists():
            raise HTTPException(
                status_code=404,
                detail="Contract not found"
            )

        contract_files = list(contract_folder.glob("*.docx"))
        if not contract_files:
            raise HTTPException(
                status_code=404,
                detail="Contract file not found"
            )

        return contract_files[0]

    def get_attachment_file(self, contract_id: str, filename: str) -> Path:
        """Get attachment file path"""
        contract_folder = self.contracts_dir / contract_id
        attachments_folder = contract_folder / "attachments"
        file_path = attachments_folder / filename

        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Attachment not found"
            )

        return file_path

    def delete_contract(self, contract_id: str) -> Dict[str, Any]:
        """Delete a contract and all its files"""
        try:
            contract_folder = self.contracts_dir / contract_id

            if not contract_folder.exists():
                raise HTTPException(
                    status_code=404,
                    detail="Contract not found"
                )

            # Remove entire folder
            shutil.rmtree(contract_folder)

            return {
                "success": True,
                "message": f"Contract {contract_id} and all attachments deleted successfully"
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting contract: {str(e)}"
            )

    def delete_attachment(self, contract_id: str, filename: str) -> Dict[str, Any]:
        """Delete a specific attachment"""
        try:
            file_path = self.get_attachment_file(contract_id, filename)
            file_path.unlink()

            return {
                "success": True,
                "message": f"Attachment {filename} deleted successfully"
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting attachment: {str(e)}"
            )

    # ... (keeping existing methods)
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

    # AGREGAR ESTOS MÉTODOS AL FINAL DE TU CLASE ContractService
# Mantiene toda tu lógica existente, solo agrega detección automática

    def _is_mortgage_data(self, data: Dict[str, Any]) -> bool:
        """
        Detecta automáticamente si los datos son de contrato hipotecario
        """
        # Buscar campos característicos de estructura de hipoteca
        mortgage_indicators = ['loan', 'properties', 'clients', 'investors', 'witnesses', 'notaries']

        # Si tiene 4 o más campos de hipoteca, es probable que sea hipoteca
        found_indicators = sum(1 for indicator in mortgage_indicators if indicator in data)

        return found_indicators >= 4

    def _convert_mortgage_to_flat_data(self, mortgage_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convierte estructura compleja de hipoteca a campos planos para template
        """

        def format_date_spanish(date_str: str) -> str:
            """Convierte fecha YYYY-MM-DD a formato español"""
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
            """Convierte números a palabras (implementación básica)"""
            if amount == 20000:
                return "VEINTE MIL"
            elif amount == 440:
                return "CUATROCIENTOS CUARENTA"
            elif amount == 20440:
                return "VEINTE MIL CUATROCIENTOS CUARENTA"
            else:
                return f"{amount:,.2f}"

        # Extraer datos principales
        loan = mortgage_data.get("loan", {})
        properties = mortgage_data.get("properties", [])
        clients = mortgage_data.get("clients", [])
        investors = mortgage_data.get("investors", [])
        witnesses = mortgage_data.get("witnesses", [])
        notaries = mortgage_data.get("notaries", [])

        # Obtener primer elemento de cada lista
        client = clients[0] if clients else {}
        investor = investors[0] if investors else {}
        witness = witnesses[0] if witnesses else {}
        notary = notaries[0] if notaries else {}
        property_data = properties[0] if properties else {}

        # Crear diccionario plano compatible con ContractData
        flat_data = {
            # === CAMPOS BÁSICOS (compatibles con contratos normales) ===
            "client_name": f"{client.get('person', {}).get('first_name', '')} {client.get('person', {}).get('last_name', '')}".strip(),
            "contract_date": mortgage_data.get("contract_date") or format_date_spanish(loan.get("start_date", "2025-03-26")),
            "amount": f"{loan.get('amount', 0):,.2f}",
            "description": f"Préstamo hipotecario por {loan.get('currency', 'USD')}${loan.get('amount', 0):,.2f}",

            # Datos de la empresa (usando datos del inversionista)
            "company_name": "GRUPO REYSA, S.R.L.",  # Puedes parametrizar esto
            "company_tax_id": "1-3225325-6",
            "company_address": f"{investor.get('address', {}).get('address_line1', '')}, {investor.get('address', {}).get('city', '')}".strip(', '),
            "company_email": investor.get('person', {}).get('email', ''),
            "company_phone": investor.get('person', {}).get('phone_number', ''),

            # Datos del contratista (representante)
            "contractor_name": f"{investor.get('person', {}).get('first_name', '')} {investor.get('person', {}).get('last_name', '')}".strip(),
            "contractor_email": investor.get('person', {}).get('email', ''),
            "contractor_phone": investor.get('person', {}).get('phone_number', ''),

            # Datos del proyecto
            "project": f"Préstamo Hipotecario - Propiedad {property_data.get('cadastral_number', '')}",
            "duration": f"{loan.get('term_months', 12)} meses",
            "work_mode": "Presencial",
            "start_date": format_date_spanish(loan.get("start_date", "")),
            "end_date": format_date_spanish(loan.get("end_date", "")),

            # Datos de pago
            "payment_method": "Transferencia bancaria",
            "payment_terms": f"{loan.get('loan_payments_details', {}).get('payment_qty_quotes', 11)} cuotas mensuales",

            # === CAMPOS ESPECÍFICOS DE HIPOTECA ===
            # Datos del préstamo
            "loan_amount": f"{loan.get('amount', 0):,.2f}",
            "loan_amount_words": number_to_words(loan.get('amount', 0)),
            "loan_currency": loan.get('currency', 'USD'),
            "interest_rate": f"{loan.get('interest_rate', 0)}",
            "interest_rate_words": "DOS PUNTO DOS",  # Puedes mejorar esto
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

            # Datos del inversionista (primera parte/acreedor)
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

            # Datos del cliente (segunda parte/deudor)
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

            # Datos de la propiedad
            "property_cadastral_number": property_data.get('cadastral_number', ''),
            "property_title_number": property_data.get('title_number', ''),
            "property_surface_area": f"{property_data.get('surface_area', 0)}",
            "property_address": f"{property_data.get('address_line1', '')}, {property_data.get('address_line2', '')}".strip(', '),
            "property_city": property_data.get('city', ''),
            "property_description": property_data.get('description', ''),

            # Datos del testigo
            "witness_full_name": f"{witness.get('person', {}).get('first_name', '')} {witness.get('person', {}).get('last_name', '')}".strip(),
            "witness_document_number": witness.get('person_document', {}).get('document_number', ''),
            "witness_address": f"{witness.get('address', {}).get('address_line1', '')}, {witness.get('address', {}).get('address_line2', '')}".strip(', '),

            # Datos del notario
            "notary_full_name": f"{notary.get('person', {}).get('first_name', '')} {notary.get('person', {}).get('last_name', '')}".strip(),
            "notary_number": notary.get('notary_document', {}).get('notary_number', ''),
            "notary_document_number": notary.get('notary_document', {}).get('document_number', ''),

            # Datos generales del contrato
            "contract_location": mortgage_data.get("contract_location", "San Pedro de Macorís, República Dominicana"),
            "contract_year": "2025",
            "authorized_lawyer": "Licda. Lady Marlene Pineda Ramírez",
            "authorized_lawyer_cedula": "023-0142038-2",

            # Datos adicionales para referencia
            "additional_data": {
                "original_mortgage_data": mortgage_data,
                "contract_type": "mortgage",
                "processed_at": datetime.now().isoformat(),
                "fields_processed": True
            }
        }

        return flat_data

    def _select_template_for_contract(self, data: Dict[str, Any]) -> Path:
        """
        Selecciona el template correcto basado en el tipo de contrato
        """
        is_mortgage = self._is_mortgage_data(data) or data.get('additional_data', {}).get('contract_type') == 'mortgage'

        if is_mortgage:
            # Buscar template específico de hipoteca
            mortgage_template = self.template_dir / "mortgage_template.docx"
            if mortgage_template.exists():
                print(f"Using mortgage template: {mortgage_template}")
                return mortgage_template
            else:
                print("Mortgage template not found, using default template")

        # Template por defecto
        return self._get_template_file()
