"""
Sentinel Bank — Backend API
FastAPI + Motor (async MongoDB)
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import DuplicateKeyError, OperationFailure

from app.core.errors import (
    duplicate_key_handler,
    operation_failure_handler,
    generic_error_handler,
)
from app.db.session import init_client, close_client, check_connection
from app.routers.sentinel import router


# ---------------------------------------------------------------------------
# Lifespan: iniciar/cerrar Motor al arrancar/detener la aplicación
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_client()
    yield
    close_client()


# ---------------------------------------------------------------------------
# Aplicación
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Sentinel Bank API",
    description=(
        "Backend de detección de fraude financiero para Sentinel Bank. "
        "Detecta velocity attacks, redes de lavado y anomalías geográficas "
        "usando pipelines de agregación sobre MongoDB."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Manejadores de error de MongoDB
# ---------------------------------------------------------------------------

app.add_exception_handler(DuplicateKeyError,  duplicate_key_handler)
app.add_exception_handler(OperationFailure,   operation_failure_handler)
app.add_exception_handler(Exception,          generic_error_handler)

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

app.include_router(router, prefix="/api/v1")

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Sistema"], summary="Estado de la API y MongoDB")
async def health():
    db_ok = await check_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
    }
