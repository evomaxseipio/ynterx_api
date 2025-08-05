"""
Utilidades de formateo para fechas y números
"""
from datetime import datetime
from typing import Union

class DateFormatter:
    """Utilidades para formateo de fechas"""

    MONTHS_SPANISH = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }

    @staticmethod
    def to_spanish(date_str: str) -> str:
        """
        Convierte fecha YYYY-MM-DD a formato español
        Ejemplo: "2025-03-26" → "26 de marzo de 2025"
        """
        if not date_str:
            return ""

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            month = DateFormatter.MONTHS_SPANISH[date_obj.month]
            return f"{date_obj.day} de {month} de {date_obj.year}"
        except (ValueError, KeyError):
            return date_str

    @staticmethod
    def extract_date_parts(date_str: str) -> dict:
        """
        Extrae partes de la fecha para uso en templates
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return {
                "day": str(date_obj.day),
                "month": DateFormatter.MONTHS_SPANISH[date_obj.month].upper(),
                "year": str(date_obj.year),
                "year_words": DateFormatter._year_to_words(date_obj.year)
            }
        except (ValueError, KeyError):
            return {"day": "", "month": "", "year": "", "year_words": ""}

    @staticmethod
    def _year_to_words(year: int) -> str:
        """Convierte año a palabras"""
        year_words = {
            2025: "DOS MIL VEINTICINCO",
            2026: "DOS MIL VEINTISÉIS",
            2024: "DOS MIL VEINTICUATRO"
        }
        return year_words.get(year, str(year))

class NumberFormatter:
    """Utilidades para convertir números a palabras en español"""

    # Números comunes en contratos hipotecarios
    NUMBER_WORDS = {
        0: "CERO",
        440: "CUATROCIENTOS CUARENTA",
        1000: "MIL",
        2000: "DOS MIL",
        5000: "CINCO MIL",
        10000: "DIEZ MIL",
        15000: "QUINCE MIL",
        20000: "VEINTE MIL",
        20440: "VEINTE MIL CUATROCIENTOS CUARENTA",
        25000: "VEINTICINCO MIL",
        30000: "TREINTA MIL",
        50000: "CINCUENTA MIL",
        100000: "CIEN MIL"
    }

    # Números básicos del 1-20
    BASIC_NUMBERS = {
        1: "UNO", 2: "DOS", 3: "TRES", 4: "CUATRO", 5: "CINCO",
        6: "SEIS", 7: "SIETE", 8: "OCHO", 9: "NUEVE", 10: "DIEZ",
        11: "ONCE", 12: "DOCE", 13: "TRECE", 14: "CATORCE", 15: "QUINCE",
        16: "DIECISÉIS", 17: "DIECISIETE", 18: "DIECIOCHO", 19: "DIECINUEVE", 20: "VEINTE"
    }

    @staticmethod
    def to_words_spanish(amount: Union[int, float]) -> str:
        """
        Convierte número a palabras en español
        """
        if not isinstance(amount, (int, float)):
            return str(amount)

        # Convertir a entero para lookup
        amount_int = int(amount)

        # Si existe conversión directa, usarla
        if amount_int in NumberFormatter.NUMBER_WORDS:
            return NumberFormatter.NUMBER_WORDS[amount_int]

        # Para números no mapeados, usar lógica básica
        return NumberFormatter._convert_complex_number(amount_int)

    @staticmethod
    def _convert_complex_number(num: int) -> str:
        """Convierte números complejos a palabras (implementación básica)"""
        if num < 21:
            return NumberFormatter.BASIC_NUMBERS.get(num, str(num))
        elif num < 1000:
            return f"{num}"  # Por simplicidad
        elif num < 10000:
            thousands = num // 1000
            hundreds = num % 1000
            if hundreds == 0:
                return f"{NumberFormatter._get_basic_word(thousands)} MIL"
            else:
                return f"{NumberFormatter._get_basic_word(thousands)} MIL {hundreds}"
        else:
            # Para números muy grandes, usar formato con separadores
            return f"{num:,}".replace(",", " MIL ")

    @staticmethod
    def _get_basic_word(num: int) -> str:
        """Obtiene palabra para números básicos"""
        return NumberFormatter.BASIC_NUMBERS.get(num, str(num))

class CurrencyFormatter:
    """Utilidades para formateo de moneda"""

    @staticmethod
    def format_amount(amount: Union[int, float], currency: str = "USD") -> str:
        """
        Formatea cantidad con separadores de miles
        Ejemplo: 20000 → "20,000.00"
        """
        if not isinstance(amount, (int, float)):
            return "0.00"
        return f"{amount:,.2f}"

    @staticmethod
    def format_currency_symbol(currency: str) -> str:
        """
        Obtiene símbolo de moneda
        """
        symbols = {
            "USD": "US$",
            "DOP": "RD$",
            "EUR": "€"
        }
        return symbols.get(currency, currency)

class AddressFormatter:
    """Utilidades para formateo de direcciones"""

    @staticmethod
    def format_full_address(address_line1: str, address_line2: str = "", city: str = "") -> str:
        """
        Formatea dirección completa eliminando comas extra
        """
        parts = [part.strip() for part in [address_line1, address_line2, city] if part.strip()]
        return ", ".join(parts)

    @staticmethod
    def format_name(first_name: str, last_name: str, middle_name: str = "") -> str:
        """
        Formatea nombre completo
        """
        names = [name.strip() for name in [first_name, middle_name, last_name] if name.strip()]
        return " ".join(names)
