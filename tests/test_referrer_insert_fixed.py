#!/usr/bin/env python3
"""
Script para probar la inserción del referidor con el procedimiento corregido
"""
import asyncio
import json
import logging
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_referrer_insert_fixed():
    """Probar la inserción del referidor con el procedimiento corregido"""
    logger.info("🔍 Probando inserción del referidor con procedimiento corregido...")
    
    DATABASE_URL = str(settings.DATABASE_ASYNC_URL).replace("?sslmode=require", "")
    connect_args = {}
    if "sslmode" in str(settings.DATABASE_ASYNC_URL):
        connect_args["ssl"] = True
    
    engine = create_async_engine(DATABASE_URL, connect_args=connect_args)
    
    try:
        async with engine.connect() as connection:
            # Primero crear la persona
            person_data = {
                "first_name": "CARLOS",
                "last_name": "RODRIGUEZ LOPEZ",
                "middle_name": "Manuel",
                "date_of_birth": None,
                "gender": "Masculino",
                "nationality_country": "República Dominicana",
                "marital_status": "Casado",
                "occupation": "Agente Inmobiliario",
                "person_role_id": 8,  # ID correcto para referidor
                "documents": [
                    {
                        "is_primary": True,
                        "document_type": "Cédula",
                        "document_number": "123-4567890-1",
                        "issuing_country_id": "1",
                        "document_issue_date": None,
                        "document_expiry_date": None
                    }
                ],
                "addresses": [
                    {
                        "address_line1": "CALLE PRINCIPAL 123",
                        "address_line2": "Santo Domingo",
                        "city_id": "1",
                        "postal_code": "10101",
                        "address_type": "Casa",
                        "is_principal": True
                    }
                ],
                "additional_data": {
                    "phone_number": "809-555-0123",
                    "email": "carlos.rodriguez@inmobiliaria.com",
                    "photoPath": "/data/user/0/com.gcapital.gcapital_app/cache/extracted_face_1754615754386.jpg",
                    "referral_code": "REF-2025-001",
                    "commission_percentage": "5.0",
                    "referral_channel": "Inmobiliaria",
                    "notes": "Referidor activo con buena reputación en el mercado"
                }
            }
            
            documents_json = json.dumps(person_data["documents"])
            addresses_json = json.dumps(person_data["addresses"])
            additional_data_json = json.dumps(person_data["additional_data"])
            
            logger.info("📋 Datos del referidor a insertar:")
            logger.info(f"  - Nombre: {person_data['first_name']} {person_data['last_name']}")
            logger.info(f"  - person_role_id: {person_data['person_role_id']}")
            logger.info(f"  - referral_code: {person_data['additional_data']['referral_code']}")
            logger.info(f"  - commission_percentage: {person_data['additional_data']['commission_percentage']}")
            
            # Crear la persona usando sp_insert_person_complete
            query_string = """
                SELECT sp_insert_person_complete(
                    :p_first_name, :p_last_name, :p_middle_name, :p_date_of_birth,
                    :p_gender, :p_nationality_country, :p_marital_status, :p_occupation,
                    :p_documents, :p_addresses, :p_additional_data, :p_person_role_id,
                    :p_created_by, :p_updated_by
                ) as result
            """
            
            logger.info("🚀 Ejecutando procedimiento almacenado sp_insert_person_complete...")
            result = await connection.execute(
                text(query_string),
                {
                    "p_first_name": person_data["first_name"],
                    "p_last_name": person_data["last_name"],
                    "p_middle_name": person_data["middle_name"],
                    "p_date_of_birth": person_data["date_of_birth"],
                    "p_gender": person_data["gender"],
                    "p_nationality_country": person_data["nationality_country"],
                    "p_marital_status": person_data["marital_status"],
                    "p_occupation": person_data["occupation"],
                    "p_documents": documents_json,
                    "p_addresses": addresses_json,
                    "p_additional_data": additional_data_json,
                    "p_person_role_id": person_data["person_role_id"],
                    "p_created_by": None,
                    "p_updated_by": None
                }
            )
            
            row = result.fetchone()
            if row and row[0]:
                logger.info("✅ Procedimiento almacenado ejecutado exitosamente")
                logger.info(f"📄 Resultado: {row[0]}")
                
                if isinstance(row[0], str):
                    stored_proc_result = json.loads(row[0])
                else:
                    stored_proc_result = row[0]
                
                logger.info(f"📋 Resultado parseado: {stored_proc_result}")
                
                if stored_proc_result.get('success', False):
                    person_id = stored_proc_result.get('data', {}).get('person_id')
                    logger.info(f"✅ Persona creada exitosamente con ID: {person_id}")
                    
                    if person_id:
                        # Verificar si se creó el registro en la tabla referrer
                        referrer_check = await connection.execute(
                            text("SELECT * FROM referrer WHERE person_id = :person_id"),
                            {"person_id": person_id}
                        )
                        referrer_row = referrer_check.fetchone()
                        
                        if referrer_row:
                            logger.info("✅ ¡EXITOSO! Se creó registro en tabla referrer")
                            logger.info(f"  - referrer_id: {referrer_row[0]}")
                            logger.info(f"  - person_id: {referrer_row[1]}")
                            logger.info(f"  - referral_code: {referrer_row[2]}")
                            logger.info(f"  - referrer_phone_number: {referrer_row[3]}")
                            logger.info(f"  - referrer_email: {referrer_row[4]}")
                            logger.info(f"  - commission_percentage: {referrer_row[7]}")
                            logger.info(f"  - notes: {referrer_row[8]}")
                        else:
                            logger.warning("⚠️ No se encontró registro en tabla referrer")
                            
                        # Verificar también la tabla person
                        person_check = await connection.execute(
                            text("SELECT person_id, first_name, last_name, person_role_id FROM person WHERE person_id = :person_id"),
                            {"person_id": person_id}
                        )
                        person_row = person_check.fetchone()
                        if person_row:
                            logger.info("✅ Persona verificada en tabla person:")
                            logger.info(f"  - person_id: {person_row[0]}")
                            logger.info(f"  - nombre: {person_row[1]} {person_row[2]}")
                            logger.info(f"  - person_role_id: {person_row[3]}")
                else:
                    logger.error(f"❌ Error en procedimiento almacenado: {stored_proc_result.get('message')}")
            else:
                logger.error("❌ No se obtuvo resultado del procedimiento almacenado")
                
    except Exception as e:
        logger.error(f"❌ Error probando inserción: {str(e)}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_referrer_insert_fixed())
