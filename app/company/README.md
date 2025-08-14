# Company Module

Este módulo contiene funcionalidades relacionadas con empresas y consultas de información empresarial.

## Funcionalidades

### 1. Consulta de RNC

El servicio permite consultar información de empresas en la DGII (Dirección General de Impuestos Internos) de República Dominicana. **El servicio busca primero en un archivo CSV local y luego en la web si no encuentra el RNC.**

#### Endpoints de RNC

```
GET /company/rnc/{rnc}
GET /company/rnc/{rnc}/with-company
```

#### Parámetros

- `rnc` (string): Número de RNC a consultar

#### Respuesta

**Cuando se encuentra en el CSV local:**
```json
{
  "rnc": "00110344256",
  "nombre": "BIENVENIDA BERIGUETE VERIGUETE DE MELO",
  "actividad_economica": "FABRICACIÓN DE MALETAS, BOLSOS DE MANO Y SIMILARES, ARTÍCULOS DE TALABARTERÍA Y ARTÍCULOS DE CUERO N.C.P.",
  "fecha_inicio": "05/04/2019",
  "estado": "ACTIVO",
  "regimen_pago": "NORMAL",
  "source": "csv"
}
```

**Cuando se encuentra en la web:**
```json
{
  "rnc": "101-1234567",
  "nombre": "EMPRESA EJEMPLO S.A.",
  "estado": "Activo",
  "source": "web"
}
```

