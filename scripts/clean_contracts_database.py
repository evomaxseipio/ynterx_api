#!/usr/bin/env python3
"""
Script para limpiar la base de datos de contratos y todas las tablas relacionadas.

ESTRATEGIA DE LIMPIEZA:
1. FASE 1 - Limpieza de tablas relacionadas con contratos (excepto personas):
   - Se limpian en orden inverso de dependencias para respetar foreign keys
   - Orden: payment_transactions → payment_schedule → contract_loan → contract_participant → 
            contract_bank_account → contract_property → contract → contracts → contract_paragraphs
   - También: property (si está relacionada con contratos)

2. FASE 2 - Limpieza de todas las demás tablas (excepto personas):
   - Se limpian todas las tablas restantes que no sean de personas ni ya limpiadas
   - Excluye: person, y otras tablas relacionadas con personas

3. RESET - Resetea secuencias de las tablas limpiadas

NOTA: Este script NO modifica tablas relacionadas con personas (person, etc.)
"""

import asyncio
import logging
import sys
from typing import List, Set
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Obtener la URL de la base de datos
DATABASE_URL = str(settings.DATABASE_ASYNC_URL).replace("?sslmode=require", "")

# Configurar opciones de conexión
connect_args = {}
if "sslmode" in str(settings.DATABASE_ASYNC_URL):
    connect_args["ssl"] = True

# Tablas relacionadas con contratos (en orden de eliminación - de más dependiente a menos)
CONTRACT_RELATED_TABLES = [
    "payment_transactions",      # Depende de payment_schedule
    "payment_schedule",          # Depende de contract_loan
    "contract_loan",             # Depende de contract
    "contract_participant",      # Depende de contract y person (person no se toca)
    "contract_bank_account",     # Depende de contract y person (person no se toca)
    "contract_property",         # Depende de contract y property
    "property",                  # Puede estar relacionada con contratos
    "contract",                  # Tabla principal de contratos
    "contracts",                 # Tabla alternativa de contratos (modelo Contract)
    "contract_paragraphs",       # Párrafos de contratos
]

# Tablas relacionadas con personas que NO deben tocarse
PERSON_TABLES = {
    "person",
    "person_address",
    "person_document",
    "person_phone",
    "person_email",
    "client",                    # Puede estar relacionada con person
    "investor",                  # Puede estar relacionada con person
    "customer",                  # Puede estar relacionada con person
    "user",                      # Usuarios del sistema
    "users",                     # Tabla alternativa de usuarios
    "referrer",                  # Referidores (relacionados con person)
    "witness",                   # Testigos (relacionados con person)
    "notary",                    # Notarios (relacionados con person)
}

# Tablas del sistema/configuración que generalmente no se deben limpiar
SYSTEM_TABLES = {
    "alembic_version",          # Control de migraciones
    "contract_type",            # Tipos de contrato (datos de referencia)
    "contract_status",          # Estados de contrato (datos de referencia)
    "contract_service",         # Servicios de contrato (datos de referencia)
    "person_type",              # Tipos de persona (datos de referencia)
    "gender",                   # Géneros (datos de referencia)
    "marital_status",           # Estados civiles (datos de referencia)
    "education_level",          # Niveles de educación (datos de referencia)
    "country",                  # Países (datos de referencia)
    "province",                 # Provincias (datos de referencia)
    "city",                     # Ciudades (datos de referencia)
    "document_type",            # Tipos de documento (datos de referencia)
}

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

