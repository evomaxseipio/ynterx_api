# ynterxal - API

API para la gestión de contratos y relaciones cliente-referidor.

## Estructura del Proyecto

```
ynterx_api/
├── app/                    # Código principal de la aplicación
├── test/                   # Archivos de prueba y testing
├── database/               # Scripts y stored procedures de BD
├── docs/                   # Documentación del proyecto
├── scripts/                # Scripts de utilidad y mantenimiento
├── venv/                   # Entorno virtual de Python
├── requirements.txt         # Dependencias del proyecto
├── pyproject.toml          # Configuración del proyecto
└── README.md              # Este archivo
```

## Requisitos

- [Python 3.12](https://www.python.org/downloads/release/python-3120/) o superior
- [uv](https://docs.astral.sh/uv/) para la gestión de paquetes y entornos de Python.
- [PostgreSQL](https://www.postgresql.org/) para la base de datos.

## Instalación

1. Clonar el repositorio
2. Crear entorno virtual: `python -m venv venv`
3. Activar entorno: `source venv/bin/activate`
4. Instalar dependencias: `pip install -r requirements.txt`
5. Configurar variables de entorno en `.env`
6. Ejecutar migraciones de base de datos

## Uso

### Iniciar el servidor
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Ejecutar pruebas
```bash
# Probar contrato con referidor
curl -X POST "http://localhost:8000/contracts/generate-complete" \
  -H "Content-Type: application/json" \
  -d @test/test_referrer_fixed.json
```

### Scripts de utilidad
```bash
# Limpiar base de datos
./scripts/clean_db.sh

# Formatear código
./scripts/format.sh

# Linting
./scripts/lint.sh
```

## Características Principales

- ✅ Generación de contratos con Word
- ✅ Gestión de participantes (clientes, inversores, testigos, referidores)
- ✅ Relaciones cliente-referidor automáticas
- ✅ Sistema de autenticación JWT
- ✅ Integración con Google Drive
- ✅ Manejo de propiedades y préstamos

## Documentación

- `docs/`: Documentación completa del proyecto
- `test/`: Archivos de prueba y ejemplos
- `database/`: Scripts de base de datos
- `scripts/`: Utilidades de mantenimiento

## Patrones de Conexión DB

### Pool de Conexiones

Para operaciones de lectura:

```python
@router.get("/{id}")
async def get_item(request: Request):
    pool = request.app.state.pool
    async with pool.acquire() as connection:
        return await Service.get_item(connection=connection)
```

**Uso**: Consultas SELECT, operaciones sin transacciones, alta concurrencia.

### Inyección de Dependencias

Para operaciones transaccionales:

```python
@router.post("/")
async def create_item(data: ItemCreate, db: DepDatabase):
    return await Service.create_item(data, connection=db)
```

**Uso**: INSERT/UPDATE/DELETE, operaciones multi-tabla, garantía de consistencia.

## Variables de Entorno

- `DATABASE_URL`: URL de la base de datos.
- `DATABASE_ASYNC_URL`: URL de la base de datos asincrónica.
- `ENVIRONMENT`: Indica el entorno de ejecución (LOCAL, PRODUCTION).
- `CORS_HEADERS`: Headers CORS.
- `CORS_ORIGINS`: Orígenes CORS.
- `AUTH_SESSION_TTL_SECONDS`: Tiempo de vida de la sesión de autenticación.
