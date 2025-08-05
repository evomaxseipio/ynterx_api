# Módulo de Testigos

Este módulo proporciona endpoints para obtener información de testigos utilizando la función almacenada `sp_get_witnesses`.

## Endpoints

### GET /witnesses
Obtiene todos los testigos registrados en el sistema.

**Respuesta:**
```json
{
    "success": true,
    "error": null,
    "message": "Testigos recuperados exitosamente",
    "data": {
        "witnesses": [
            {
                "person": {
                    "first_name": "JUAN",
                    "last_name": "PÉREZ",
                    "middle_name": "CARLOS",
                    "date_of_birth": "1985-03-15",
                    "gender": "MASCULINO",
                    "nationality_country": "REPÚBLICA DOMINICANA",
                    "marital_status": "CASADO",
                    "occupation": "ABOGADO"
                },
                "person_document": {
                    "is_primary": true,
                    "document_type": "Cédula",
                    "document_number": "123-4567890-1",
                    "issuing_country_id": "1",
                    "document_issue_date": "2020-01-15",
                    "document_expiry_date": "2030-01-15"
                },
                "address": {
                    "address_line1": "CALLE PRINCIPAL #123",
                    "address_line2": "EDIFICIO CENTRAL, APT 5A",
                    "city_id": "1",
                    "postal_code": "10101",
                    "address_type": "Casa",
                    "is_principal": true
                },
                "person_role_id": 9,
                "additional_data": {
                    "witness_id": "abc123-def456-ghi789-jkl012",
                    "relationship": "Amigo del contratante"
                }
            }
        ]
    }
}
```

### GET /witnesses/{witness_id}
Obtiene un testigo específico por su ID.

**Parámetros:**
- `witness_id` (UUID): ID del testigo a obtener

**Respuesta:**
Misma estructura que el endpoint anterior, pero con un solo testigo en el array.

## Estructura de Datos

El módulo utiliza la función almacenada `sp_get_witnesses` que devuelve:

- **Información personal**: nombre, apellido, fecha de nacimiento, género, etc.
- **Documento**: tipo de documento, número, fechas de emisión y expiración
- **Dirección**: dirección principal del testigo
- **Datos adicionales**: ID del testigo y relación con el contrato

## Diferencias con Notarios

A diferencia de los notarios, los testigos tienen:
- `person_role_id`: 9 (en lugar de 8 para notarios)
- `additional_data`: Solo incluye `witness_id` y `relationship` (sin licencia, jurisdicción, etc.)

## Manejo de Errores

- `WITNESS_NOT_FOUND`: El testigo con el ID especificado no existe
- `NO_DATA`: No se encontraron testigos con los criterios indicados
- `DATABASE_ERROR`: Error inesperado en la base de datos
- `PARSE_ERROR`: Error al procesar los datos JSON

## Autenticación

Todos los endpoints requieren autenticación mediante el token JWT. 