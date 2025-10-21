"""
Ejemplo de integración del módulo loan_payments con la creación de contratos

Este archivo muestra cómo integrar automáticamente la generación de cronogramas
de pagos cuando se crea un contrato con información de préstamo.
"""

from datetime import date
from decimal import Decimal
from typing import Dict, Any
from uuid import UUID

from .service import LoanPaymentService
from .schemas import GeneratePaymentScheduleRequest


class LoanPaymentIntegration:
    """
    Clase para integrar la generación de cronogramas de pagos
    con el proceso de creación de contratos
    """
    
    def __init__(self, loan_payment_service: LoanPaymentService):
        self.loan_payment_service = loan_payment_service
    
    async def generate_payment_schedule_for_contract(
        self,
        contract_loan_id: int,
        loan_data: Dict[str, Any],
        contract_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Genera automáticamente el cronograma de pagos para un contrato
        
        Args:
            contract_loan_id: ID del préstamo del contrato
            loan_data: Datos del préstamo
            contract_data: Datos del contrato
            
        Returns:
            Resultado de la generación del cronograma
        """
        try:
            # Extraer datos necesarios del loan_data
            loan_payments_details = loan_data.get("loan_payments_details", {})
            
            # Calcular fechas
            contract_date = self._parse_date(contract_data.get("contract_date"))
            contract_end_date = self._parse_date(contract_data.get("contract_end_date"))
            
            # Si no hay fecha de finalización, calcular basado en el plazo
            if not contract_end_date and loan_data.get("term_months"):
                from datetime import timedelta
                contract_end_date = contract_date + timedelta(days=30 * loan_data["term_months"])
            
            # Crear request para generar el cronograma
            payment_request = GeneratePaymentScheduleRequest(
                contract_loan_id=contract_loan_id,
                monthly_quotes=loan_payments_details.get("payment_qty_quotes", 12),
                monthly_amount=Decimal(str(loan_payments_details.get("monthly_payment", 0))),
                interest_amount=Decimal(str(loan_data.get("interest_amount", 0))),
                start_date=contract_date,
                end_date=contract_end_date,
                last_payment_date=contract_end_date,
                last_principal=Decimal(str(loan_payments_details.get("final_payment", 0))),
                last_interest=Decimal(str(loan_data.get("interest_amount", 0)))
            )
            
            # Generar el cronograma
            result = await self.loan_payment_service.generate_payment_schedule(payment_request)
            
            return {
                "success": True,
                "message": "Cronograma de pagos generado exitosamente",
                "payment_schedule_result": result,
                "contract_loan_id": contract_loan_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error generando cronograma de pagos: {str(e)}",
                "contract_loan_id": contract_loan_id
            }
    
    def _parse_date(self, date_str: str) -> date:
        """Convierte fecha del formato DD/MM/YYYY a objeto date"""
        if not date_str:
            return date.today()
        try:
            day, month, year = date_str.split('/')
            return date(int(year), int(month), int(day))
        except (ValueError, AttributeError):
            return date.today()


# Ejemplo de uso en el servicio de contratos
async def integrate_with_contract_creation_example():
    """
    Ejemplo de cómo integrar la generación de pagos en el proceso de creación de contratos
    """
    
    # Simular datos de contrato y préstamo
    contract_data = {
        "contract_date": "01/01/2024",
        "contract_end_date": "31/12/2024",
        "contract_type_id": 1,
        "description": "Préstamo hipotecario"
    }
    
    loan_data = {
        "amount": 100000.00,
        "currency": "USD",
        "interest_rate": 0.05,
        "term_months": 12,
        "loan_type": "hipotecario",
        "interest_amount": 5000.00,
        "loan_payments_details": {
            "monthly_payment": 8750.00,
            "final_payment": 8750.00,
            "payment_qty_quotes": 12,
            "payment_type": "monthly"
        }
    }
    
    # Simular creación del préstamo (esto normalmente se hace en el servicio de contratos)
    contract_loan_id = 123  # ID que se obtiene después de crear el préstamo
    
    # Crear instancia del servicio de pagos
    # db = DepDatabase  # Esto vendría como dependencia
    # loan_payment_service = LoanPaymentService(db)
    # integration = LoanPaymentIntegration(loan_payment_service)
    
    # Generar cronograma de pagos
    # result = await integration.generate_payment_schedule_for_contract(
    #     contract_loan_id=contract_loan_id,
    #     loan_data=loan_data,
    #     contract_data=contract_data
    # )
    
    # print(f"Resultado: {result}")


# Ejemplo de modificación del servicio de contratos
def modify_contract_service_example():
    """
    Ejemplo de cómo modificar el servicio de contratos para incluir la generación de pagos
    """
    
    # En app/contracts/loan_property_service.py, modificar el método create_contract_loan:
    
    """
    @staticmethod
    async def create_contract_loan(
        contract_id: UUID,
        loan_data: Dict[str, Any],
        connection: AsyncConnection
    ) -> Dict[str, Any]:
        try:
            if not loan_data:
                return {"success": True, "message": "No loan data provided", "loan_id": None}

            # Crear el préstamo (código existente)
            loan_insert = contract_loan.insert().values(
                contract_id=contract_id,
                loan_amount=loan_data.get("amount"),
                currency=loan_data.get("currency", "USD"),
                interest_rate=loan_data.get("interest_rate"),
                term_months=loan_data.get("term_months"),
                loan_type=loan_data.get("loan_type"),
                monthly_payment=loan_data.get("loan_payments_details", {}).get("monthly_payment"),
                final_payment=loan_data.get("loan_payments_details", {}).get("final_payment"),
                discount_rate=loan_data.get("loan_payments_details", {}).get("discount_rate"),
                payment_qty_quotes=loan_data.get("loan_payments_details", {}).get("payment_qty_quotes"),
                payment_type=loan_data.get("loan_payments_details", {}).get("payment_type"),
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ).returning(contract_loan.c.contract_loan_id)

            result = await fetch_one(loan_insert, connection=connection, commit_after=True)
            loan_id = result["contract_loan_id"]

            # NUEVO: Generar cronograma de pagos automáticamente
            try:
                from app.loan_payments.service import LoanPaymentService
                from app.loan_payments.schemas import GeneratePaymentScheduleRequest
                
                loan_payment_service = LoanPaymentService(connection)
                
                # Obtener datos del contrato para las fechas
                contract_query = "SELECT contract_date, end_date FROM contract WHERE contract_id = :contract_id"
                contract_result = await connection.execute(
                    sql_text(contract_query), 
                    {"contract_id": contract_id}
                )
                contract_info = contract_result.fetchone()
                
                # Crear request para generar pagos
                payment_request = GeneratePaymentScheduleRequest(
                    contract_loan_id=loan_id,
                    monthly_quotes=loan_data.get("loan_payments_details", {}).get("payment_qty_quotes", 12),
                    monthly_amount=Decimal(str(loan_data.get("loan_payments_details", {}).get("monthly_payment", 0))),
                    interest_amount=Decimal(str(loan_data.get("interest_amount", 0))),
                    start_date=contract_info.contract_date,
                    end_date=contract_info.end_date or contract_info.contract_date,
                    last_payment_date=contract_info.end_date or contract_info.contract_date,
                    last_principal=Decimal(str(loan_data.get("loan_payments_details", {}).get("final_payment", 0))),
                    last_interest=Decimal(str(loan_data.get("interest_amount", 0)))
                )
                
                payment_result = await loan_payment_service.generate_payment_schedule(payment_request)
                
                print(f"✅ Cronograma de pagos generado: {payment_result.message}")
                
            except Exception as payment_error:
                print(f"⚠️ Error generando cronograma de pagos: {str(payment_error)}")
                # No fallar la creación del contrato por errores en pagos

            return {
                "success": True,
                "message": "Loan created successfully with payment schedule",
                "loan_id": loan_id
            }

        except Exception as e:
            print(f"❌ Error creando loan: {str(e)}")
            return {
                "success": False,
                "message": f"Error creating loan: {str(e)}",
                "loan_id": None
            }
    """
    
    pass


if __name__ == "__main__":
    # Ejecutar ejemplo
    import asyncio
    asyncio.run(integrate_with_contract_creation_example())
