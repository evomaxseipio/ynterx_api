#!/usr/bin/env python3
"""
Script de prueba para el endpoint de auto-payment con generación de recibo
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
ENDPOINT = "/loan-payments/auto-payment"

# Datos de prueba basados en tu consulta SQL
test_data = {
    "contract_loan_id": 8,
    "amount": 1000.0,
    "payment_method": "Cash",
    "reference": "TRF333",
    "transaction_date": "2025-08-24T00:00:00",
    "notes": "Prueba de auto-payment con recibo",
    "url_bank_receipt": "https://drive.google.com/file/d/1oKanDqy6hdKAbiK-zss4sOUibgxY_IxB/view?usp=drivesdk",
    "url_payment_receipt": None
}

def test_auto_payment():
    """Prueba el endpoint de auto-payment"""
    
    print("🧪 PROBANDO AUTO-PAYMENT CON GENERACIÓN DE RECIBO")
    print("=" * 60)
    print(f"URL: {BASE_URL}{ENDPOINT}")
    print(f"Datos: {json.dumps(test_data, indent=2)}")
    print("-" * 60)
    
    try:
        # Hacer la petición
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ÉXITO - Respuesta recibida:")
            print(json.dumps(result, indent=2))
            
            # Verificar si se generó el recibo
            if "receipt" in result:
                receipt = result["receipt"]
                print("\n🎉 RECIBO GENERADO EXITOSAMENTE:")
                print(f"  - Receipt ID: {receipt.get('receipt_id')}")
                print(f"  - Filename: {receipt.get('filename')}")
                print(f"  - Drive Link: {receipt.get('drive_link')}")
                print(f"  - Image Base64: {receipt.get('image_base64', '')[:50]}...")
                
                # Guardar la imagen si se generó
                if receipt.get('image_base64'):
                    import base64
                    image_data = receipt['image_base64'].replace('data:image/png;base64,', '')
                    with open(f"test_receipt_{receipt['receipt_id']}.png", "wb") as f:
                        f.write(base64.b64decode(image_data))
                    print(f"  - Imagen guardada como: test_receipt_{receipt['receipt_id']}.png")
            else:
                print("⚠️  No se generó recibo en la respuesta")
                
        else:
            print("❌ ERROR - Respuesta del servidor:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar al servidor")
        print("Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_auto_payment()