async def clean_table(connection, table_name: str, dry_run: bool = False) -> bool:
    """Limpiar una tabla específica usando TRUNCATE CASCADE"""
    try:
        if dry_run:
            logger.info(f"🔍 [DRY RUN] Limpiaría tabla '{table_name}'")
            return True
            
        # Deshabilitar triggers temporalmente para evitar problemas con foreign keys
        await connection.execute(text(f"SET session_replication_role = replica;"))
        
        # Contar registros antes de limpiar
        count_result = await connection.execute(text(f"SELECT COUNT(*) FROM {table_name};"))
        count_before = count_result.scalar()
        
        # Truncate la tabla con CASCADE para manejar foreign keys
        await connection.execute(text(f"TRUNCATE TABLE {table_name} CASCADE;"))
        
        # Restaurar triggers
        await connection.execute(text(f"SET session_replication_role = DEFAULT;"))
        
        logger.info(f"✅ Tabla '{table_name}' limpiada exitosamente ({count_before} registros eliminados)")
        return True
    except Exception as e:
        logger.error(f"❌ Error limpiando tabla '{table_name}': {str(e)}")
        return False

async def reset_sequences_for_table(connection, table_name: str, dry_run: bool = False):
    """Resetear secuencias asociadas a una tabla específica"""
    try:
        # Obtener secuencias relacionadas con la tabla
        result = await connection.execute(text(f"""
            SELECT DISTINCT sequence_name 
            FROM information_schema.sequences 
            WHERE sequence_schema = 'public'
            AND (sequence_name LIKE '{table_name}_%seq'
            OR sequence_name LIKE '{table_name}_%_seq');
        """))
        
        sequences = [row[0] for row in result.fetchall()]
        
        for sequence in sequences:
            try:
                if dry_run:
                    logger.info(f"🔍 [DRY RUN] Resetearía secuencia '{sequence}'")
                else:
                    await connection.execute(text(f"ALTER SEQUENCE {sequence} RESTART WITH 1;"))
                    logger.info(f"✅ Secuencia '{sequence}' reseteada")
            except Exception as e:
                logger.warning(f"⚠️ Error reseteando secuencia '{sequence}': {str(e)}")
                
    except Exception as e:
        logger.warning(f"⚠️ Error obteniendo secuencias para tabla '{table_name}': {str(e)}")

async def clean_contracts_phase(connection, all_tables: Set[str], dry_run: bool = False):
    """FASE 1: Limpiar tablas relacionadas con contratos"""
    logger.info("\n" + "="*60)
    logger.info("FASE 1: LIMPIEZA DE TABLAS RELACIONADAS CON CONTRATOS")
    logger.info("="*60)
    
    # Filtrar solo las tablas que existen en la base de datos
    tables_to_clean = [table for table in CONTRACT_RELATED_TABLES if table in all_tables]
    
    if not tables_to_clean:
        logger.warning("⚠️ No se encontraron tablas de contratos para limpiar")
        return 0
    
    logger.info(f"📋 Tablas de contratos encontradas: {len(tables_to_clean)}")
    for table in tables_to_clean:
        logger.info(f"   - {table}")
    
    success_count = 0
    for table in tables_to_clean:
        if await clean_table(connection, table, dry_run):
            success_count += 1
            if not dry_run:
                await reset_sequences_for_table(connection, table, dry_run)
    
    logger.info(f"\n✅ Fase 1 completada: {success_count}/{len(tables_to_clean)} tablas limpiadas")
    return success_count

async def clean_other_tables_phase(connection, all_tables: Set[str], dry_run: bool = False):
    """FASE 2: Limpiar todas las demás tablas (excepto personas y sistema)"""
    logger.info("\n" + "="*60)
    logger.info("FASE 2: LIMPIEZA DE DEMÁS TABLAS")
    logger.info("="*60)
    
    # Determinar qué tablas limpiar en la Fase 2
    exclude_tables = PERSON_TABLES | SYSTEM_TABLES | set(CONTRACT_RELATED_TABLES)
    
    tables_to_clean = [table for table in all_tables if table not in exclude_tables]
    
    if not tables_to_clean:
        logger.info("ℹ️ No hay tablas adicionales para limpiar en Fase 2")
        return 0
    
    logger.info(f"📋 Tablas adicionales encontradas: {len(tables_to_clean)}")
    logger.info("📋 Tablas excluidas (personas y sistema):")
    for table in sorted(PERSON_TABLES | SYSTEM_TABLES):
        if table in all_tables:
            logger.info(f"   - {table} (excluida)")
    
    logger.info("\n📋 Tablas a limpiar en Fase 2:")
    for table in sorted(tables_to_clean):
        logger.info(f"   - {table}")
    
    success_count = 0
    for table in sorted(tables_to_clean):
        if await clean_table(connection, table, dry_run):
            success_count += 1
            if not dry_run:
                await reset_sequences_for_table(connection, table, dry_run)
    
    logger.info(f"\n✅ Fase 2 completada: {success_count}/{len(tables_to_clean)} tablas limpiadas")
    return success_count

