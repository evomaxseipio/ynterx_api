# GCapital - API

## Requisitos

* [Python 3.12](https://www.python.org/downloads/release/python-3120/) o superior
* [uv](https://docs.astral.sh/uv/) para la gestión de paquetes y entornos de Python.
* [PostgreSQL](https://www.postgresql.org/) para la base de datos.

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

* `DATABASE_URL`: URL de la base de datos.
* `DATABASE_ASYNC_URL`: URL de la base de datos asincrónica.
* `ENVIRONMENT`: Indica el entorno de ejecución (LOCAL, PRODUCTION).
* `CORS_HEADERS`: Headers CORS.
* `CORS_ORIGINS`: Orígenes CORS.
* `AUTH_SESSION_TTL_SECONDS`: Tiempo de vida de la sesión de autenticación.
