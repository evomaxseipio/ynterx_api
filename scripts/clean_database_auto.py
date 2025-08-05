#!/usr/bin/env python3
"""
Script automatizado para limpiar todas las tablas de la base de datos
Versión sin confirmación del usuario para uso en scripts automatizados
"""

import asyncio
import logging
import sys
from typing import List
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Obtener la URL de la base de datos
DATABASE_URL = str(settings.DATABASE_ASYNC_URL).replace("?sslmode=require", "")

# Configurar opciones de conexión
connect_args = {}
if "sslmode" in str(settings.DATABASE_ASYNC_URL):
    connect_args["ssl"] = True

async def get_all_tables() -> List[str]:
    """Obtener todas las tablas de la base de datos"""
    engine = create_async_engine(DATABASE_URL, connect_args=connect_args)
    
    async with engine.connect() as connection:
        # Obtener todas las tablas del esquema público
        result = await connection.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """))
        
        tables = [row[0] for row in result.fetchall()]
        await engine.dispose()
        return tables

async def clean_table(connection, table_name: str) -> bool:
    """Limpiar una tabla específica usando TRUNCATE CASCADE"""
    try:
        # Deshabilitar triggers temporalmente para evitar problemas con foreign keys
        await connection.execute(text(f"SET session_replication_role = replica;"))
        
        # Truncar la tabla con CASCADE para manejar foreign keys
        await connection.execute(text(f"TRUNCATE TABLE {table_name} CASCADE;"))
        
        # Restaurar triggers
        await connection.execute(text(f"SET session_replication_role = DEFAULT;"))
        
        logger.info(f"✅ Tabla '{table_name}' limpiada exitosamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error limpiando tabla '{table_name}': {str(e)}")
        return False

async def reset_sequences(connection):
    """Resetear todas las secuencias de la base de datos"""
    try:
        # Obtener todas las secuencias
        result = await connection.execute(text("""
            SELECT sequence_name 
            FROM information_schema.sequences 
            WHERE sequence_schema = 'public';
        """))
        
        sequences = [row[0] for row in result.fetchall()]
        
        for sequence in sequences:
            try:
                await connection.execute(text(f"ALTER SEQUENCE {sequence} RESTART WITH 1;"))
                logger.info(f"✅ Secuencia '{sequence}' reseteada")
            except Exception as e:
                logger.warning(f"⚠️ Error reseteando secuencia '{sequence}': {str(e)}")
                
    except Exception as e:
        logger.error(f"❌ Error reseteando secuencias: {str(e)}")

async def clean_database_auto():
    """Función principal para limpiar toda la base de datos (automática)"""
    logger.info("🚀 Iniciando limpieza automática de la base de datos...")
    
    engine = create_async_engine(DATABASE_URL, connect_args=connect_args)
    
    try:
        async with engine.begin() as connection:
            # Obtener todas las tablas
            tables = await get_all_tables()
            
            if not tables:
                logger.warning("⚠️ No se encontraron tablas para limpiar")
                return True
            
            logger.info(f"📋 Encontradas {len(tables)} tablas para limpiar")
            
            # Limpiar cada tabla
            success_count = 0
            for table in tables:
                success = await clean_table(connection, table)
                if success:
                    success_count += 1
            
            # Resetear secuencias
            logger.info("🔄 Reseteando secuencias...")
            await reset_sequences(connection)
            
            logger.info(f"✅ Limpieza completada: {success_count}/{len(tables)} tablas limpiadas")
            return success_count == len(tables)
            
    except Exception as e:
        logger.error(f"❌ Error durante la limpieza: {str(e)}")
        raise
    finally:
        await engine.dispose()

async def main():
    """Función principal"""
    try:
        success = await clean_database_auto()
        if success:
            logger.info("🎉 Proceso de limpieza completado exitosamente")
            sys.exit(0)
        else:
            logger.error("⚠️ Algunas tablas no pudieron ser limpiadas")
            sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Error fatal: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 