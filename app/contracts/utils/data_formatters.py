from datetime import datetime
from typing import Optional
from app.utils.date_formatter import formatear_fecha_legal, formatear_fecha_simple, parse_fecha_string
from app.utils.number_to_text import numero_a_texto_con_monto, numero_a_texto_simple


def format_full_name(first_name: str, middle_name: str, last_name: str) -> str:
    """
    Formatea el nombre completo en mayúsculas con espacios sencillos.
    """
    # Construir el nombre completo
    name_parts = []
    if first_name:
        name_parts.append(first_name)
    if middle_name:
        name_parts.append(middle_name)
    if last_name:
        name_parts.append(last_name)
    
    # Unir con espacios y convertir a mayúsculas
    full_name = " ".join(name_parts)
    # Normalizar espacios (reemplazar múltiples espacios con uno solo)
    full_name = " ".join(full_name.split())
    return full_name.upper()


def format_dates(contract_date_str: Optional[str] = None, contract_end_date_str: Optional[str] = None) -> dict:
    """
    Formatea las fechas del contrato para uso en plantillas.
    """
    result = {
        "current_date": datetime.now().strftime("%d de %B de %Y"),
        "current_year": datetime.now().year,
        "current_month": datetime.now().strftime("%B"),
        "current_day": datetime.now().day,
    }
    
    if contract_date_str:
        contract_date_obj = parse_fecha_string(contract_date_str)
        
        # loan_start_date = contract_date (sin modificar)
        loan_start_date_text = formatear_fecha_legal(contract_date_obj)
        loan_start_date_simple = formatear_fecha_simple(contract_date_obj)
        
        # first_payment_date = contract_date + 1 mes
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta
        
        first_payment_date_obj = contract_date_obj + relativedelta(months=1)
        first_payment_date_text = formatear_fecha_legal(first_payment_date_obj)
        first_payment_date_simple = formatear_fecha_simple(first_payment_date_obj)
        
        result.update({
            "loan_start_date_text": loan_start_date_text,
            "loan_start_date_simple": loan_start_date_simple,
            "first_payment_date_text": first_payment_date_text,
            "first_payment_date_simple": first_payment_date_simple,
        })
    else:
        result.update({
            "loan_start_date_text": "FECHA A DETERMINAR",
            "loan_start_date_simple": "FECHA A DETERMINAR",
            "first_payment_date_text": "FECHA A DETERMINAR",
            "first_payment_date_simple": "FECHA A DETERMINAR",
        })
    
    if contract_end_date_str:
        contract_end_date_obj = parse_fecha_string(contract_end_date_str)
        last_payment_date_text = formatear_fecha_legal(contract_end_date_obj)
        last_payment_date_simple = formatear_fecha_simple(contract_end_date_obj)
        
        result.update({
            "last_payment_date_text": last_payment_date_text,
            "last_payment_date_simple": last_payment_date_simple,
        })
    else:
        result.update({
            "last_payment_date_text": "FECHA A DETERMINAR",
            "last_payment_date_simple": "FECHA A DETERMINAR",
        })
    
    return result


def format_loan_amounts(loan_amount: float, loan_currency: str = "USD") -> dict:
    """
    Formatea los montos del préstamo para uso en plantillas.
    """
    # Generar texto legal del monto (con formato numérico)
    loan_amount_text = numero_a_texto_con_monto(loan_amount, loan_currency)
    
    # Generar texto simple del monto (sin formato numérico)
    loan_amount_text_simple = numero_a_texto_simple(loan_amount, loan_currency)
    
    return {
        "loan_amount": f"{loan_amount:,.2f}",
        "loan_amount_raw": loan_amount,
        "loan_amount_text": loan_amount_text,
        "loan_amount_text_simple": loan_amount_text_simple,
        "loan_currency": loan_currency,
    }


def format_payment_amounts(monthly_payment: float, final_payment: float, currency: str = "USD") -> dict:
    """
    Formatea los montos de pago para uso en plantillas.
    """
    monthly_payment_text = numero_a_texto_con_monto(monthly_payment, currency)
    final_payment_text = numero_a_texto_con_monto(final_payment, currency)
    
    return {
        "monthly_payment": f"{monthly_payment:,.2f}",
        "monthly_payment_raw": monthly_payment,
        "monthly_payment_text": monthly_payment_text,
        "final_payment": f"{final_payment:,.2f}",
        "final_payment_raw": final_payment,
        "final_payment_text": final_payment_text,
    }
