# Módulo de Referentes

Este módulo proporciona endpoints para obtener información de referentes utilizando la función almacenada `sp_get_referrers`.

## Endpoints

### GET /referrers
Obtiene todos los referentes registrados en el sistema.

**Respuesta:**
```json
{
    "success": true,
    "error": null,
    "message": "Referentes recuperados exitosamente",
    "data": {
        "referrers": [
            {
                "person": {
                    "first_name": "MARÍA",
                    "last_name": "GONZÁLEZ",
                    "middle_name": "ISABEL",
                    "date_of_birth": "1980-07-22",
                    "gender": "FEMENINO",
                    "nationality_country": "REPÚBLICA DOMINICANA",
                    "marital_status": "CASADA",
                    "occupation": "GERENTE COMERCIAL"
                },
                "person_document": {
                    "is_primary": true,
                    "document_type": "Cédula",
                    "document_number": "987-6543210-9",
                    "issuing_country_id": "1",
                    "document_issue_date": "2019-03-10",
                    "document_expiry_date": "2029-03-10"
                },
                "address": {
                    "address_line1": "AVENIDA PRINCIPAL #789",
                    "address_line2": "TORRE EJECUTIVA, OFICINA 12",
                    "city_id": "1",
                    "postal_code": "10303",
                    "address_type": "Oficina",
                    "is_principal": true
                },
                "person_role_id": 10,
                "additional_data": {
                    "referrer_id": "def456-ghi789-jkl012-mno345",
                    "company_name": "EMPRESA EJEMPLO S.A.",
                    "position": "Gerente de Ventas",
                    "notes": "Referente confiable con buena trayectoria"
                }
            }
        ]
    }
}
```

### GET /referrers/{referrer_id}
Obtiene un referente específico por su ID.

**Parámetros:**
- `referrer_id` (UUID): ID del referente a obtener

**Respuesta:**
Misma estructura que el endpoint anterior, pero con un solo referente en el array.

## Estructura de Datos

El módulo utiliza la función almacenada `sp_get_referrers` que devuelve:

- **Información personal**: nombre, apellido, fecha de nacimiento, género, etc.
- **Documento**: tipo de documento, número, fechas de emisión y expiración
- **Dirección**: dirección principal del referente
- **Datos adicionales**: ID del referente, nombre de la empresa, posición y notas

## Diferencias con Otros Módulos

A diferencia de otros módulos, los referentes tienen:
- `person_role_id`: 10 (en lugar de 8 para notarios, 9 para testigos)
- `additional_data`: Incluye `referrer_id`, `company_name`, `position` y `notes`

## Manejo de Errores

- `REFERRER_NOT_FOUND`: El referente con el ID especificado no existe
- `NO_DATA`: No se encontraron referentes con los criterios indicados
- `DATABASE_ERROR`: Error inesperado en la base de datos
- `PARSE_ERROR`: Error al procesar los datos JSON

## Autenticación

Todos los endpoints requieren autenticación mediante el token JWT. 