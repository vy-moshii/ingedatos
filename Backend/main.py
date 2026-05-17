"""
AgroCredit Insight — Backend API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError

from app.core.errors import (
    integrity_error_handler,
    operational_error_handler,
    programming_error_handler,
    generic_error_handler,
)
from app.db.session import check_connection
from app.routers.agrocredit import router

# ---------------------------------------------------------------------------
# Instancia principal
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AgroCredit Insight API",
    description=(
        "Backend de la plataforma AgroCredit Insight para análisis de inclusión "
        "financiera agrícola. Consume vistas SQL, llama funciones PL/pgSQL y "
        "permite cargar/modificar indicadores Findex."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS  (ajustar origins en producción)
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Manejadores de error de PostgreSQL
# ---------------------------------------------------------------------------

app.add_exception_handler(IntegrityError,    integrity_error_handler)
app.add_exception_handler(OperationalError,  operational_error_handler)
app.add_exception_handler(ProgrammingError,  programming_error_handler)
app.add_exception_handler(Exception,         generic_error_handler)

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

app.include_router(router, prefix="/api/v1")

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Sistema"], summary="Estado de la API y la base de datos")
def health():
    db_ok = check_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
    }
