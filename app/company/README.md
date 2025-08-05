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
    "rnc": "132253256",
    "rm": "123456",
    "email": "info@gruporeysa.com",
    "phone": "809-555-0123",
    "website": "https://gruporeysa.com",
    "company_type": "SERVICIOS",
    "tax_id": "132253256",
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
GET    /company/by-rnc/{rnc}       # Obtener empresa por RNC
PUT    /company/{company_id}        # Actualizar empresa
DELETE /company/{company_id}        # Eliminar empresa (soft delete)
GET    /company/search/rnc/{rnc}   # Buscar empresas por RNC
GET    /company/type/{company_type} # Obtener empresas por tipo
```

#### Modelo de Empresa

```json
{
  "company_id": 1,
  "company_name": "GRUPO REYSA SRL",
  "rnc": "132253256",
  "rm": "123456",
  "email": "info@gruporeysa.com",
  "phone": "809-555-0123",
  "website": "https://gruporeysa.com",
  "company_type": "SERVICIOS",
  "tax_id": "132253256",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

#### Ejemplos de uso

**Crear empresa:**
```bash
curl -X POST "http://localhost:8000/company/" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "GRUPO REYSA SRL",
    "rnc": "132253256",
    "rm": "123456",
    "email": "info@gruporeysa.com",
    "phone": "809-555-0123",
    "website": "https://gruporeysa.com",
    "company_type": "SERVICIOS",
    "tax_id": "132253256"
  }'
```

**Listar empresas:**
```bash
curl -X GET "http://localhost:8000/company/?page=1&per_page=10&search=REYSA"
```

**Consultar RNC:**
```bash
curl -X GET "http://localhost:8000/company/rnc/132253256"
```

**Consultar RNC con verificación de empresa:**
```bash
curl -X GET "http://localhost:8000/company/rnc/132253256/with-company"
```

#### Códigos de error

- `404`: No se encontraron datos para el RNC consultado o empresa no encontrada
- `500`: Error interno del servidor
- `503`: El sitio web de la DGII no está disponible temporalmente
- `504`: Timeout al conectar con la DGII

## Funcionamiento

### 1. Búsqueda en CSV Local

El servicio primero busca en el archivo `RNC_Contribuyentes_Actualizado_26_Jul_2025.csv` ubicado en `app/utils/`. Este archivo contiene más de 1 millón de registros de RNC actualizados.

### 2. Búsqueda en la Web

Si el RNC no se encuentra en el CSV local, el servicio hace una consulta al sitio web oficial de la DGII.

### 3. Formatos de RNC Soportados

El servicio acepta diferentes formatos de RNC:

- `00110344256` (sin guiones)
- `001-1034425-6` (con guiones)
- `001 1034425 6` (con espacios)

### 4. Base de Datos

Las empresas se almacenan en la tabla `company` con los siguientes campos:

- `company_id`: ID único de la empresa
- `company_name`: Nombre de la empresa
- `rnc`: Número de RNC
- `rm`: Número de RM
- `email`: Correo electrónico
- `phone`: Teléfono
- `website`: Sitio web
- `company_type`: Tipo de empresa
- `tax_id`: ID fiscal
- `is_active`: Estado activo/inactivo
- `created_at`: Fecha de creación
- `updated_at`: Fecha de última actualización

## Estructura del módulo

```
app/company/
├── __init__.py          # Inicialización del paquete
├── models.py            # Modelos Pydantic para validación
├── database.py          # Operaciones de base de datos
├── service.py           # Lógica de negocio (RNC + CRUD)
├── router.py            # Definición de endpoints de la API
├── test_rnc.py          # Archivo de prueba para el servicio
└── README.md           # Esta documentación
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
- **ESTADO**: Estado actual del contribuyente (ACTIVO, SUSPENDIDO, etc.)
- **RÉGIMEN DE PAGO**: Tipo de régimen de pago

## Notas importantes

1. **Rendimiento**: Las búsquedas en CSV son mucho más rápidas que las consultas web
2. **Actualización**: El archivo CSV se actualiza periódicamente con datos de la DGII
3. **Fallback**: Si el CSV no está disponible, el servicio funciona solo con consultas web
4. **Codificación**: El archivo CSV usa codificación ISO-8859-1 (Latin-1)
5. **Memoria**: El CSV se carga en memoria para búsquedas rápidas (~104MB de datos)
6. **Soft Delete**: Las empresas se eliminan de forma lógica (is_active = false)
7. **Paginación**: Las listas de empresas incluyen paginación automática
8. **Búsqueda**: Soporte para búsqueda por nombre y RNC
