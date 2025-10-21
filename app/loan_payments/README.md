# Loan Payments Module

Este módulo maneja la generación de cronogramas de pagos para préstamos de contratos. Se integra con la función SQL `sp_generate_loan_payment_schedule` para crear cronogramas de pagos automáticamente cuando se crean contratos.

## Características

- **Generación automática de cronogramas**: Crea cronogramas de pagos mensuales usando la función SQL
- **Integración con contratos**: Se puede llamar automáticamente después de crear un préstamo
- **Validación de parámetros**: Valida todos los parámetros necesarios para la función SQL

## Estructura del Módulo

```
loan_payments/
├── __init__.py          # Inicialización del módulo
├── models.py           # Modelos de base de datos
├── schemas.py          # Esquemas Pydantic
├── service.py          # Lógica de negocio
├── router.py           # Endpoints de la API
├── README.md           # Documentación
├── integration_example.py        # Ejemplo de integración
└── IMPLEMENTATION_SUMMARY.md     # Resumen de implementación
```

## Tablas de Base de Datos

### payment_schedule
Almacena el cronograma de pagos programados:
- `payment_schedule_id`: ID único del pago
- `contract_loan_id`: Referencia al préstamo del contrato
- `payment_number`: Número de cuota
- `due_date`: Fecha de vencimiento
- `amount_due`: Monto total a pagar
- `capital_amount`: Monto del capital
- `interest_amount`: Monto del interés
- `balance`: Saldo restante
- `payment_status`: Estado del pago (pending, paid, overdue, partial)
- `payment_date`: Fecha de pago real
- `amount_paid`: Monto pagado
- `notes`: Notas adicionales

### payment_transactions
Almacena las transacciones específicas de cada pago:
- `payment_transaction_id`: ID único de la transacción
- `payment_schedule_id`: Referencia al pago programado
- `transaction_type`: Tipo de transacción (payment, refund, adjustment)
- `amount`: Monto de la transacción
- `payment_method`: Método de pago
- `reference_number`: Número de referencia
- `transaction_date`: Fecha de la transacción
- `processed_by`: Usuario que procesó la transacción

## Endpoints de la API

### POST /loan-payments/generate-schedule
Genera el cronograma de pagos para un préstamo.

**Parámetros:**
- `contract_loan_id`: ID del préstamo del contrato
- `monthly_quotes`: Número de cuotas mensuales
- `monthly_amount`: Monto mensual del capital
- `interest_amount`: Monto del interés mensual
- `start_date`: Fecha de inicio del préstamo
- `end_date`: Fecha de finalización del préstamo
- `last_payment_date`: Fecha del último pago
- `last_principal`: Monto del capital del último pago
- `last_interest`: Monto del interés del último pago

**Respuesta:**
```json
{
  "success": true,
  "message": "Cronograma de pagos generado exitosamente",
  "contract_loan_id": 123,
  "total_payments_generated": 12,
  "schedule_summary": null
}
```

### GET /loan-payments/health
Endpoint de verificación de salud del módulo.

## Integración con Contratos

Para integrar este módulo con la creación de contratos, se debe llamar al endpoint `/loan-payments/generate-schedule` después de crear un contrato con información de préstamo.

### Ejemplo de Integración

```python
# Después de crear el contrato y el préstamo
payment_request = GeneratePaymentScheduleRequest(
    contract_loan_id=contract_loan.contract_loan_id,
    monthly_quotes=12,
    monthly_amount=Decimal("1000.00"),
    interest_amount=Decimal("50.00"),
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31),
    last_payment_date=date(2024, 12, 31),
    last_principal=Decimal("1000.00"),
    last_interest=Decimal("50.00")
)

response = await loan_payment_service.generate_payment_schedule(payment_request)
```

## Función SQL

El módulo llama a la función SQL `sp_generate_loan_payment_schedule` con los siguientes parámetros:

```sql
SELECT public.sp_generate_loan_payment_schedule(
    :contract_loan_id,      -- ID del préstamo del contrato
    :monthly_quotes,        -- Número de cuotas mensuales
    :monthly_amount,        -- Monto mensual del capital
    :interest_amount,       -- Monto del interés mensual
    :start_date,           -- Fecha de inicio del préstamo
    :end_date,             -- Fecha de finalización del préstamo
    :last_payment_date,    -- Fecha del último pago
    :last_principal,       -- Monto del capital del último pago
    :last_interest         -- Monto del interés del último pago
);
```

## Dependencias

- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL (para la función SQL)

## Configuración

El módulo utiliza la configuración de base de datos existente en `app.database` y las dependencias de autenticación en `app.auth.dependencies`.

## Próximos Pasos

Este módulo está diseñado para ser expandido con funcionalidades adicionales como:
- Consulta de cronogramas de pagos
- Actualización de estados de pago
- Gestión de transacciones
- Reportes y estadísticas
- Filtrado y búsqueda de pagos
