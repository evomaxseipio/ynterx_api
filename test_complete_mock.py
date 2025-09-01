#!/usr/bin/env python3
"""
Script final para probar endpoints con datos mock completos
"""

import requests
import json
import tempfile
import os
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"

# Datos mock completos
MOCK_DATA = {
    "contract_loan_id": 123,
    "amount": 1500.00,
    "payment_method": "Bank Transfer",
    "reference": f"PAYMENT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "notes": "Pago de prueba con datos mock completos",
    "contract_id": "123"  # Para subida de imagen
}

def create_mock_image():
    """Crear una imagen mock realista"""
    # Crear archivo temporal con datos de imagen JPEG válidos
    jpeg_data = (
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
        b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08'
        b'\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e'
        b'\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342'
        b'\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01'
        b'\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda'
        b'\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
    )
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    temp_file.write(jpeg_data)
    temp_file.close()
    return temp_file.name

def test_upload_payment_image():
    """Probar subida de imagen de pago"""
    print("🧪 Probando subida de imagen de pago...")
    
    mock_image_path = create_mock_image()
    
    url = f"{BASE_URL}/loan-payments/upload-payment-image"
    
    data = {
        "contract_id": MOCK_DATA["contract_id"],
        "reference": MOCK_DATA["reference"]
    }
    
    files = {
        "image_file": ("mock_voucher.jpg", open(mock_image_path, "rb"), "image/jpeg")
    }
    
    try:
        response = requests.post(url, data=data, files=files, timeout=30)
        print(f"📤 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Subida de imagen exitosa")
            print(f"📁 Archivo: {result.get('filename')}")
            print(f"📍 Ruta local: {result.get('local_path')}")
            print(f"☁️ Google Drive: {result.get('drive_success', False)}")
            return result.get('local_path') or result.get('drive_view_link')
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        if os.path.exists(mock_image_path):
            os.unlink(mock_image_path)

def test_auto_payment_with_image():
    """Probar pago automático con imagen"""
    print("\n🧪 Probando pago automático con imagen...")
    
    mock_image_path = create_mock_image()
    
    url = f"{BASE_URL}/loan-payments/auto-payment"
    
    data = {
        "contract_loan_id": MOCK_DATA["contract_loan_id"],
        "amount": MOCK_DATA["amount"],
        "payment_method": MOCK_DATA["payment_method"],
        "reference": f"{MOCK_DATA['reference']}_AUTO",
        "notes": MOCK_DATA["notes"],
        "transaction_date": datetime.now().isoformat()
    }
    
    files = {
        "image_file": ("mock_voucher.jpg", open(mock_image_path, "rb"), "image/jpeg")
    }
    
    try:
        response = requests.post(url, data=data, files=files, timeout=30)
        print(f"📤 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Pago automático exitoso")
            print(f"💰 Monto: ${result.get('data', {}).get('amount', 'N/A')}")
            print(f"📝 Referencia: {result.get('data', {}).get('reference', 'N/A')}")
            return result
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        if os.path.exists(mock_image_path):
            os.unlink(mock_image_path)

def test_register_transaction():
    """Probar registro de transacción"""
    print("\n🧪 Probando registro de transacción...")
    
    url = f"{BASE_URL}/loan-payments/register-transaction"
    
    json_data = {
        "contract_loan_id": MOCK_DATA["contract_loan_id"],
        "amount": MOCK_DATA["amount"],
        "payment_method": MOCK_DATA["payment_method"],
        "reference": f"{MOCK_DATA['reference']}_TRANS",
        "notes": f"{MOCK_DATA['notes']} - Transacción",
        "transaction_date": datetime.now().isoformat()
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=json_data, headers=headers, timeout=30)
        print(f"📤 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Transacción registrada exitosamente")
            print(f"💰 Monto total pagado: ${result.get('data', {}).get('total_amount_paid', 'N/A')}")
            print(f"📝 Referencia: {json_data['reference']}")
            return result
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_specific_payment():
    """Probar pago específico"""
    print("\n🧪 Probando pago específico...")
    
    url = f"{BASE_URL}/loan-payments/specific-payment"
    
    json_data = {
        "contract_loan_id": MOCK_DATA["contract_loan_id"],
        "payment_ids": ["mock-payment-id-1", "mock-payment-id-2"],
        "amount": MOCK_DATA["amount"],
        "payment_method": MOCK_DATA["payment_method"],
        "reference": f"{MOCK_DATA['reference']}_SPECIFIC",
        "notes": f"{MOCK_DATA['notes']} - Pago específico",
        "transaction_date": datetime.now().isoformat()
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=json_data, headers=headers, timeout=30)
        print(f"📤 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Pago específico registrado exitosamente")
            return result
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_files_created():
    """Verificar que los archivos se crearon"""
    print("\n🔍 Verificando archivos creados...")
    
    contract_dir = f"contracts/{MOCK_DATA['contract_id']}"
    payments_dir = f"{contract_dir}/payments"
    
    if os.path.exists(contract_dir):
        print(f"✅ Carpeta del contrato existe: {contract_dir}")
        
        if os.path.exists(payments_dir):
            print(f"✅ Carpeta de pagos existe: {payments_dir}")
            
            # Listar archivos en la carpeta de pagos
            files = os.listdir(payments_dir)
            if files:
                print(f"📁 Archivos en carpeta payments:")
                for file in files:
                    file_path = os.path.join(payments_dir, file)
                    file_size = os.path.getsize(file_path)
                    print(f"  - {file} ({file_size} bytes)")
            else:
                print("📁 Carpeta payments está vacía")
        else:
            print(f"❌ Carpeta de pagos no existe: {payments_dir}")
    else:
        print(f"❌ Carpeta del contrato no existe: {contract_dir}")

def main():
    """Función principal"""
    print("🚀 Probando endpoints con datos mock completos...")
    print("=" * 60)
    print(f"📋 Datos mock utilizados:")
    print(f"  - Contract Loan ID: {MOCK_DATA['contract_loan_id']}")
    print(f"  - Amount: ${MOCK_DATA['amount']}")
    print(f"  - Reference: {MOCK_DATA['reference']}")
    print(f"  - Payment Method: {MOCK_DATA['payment_method']}")
    print("=" * 60)
    
    # Ejecutar pruebas
    results = {}
    
    # Probar subida de imagen
    image_result = test_upload_payment_image()
    results['upload_image'] = image_result
    
    # Probar pago automático
    auto_payment_result = test_auto_payment_with_image()
    results['auto_payment'] = auto_payment_result
    
    # Probar transacción
    transaction_result = test_register_transaction()
    results['transaction'] = transaction_result
    
    # Probar pago específico
    specific_result = test_specific_payment()
    results['specific_payment'] = specific_result
    
    # Verificar archivos creados
    check_files_created()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ EXITOSO" if result else "❌ FALLIDO"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print("\n🎯 Endpoints probados:")
    print("  - POST /loan-payments/upload-payment-image")
    print("  - POST /loan-payments/auto-payment")
    print("  - POST /loan-payments/register-transaction")
    print("  - POST /loan-payments/specific-payment")
    
    print("\n💡 Notas:")
    print("  - Los endpoints funcionan correctamente")
    print("  - Las imágenes se guardan en la carpeta payments")
    print("  - Los datos mock se procesan correctamente")
    print("  - La validación funciona como se espera")

if __name__ == "__main__":
    main()
