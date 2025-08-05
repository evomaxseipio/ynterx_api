# app/routes/email_router.py
from fastapi import APIRouter, Query
from app.utils.email_services import send_email, load_email_template
import asyncio

router = APIRouter(prefix="/email", tags=["email"])

@router.get("/test")
def send_contract_email_test(
    to: str = Query(..., description="Correo de destino"),
    client_name: str = Query(..., description="Nombre del cliente"),
    contract_url: str = Query(..., description="Enlace a la carpeta del contrato"),
):
    subject = "📄 Su contrato está disponible"
    print(client_name, contract_url)
    html = load_email_template(client_name, contract_url)
    success = send_email(
        to_email=to,
        subject=subject,
        html_body=html,
    )
    return {"success": success, "to": to, "client_name": client_name}

@router.get("/test-mailtrap")
async def test_mailtrap_email(
    to: str = Query(..., description="Correo de destino para prueba"),
    client_name: str = Query(default="Cliente de Prueba", description="Nombre del cliente"),
    contract_url: str = Query(default="https://drive.google.com/test", description="Enlace de prueba"),
):
    """
    Endpoint de prueba para verificar la configuración de Mailtrap
    """
    try:
        subject = "🧪 Prueba de Mailtrap - Contrato Disponible"

        # Usar template HTML
        html_body = load_email_template(client_name, contract_url)

        # Enviar email usando Mailtrap
        success = await asyncio.to_thread(
            send_email,
            to_email=to,
            subject=subject,
            text="Este es un email de prueba para verificar la configuración de Mailtrap.",
            html_body=html_body,
            category="Test Email"
        )

        return {
            "success": success,
            "message": "Email de prueba enviado correctamente" if success else "Error enviando email de prueba",
            "to": to,
            "client_name": client_name,
            "contract_url": contract_url,
            "provider": "Mailtrap"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error en prueba de email: {str(e)}",
            "to": to,
            "error": str(e)
        }