**Con información de empresa en BD:**
```json
{
  "rnc": "132253256",
  "nombre": "GRUPO REYSA SRL",
  "actividad_economica": "SERVICIOS JURÍDICOS",
  "fecha_inicio": "08/02/2021",
  "estado": "ACTIVO",
  "regimen_pago": "NORMAL",
  "source": "csv",
  "company_in_db": true,
  "company_data": {
    "company_id": 1,
    "company_name": "GRUPO REYSA SRL",
    "company_rnc": "132253256",
    "mercantil_registry": "123456",
    "nationality": "Dominicana",
    "email": "info@gruporeysa.com",
    "phone": "809-555-0123",
    "website": "https://gruporeysa.com",
    "company_type": "SERVICIOS",
    "company_description": "Empresa de servicios jurídicos",
    "frontImagePath": "/images/front.jpg",
    "backImagePath": "/images/back.jpg",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

### 2. Gestión de Empresas

CRUD completo para gestionar empresas en la base de datos.

#### Endpoints de Empresas

```
POST   /company/                    # Crear empresa
GET    /company/                    # Listar empresas (con paginación)
GET    /company/{company_id}        # Obtener empresa por ID
PUT    /company/{company_id}        # Actualizar empresa
DELETE /company/{company_id}        # Eliminar empresa (soft delete)
GET    /company/{company_id}/with-relations  # Obtener empresa con direcciones y gerentes
```

#### Endpoints de Direcciones de Empresa

```
POST   /company/{company_id}/addresses       # Crear dirección
GET    /company/{company_id}/addresses       # Listar direcciones de empresa
GET    /company/addresses/{address_id}       # Obtener dirección por ID
PUT    /company/addresses/{address_id}       # Actualizar dirección
DELETE /company/addresses/{address_id}       # Eliminar dirección (soft delete)
```

#### Endpoints de Gerentes de Empresa

```
POST   /company/{company_id}/managers        # Crear gerente
GET    /company/{company_id}/managers        # Listar gerentes de empresa
GET    /company/managers/{manager_id}        # Obtener gerente por ID
PUT    /company/managers/{manager_id}        # Actualizar gerente
DELETE /company/managers/{manager_id}        # Eliminar gerente (soft delete)
```

#### Modelo de Datos de Empresa

```json
{
  "company_id": 1,
  "company_name": "EMPRESA EJEMPLO S.A.",
  "company_rnc": "101-1234567",
  "mercantil_registry": "123456",
  "nationality": "Dominicana",
  "email": "info@empresa.com",
  "phone": "809-555-0123",
  "website": "https://empresa.com",
  "company_type": "SERVICIOS",
  "company_description": "Descripción de la empresa",
  "frontImagePath": "/images/front.jpg",
  "backImagePath": "/images/back.jpg",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

#### Modelo de Datos de Dirección

```json
{
  "company_address_id": 1,
  "company_id": 1,
  "address_line1": "Calle Principal 123",
  "address_line2": "Edificio A, Piso 2",
  "city": "Santo Domingo",
  "postal_code": "10101",
  "address_type": "Business",
  "email": "direccion@empresa.com",
  "phone": "809-555-0124",
  "is_principal": true,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

#### Modelo de Datos de Gerente

```json
{
  "manager_id": 1,
  "company_id": 1,
  "manager_full_name": "Juan Pérez",
  "manager_position": "Director General",
  "manager_address": "Calle del Gerente 456",
  "manager_document_number": "402-1234567-8",
  "manager_nationality": "Dominicana",
  "manager_civil_status": "Casado",
  "is_principal": true,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "created_by": "uuid-person-id",
  "updated_by": "uuid-person-id"
}
```

### 3. Búsqueda y Filtros

```
GET /company/search/rnc/{rnc}       # Buscar empresas por RNC (parcial)
GET /company/type/{company_type}    # Obtener empresas por tipo
```

## Estructura de la Base de Datos

### Tabla company
- `company_id`: ID único de la empresa (IDENTITY)
- `company_name`: Nombre de la empresa (200 caracteres)
- `company_rnc`: Número de RNC (20 caracteres)
- `mercantil_registry`: Número de registro mercantil (20 caracteres)
- `nationality`: Nacionalidad de la empresa (100 caracteres)
- `email`: Correo electrónico (100 caracteres)
- `phone`: Teléfono (20 caracteres)
- `website`: Sitio web (100 caracteres)
- `company_type`: Tipo de empresa (30 caracteres)
- `company_description`: Descripción de la empresa (texto)
- `frontImagePath`: Ruta de imagen frontal (texto)
- `backImagePath`: Ruta de imagen trasera (texto)
- `is_active`: Estado activo/inactivo (boolean)
- `created_at`: Fecha de creación (timestamp)
- `updated_at`: Fecha de última actualización (timestamp)

### Tabla company_address
- `company_address_id`: ID único de la dirección (IDENTITY)
- `company_id`: ID de la empresa (foreign key)
- `address_line1`: Línea de dirección principal (100 caracteres)
- `address_line2`: Línea de dirección secundaria (100 caracteres)
- `city`: Ciudad (100 caracteres)
- `postal_code`: Código postal (20 caracteres)
- `address_type`: Tipo de dirección (20 caracteres, default 'Business')
- `email`: Correo electrónico de la dirección (100 caracteres)
- `phone`: Teléfono de la dirección (20 caracteres)
- `is_principal`: Si es la dirección principal (boolean)
- `is_active`: Estado activo/inactivo (boolean)
- `created_at`: Fecha de creación (timestamp)
- `updated_at`: Fecha de última actualización (timestamp)

### Tabla company_manager
- `manager_id`: ID único del gerente (IDENTITY)
- `company_id`: ID de la empresa (foreign key con CASCADE)
- `manager_full_name`: Nombre completo del gerente (200 caracteres)
- `manager_position`: Cargo del gerente (100 caracteres)
- `manager_address`: Dirección del gerente (texto)
- `manager_document_number`: Número de documento del gerente (50 caracteres)
- `manager_nationality`: Nacionalidad del gerente (50 caracteres)
- `manager_civil_status`: Estado civil del gerente (50 caracteres)
- `is_principal`: Si es el gerente principal (boolean)
- `is_active`: Estado activo/inactivo (boolean)
- `created_at`: Fecha de creación (timestamp)
- `updated_at`: Fecha de última actualización (timestamp)
- `created_by`: ID de la persona que creó el registro (UUID, foreign key a person)
- `updated_by`: ID de la persona que actualizó el registro (UUID, foreign key a person)

## Estructura del módulo

```
app/company/
├── __init__.py              # Inicialización del paquete
├── models.py                # Modelos Pydantic para validación
├── database.py              # Operaciones de base de datos
├── service.py               # Lógica de negocio (RNC + CRUD)
├── router.py                # Definición de endpoints de la API
├── sqlalchemy_models.py     # Modelos SQLAlchemy para las tablas
├── test_rnc.py              # Archivo de prueba para el servicio
└── README.md               # Esta documentación
```

## Dependencias

El módulo requiere las siguientes dependencias adicionales:

- `beautifulsoup4==4.12.2`: Para el parsing de HTML
- `httpx==0.28.1`: Para las peticiones HTTP asíncronas (ya incluida)
- `asyncpg==0.30.0`: Para operaciones de base de datos (ya incluida)

## Archivo CSV

El archivo `RNC_Contribuyentes_Actualizado_26_Jul_2025.csv` contiene:

- **RNC**: Número de identificación fiscal
- **RAZÓN SOCIAL**: Nombre de la empresa
- **ACTIVIDAD ECONÓMICA**: Tipo de actividad comercial
- **FECHA DE INICIO OPERACIONES**: Fecha de inicio de operaciones
- **ESTADO**: Estado del contribuyente
- **RÉGIMEN DE PAGO**: Tipo de régimen de pago

## Notas de Implementación

### Cambios en el Esquema

Los modelos han sido actualizados para reflejar la nueva estructura de base de datos:

1. **Campo RNC**: Cambió de `rnc` a `company_rnc`
2. **Campo RM**: Cambió de `rm` a `mercantil_registry`
3. **Nuevos campos**: Se agregaron `nationality`, `company_description`, `frontImagePath`, `backImagePath`
4. **Eliminado**: Se removió el campo `tax_id`

### Relaciones

- Una empresa puede tener múltiples direcciones
- Una empresa puede tener múltiples gerentes
- Las direcciones y gerentes tienen un campo `is_principal` para identificar los principales
- Los gerentes tienen referencias a la tabla `person` para auditoría

### Soft Delete

Todas las entidades implementan soft delete mediante el campo `is_active`, manteniendo la integridad referencial y permitiendo la recuperación de datos si es necesario.
