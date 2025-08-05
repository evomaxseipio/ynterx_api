# Scripts de Limpieza de Base de Datos

Este directorio contiene scripts para limpiar todas las tablas de la base de datos sin eliminarlas, solo removiendo los datos.

## Archivos

- `clean_database.py` - Script interactivo con confirmación del usuario
- `clean_database_auto.py` - Script automatizado sin confirmación
- `clean_db.sh` - Script bash para facilitar la ejecución

## Uso

### Opción 1: Script Bash (Recomendado)

```bash
# Limpieza interactiva (con confirmación)
./scripts/clean_db.sh

# Limpieza automática (sin confirmación)
./scripts/clean_db.sh --auto
```

### Opción 2: Scripts Python Directos

```bash
# Limpieza interactiva
python scripts/clean_database.py

# Limpieza automática
python scripts/clean_database_auto.py
```

## ¿Qué hace el script?

1. **Conecta a la base de datos** usando la configuración de `app/config.py`
2. **Obtiene todas las tablas** del esquema público
3. **Limpia cada tabla** usando `TRUNCATE CASCADE` para manejar foreign keys
4. **Resetea todas las secuencias** para que empiecen desde 1
5. **Mantiene la estructura** de las tablas intacta

## Características

- ✅ **Seguro**: Solo elimina datos, no estructura
- ✅ **Maneja Foreign Keys**: Usa CASCADE para evitar errores
- ✅ **Resetea Secuencias**: Los IDs vuelven a empezar desde 1
- ✅ **Logging Detallado**: Muestra el progreso de cada operación
- ✅ **Manejo de Errores**: Continúa aunque algunas tablas fallen
- ✅ **Confirmación**: Versión interactiva pide confirmación

## Tablas que se limpian

El script detecta automáticamente todas las tablas del esquema público, incluyendo:

- `users`
- `user_roles`
- `person`
- `gender`
- `marital_status`
- `education_level`
- `country`
- `city`
- `address`
- `referrer`
- `contract`
- `contract_participant`
- `contract_loan`
- `property`
- `contract_property`
- `contract_bank_account`
- `contract_paragraphs`
- Y cualquier otra tabla que exista

## Precauciones

⚠️ **ADVERTENCIA**: Este script elimina TODOS los datos de TODAS las tablas.

- Hacer backup antes de ejecutar
- Verificar que estés en el entorno correcto
- Asegurar que la configuración de base de datos sea correcta

## Troubleshooting

### Error de conexión
```
❌ Error durante la limpieza: connection to server at...
```
- Verificar que la base de datos esté activa
- Verificar las credenciales en `.env`

### Error de permisos
```
❌ Error limpiando tabla 'users': permission denied
```
- Verificar que el usuario de BD tenga permisos de TRUNCATE
- Verificar que no haya conexiones activas a las tablas

### Error de foreign keys
```
❌ Error limpiando tabla 'contract_participant': foreign key violation
```
- El script maneja esto automáticamente con CASCADE
- Si persiste, verificar que no haya triggers personalizados

## Ejemplo de Output

```
🚀 Iniciando limpieza de la base de datos...
📋 Encontradas 15 tablas para limpiar:
   - address
   - city
   - contract
   - contract_bank_account
   - contract_loan
   - contract_participant
   - contract_paragraphs
   - contract_property
   - country
   - education_level
   - gender
   - marital_status
   - person
   - property
   - referrer
   - user_roles
   - users

¿Estás seguro de que quieres limpiar TODAS las tablas? (yes/no): yes

✅ Tabla 'address' limpiada exitosamente
✅ Tabla 'city' limpiada exitosamente
✅ Tabla 'contract' limpiada exitosamente
...
🔄 Reseteando secuencias...
✅ Secuencia 'user_roles_user_role_id_seq' reseteada
✅ Secuencia 'property_property_id_seq' reseteada

✅ Limpieza completada:
   - Tablas limpiadas: 17/17
   - Secuencias reseteadas
🎉 Proceso de limpieza completado exitosamente
``` 