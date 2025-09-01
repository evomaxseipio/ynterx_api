#!/usr/bin/env python3
"""
Script de prueba para los endpoints de imágenes de pagos
"""

import requests
import json
from pathlib import Path

# Configuración
BASE_URL = "http://localhost:8000"
TOKEN = "your-jwt-token-here"  # Reemplazar con token válido

def test_upload_payment_image():
    """Probar subida de imagen de pago"""
    print("🧪 Probando subida de imagen de pago...")
    
    # Crear imagen de prueba
    test_image_path = Path("test_voucher.jpg")
    if not test_image_path.exists():
        print("❌ Archivo test_voucher.jpg no encontrado. Creando archivo de prueba...")
        # Crear un archivo de prueba simple
        with open(test_image_path, "wb") as f:
            f.write(b"fake image data")
    
    url = f"{BASE_URL}/loan-payments/upload-payment-image"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    
    data = {
        "contract_id": "TEST_CONTRACT_123",
        "reference": "PAYMENT_REF_456"
    }
    
    files = {
        "image_file": ("test_voucher.jpg", open(test_image_path, "rb"), "image/jpeg")
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, files=files)
        print(f"📤 Response Status: {response.status_code}")
        print(f"📤 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Subida de imagen exitosa")
        else:
            print("❌ Error en subida de imagen")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_register_payment_with_image():
    """Probar registro de pago con imagen usando endpoint existente"""
    print("\n🧪 Probando registro de pago con imagen usando endpoint existente...")
    
    # Crear imagen de prueba
    test_image_path = Path("test_voucher.jpg")
    if not test_image_path.exists():
        print("❌ Archivo test_voucher.jpg no encontrado. Creando archivo de prueba...")
        # Crear un archivo de prueba simple
        with open(test_image_path, "wb") as f:
            f.write(b"fake image data")
    
    url = f"{BASE_URL}/loan-payments/auto-payment"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    
    data = {
        "contract_loan_id": "123",
        "amount": "1000.00",
        "payment_method": "Bank Transfer",
        "reference": "PAYMENT_REF_789",
        "notes": "Pago de prueba con imagen"
    }
    
    files = {
        "image_file": ("test_voucher.jpg", open(test_image_path, "rb"), "image/jpeg")
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, files=files)
        print(f"📤 Response Status: {response.status_code}")
        print(f"📤 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Registro de pago con imagen exitoso")
        else:
            print("❌ Error en registro de pago")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_endpoints_without_auth():
    """Probar endpoints sin autenticación (debería fallar)"""
    print("\n🧪 Probando endpoints sin autenticación...")
    
    endpoints = [
        "/loan-payments/upload-payment-image",
        "/loan-payments/auto-payment"
    ]
    
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.post(url, data={"test": "data"})
            print(f"📤 {endpoint}: Status {response.status_code}")
            
            if response.status_code == 401:
                print(f"✅ {endpoint}: Autenticación requerida (correcto)")
            else:
                print(f"⚠️  {endpoint}: Respuesta inesperada")
                
        except Exception as e:
            print(f"❌ {endpoint}: Error {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de endpoints de imágenes de pagos...")
    print("=" * 60)
    
    # Verificar que el servidor esté corriendo
    try:
        health_response = requests.get(f"{BASE_URL}/docs")
        if health_response.status_code == 200:
            print("✅ Servidor está corriendo")
        else:
            print("⚠️  Servidor puede no estar corriendo")
    except:
        print("❌ No se puede conectar al servidor. Asegúrate de que esté corriendo en http://localhost:8000")
        exit(1)
    
    # Ejecutar pruebas
    test_endpoints_without_auth()
    
    if TOKEN != "your-jwt-token-here":
        test_upload_payment_image()
        test_register_payment_with_image()
    else:
        print("\n⚠️  Para probar con autenticación, actualiza la variable TOKEN en este script")
    
    print("\n" + "=" * 60)
    print("🏁 Pruebas completadas")
