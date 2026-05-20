# Sentinel Bank — Backend API

Backend de detección de fraude financiero construido con **FastAPI** y **MongoDB (Motor async)**. Expone endpoints REST y un WebSocket de tiempo real para alimentar el dashboard de Sentinel Bank.

---

## Requisitos del sistema

| Herramienta | Versión mínima | Notas |
|---|---|---|
| Python | 3.11+ | Se requiere soporte de `match` y type hints modernos |
| MongoDB | 6.0+ | Requerido para `$setWindowFields` y Change Streams |
| pip | 23+ | Para resolver el lock de dependencias correctamente |

> MongoDB debe correr como **replica set** (aunque sea de un solo nodo) para que los Change Streams del WebSocket funcionen. Un standalone no soporta `watch()`.

---

## Dependencias

```
fastapi==0.115.12
uvicorn[standard]==0.34.2
motor==3.3.2
pymongo==4.6.1
pydantic==2.11.4
pydantic-settings==2.9.1
python-dotenv==1.1.0
websockets==12.0
```

No se usa SQLAlchemy ni psycopg2. Todo acceso a datos es async con Motor.

---

## Estructura del proyecto

```
sentinel/
├── app/
│   ├── main.py                  # Entrypoint FastAPI (lifespan, CORS, handlers)
│   ├── core/
│   │   ├── config.py            # Settings desde .env
│   │   └── errors.py            # Manejadores de error de MongoDB
│   ├── db/
│   │   └── session.py           # Cliente Motor singleton + get_db()
│   ├── schemas/
│   │   └── schemas.py           # Modelos Pydantic (ObjectId → str)
│   ├── services/
│   │   └── sentinel.py          # Pipelines de detección y lógica de negocio
│   └── routers/
│       └── sentinel.py          # Endpoints REST + WebSocket
├── .env.example
└── requirements.txt
```

---

## Configuración

### 1. Clonar e instalar dependencias

```bash
git clone <repo>
cd sentinel

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Variables de entorno

```bash
cp .env.example .env
```

Editar `.env`:

```env
MONGODB_URL=mongodb://localhost:27017
DB_NAME=sentinel_bank
```

Si MongoDB corre con autenticación o en otro host:

```env
MONGODB_URL=mongodb://usuario:contraseña@host:27017/?authSource=admin
DB_NAME=sentinel_bank
```

### 3. Configurar MongoDB como replica set (requerido para WebSocket)

Si usas una instancia local standalone, conviértela a replica set de un nodo:

```bash
# En mongosh
rs.initiate()
```

O levanta MongoDB directamente con la flag:

```bash
mongod --replSet rs0 --dbpath /data/db
```

### 4. Levantar el servidor

```bash
uvicorn app.main:app --reload
```

El servidor queda disponible en `http://localhost:8000`.

---

## Endpoints

La documentación interactiva completa está en:

- **Swagger UI** → `http://localhost:8000/docs`
- **ReDoc** → `http://localhost:8000/redoc`

### Clientes

| Método | Ruta | Parámetros | Descripción |
|---|---|---|---|
| GET | `/api/v1/clientes` | `skip`, `limit` | Lista paginada de clientes |
| GET | `/api/v1/clientes/{id}` | — | Cliente por ID |

### Transacciones

| Método | Ruta | Parámetros | Descripción |
|---|---|---|---|
| GET | `/api/v1/transacciones` | `skip`, `limit`, `clienteId`, `sospechosa` | Lista paginada con filtros opcionales |

### Alertas

| Método | Ruta | Parámetros | Descripción |
|---|---|---|---|
| GET | `/api/v1/alertas` | `skip`, `limit`, `tipoAlerta` | Lista paginada con filtro opcional por tipo |

### Detección de fraude

Todos los endpoints de detección **insertan alertas** en la colección `alertas` y responden:

```json
{
  "alertas_generadas": 3,
  "detalle": [...]
}
```

| Método | Ruta | Parámetros | Descripción |
|---|---|---|---|
| POST | `/api/v1/deteccion/velocity` | `umbral` (default 10) | Velocity attack: más de N transacciones en 300 s |
| POST | `/api/v1/deteccion/lavado` | `max_depth` (default 3) | Redes de lavado vía `$graphLookup` |
| POST | `/api/v1/deteccion/geo` | `vel_max_kmh` (default 900) | Anomalía geográfica por velocidad implícita |
| POST | `/api/v1/panico` | body `{ "clienteId": "..." }` | Mueve cliente a lista negra |

### Sistema

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Estado de la API y conexión a MongoDB |

### WebSocket

| Ruta | Descripción |
|---|---|
| `ws://localhost:8000/api/v1/ws/alertas` | Stream en tiempo real de nuevas alertas |

El WebSocket escucha el Change Stream de la colección `alertas`. Cada vez que se inserta una alerta (por cualquier endpoint de detección o pánico), el documento completo se envía como JSON a todos los clientes conectados. Si el stream falla internamente, el servidor cierra la conexión con código `1011`.

---

## Colecciones MongoDB esperadas

El backend **no crea ni modifica** el esquema de `clientes` ni `transacciones`. Estas colecciones deben existir previamente con la siguiente estructura:

**`clientes`**
```json
{
  "_id": ObjectId,
  "nombre": "string",
  "email": "string",
  "score_riesgo": 75.0,
  "ubicacion_habitual": { "type": "Point", "coordinates": [-74.08, 4.71] },
  "ips_conocidas": ["192.168.1.1"],
  "dispositivos_autorizados": ["device_id"]
}
```

**`transacciones`**
```json
{
  "_id": ObjectId,
  "cliente_id": ObjectId,
  "monto": 1500.00,
  "fecha": ISODate,
  "categoria": "transferencia",
  "ip": "192.168.1.1",
  "ubicacion": { "type": "Point", "coordinates": [-74.08, 4.71] },
  "destino_id": ObjectId,
  "tipo": "string",
  "sospechosa": false
}
```

La colección `alertas` y `lista_negra` las crea el backend automáticamente al insertar.

---

## Manejo de errores

| Error MongoDB | HTTP | Descripción |
|---|---|---|
| `DuplicateKeyError` | 422 | Documento con clave única duplicada |
| `OperationFailure` | 500 | Fallo en operación de MongoDB (mensaje original incluido) |
| `Exception` genérica | 500 | Error no manejado |

Los errores 404 (cliente no encontrado) y 422 de validación Pydantic se manejan directamente en los endpoints.
