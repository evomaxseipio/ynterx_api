#!/usr/bin/env python3
"""
Script de prueba para el endpoint /loan-payments/register-payment
"""

import requests
from pathlib import Path
from PIL import Image, ImageDraw
import os

# Configuración
BASE_URL = "http://localhost:8000"
CONTRACT_LOAN_ID = 1  # Cambia esto según tus datos

def create_test_image(filename: str):
    """Crear una imagen PNG simple para pruebas"""
    img = Image.new('RGB', (200, 100), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((10, 40), "TEST VOUCHER", fill='black')
    img.save(filename, 'PNG')
    print(f"📷 Imagen de prueba creada: {filename}")

def test_register_payment_with_image():
    """Probar el registro de pago con imagen"""

    print("🚀 Iniciando prueba de registro de pago con imagen...\n")

    # Crear imagen de prueba
    test_image_path = "test_voucher.png"
    create_test_image(test_image_path)

    try:
        url = f"{BASE_URL}/loan-payments/register-payment"

        # Datos del formulario (todos como form-data)
        data = {
            'contract_loan_id': CONTRACT_LOAN_ID,
            'amount': 1000.0,
            'payment_method': 'Transfer',
            'reference': 'TEST_REF_001',
            'notes': 'Pago de prueba con imagen'
        }

        # Archivo de imagen
        with open(test_image_path, 'rb') as f:
            files = {
                'image_file': ('voucher.png', f, 'image/png')
            }

            print(f"📤 Enviando petición a: {url}")
            print(f"📋 Datos: {data}")
            print(f"🖼️  Archivo: {test_image_path}\n")

            response = requests.post(url, data=data, files=files)

        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response:\n{response.json()}\n")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Pago registrado exitosamente!")
                if result.get('voucher_url'):
                    print(f"   - Voucher URL: {result.get('voucher_url')}")
                if result.get('voucher_filename'):
                    print(f"   - Filename: {result.get('voucher_filename')}")
            else:
                print(f"❌ Error: {result.get('message')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Limpiar archivo de prueba
        if os.path.exists(test_image_path):
            os.unlink(test_image_path)
            print(f"\n🧹 Archivo de prueba eliminado")

def test_register_payment_without_image():
    """Probar el registro de pago SIN imagen"""

    print("\n🚀 Iniciando prueba de registro de pago SIN imagen...\n")

    try:
        url = f"{BASE_URL}/loan-payments/register-payment"

        # Datos del formulario (todos como form-data)
        data = {
            'contract_loan_id': CONTRACT_LOAN_ID,
            'amount': 500.0,
            'payment_method': 'Cash',
            'reference': 'TEST_REF_002',
            'notes': 'Pago de prueba sin imagen'
        }

        print(f"📤 Enviando petición a: {url}")
        print(f"📋 Datos: {data}\n")

        response = requests.post(url, data=data)

        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response:\n{response.json()}\n")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Pago registrado exitosamente!")
            else:
                print(f"❌ Error: {result.get('message')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBAS DE REGISTRO DE PAGO")
    print("=" * 60)

    # Prueba con imagen
    test_register_payment_with_image()

    print("\n" + "=" * 60 + "\n")

    # Prueba sin imagen
    test_register_payment_without_image()

    print("\n" + "=" * 60)
    print("PRUEBAS COMPLETADAS")
    print("=" * 60)
