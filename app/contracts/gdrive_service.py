# gdrive_service.py
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import HTTPException

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class GoogleDriveService:
    """Servicio para interactuar con Google Drive"""

    def __init__(self):
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google Drive dependencies not installed. Run: pip install google-api-python-client google-auth")

        self.credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
        self.main_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

        if not self.credentials_path:
            raise ValueError("GOOGLE_CREDENTIALS_PATH environment variable not set")

        if not Path(self.credentials_path).exists():
            raise FileNotFoundError(f"Google credentials file not found: {self.credentials_path}")

        self._authenticate()

        # Crear o encontrar carpeta principal
        if not self.main_folder_id:
            self.main_folder_id = self._create_main_folder()

    def _authenticate(self):
        """Autenticar con Google Drive API"""
        try:
            scopes = ['https://www.googleapis.com/auth/drive']
            credentials = Credentials.from_service_account_file(
                self.credentials_path, scopes=scopes
            )
            self.service = build('drive', 'v3', credentials=credentials)
        except Exception as e:
            raise HTTPException(500, f"Error authenticating with Google Drive: {str(e)}")

    def _create_main_folder(self) -> str:
        """Crear carpeta principal 'Ynterx_Contracts'"""
        folder_metadata = {
            'name': 'Ynterx_Contracts',
            'mimeType': 'application/vnd.google-apps.folder'
        }

        try:
            folder = self.service.files().create(body=folder_metadata, fields='id').execute()
            folder_id = folder.get('id')

            # Hacer la carpeta pública para lectura
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            self.service.permissions().create(
                fileId=folder_id,
                body=permission
            ).execute()

            return folder_id
        except Exception as e:
            raise HTTPException(500, f"Error creating main folder: {str(e)}")

    def _create_contract_folder(self, contract_id: str) -> str:
        """Crear carpeta individual para contrato"""
        folder_metadata = {
            'name': contract_id,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [self.main_folder_id]
        }

        try:
            folder = self.service.files().create(body=folder_metadata, fields='id').execute()
            return folder.get('id')
        except Exception as e:
            raise HTTPException(500, f"Error creating contract folder: {str(e)}")

    def _upload_file(self, file_path: Path, parent_folder_id: str, file_name: Optional[str] = None) -> Dict[str, str]:
        """Subir archivo a Google Drive"""
        if not file_name:
            file_name = file_path.name

        file_metadata = {
            'name': file_name,
            'parents': [parent_folder_id]
        }

        # Determinar tipo MIME
        if file_path.suffix.lower() == '.docx':
            mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif file_path.suffix.lower() == '.pdf':
            mime_type = 'application/pdf'
        elif file_path.suffix.lower() in ['.jpg', '.jpeg']:
            mime_type = 'image/jpeg'
        elif file_path.suffix.lower() == '.png':
            mime_type = 'image/png'
        else:
            mime_type = 'application/octet-stream'

        media = MediaFileUpload(str(file_path), mimetype=mime_type)

        try:
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink,webContentLink'
            ).execute()

            return {
                'file_id': file.get('id'),
                'web_view_link': file.get('webViewLink'),
                'download_link': file.get('webContentLink')
            }
        except Exception as e:
            raise HTTPException(500, f"Error uploading file to Drive: {str(e)}")

    def _upload_metadata(self, metadata: Dict[str, Any], folder_id: str) -> str:
        """Subir metadatos como archivo JSON"""
        # Crear archivo temporal
        temp_file = Path("/tmp/metadata.json")
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)

        try:
            result = self._upload_file(temp_file, folder_id, "metadata.json")
            temp_file.unlink()  # Limpiar archivo temporal
            return result['file_id']
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            raise e

    async def upload_contract(self, contract_id: str, contract_path: Path, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Subir contrato completo a Google Drive"""
        try:
            # Crear carpeta del contrato
            contract_folder_id = self._create_contract_folder(contract_id)

            # Subir archivo del contrato
            contract_result = self._upload_file(contract_path, contract_folder_id)

            # Subir metadatos
            metadata_file_id = self._upload_metadata(metadata, contract_folder_id)

            # Crear enlace público a la carpeta
            folder_link = f"https://drive.google.com/drive/folders/{contract_folder_id}"

            return {
                "drive_success": True,
                "drive_folder_id": contract_folder_id,
                "drive_file_id": contract_result['file_id'],
                "drive_link": folder_link,
                "drive_view_link": contract_result['web_view_link'],
                "metadata_file_id": metadata_file_id
            }

        except Exception as e:
            return {
                "drive_success": False,
                "drive_error": str(e)
            }

    async def upload_attachment(self, contract_id: str, file_path: Path) -> Dict[str, Any]:
        """Subir archivo adjunto a carpeta existente"""
        # Buscar carpeta del contrato
        try:
            query = f"name='{contract_id}' and mimeType='application/vnd.google-apps.folder' and parents='{self.main_folder_id}'"
            results = self.service.files().list(q=query, fields='files(id)').execute()
            folders = results.get('files', [])

            if not folders:
                raise HTTPException(404, f"Contract folder {contract_id} not found in Drive")

            folder_id = folders[0]['id']

            # Subir archivo
            result = self._upload_file(file_path, folder_id)

            return {
                "success": True,
                "drive_file_id": result['file_id'],
                "drive_link": result['web_view_link']
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def test_connection(self) -> Dict[str, Any]:
        """Probar conexión con Google Drive"""
        try:
            # Test básico: listar archivos en la carpeta principal
            results = self.service.files().list(
                q=f"parents='{self.main_folder_id}'",
                pageSize=1,
                fields="files(id, name)"
            ).execute()

            return {
                "success": True,
                "message": "Google Drive connection successful",
                "main_folder_id": self.main_folder_id,
                "files_in_main_folder": len(results.get('files', []))
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Google Drive connection failed: {str(e)}"
            }

    def get_folder_link(self, contract_id: str) -> Optional[str]:
        """Obtener enlace público de carpeta de contrato"""
        try:
            query = f"name='{contract_id}' and mimeType='application/vnd.google-apps.folder' and parents='{self.main_folder_id}'"
            results = self.service.files().list(q=query, fields='files(id)').execute()
            folders = results.get('files', [])

            if folders:
                folder_id = folders[0]['id']
                return f"https://drive.google.com/drive/folders/{folder_id}"

            return None

        except Exception:
            return None
