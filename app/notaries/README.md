# Módulo de Notarios

Este módulo proporciona endpoints para obtener información de notarios utilizando la función almacenada `sp_get_notaries`.

## Endpoints

### GET /notaries
Obtiene todos los notarios registrados en el sistema.

**Respuesta:**
```json
{
    "success": true,
    "error": null,
    "message": "Notarios recuperados exitosamente",
    "data": {
        "notaries": [
            {
                "person": {
                    "first_name": "MAXIMILIANO",
                    "last_name": "MARTINS",
                    "middle_name": "SEIPIO",
                    "date_of_birth": "1976-05-18",
                    "gender": "MASCULINO",
                    "nationality_country": "REPÚBLICA DOMINICANA",
                    "marital_status": "SOLTERO",
                    "occupation": "INGENIERO DE SOFTWARE"
                },
                "person_document": {
                    "is_primary": true,
                    "document_type": "Cédula",
                    "document_number": "023-0093859-0",
                    "issuing_country_id": "1",
                    "document_issue_date": "2018-05-18",
                    "document_expiry_date": "2028-05-18"
                },
                "address": {
                    "address_line1": "CALLE DUARTE #456",
                    "address_line2": "EDIFICIO LOS PRADOS, APT 3B",
                    "city_id": "1",
                    "postal_code": "10210",
                    "address_type": "Casa",
                    "is_principal": true
                },
                "person_role_id": 8,
                "additional_data": {
                    "notary_id": "23139f29-17c6-49c0-a001-ca3510bb65be",
                    "license_number": "1278",
                    "jurisdiction": "San dbdhdhd",
                    "office_name": "bdbdhdh",
                    "professional_email": "",
                    "professional_phone": ""
                }
            }
        ]
    }
}
```

### GET /notaries/{notary_id}
Obtiene un notario específico por su ID.

**Parámetros:**
- `notary_id` (UUID): ID del notario a obtener

**Respuesta:**
Misma estructura que el endpoint anterior, pero con un solo notario en el array.

## Estructura de Datos

El módulo utiliza la función almacenada `sp_get_notaries` que devuelve:

- **Información personal**: nombre, apellido, fecha de nacimiento, género, etc.
- **Documento**: tipo de documento, número, fechas de emisión y expiración
- **Dirección**: dirección principal del notario
- **Datos adicionales**: número de licencia, jurisdicción, nombre de oficina, etc.

## Manejo de Errores

- `NOTARY_NOT_FOUND`: El notario con el ID especificado no existe
- `NO_DATA`: No se encontraron notarios con los criterios indicados
- `DATABASE_ERROR`: Error inesperado en la base de datos
- `PARSE_ERROR`: Error al procesar los datos JSON

## Autenticación

Todos los endpoints requieren autenticación mediante el token JWT. 