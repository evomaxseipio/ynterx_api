# Carpeta de Pruebas

Esta carpeta contiene todos los archivos de prueba para el sistema de contratos.

## Contenido

### Archivos JSON de prueba
- `test_*.json`: Archivos JSON con datos de prueba para diferentes escenarios de contratos
- `json_*.json`: Archivos JSON corregidos y definitivos para pruebas

### Scripts de prueba
- `test_*.py`: Scripts de Python para probar diferentes funcionalidades del sistema

## Uso

Los archivos de esta carpeta se utilizan para:
1. Probar la generación de contratos
2. Validar la inserción de datos en la base de datos
3. Verificar la funcionalidad de client_referrer
4. Probar diferentes tipos de contratos y participantes

## Ejemplos

```bash
# Probar un contrato con referidor
curl -X POST "http://localhost:8000/contracts/generate-complete" \
  -H "Content-Type: application/json" \
  -d @test/test_referrer_fixed.json
```
