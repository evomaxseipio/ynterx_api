# Script de Limpieza de Base de Datos de Contratos

## Descripción

Este script (`clean_contracts_database.py`) está diseñado para limpiar de forma segura y ordenada todas las tablas relacionadas con contratos, preservando las tablas de personas y tablas de referencia del sistema.

## Ubicación

```
scripts/clean_contracts_database.py
```

## ¿Qué hace el script?

El script ejecuta una limpieza en **DOS FASES** principales:

### FASE 1: Limpieza de Tablas Relacionadas con Contratos

Limpia las siguientes tablas en el orden especificado (respetando dependencias de foreign keys):

1. **payment_transactions** - Transacciones de pago (depende de payment_schedule)
2. **payment_schedule** - Cronograma de pagos (depende de contract_loan)
3. **contract_loan** - Información de préstamos (depende de contract)
4. **contract_participant** - Participantes en contratos (depende de contract y person)
5. **contract_bank_account** - Cuentas bancarias de contratos (depende de contract y person)
6. **contract_property** - Propiedades relacionadas con contratos (depende de contract y property)
7. **property** - Propiedades (puede estar relacionada con contratos)
8. **contract** - Tabla principal de contratos
9. **contracts** - Tabla alternativa de contratos (modelo Contract legacy)
10. **contract_paragraphs** - Párrafos de contratos

**Nota:** El script NO elimina las relaciones con `person`, solo limpia las tablas de contratos.

### FASE 2: Limpieza de Demás Tablas

Limpia todas las demás tablas del sistema que:
- NO sean tablas de personas
- NO sean tablas de referencia del sistema
- NO hayan sido limpiadas en la Fase 1

### Tablas que se PRESERVAN (NO se limpian)

#### Tablas de Personas
- `person`
- `person_address`
- `person_document`
- `person_phone`
- `person_email`
- `client`
- `investor`
- `customer`
- `user` / `users`
- `referrer`
- `witness`
- `notary`

#### Tablas del Sistema y Referencia
- `alembic_version` - Control de migraciones
- `contract_type` - Tipos de contrato (datos de referencia)
- `contract_status` - Estados de contrato (datos de referencia)
- `contract_service` - Servicios de contrato (datos de referencia)
- `person_type` - Tipos de persona (datos de referencia)
- `gender` - Géneros (datos de referencia)
- `marital_status` - Estados civiles (datos de referencia)
- `education_level` - Niveles de educación (datos de referencia)
- `country` - Países (datos de referencia)
- `province` - Provincias (datos de referencia)
- `city` - Ciudades (datos de referencia)
- `document_type` - Tipos de documento (datos de referencia)

## Características Adicionales

1. **Reseteo de Secuencias:** Después de limpiar cada tabla, resetea las secuencias asociadas (auto-incrementales) a 1
2. **Conteo de Registros:** Muestra cuántos registros se eliminaron de cada tabla
3. **Manejo de Foreign Keys:** Usa `TRUNCATE CASCADE` y deshabilita temporalmente triggers para manejar dependencias
4. **Modo Dry-Run:** Permite simular la limpieza sin ejecutarla realmente
5. **Confirmación de Usuario:** Solicita confirmación antes de ejecutar (excepto en modo automatizado)

## Uso

### Modo Interactivo (con confirmación)

```bash
python scripts/clean_contracts_database.py
```

### Modo Dry-Run (simular sin ejecutar)

```bash
python scripts/clean_contracts_database.py --dry-run
```

### Modo Automatizado (sin confirmación)

```bash
python scripts/clean_contracts_database.py --no-confirm
```

### Combinación Dry-Run + Automatizado

```bash
python scripts/clean_contracts_database.py --dry-run --no-confirm
```

## Ejemplo de Salida

```
🚀 Iniciar limpieza de la base de datos de contratos...
📊 Total de tablas en la base de datos: 25

⚠️ ADVERTENCIA: Esta operación eliminará TODOS los datos de:
   - Tablas relacionadas con contratos
   - Todas las demás tablas del sistema (excepto personas y tablas de referencia)

📋 Tablas que se PRESERVARÁN:
   ✓ city
   ✓ country
   ✓ person
   ...

============================================================
FASE 1: LIMPIEZA DE TABLAS RELACIONADAS CON CONTRATOS
============================================================
📋 Tablas de contratos encontradas: 10
   - payment_transactions
   - payment_schedule
   ...
✅ Tabla 'payment_transactions' limpiada exitosamente (150 registros eliminados)
...
✅ Fase 1 completada: 10/10 tablas limpiadas

============================================================
FASE 2: LIMPIEZA DE DEMÁS TABLAS
============================================================
📋 Tablas adicionales encontradas: 5
...
✅ Fase 2 completada: 5/5 tablas limpiadas

============================================================
📊 RESUMEN DE LIMPIEZA
============================================================
✅ Tablas de contratos limpiadas: 10
✅ Otras tablas limpiadas: 5
✅ Total de tablas limpiadas: 15
🛡️ Tablas preservadas: 10
```

## Precauciones

⚠️ **ADVERTENCIA IMPORTANTE:**

1. Este script **ELIMINA PERMANENTEMENTE** todos los datos de las tablas especificadas
2. Se recomienda **hacer un backup** de la base de datos antes de ejecutar
3. Usa `--dry-run` primero para ver qué tablas se limpiarían
4. Las tablas de personas se preservan, pero las relaciones con contratos se eliminan
5. Las tablas de referencia del sistema se preservan (tipos, estados, etc.)

## Requisitos

- Python 3.7+
- Acceso a la base de datos configurada en `app.config.settings`
- Permisos de escritura en la base de datos
- Dependencias del proyecto instaladas

## Notas Técnicas

- Usa `TRUNCATE CASCADE` para manejar foreign keys automáticamente
- Deshabilita temporalmente triggers con `session_replication_role = replica`
- Las secuencias se resetean a 1 después de limpiar cada tabla
- Usa transacciones para garantizar atomicidad

