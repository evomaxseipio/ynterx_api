# Implementación: Almacenamiento de URLs de Google Drive en Base de Datos

## Resumen del Problema

**Problema identificado**: Las URLs de Google Drive NO se estaban almacenando en la base de datos cuando los archivos se subían exitosamente a Google Drive.

## Análisis del Código Original

### ✅ Lo que SÍ funcionaba:
1. **Generación de contratos**: El sistema generaba correctamente los contratos
2. **Subida a Google Drive**: Los archivos se subían exitosamente a Google Drive
3. **Devolución de URLs**: El servicio de Google Drive devolvía las URLs correctamente:
   - `drive_link`: Enlace a la carpeta del contrato
   - `drive_view_link`: Enlace de vista del archivo
   - `drive_folder_id`: ID de la carpeta
   - `drive_file_id`: ID del archivo

### ❌ Lo que NO funcionaba:
1. **Almacenamiento en BD**: Las URLs de Google Drive NO se guardaban en la base de datos
2. **Método incompleto**: El método `update_contract_with_document_info` solo actualizaba rutas locales

## Solución Implementada

### 1. Modificación del método `update_contract_with_document_info`

**Archivo**: `app/contracts/contract_creation_service.py`

**Cambios realizados**:
- Agregada lógica para determinar qué URLs usar (Google Drive vs rutas locales)
- Priorización de URLs de Google Drive cuando están disponibles
- Logs de confirmación para verificar qué URLs se almacenan

```python
# Antes (solo rutas locales):
file_path=document_result.get("path"),
folder_path=document_result.get("folder_path"),

# Después (URLs de Google Drive cuando están disponibles):
file_path = document_result.get("path")  # Ruta local por defecto
folder_path = document_result.get("folder_path")  # Ruta local por defecto

# Si Google Drive está habilitado y se subió exitosamente, usar URLs de Drive
if document_result.get("drive_success") and document_result.get("drive_link"):
    file_path = document_result.get("drive_view_link", file_path)
    folder_path = document_result.get("drive_link", folder_path)
```

### 2. Mejora del método `update_contract` en el servicio de generación

**Archivo**: `app/contracts/services/contract_generation_service.py`

**Cambios realizados**:
- Agregado soporte para Google Drive en actualizaciones de contratos
- Incluidas rutas locales en la respuesta para compatibilidad
- Integración con el servicio de Google Drive para actualizaciones

### 3. Agregado endpoint de actualización en el router principal

**Archivo**: `app/contracts/router.py`

**Cambios realizados**:
- Agregado endpoint `PATCH /{contract_id}/update`
- Integración con el método `update_contract_with_document_info`
- Manejo de errores apropiado

## Campos de Base de Datos Utilizados

Se utilizan los campos existentes en la tabla `contract`:

- **`file_path`**: Almacena la URL del archivo (Google Drive o ruta local)
- **`folder_path`**: Almacena la URL de la carpeta (Google Drive o ruta local)

### Mapeo de URLs:

| Campo BD | Con Google Drive | Sin Google Drive |
|----------|------------------|------------------|
| `file_path` | `drive_view_link` | Ruta local del archivo |
| `folder_path` | `drive_link` | Ruta local de la carpeta |

## Flujo de Funcionamiento

### 1. Creación de Contrato
```
1. Generar documento → 2. Subir a Google Drive → 3. Actualizar BD con URLs
```

### 2. Actualización de Contrato
```
1. Regenerar documento → 2. Subir a Google Drive → 3. Actualizar BD con URLs
```

## Verificación de Implementación

### Script de Prueba Ejecutado
Se creó y ejecutó un script de prueba que confirmó:

✅ **Con Google Drive habilitado**:
- `file_path`: `https://drive.google.com/file/d/1XYZ789GHI012/view?usp=sharing`
- `folder_path`: `https://drive.google.com/drive/folders/1ABC123DEF456`

✅ **Sin Google Drive habilitado**:
- `file_path`: `/app/generated_contracts/contract_xxx/contract_xxx.docx`
- `folder_path`: `/app/generated_contracts/contract_xxx`

## Logs de Confirmación

El sistema ahora muestra logs claros indicando qué URLs se almacenan:

```
✅ URLs de Google Drive almacenadas en BD:
   - file_path: https://drive.google.com/file/d/1XYZ789GHI012/view?usp=sharing
   - folder_path: https://drive.google.com/drive/folders/1ABC123DEF456
```

O:

```
📁 Rutas locales almacenadas en BD:
   - file_path: /app/generated_contracts/contract_xxx/contract_xxx.docx
   - folder_path: /app/generated_contracts/contract_xxx
```

## Beneficios de la Implementación

1. **Flexibilidad**: Funciona tanto con Google Drive como sin él
2. **Compatibilidad**: Usa campos existentes de la base de datos
3. **Trazabilidad**: Logs claros para verificar qué URLs se almacenan
4. **Consistencia**: Mismo comportamiento en creación y actualización
5. **Robustez**: Manejo de errores apropiado

## Configuración Requerida

Para habilitar Google Drive, asegurar que las siguientes variables de entorno estén configuradas:

```bash
USE_GOOGLE_DRIVE=true
GOOGLE_DRIVE_FOLDER_ID=your_folder_id
```

## Conclusión

✅ **PROBLEMA RESUELTO**: Las URLs de Google Drive ahora se almacenan correctamente en la base de datos en los campos `file_path` y `folder_path` de la tabla `contract`.

✅ **VERIFICACIÓN COMPLETADA**: El script de prueba confirmó que la lógica funciona correctamente tanto con Google Drive habilitado como deshabilitado.

✅ **IMPLEMENTACIÓN COMPLETA**: Los cambios cubren creación y actualización de contratos, con logs de confirmación y manejo de errores apropiado.
