from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from fastapi import HTTPException
from docxtpl import DocxTemplate
import os
import json

class ContractService:
    """Service class for handling contract operations"""

    def __init__(self):
        # Set paths relative to the project root
        self.base_dir = Path(__file__).parent.parent  # Go up to project root
        self.template_dir = self.base_dir / "templates"
        self.contract_dir = self.base_dir / "generated_contracts"
        self._ensure_directories()

    def _ensure_directories(self):
        """Create directories if they don't exist"""
        self.template_dir.mkdir(exist_ok=True)
        self.contract_dir.mkdir(exist_ok=True)

    def _get_template_file(self) -> Path:
        """Find the first .docx file in the templates folder"""
        template_files = list(self.template_dir.glob("*.docx"))
        if not template_files:
            raise HTTPException(
                status_code=404,
                detail="No .docx template found in templates folder"
            )
        return template_files[0]

    def _generate_filename(self) -> str:
        """Generate unique filename with date and time"""
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H-%M-%S")
        return f"contract_{date}_{time}.docx"

    def _validate_filename(self, filename: str) -> bool:
        """Validate filename for security"""
        return (
            filename.endswith('.docx') and
            '..' not in filename and
            '/' not in filename and
            '\\' not in filename
        )

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

    def generate_contract(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contract from template with provided data"""
        try:
            # Get template
            template_path = self._get_template_file()

            # Print debug info
            print(f"Template path: {template_path}")
            print(f"Data received: {json.dumps(data, indent=2)}")

            # Load template
            doc = DocxTemplate(template_path)

            # Clean data to avoid template issues
            cleaned_data = self._clean_data_for_template(data)
            print(f"Cleaned data: {json.dumps(cleaned_data, indent=2)}")

            # Render template with data
            try:
                doc.render(cleaned_data)
            except Exception as e:
                print(f"Template rendering error: {str(e)}")
                print(f"Error type: {type(e).__name__}")

                # Try with simpler data structure for debugging
                simple_data = {
                    "client_name": data.get("client_name", "Test Client"),
                    "contract_date": data.get("contract_date", "2025-06-24"),
                    "amount": data.get("amount", "1000"),
                    "description": data.get("description", "Test Service")
                }

                try:
                    # Test with simple data
                    doc = DocxTemplate(template_path)  # Reload template
                    doc.render(simple_data)
                    print("Simple data rendering successful - issue is with complex nested data")
                except Exception as simple_error:
                    print(f"Simple data also failed: {str(simple_error)}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Template syntax error. Please check your Word template format. Error: {str(simple_error)}"
                    )

                raise HTTPException(
                    status_code=400,
                    detail=f"Error processing template with your data. Try using simpler field names without special characters. Error: {str(e)}"
                )

            # Generate filename and save
            filename = self._generate_filename()
            output_path = self.contract_dir / filename
            doc.save(output_path)

            return {
                "success": True,
                "message": "Contract generated successfully",
                "filename": filename,
                "path": str(output_path),
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

    def list_contracts(self) -> Dict[str, Any]:
        """List all generated contracts"""
        try:
            contract_files = []
            for file in self.contract_dir.glob("*.docx"):
                stat = file.stat()
                contract_files.append({
                    "filename": file.name,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "size_bytes": stat.st_size
                })

            # Sort by creation date (newest first)
            contract_files.sort(key=lambda x: x["created_at"], reverse=True)

            return {
                "success": True,
                "contracts": contract_files,
                "total": len(contract_files)
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error listing contracts: {str(e)}"
            )

    def get_contract_file(self, filename: str) -> Path:
        """Get contract file path and validate it exists"""
        if not self._validate_filename(filename):
            raise HTTPException(
                status_code=400,
                detail="Invalid filename"
            )

        file_path = self.contract_dir / filename

        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )

        return file_path

    def delete_contract(self, filename: str) -> Dict[str, Any]:
        """Delete a specific contract"""
        try:
            file_path = self.get_contract_file(filename)
            file_path.unlink()

            return {
                "success": True,
                "message": f"Contract {filename} deleted successfully"
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting file: {str(e)}"
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
            "note": "Use simple field names in template: {{client_name}}, {{contract_date}}, {{company_name}}, etc. Avoid nested objects for now."
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
