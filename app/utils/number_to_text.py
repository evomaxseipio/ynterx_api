#!/usr/bin/env python3
"""
Módulo para convertir números a texto legal
"""

from num2words import num2words
from typing import Union


def numero_a_texto_con_monto(monto: Union[float, int], moneda: str = "USD") -> str:
    """
    Convierte una cantidad numérica a texto legal, por ejemplo:
    30000.00 → TREINTA MIL DÓLARES ESTADOUNIDENSES (USD 30,000.00)
    
    Args:
        monto: Cantidad numérica a convertir
        moneda: Código de moneda (USD, DOP, etc.)
    
    Returns:
        str: Texto legal formateado en mayúsculas
    """
    # Convertimos la parte entera a palabras
    parte_entera = int(monto)
    texto = num2words(parte_entera, lang='es').upper()

    # Determinamos el texto de la moneda
    if moneda == "USD":
        moneda_texto = "DÓLARES ESTADOUNIDENSES"
        simbolo = "USD"
    elif moneda == "DOP":
        moneda_texto = "PESOS DOMINICANOS"
        simbolo = "RD$"
    else:
        moneda_texto = moneda.upper()
        simbolo = moneda

    # Formato de número con coma para miles y punto para decimales (formato inglés)
    monto_formateado = f"{monto:,.2f}"

    return f"{texto} {moneda_texto} ({simbolo} {monto_formateado})"


def numero_a_texto_simple(monto: Union[float, int], moneda: str = "USD") -> str:
    """
    Convierte una cantidad numérica a texto simple, por ejemplo:
    30000.00 → TREINTA MIL DÓLARES ESTADOUNIDENSES
    
    Args:
        monto: Cantidad numérica a convertir
        moneda: Código de moneda (USD, DOP, etc.)
    
    Returns:
        str: Texto simple sin formato numérico
    """
    # Convertimos la parte entera a palabras
    parte_entera = int(monto)
    texto = num2words(parte_entera, lang='es').upper()

    # Determinamos el texto de la moneda
    if moneda == "USD":
        moneda_texto = "DÓLARES ESTADOUNIDENSES"
    elif moneda == "DOP":
        moneda_texto = "PESOS DOMINICANOS"
    else:
        moneda_texto = moneda.upper()

    return f"{texto} {moneda_texto}"


def formatear_monto(monto: Union[float, int], moneda: str = "USD") -> str:
    """
    Formatea un monto con símbolo de moneda, por ejemplo:
    30000.00 → USD 30,000.00
    
    Args:
        monto: Cantidad numérica a formatear
        moneda: Código de moneda (USD, DOP, etc.)
    
    Returns:
        str: Monto formateado con símbolo
    """
    if moneda == "USD":
        simbolo = "USD"
    elif moneda == "DOP":
        simbolo = "RD$"
    else:
        simbolo = moneda

    # Formato de número con coma para miles y punto para decimales (formato inglés)
    monto_formateado = f"{monto:,.2f}"

    return f"{simbolo} {monto_formateado}"


# Ejemplos de uso
if __name__ == "__main__":
    print("🧪 Probando funciones de conversión de números a texto...")
    print("=" * 60)
    
    # Ejemplos
    montos = [
        (30000.00, "USD"),
        (150000.50, "USD"),
        (5000.00, "DOP"),
        (1000000.00, "USD"),
        (25000.75, "DOP")
    ]
    
    for monto, moneda in montos:
        print(f"\n💰 Monto: {monto} {moneda}")
        print(f"   Texto legal: {numero_a_texto_con_monto(monto, moneda)}")
        print(f"   Texto simple: {numero_a_texto_simple(monto, moneda)}")
        print(f"   Formato: {formatear_monto(monto, moneda)}")
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas") 