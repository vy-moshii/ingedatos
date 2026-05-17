# AgroCredit Insight — Backend API

FastAPI + PostgreSQL (SQLAlchemy) para análisis de inclusión financiera agrícola.

## Estructura

```
agroc/
├── app/
│   ├── main.py                  # Entrypoint FastAPI
│   ├── core/
│   │   ├── config.py            # Settings (.env)
│   │   └── errors.py            # Manejadores de error de PostgreSQL
│   ├── db/
│   │   └── session.py           # Engine y dependencia get_db
│   ├── schemas/
│   │   └── schemas.py           # Pydantic models (camelCase aliases)
│   ├── services/
│   │   └── agrocredit.py        # Consultas SQL (vistas + funciones)
│   └── routers/
│       └── agrocredit.py        # Endpoints FastAPI
├── sql/
│   └── views_and_functions.sql  # Vistas, funciones y trigger de auditoría
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

```bash
# 1. Clonar y entrar al directorio
cd agroc

# 2. Crear entorno virtual e instalar dependencias
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con los datos reales de la BD

# 4. Ejecutar el SQL en PostgreSQL (vistas, funciones, trigger)
psql -U usuario -d agrocredit -f sql/views_and_functions.sql

# 5. Levantar el servidor
uvicorn app.main:app --reload
```

## Endpoints

La documentación interactiva está disponible en:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**:      http://localhost:8000/redoc

### Dashboard (GET)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/paises` | Lista de países |
| GET | `/api/v1/indicadores-findex` | Indicadores Findex (`?paisId=&anio=`) |
| GET | `/api/v1/oferta-credito` | Oferta crediticia agrícola (`?paisId=&anio=`) |
| GET | `/api/v1/tipo-credito` | Distribución por tipo de crédito (`?paisId=&anio=`) |
| GET | `/api/v1/rural-urbano` | Brecha rural/urbano (`?paisId=&anio=`) |
| GET | `/api/v1/diagnostico/{pais_id}/{anio}` | Diagnóstico via `fn_diagnostico()` |
| GET | `/api/v1/recomendaciones/{pais_id}/{anio}` | Recomendaciones via `fn_recomendaciones()` |
| GET | `/api/v1/datos-faltantes` | Reporte de NULLs |
| GET | `/api/v1/metadatos` | Diccionario de variables (`?tabla=`) |

### Carga / Modificación (Indicadores Findex)

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/indicadores-findex` | Crear indicador (activa trigger de auditoría) |
| PUT | `/api/v1/indicadores-findex/{id}` | Actualizar parcialmente (activa trigger) |
| DELETE | `/api/v1/indicadores-findex/{id}` | Eliminar indicador |

### Sistema

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado de la API y la BD |

## Diseño

- **Vistas SQL**: cada GET de dashboard consume una vista `vw_*` definida en PostgreSQL.
- **Funciones PL/pgSQL**: `fn_diagnostico` y `fn_recomendaciones` encapsulan la lógica analítica.
- **Triggers**: `trg_audit_indicadores` se activa automáticamente en INSERT/UPDATE/DELETE sobre `indicadores_findex`.
- **Errores de PostgreSQL**: los `RAISE EXCEPTION` de triggers y funciones se capturan y devuelven como HTTP 422 con el mensaje original.
- **camelCase**: todos los endpoints devuelven JSON con nombres de campo en camelCase para compatibilidad con el frontend.
