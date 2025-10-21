#!/usr/bin/env python3
"""
Script simple para probar la generación de contrato
"""
import asyncio
import json
import logging
from app.database import get_async_session
from app.contracts.router import generate_contract_complete

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_simple_contract():
    """Probar la generación de contrato"""
    logger.info("🔍 Iniciando prueba de generación de contrato...")
    
    # Cargar el JSON de prueba
    with open('test_referrer_fixed.json', 'r') as f:
        data = json.load(f)
    
    logger.info(f"📄 JSON cargado con {len(data)} campos principales")
    
    # Verificar participantes
    participant_roles = [
        ("clients", "cliente", 1),
        ("investors", "inversionista", 2),
        ("witnesses", "testigo", 3),
        ("notaries", "notario", 7),
        ("notary", "notario", 7),
        ("referents", "referidor", 8)
    ]
    
    logger.info("👥 Verificando participantes en el JSON:")
    for group_name, role_name, default_role_id in participant_roles:
        group_data = data.get(group_name, [])
        logger.info(f"  - {group_name}: {len(group_data)} elementos")
        if group_data:
            for idx, participant in enumerate(group_data):
                if "person" in participant:
                    person = participant["person"]
                    person_role_id = person.get("person_role_id", default_role_id)
                    logger.info(f"    {idx+1}. {person.get('first_name', 'N/A')} {person.get('last_name', 'N/A')} (role_id: {person_role_id})")
    
    # Verificar si hay referentes
    referents = data.get("referents", [])
    logger.info(f"🔍 Referentes encontrados: {len(referents)}")
    if referents:
        for idx, referent in enumerate(referents):
            if "person" in referent:
                person = referent["person"]
                logger.info(f"  {idx+1}. {person.get('first_name', 'N/A')} {person.get('last_name', 'N/A')} (role_id: {person.get('person_role_id', 'N/A')})")
    
    logger.info("✅ JSON verificado correctamente")

if __name__ == "__main__":
    asyncio.run(test_simple_contract())

