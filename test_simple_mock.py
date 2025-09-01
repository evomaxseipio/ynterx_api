#!/usr/bin/env python3
"""
Script simple para probar endpoints con datos mock
"""

import requests
import json
import tempfile
import os

# Configuración
BASE_URL = "http://localhost:8000"

def create_simple_mock_image():
    """Crear una imagen mock simple"""
    # Crear archivo temporal con datos fake
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    temp_file.write(b"fake image data for testing")
    temp_file.close()
    return temp_file.name

def test_upload_endpoint():
    """Probar endpoint de subida de imagen"""
    print("🧪 Probando endpoint de subida de imagen...")
    
    # Crear imagen mock
    mock_image_path = create_simple_mock_image()
    
    url = f"{BASE_URL}/loan-payments/upload-payment-image"
    
    data = {
        "contract_id": "123",
        "reference": "TEST_PAYMENT_001"
    }
    
    files = {
        "image_file": ("test_voucher.jpg", open(mock_image_path, "rb"), "image/jpeg")
    }
    
    try:
        response = requests.post(url, data=data, files=files, timeout=10)
        print(f"📤 Status: {response.status_code}")
        print(f"📤 Response: {response.text[:200]}...")  # Primeros 200 caracteres
        
        if response.status_code == 200:
            print("✅ Subida exitosa")
        elif response.status_code == 401:
            print("✅ Autenticación requerida (correcto)")
        elif response.status_code == 422:
            print("✅ Validación funcionando (correcto)")
        else:
            print(f"⚠️ Respuesta inesperada: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Limpiar archivo temporal
        if os.path.exists(mock_image_path):
            os.unlink(mock_image_path)

def test_auto_payment_endpoint():
    """Probar endpoint de pago automático"""
    print("\n🧪 Probando endpoint de pago automático...")
    
    # Crear imagen mock
    mock_image_path = create_simple_mock_image()
    
    url = f"{BASE_URL}/loan-payments/auto-payment"
    
    data = {
        "contract_loan_id": "123",
        "amount": "1500.00",
        "payment_method": "Bank Transfer",
        "reference": "TEST_PAYMENT_002",
        "notes": "Pago de prueba con datos mock"
    }
    
    files = {
        "image_file": ("test_voucher.jpg", open(mock_image_path, "rb"), "image/jpeg")
    }
    
    try:
        response = requests.post(url, data=data, files=files, timeout=10)
        print(f"📤 Status: {response.status_code}")
        print(f"📤 Response: {response.text[:200]}...")  # Primeros 200 caracteres
        
        if response.status_code == 200:
            print("✅ Pago registrado exitosamente")
        elif response.status_code == 401:
            print("✅ Autenticación requerida (correcto)")
        elif response.status_code == 422:
            print("✅ Validación funcionando (correcto)")
        else:
            print(f"⚠️ Respuesta inesperada: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Limpiar archivo temporal
        if os.path.exists(mock_image_path):
            os.unlink(mock_image_path)

def test_register_transaction_endpoint():
    """Probar endpoint de registro de transacción"""
    print("\n🧪 Probando endpoint de registro de transacción...")
    
    url = f"{BASE_URL}/loan-payments/register-transaction"
    
    # Datos JSON para el endpoint
    json_data = {
        "contract_loan_id": 123,
        "amount": 1500.00,
        "payment_method": "Bank Transfer",
        "reference": "TEST_PAYMENT_003",
        "notes": "Transacción de prueba con datos mock"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=json_data, headers=headers, timeout=10)
        print(f"📤 Status: {response.status_code}")
        print(f"📤 Response: {response.text[:200]}...")  # Primeros 200 caracteres
        
        if response.status_code == 200:
            print("✅ Transacción registrada exitosamente")
        elif response.status_code == 401:
            print("✅ Autenticación requerida (correcto)")
        elif response.status_code == 422:
            print("✅ Validación funcionando (correcto)")
        else:
            print(f"⚠️ Respuesta inesperada: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_server_health():
    """Probar salud del servidor"""
    print("🔍 Probando salud del servidor...")
    
    try:
        # Probar endpoint de documentación
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print(f"📤 /docs Status: {response.status_code}")
        
        # Probar endpoint de OpenAPI
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        print(f"📤 /openapi.json Status: {response.status_code}")
        
        if response.status_code == 200:
            openapi_data = response.json()
            paths = openapi_data.get('paths', {})
            
            # Verificar que nuestros endpoints estén en la documentación
            payment_endpoints = [
                '/loan-payments/upload-payment-image',
                '/loan-payments/auto-payment',
                '/loan-payments/register-transaction'
            ]
            
            print("\n📋 Endpoints disponibles:")
            for endpoint in payment_endpoints:
                if endpoint in paths:
                    print(f"✅ {endpoint}")
                else:
                    print(f"❌ {endpoint} (no encontrado)")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🚀 Probando endpoints con datos mock...")
    print("=" * 50)
    
    # Probar salud del servidor
    test_server_health()
    
    # Probar endpoints
    test_upload_endpoint()
    test_auto_payment_endpoint()
    test_register_transaction_endpoint()
    
    print("\n" + "=" * 50)
    print("🏁 Pruebas completadas")
    print("\n💡 Notas:")
    print("- Status 401: Autenticación requerida (normal)")
    print("- Status 422: Validación de datos (normal)")
    print("- Status 200: Operación exitosa (requiere token válido)")

if __name__ == "__main__":
    main()
