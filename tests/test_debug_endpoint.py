#!/usr/bin/env python3
"""
Script para probar el endpoint y ver logs del servidor
"""
import asyncio
import aiohttp
import json

async def test_endpoint():
    """Probar el endpoint de generación de contratos"""
    url = "http://localhost:8000/contracts/generate-complete"
    
    # Cargar el JSON de prueba
    with open('test_property_referrer.json', 'r') as f:
        data = json.load(f)
    
    print("🚀 Enviando petición al servidor...")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            print(f"📊 Status Code: {response.status}")
            print(f"📊 Headers: {dict(response.headers)}")
            
            if response.status == 200:
                result = await response.json()
                print("✅ Respuesta exitosa")
                print(f"📋 Contract ID: {result.get('contract_id')}")
                print(f"📋 Contract Number: {result.get('contract_number')}")
            else:
                error_text = await response.text()
                print(f"❌ Error: {error_text}")

if __name__ == "__main__":
    asyncio.run(test_endpoint())

