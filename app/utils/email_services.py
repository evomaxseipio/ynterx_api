import os
import logging
import requests
from typing import List
from pathlib import Path
from app.config import settings

log = logging.getLogger(__name__)

MAILTRAP_SEND_URL = "https://send.api.mailtrap.io/api/send"
TEMPLATE_PATH = Path(__file__).parent / "templates" / "contract_email_template.html"


def load_email_template(client_name: str, contract_folder_url: str) -> str:
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()
        html = html.replace("{{client_name}}", client_name)
        html = html.replace("{{contract_folder_url}}", contract_folder_url)
        return html


def send_email(
    to_email: str,
    subject: str,
    text: str = "",
    html_body: str = "",
    category: str = "Contract Notification"
) -> bool:
    # Usar Mailtrap para notificaciones de contratos
    try:
        payload = {
            "from": {
                "email": settings.SMTP_FROM_EMAIL,
                "name": "YnterX Notificaciones"
            },
            "to": [{"email": to_email}],
            "subject": subject,
            "text": text or "Contrato disponible para revisión.",
            "html": html_body,
            "category": category
        }

        headers = {
            "Authorization": f"Bearer {settings.MAILTRAP_API_TOKEN}",
            "Content-Type": "application/json"
        }

        log.info(f"Enviando correo vía Mailtrap API a: {to_email}")
        log.debug(f"Payload: {payload}")
        log.debug(f"Headers: {headers}")

        response = requests.post(MAILTRAP_SEND_URL, json=payload, headers=headers)

        # Log the response for debugging
        log.info(f"Mailtrap API Response Status: {response.status_code}")
        log.info(f"Mailtrap API Response: {response.text}")

        response.raise_for_status()

        log.info(f"Correo enviado correctamente vía Mailtrap API a: {to_email}")
        return True

    except requests.exceptions.HTTPError as e:
        log.error(f"Error HTTP al enviar correo con Mailtrap API: {e}")
        log.error(f"Response status: {e.response.status_code}")
        log.error(f"Response text: {e.response.text}")
        return False
    except Exception as e:
        log.error(f"Error al enviar correo con Mailtrap API: {e}")
        return False
