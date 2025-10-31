from typing import Dict, Any, Optional, List, Union
from datetime import datetime, date
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import text as sql_text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload

from .models import payment_schedule, payment_transactions, PaymentSchedule, PaymentTransaction
from .schemas import (
    GeneratePaymentScheduleRequest,
    GeneratePaymentScheduleResponse,
    RegisterPaymentTransactionRequest,
    RegisterPaymentTransactionResponse,
    LoanSummaryResponse
)
from app.database import DepDatabase


class LoanPaymentService:
    """Servicio para gestión de pagos de préstamos"""

    def __init__(self, db: DepDatabase):
        self.db = db

    async def generate_payment_schedule(self, request: GeneratePaymentScheduleRequest) -> GeneratePaymentScheduleResponse:
        """
        Genera el cronograma de pagos para un préstamo usando la función SQL
        """
        try:
            query = sql_text("""
                SELECT public.sp_generate_loan_payment_schedule(
                    :contract_loan_id,
                    :monthly_quotes,
                    :monthly_amount,
                    :interest_amount,
                    :start_date,
                    :end_date,
                    :last_payment_date,
                    :last_principal,
                    :last_interest
                )
            """)
            
            await self.db.execute(
                query,
                {
                    "contract_loan_id": request.contract_loan_id,
                    "monthly_quotes": request.monthly_quotes,
                    "monthly_amount": request.monthly_amount,
                    "interest_amount": request.interest_amount,
                    "start_date": request.start_date,
                    "end_date": request.end_date,
                    "last_payment_date": request.last_payment_date,
                    "last_principal": request.last_principal,
                    "last_interest": request.last_interest
                }
            )
            
            await self.db.commit()
            
            return GeneratePaymentScheduleResponse(
                success=True,
                message="Cronograma de pagos generado exitosamente",
                contract_loan_id=request.contract_loan_id,
                total_payments_generated=request.monthly_quotes,
                schedule_summary=None
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al generar el cronograma de pagos: {str(e)}"
            )

    async def get_payment_schedule(self, contract_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene el cronograma de pagos de un contrato usando la función SQL sp_get_payment_schedule
        """
        try:
            if contract_id:
                query = sql_text("SELECT sp_get_payment_schedule(:contract_id)")
                result = await self.db.execute(query, {"contract_id": contract_id})
            else:
                query = sql_text("SELECT sp_get_payment_schedule()")
                result = await self.db.execute(query)
            
            # Obtener el resultado
            row = result.fetchone()
            if not row or not row[0]:
                return {
                    "success": False,
                    "error": "NO_DATA",
                    "message": "No se encontraron datos de pagos",
                    "data": None
                }
            
            # El resultado ya viene como diccionario desde la función SQL
            payment_data = row[0]
            
            # Si es un string JSON, parsearlo
            if isinstance(payment_data, str):
                import json
                try:
                    payment_data = json.loads(payment_data)
                except json.JSONDecodeError as e:
                    return {
                        "success": False,
                        "error": "PARSE_ERROR",
                        "message": f"Error al procesar los datos de pagos: {str(e)}",
                        "data": None
                    }
            
            # Adaptar la estructura para que sea compatible con el schema
            if isinstance(payment_data, dict):
                # Si tiene "paymentt_list", adaptarlo a "data"
                if "paymentt_list" in payment_data:
                    payment_data["data"] = payment_data.pop("paymentt_list")
                # Si tiene "data" pero no "paymentt_list", dejarlo como está
                elif "data" not in payment_data:
                    # Si no tiene ninguna de las dos claves, asumir que el diccionario completo es la data
                    payment_data = {
                        "success": payment_data.get("success", True),
                        "data": [payment_data] if isinstance(payment_data, dict) else [],
                        "error": payment_data.get("error"),
                        "message": payment_data.get("message")
                    }
            
            return payment_data
                
        except Exception as e:
            return {
                "success": False,
                "error": "DATABASE_ERROR",
                "message": f"Error inesperado al recuperar pagos: {str(e)}",
                "data": None
            }

    async def register_auto_payment(self, contract_loan_id: int, amount: float,
                                     payment_method: str = "Cash", reference: Optional[str] = None, 
                                     transaction_date: Optional[datetime] = None, 
                                     notes: Optional[str] = None,
                                     url_bank_receipt: Optional[str] = None,
                                     url_payment_receipt: Optional[str] = None) -> Dict[str, Any]:
        """
        Registra un pago automático usando la función SQL sp_register_payment_transaction
        """
        try:
            query = sql_text("""
                SELECT sp_register_payment_transaction(
                    :contract_loan_id,
                    :amount,
                    :payment_method,
                    :reference,
                    :transaction_date,
                    :url_bank_receipt,
                    :url_payment_receipt,
                    :notes
                )
            """)
            
            # Usar la fecha actual si no se proporciona
            if not transaction_date:
                transaction_date = datetime.now()
            
            params = {
                "contract_loan_id": contract_loan_id,
                "amount": amount,
                "payment_method": payment_method,
                "reference": reference,
                "transaction_date": transaction_date,
                "notes": notes,
                "url_bank_receipt": url_bank_receipt,
                "url_payment_receipt": url_payment_receipt
            }

            print(f"[auto-payment] Ejecutando sp_register_payment_transaction con params: {params}")

            result = await self.db.execute(
                query,
                params
            )
            
            await self.db.commit()
            
            # Obtener el resultado
            row = result.fetchone()
            print(f"[auto-payment] Respuesta cruda del SP (row): {row}")
            if not row or not row[0]:
                return {
                    "success": False,
                    "error": "NO_DATA",
                    "message": "No se recibió respuesta del procedimiento",
                    "data": None
                }
            
            # El resultado ya viene como diccionario desde la función SQL
            payment_data = row[0]
            try:
                keys = list(payment_data.keys()) if isinstance(payment_data, dict) else type(payment_data)
            except Exception:
                keys = str(type(payment_data))
            print(f"[auto-payment] payment_data keys/tipo: {keys}")
            
            # Si es un string JSON, parsearlo
            if isinstance(payment_data, str):
                import json
                try:
                    payment_data = json.loads(payment_data)
                except json.JSONDecodeError as e:
                    return {
                        "success": False,
                        "error": "PARSE_ERROR",
                        "message": f"Error al procesar la respuesta: {str(e)}",
                        "data": None
                    }
            
            return payment_data
                
        except Exception as e:
            return {
                "success": False,
                "error": "DATABASE_ERROR",
                "message": f"Error inesperado al registrar el pago: {str(e)}",
                "data": None
            }

    async def register_specific_payments(self, contract_loan_id: int, payment_ids: List[str], amount: float,
                                         payment_method: str = "Cash", reference: Optional[str] = None, 
                                         transaction_date: Optional[datetime] = None, 
                                         notes: Optional[str] = None,
                                         url_bank_receipt: Optional[str] = None,
                                         url_payment_receipt: Optional[str] = None) -> Dict[str, Any]:
        """
        Registra pagos específicos usando la función SQL sp_register_specific_payments
        """
        try:
            query = sql_text("""
                SELECT sp_register_specific_payments(
                    :contract_loan_id,
                    :payment_ids,
                    :amount,
                    :payment_method,
                    :reference,
                    :transaction_date,
                    :url_bank_receipt,
                    :url_payment_receipt,
                    :notes
                )
            """)
            
            # Usar la fecha actual si no se proporciona
            if not transaction_date:
                transaction_date = datetime.now()
            
            result = await self.db.execute(
                query,
                {
                    "contract_loan_id": contract_loan_id,
                    "payment_ids": payment_ids,
                    "amount": amount,
                    "payment_method": payment_method,
                    "reference": reference,
                    "transaction_date": transaction_date,
                    "url_bank_receipt": url_bank_receipt,
                    "url_payment_receipt": url_payment_receipt,
                    "notes": notes
                }
            )
            
            await self.db.commit()
            
            # Obtener el resultado
            row = result.fetchone()
            if not row or not row[0]:
                return {
                    "success": False,
                    "error": "NO_DATA",
                    "message": "No se recibió respuesta del procedimiento",
                    "data": None
                }
            
            # El resultado ya viene como diccionario desde la función SQL
            payment_data = row[0]
            
            # Si es un string JSON, parsearlo
            if isinstance(payment_data, str):
                import json
                try:
                    payment_data = json.loads(payment_data)
                except json.JSONDecodeError as e:
                    return {
                        "success": False,
                        "error": "PARSE_ERROR",
                        "message": f"Error al procesar la respuesta: {str(e)}",
                        "data": None
                    }
            
            return payment_data
                
        except Exception as e:
            return {
                "success": False,
                "error": "DATABASE_ERROR",
                "message": f"Error inesperado al registrar los pagos específicos: {str(e)}",
                "data": None
            }

    async def register_payment_transaction(self, request: RegisterPaymentTransactionRequest) -> RegisterPaymentTransactionResponse:
        """
        Registra una transacción de pago usando la función SQL
        """
        try:
            query = sql_text("""
                SELECT sp_register_payment_transaction(
                    :contract_loan_id,
                    :amount,
                    :payment_method,
                    :reference,
                    :transaction_date,
                    :url_bank_receipt,
                    :url_payment_receipt,
                    :notes
                )
            """)
            
            # Usar payment_image_url como url_bank_receipt si está disponible
            url_bank_receipt = request.payment_image_url if request.payment_image_url else request.url_bank_receipt
            
            result = await self.db.execute(
                query,
                {
                    "contract_loan_id": request.contract_loan_id,
                    "amount": float(request.amount),
                    "payment_method": request.payment_method,
                    "reference": request.reference,
                    "transaction_date": datetime.fromisoformat(request.transaction_date) if request.transaction_date else datetime.now(),
                    "url_bank_receipt": url_bank_receipt,
                    "url_payment_receipt": request.url_payment_receipt,
                    "notes": request.notes
                }
            )
            
            await self.db.commit()
            
            # Obtener el resultado de la función SQL
            transaction_result = result.fetchone()
            
            # Devolver directamente el resultado del procedimiento
            return transaction_result[0] if transaction_result else None
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al registrar la transacción de pago: {str(e)}"
            )