async def clean_contracts_database(dry_run: bool = False, confirm: bool = True):
    """Función principal para limpiar la base de datos de contratos"""
    action = "[DRY RUN] Simular limpieza" if dry_run else "Iniciar limpieza"
    logger.info(f"🚀 {action} de la base de datos de contratos...")
    
    engine = create_async_engine(DATABASE_URL, connect_args=connect_args)
    
    try:
        async with engine.begin() as connection:
            # Obtener todas las tablas
            all_tables_list = await get_all_tables()
            all_tables = set(all_tables_list)
            
            if not all_tables_list:
                logger.warning("⚠️ No se encontraron tablas en la base de datos")
                return False
            
            logger.info(f"📊 Total de tablas en la base de datos: {len(all_tables_list)}")
            
            # Confirmar con el usuario (si no es dry run)
            if not dry_run and confirm:
                logger.info("\n⚠️ ADVERTENCIA: Esta operación eliminará TODOS los datos de:")
                logger.info("   - Tablas relacionadas con contratos")
                logger.info("   - Todas las demás tablas del sistema (excepto personas y tablas de referencia)")
                logger.info("\n📋 Tablas que se PRESERVARÁN:")
                for table in sorted(PERSON_TABLES | SYSTEM_TABLES):
                    if table in all_tables:
                        logger.info(f"   ✓ {table}")
                
                response = input("\n¿Estás seguro de que quieres continuar? (yes/no): ")
                if response.lower() not in ['yes', 'y', 'si', 's']:
                    logger.info("❌ Operación cancelada por el usuario")
                    return False
            
            # FASE 1: Limpiar tablas de contratos
            phase1_count = await clean_contracts_phase(connection, all_tables, dry_run)
            
            # FASE 2: Limpiar demás tablas
            phase2_count = await clean_other_tables_phase(connection, all_tables, dry_run)
            
            total_count = phase1_count + phase2_count
            
            logger.info("\n" + "="*60)
            logger.info("📊 RESUMEN DE LIMPIEZA")
            logger.info("="*60)
            logger.info(f"✅ Tablas de contratos limpiadas: {phase1_count}")
            logger.info(f"✅ Otras tablas limpiadas: {phase2_count}")
            logger.info(f"✅ Total de tablas limpiadas: {total_count}")
            logger.info(f"🛡️ Tablas preservadas: {len([t for t in all_tables if t in (PERSON_TABLES | SYSTEM_TABLES)])}")
            
            if dry_run:
                logger.info("\n💡 Este fue un DRY RUN. Para ejecutar realmente, ejecuta sin --dry-run")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error durante la limpieza: {str(e)}")
        raise
    finally:
        await engine.dispose()

async def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Script para limpiar la base de datos de contratos y tablas relacionadas"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simular la limpieza sin ejecutarla realmente"
    )
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="Ejecutar sin pedir confirmación (útil para scripts automatizados)"
    )
    
    args = parser.parse_args()
    
    try:
        success = await clean_contracts_database(
            dry_run=args.dry_run,
            confirm=not args.no_confirm
        )
        if success:
            logger.info("\n🎉 Proceso de limpieza completado exitosamente")
            sys.exit(0)
        else:
            logger.warning("\n⚠️ Proceso completado con advertencias")
            sys.exit(1)
    except Exception as e:
        logger.error(f"\n💥 Error fatal: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

