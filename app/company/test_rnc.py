"""
Test file for RNC service
This file can be used to test the RNC consultation functionality
"""

import asyncio
from app.company.service import RNCService


async def test_rnc_consultation():
    """Test RNC consultation with a real RNC from CSV"""
    service = RNCService()

    # Test with a real RNC from the CSV file
    test_rnc = "00110344256"

    try:
        result = await service.consultar_rnc(test_rnc)
        print(f"✅ RNC consultation successful:")
        print(f"   RNC: {result['rnc']}")
        print(f"   Nombre: {result['nombre']}")
        print(f"   Estado: {result['estado']}")
        print(f"   Actividad Económica: {result.get('actividad_economica', 'N/A')}")
        print(f"   Fecha Inicio: {result.get('fecha_inicio', 'N/A')}")
        print(f"   Régimen Pago: {result.get('regimen_pago', 'N/A')}")
        print(f"   Source: {result.get('source', 'N/A')}")
        return result
    except Exception as e:
        print(f"❌ RNC consultation failed: {e}")
        return None


if __name__ == "__main__":
    asyncio.run(test_rnc_consultation())
