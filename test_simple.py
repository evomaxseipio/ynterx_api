#!/usr/bin/env python3
import requests
import json

# Datos de prueba
test_data = {
    "contract_loan_id": 8,
    "amount": 1000.0,
    "payment_method": "Cash",
    "reference": "TRF333",
    "transaction_date": "2025-08-24T00:00:00",
    "notes": "Prueba simple",
    "url_bank_receipt": "https://drive.google.com/file/d/1oKanDqy6hdKAbiK-zss4sOUibgxY_IxB/view?usp=drivesdk",
    "url_payment_receipt": None
}

print("Enviando petición...")
response = requests.post(
    "http://localhost:8000/loan-payments/auto-payment",
    json=test_data
)

print(f"Status: {response.status_code}")
result = response.json()
print(json.dumps(result, indent=2))

if "receipt" in result:
    print("✅ RECIBO GENERADO!")
    receipt = result["receipt"]
    print(f"Receipt ID: {receipt.get('receipt_id')}")
    print(f"Image length: {len(receipt.get('image_base64', ''))}")
else:
    print("❌ NO SE GENERÓ RECIBO")
