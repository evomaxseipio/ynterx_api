#!/usr/bin/env python3
"""
Script para debuggear el endpoint de auto-payment
"""

import asyncio
from app.loan_payments.router import get_receipt_service
from app.receipts.receipt_service import ReceiptService

async def debug_endpoint():
    """Debug del endpoint paso a paso"""
    
    print("🔍 DEBUGGING AUTO-PAYMENT ENDPOINT")
    print("=" * 50)
    
    # 1. Probar la dependencia
    print("1. Probando dependencia get_receipt_service...")
    try:
        service = get_receipt_service()
        print(f"   ✅ Tipo: {type(service)}")
        print(f"   ✅ Instancia: {service}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 2. Probar el servicio directamente
    print("\n2. Probando servicio directamente...")
    try:
        # Datos de ejemplo completos
        sample_data = {
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
                "remaining_balance": 27940.0,
                "has_advance_payment": False,
                "advance_amount": 0.0,
                "transactions": [
                    {
                        "transaction_id": "e1d1e7a2-076b-4d8d-9a69-3810463c0863",
                        "payment_id": "d6fe94e5-b76f-45ce-95d6-35d752e217d7",
                        "payment_number": 12,
                        "amount": 1000.0,
                        "type": "regular",
                        "status": "completed"
                    }
                ],
                "payment_items": [
                    {
                        "payment_id": "d6fe94e5-b76f-45ce-95d6-35d752e217d7",
                        "payment_number": 12,
                        "due_date": "2026-03-08",
                        "amount_due": 30660.0,
                        "paid_amount": 2720.0,
                        "new_status": "partial",
                        "previous_status": "partial"
                    }
                ],
                "next_payment": {
                    "payment_number": 12,
                    "due_date": "2026-03-08",
                    "amount_due": 30660.0,
                    "remaining_amount": 27940.0
                },
                "url_bank_receipt": "Prueba simple",
                "url_payment_receipt": None,
                "message": "Pago registrado exitosamente"
            }
        }
        
        result = await service.generate_receipt_from_payment(sample_data)
        print(f"   ✅ Resultado: {result}")
        print(f"   ✅ Success: {result.success}")
        print(f"   ✅ Message: {result.message}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n✅ DEBUG COMPLETADO")

if __name__ == "__main__":
    asyncio.run(debug_endpoint())
