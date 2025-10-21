#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración de Mailtrap
"""
import os
import sys
import asyncio
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.email_services import send_email, load_email_template
from app.config import settings

def test_mailtrap_configuration():
    """Prueba la configuración de Mailtrap"""
    print("🧪 Probando configuración de Mailtrap...")

    # Verificar variables de entorno
    required_vars = [
        "MAILTRAP_API_TOKEN",
        "SMTP_FROM_EMAIL"
    ]

    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var, None):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Variables de entorno faltantes: {missing_vars}")
        print("Por favor, configura las siguientes variables en tu archivo .env:")
        for var in missing_vars:
            print(f"   {var}=tu_valor_aqui")
        return False

    print("✅ Variables de entorno configuradas correctamente")
    print(f"   MAILTRAP_API_TOKEN: {settings.MAILTRAP_API_TOKEN[:10]}...")
    print(f"   SMTP_FROM_EMAIL: {settings.SMTP_FROM_EMAIL}")

    return True

def test_email_template():
    """Prueba la carga del template de email"""
    print("\n📧 Probando template de email...")

    try:
        client_name = "Juan Pérez"
        contract_url = "https://drive.google.com/test-contract"

        html_content = load_email_template(client_name, contract_url)

        if "{{client_name}}" in html_content or "{{contract_folder_url}}" in html_content:
            print("❌ Template no se procesó correctamente")
            return False

        if client_name in html_content and contract_url in html_content:
            print("✅ Template procesado correctamente")
            return True
        else:
            print("❌ Template no contiene los datos esperados")
            return False

    except Exception as e:
        print(f"❌ Error cargando template: {e}")
        return False

def test_email_sending():
    """Prueba el envío de email"""
    print("\n📤 Probando envío de email...")

    try:
        # Email de prueba (puedes cambiarlo)
        test_email = "test@example.com"

        subject = "🧪 Prueba de Mailtrap - YnterX"
        text = "Este es un email de prueba para verificar la configuración de Mailtrap."
        html_body = load_email_template("Cliente de Prueba", "https://drive.google.com/test")

        success = send_email(
            to_email=test_email,
            subject=subject,
            text=text,
            html_body=html_body,
            category="Test Email"
        )

        if success:
            print("✅ Email enviado correctamente")
            print(f"   Revisa tu inbox de Mailtrap para el email: {test_email}")
            return True
        else:
            print("❌ Error enviando email")
            return False

    except Exception as e:
        print(f"❌ Error en prueba de envío: {e}")
        return False

async def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas de Mailtrap...\n")

    # Prueba 1: Configuración
    config_ok = test_mailtrap_configuration()

    # Prueba 2: Template
    template_ok = test_email_template()

    # Prueba 3: Envío (solo si las anteriores pasaron)
    if config_ok and template_ok:
        send_ok = test_email_sending()
    else:
        send_ok = False
        print("\n⏭️  Saltando prueba de envío debido a errores anteriores")

    # Resumen
    print("\n" + "="*50)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*50)
    print(f"✅ Configuración: {'PASÓ' if config_ok else 'FALLÓ'}")
    print(f"✅ Template: {'PASÓ' if template_ok else 'FALLÓ'}")
    print(f"✅ Envío: {'PASÓ' if send_ok else 'FALLÓ'}")

    if config_ok and template_ok and send_ok:
        print("\n🎉 ¡Todas las pruebas pasaron! Mailtrap está configurado correctamente.")
        print("\n📝 Para probar desde la API:")
        print("   GET /email/test-mailtrap?to=tu_email@ejemplo.com")
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa la configuración.")

    return config_ok and template_ok and send_ok

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
