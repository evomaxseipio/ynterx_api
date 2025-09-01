#!/usr/bin/env python3
"""
Script para probar el servicio de recibo directamente
"""

import asyncio
from app.receipts.receipt_service import ReceiptService

# Datos de ejemplo basados en la respuesta del auto-payment
sample_payment_data = {
    "success": True,
    "data": {
        "contract_loan_id": 8,
        "total_amount_paid": 1000,
        "total_applied": 1000.0,
        "payment_date": "2025-08-24T00:00:00",
        "payment_method": "Cash",
        "sub_total": 1000.0,
        "discount": 0.0,
        "total_paid": 1000.0,
        "client_data": {
            "receiptNumber": "RCP-2025-001234",
            "clientName": "MARIA DEL CARMEN SEIPIO MARTINS",
            "clientId": "023-0097473-6",
            "contractNumber": "CNT-000008-2025"
        },
        "remaining_balance": 29940.0,
        "has_advance_payment": False,
        "advance_amount": 0.0,
        "transactions": [
            {
                "transaction_id": "489dc2d0-643c-4e76-a7b2-0db097ed0af1",
                "payment_id": "5c1dd155-f5d2-4fb6-bf99-f84177e6cc4b",
                "payment_number": 11,
                "amount": 280.0,
                "type": "regular",
                "status": "completed"
            }
        ],
        "payment_items": [
            {
                "payment_id": "5c1dd155-f5d2-4fb6-bf99-f84177e6cc4b",
                "payment_number": 11,
                "due_date": "2026-02-08",
                "amount_due": 660.0,
                "paid_amount": 660.0,
                "new_status": "paid",
                "previous_status": "partial"
            }
        ],
        "next_payment": {
            "payment_number": 12,
            "due_date": "2026-03-08",
            "amount_due": 30660.0,
            "remaining_amount": 29940.0
        },
        "url_bank_receipt": "https://drive.google.com/file/d/1oKanDqy6hdKAbiK-zss4sOUibgxY_IxB/view?usp=drivesdk",
        "url_payment_receipt": None,
        "message": "Pago registrado exitosamente"
    },
    "error": None,
    "message": None
}

async def test_receipt_service():
    """Prueba el servicio de recibo directamente"""
    
    print("🧪 PROBANDO SERVICIO DE RECIBO DIRECTAMENTE")
    print("=" * 50)
    
    try:
        # Crear instancia del servicio
        service = ReceiptService()
        print("✅ Servicio creado correctamente")
        
        # Generar recibo
        print("🔍 Generando recibo...")
        result = await service.generate_receipt_from_payment(sample_payment_data)
        
        print(f"🔍 Resultado: {result}")
        print(f"🔍 Success: {result.success}")
        print(f"🔍 Message: {result.message}")
        print(f"🔍 Receipt ID: {result.receipt_id}")
        print(f"🔍 Filename: {result.filename}")
        print(f"🔍 Image Base64 length: {len(result.image_base64) if result.image_base64 else 0}")
        
        if result.success and result.image_base64:
            # Guardar la imagen
            import base64
            image_data = result.image_base64.replace('data:image/png;base64,', '')
            with open(f"test_receipt_{result.receipt_id}.png", "wb") as f:
                f.write(base64.b64decode(image_data))
            print(f"✅ Imagen guardada como: test_receipt_{result.receipt_id}.png")
        else:
            print("❌ No se pudo generar la imagen")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_receipt_service())
