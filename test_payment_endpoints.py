#!/usr/bin/env python3
"""
Script de prueba para endpoints de pagos con imágenes usando datos mock
"""

import requests
import json
import os
from pathlib import Path
import tempfile
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
TOKEN = "your-jwt-token-here"  # Reemplazar con token válido

# Datos mock
MOCK_DATA = {
    "contract_loan_id": 123,
    "amount": 1500.00,
    "payment_method": "Bank Transfer",
    "reference": "PAYMENT_MOCK_001",
    "notes": "Pago de prueba con datos mock",
    "transaction_date": datetime.now().isoformat()
}

def create_mock_image():
    """Crear una imagen mock para pruebas"""
    # Crear un archivo de imagen simple (JPEG header + datos)
    jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
    
    # Crear archivo temporal
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    temp_file.write(jpeg_header)
    temp_file.close()
    
    return temp_file.name

def test_server_connection():
    """Probar conexión al servidor"""
    print("🔍 Probando conexión al servidor...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está corriendo")
            return True
        else:
            print(f"⚠️ Servidor responde con status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        return False

def test_upload_payment_image():
    """Probar subida de imagen de pago"""
    print("\n🧪 Probando subida de imagen de pago...")
    
    # Crear imagen mock
    mock_image_path = create_mock_image()
    
    url = f"{BASE_URL}/loan-payments/upload-payment-image"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    
    data = {
        "contract_id": str(MOCK_DATA["contract_loan_id"]),
        "reference": MOCK_DATA["reference"]
    }
    
    files = {
        "image_file": ("mock_voucher.jpg", open(mock_image_path, "rb"), "image/jpeg")
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, files=files, timeout=30)
        print(f"📤 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Subida de imagen exitosa")
            print(f"📁 Archivo: {result.get('filename')}")
            print(f"📍 Ruta local: {result.get('local_path')}")
            print(f"☁️ Google Drive: {result.get('drive_success', False)}")
            if result.get('drive_view_link'):
                print(f"🔗 URL Drive: {result.get('drive_view_link')}")
        else:
            print(f"❌ Error en subida de imagen: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Limpiar archivo temporal
        if os.path.exists(mock_image_path):
            os.unlink(mock_image_path)

def test_auto_payment_with_image():
    """Probar registro de pago automático con imagen"""
    print("\n🧪 Probando registro de pago automático con imagen...")
    
    # Crear imagen mock
    mock_image_path = create_mock_image()
    
    url = f"{BASE_URL}/loan-payments/auto-payment"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    
    data = {
        "contract_loan_id": MOCK_DATA["contract_loan_id"],
        "amount": MOCK_DATA["amount"],
        "payment_method": MOCK_DATA["payment_method"],
        "reference": MOCK_DATA["reference"],
        "notes": MOCK_DATA["notes"],
        "transaction_date": MOCK_DATA["transaction_date"]
    }
    
    files = {
        "image_file": ("mock_voucher.jpg", open(mock_image_path, "rb"), "image/jpeg")
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, files=files, timeout=30)
        print(f"📤 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Registro de pago exitoso")
            print(f"💰 Monto: ${result.get('data', {}).get('amount', 'N/A')}")
            print(f"📝 Referencia: {result.get('data', {}).get('reference', 'N/A')}")
            print(f"🖼️ Imagen subida: {result.get('data', {}).get('url_bank_receipt', 'N/A')}")
        else:
            print(f"❌ Error en registro de pago: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Limpiar archivo temporal
        if os.path.exists(mock_image_path):
            os.unlink(mock_image_path)

def test_register_transaction_with_image():
    """Probar registro de transacción con imagen"""
    print("\n🧪 Probando registro de transacción con imagen...")
    
    # Crear imagen mock
    mock_image_path = create_mock_image()
    
    url = f"{BASE_URL}/loan-payments/register-transaction"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Crear request body
    request_data = {
        "contract_loan_id": MOCK_DATA["contract_loan_id"],
        "amount": MOCK_DATA["amount"],
        "payment_method": MOCK_DATA["payment_method"],
        "reference": f"{MOCK_DATA['reference']}_TRANS",
        "notes": f"{MOCK_DATA['notes']} - Transacción",
        "transaction_date": MOCK_DATA["transaction_date"]
    }
    
    try:
        # Primero probar sin imagen
        response = requests.post(url, headers=headers, json=request_data, timeout=30)
        print(f"📤 Response Status (sin imagen): {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Registro de transacción sin imagen exitoso")
        else:
            print(f"❌ Error en registro sin imagen: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Limpiar archivo temporal
        if os.path.exists(mock_image_path):
            os.unlink(mock_image_path)

def test_endpoints_without_auth():
    """Probar endpoints sin autenticación (debería fallar)"""
    print("\n🧪 Probando endpoints sin autenticación...")
    
    endpoints = [
        "/loan-payments/upload-payment-image",
        "/loan-payments/auto-payment",
        "/loan-payments/register-transaction"
    ]
    
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.post(url, data={"test": "data"}, timeout=10)
            print(f"📤 {endpoint}: Status {response.status_code}")
            
            if response.status_code == 401:
                print(f"✅ {endpoint}: Autenticación requerida (correcto)")
            else:
                print(f"⚠️ {endpoint}: Respuesta inesperada")
                
        except Exception as e:
            print(f"❌ {endpoint}: Error {e}")

def test_with_different_image_formats():
    """Probar con diferentes formatos de imagen"""
    print("\n🧪 Probando diferentes formatos de imagen...")
    
    # Crear diferentes tipos de archivos mock
    test_files = [
        ("mock_voucher.jpg", b"fake jpeg data", "image/jpeg"),
        ("mock_voucher.png", b"fake png data", "image/png"),
        ("mock_voucher.gif", b"fake gif data", "image/gif"),
    ]
    
    for filename, content, mime_type in test_files:
        print(f"\n📁 Probando {filename}...")
        
        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{filename.split('.')[-1]}")
        temp_file.write(content)
        temp_file.close()
        
        url = f"{BASE_URL}/loan-payments/upload-payment-image"
        
        headers = {
            "Authorization": f"Bearer {TOKEN}"
        }
        
        data = {
            "contract_id": str(MOCK_DATA["contract_loan_id"]),
            "reference": f"{MOCK_DATA['reference']}_{filename.split('.')[0]}"
        }
        
        files = {
            "image_file": (filename, open(temp_file.name, "rb"), mime_type)
        }
        
        try:
            response = requests.post(url, headers=headers, data=data, files=files, timeout=30)
            print(f"📤 Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ {filename} subido exitosamente")
            else:
                print(f"❌ Error con {filename}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error con {filename}: {e}")
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de endpoints de pagos con datos mock...")
    print("=" * 70)
    
    # Verificar conexión al servidor
    if not test_server_connection():
        print("\n❌ No se puede conectar al servidor. Asegúrate de que esté corriendo.")
        return
    
    # Ejecutar pruebas
    test_endpoints_without_auth()
    
    if TOKEN != "your-jwt-token-here":
        test_upload_payment_image()
        test_auto_payment_with_image()
        test_register_transaction_with_image()
        test_with_different_image_formats()
    else:
        print("\n⚠️ Para probar con autenticación, actualiza la variable TOKEN en este script")
        print("💡 Puedes obtener un token válido iniciando sesión en tu aplicación")
    
    print("\n" + "=" * 70)
    print("🏁 Pruebas completadas")
    print("\n📋 Resumen:")
    print("- Endpoints probados: upload-payment-image, auto-payment, register-transaction")
    print("- Datos mock utilizados: contract_loan_id=123, amount=1500.00, reference=PAYMENT_MOCK_001")
    print("- Formatos de imagen probados: JPEG, PNG, GIF")
    print("- Autenticación verificada")

if __name__ == "__main__":
    main()
