#!/usr/bin/env python3
"""
Ejemplo de cómo usar el query completo para obtener información del contrato
"""

import sys
import asyncio
import asyncpg
import json
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append('.')

async def get_contract_complete_info(contract_id: str):
    """Obtener información completa del contrato"""
    print(f"🔍 Obteniendo información completa del contrato: {contract_id}")
    
    try:
        from app.config import settings
        conn = await asyncpg.connect(str(settings.DATABASE_URL))
        
        # Leer el query SQL
        sql_file = Path("get_contract_complete_info.sql")
        if not sql_file.exists():
            print("❌ Archivo get_contract_complete_info.sql no encontrado")
            return None
        
        sql_content = sql_file.read_text()
        
        # Ejecutar el query
        print("📋 Ejecutando query...")
        result = await conn.fetchrow(sql_content, contract_id)
        
        if result:
            print("✅ Query ejecutado exitosamente")
            
            # Convertir el resultado a un diccionario más legible
            contract_data = dict(result)
            
            # Mostrar resumen
            summary = contract_data.get('summary', {})
            print(f"\n📊 RESUMEN DEL CONTRATO:")
            print(f"   Número: {contract_data.get('contract_number', 'N/A')}")
            print(f"   Tipo: {contract_data.get('contract_type', 'N/A')}")
            print(f"   Estado: {contract_data.get('status', 'N/A')}")
            print(f"   Fecha de inicio: {contract_data.get('contract_date', 'N/A')}")
            print(f"   Fecha de fin: {contract_data.get('end_date', 'N/A')}")
            print(f"   Total participantes: {summary.get('total_participants', 0)}")
            print(f"   Clientes: {summary.get('clients_count', 0)}")
            print(f"   Inversionistas: {summary.get('investors_count', 0)}")
            print(f"   Testigos: {summary.get('witnesses_count', 0)}")
            print(f"   Notarios: {summary.get('notaries_count', 0)}")
            print(f"   Referentes: {summary.get('referrers_count', 0)}")
            print(f"   Tiene loan: {'Sí' if summary.get('has_loan', False) else 'No'}")
            print(f"   Propiedades: {summary.get('properties_count', 0)}")
            
            # Guardar resultado en archivo JSON para inspección
            output_file = f"contract_info_{contract_id}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(contract_data, f, indent=2, default=str)
            
            print(f"\n💾 Información completa guardada en: {output_file}")
            print("📋 Para ver el JSON completo, abre el archivo generado")
            
            return contract_data
        else:
            print("❌ No se encontró información para el contrato especificado")
            return None
        
    except Exception as e:
        print(f"❌ Error ejecutando query: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Ejecutar el ejemplo"""
    print("🚀 Ejemplo de query completo para contrato...")
    print("=" * 70)
    
    # Ejemplo con un contract_id específico
    contract_id = "756b7eaa-5e4c-4932-bee2-595b5e194aba"  # Reemplaza con un ID real
    
    print(f"📋 Usando contract_id: {contract_id}")
    print("💡 Para usar con otro contrato, cambia el contract_id en el script")
    
    result = await get_contract_complete_info(contract_id)
    
    print("\n" + "=" * 70)
    if result:
        print("✅ Información del contrato obtenida exitosamente")
        print("\n📋 ESTRUCTURA DEL RESULTADO:")
        print("   - contract_id, contract_number, contract_type, etc.")
        print("   - participants: {clients, investors, witnesses, notaries, referrers}")
        print("   - loan: información del préstamo")
        print("   - properties: array de propiedades")
        print("   - summary: resumen estadístico")
    else:
        print("❌ Error obteniendo información del contrato")
    
    return result

if __name__ == "__main__":
    asyncio.run(main()) 