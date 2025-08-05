#!/usr/bin/env python3
"""
Módulo para formatear fechas legales
"""

from datetime import date
from num2words import num2words

MESES = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
]


def formatear_fecha_legal(fecha: date) -> str:
    """
    Convierte una fecha al formato legal:
    2026-03-26 → VEINTISÉIS (26) del mes de MARZO del año DOS MIL VEINTISÉIS (2026)
    
    Args:
        fecha: Objeto date a formatear
    
    Returns:
        str: Fecha en formato legal
    """
    dia = fecha.day
    mes = fecha.month
    anio = fecha.year

    dia_letras = num2words(dia, lang='es').upper()
    anio_letras = num2words(anio, lang='es').upper()
    mes_texto = MESES[mes - 1]

    return f"{dia_letras} ({dia}) del mes de {mes_texto} del año {anio_letras} ({anio})"


def formatear_fecha_simple(fecha: date) -> str:
    """
    Convierte una fecha al formato simple:
    2026-03-26 → VEINTISÉIS (26) del mes de MARZO de 2026
    
    Args:
        fecha: Objeto date a formatear
    
    Returns:
        str: Fecha en formato simple
    """
    dia = fecha.day
    mes = fecha.month
    anio = fecha.year

    dia_letras = num2words(dia, lang='es').upper()
    mes_texto = MESES[mes - 1]

    return f"{dia_letras} ({dia}) del mes de {mes_texto} de {anio}"


def parse_fecha_string(fecha_str: str) -> date:
    """
    Convierte una fecha en formato string DD/MM/YYYY a objeto date
    
    Args:
        fecha_str: Fecha en formato "DD/MM/YYYY"
    
    Returns:
        date: Objeto date
    """
    if not fecha_str:
        return date.today()
    
    try:
        day, month, year = fecha_str.split('/')
        return date(int(year), int(month), int(day))
    except (ValueError, AttributeError):
        return date.today()


# Ejemplos de uso
if __name__ == "__main__":
    print("🧪 Probando funciones de formateo de fechas...")
    print("=" * 60)
    
    # Ejemplos
    fechas_prueba = [
        date(2025, 4, 26),
        date(2026, 3, 26),
        date(2025, 7, 31),
        date(2026, 7, 31),
        date(2025, 12, 25)
    ]
    
    for fecha in fechas_prueba:
        print(f"\n📅 Fecha: {fecha}")
        print(f"   Formato legal: {formatear_fecha_legal(fecha)}")
        print(f"   Formato simple: {formatear_fecha_simple(fecha)}")
    
    # Probar con strings
    print(f"\n📅 Probar con strings:")
    fechas_string = ["31/07/2025", "31/07/2026", "26/04/2025", "26/03/2026"]
    
    for fecha_str in fechas_string:
        fecha_obj = parse_fecha_string(fecha_str)
        print(f"   {fecha_str} → {formatear_fecha_legal(fecha_obj)}")
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas") 