from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError
from psycopg2.errors import (
    RaiseException,
    ForeignKeyViolation,
    UniqueViolation,
    NotNullViolation,
    CheckViolation,
)
import logging

logger = logging.getLogger(__name__)


def _pg_error_detail(exc: Exception) -> str | None:
    """Extrae el mensaje RAISE EXCEPTION de PostgreSQL si existe."""
    orig = getattr(exc, "orig", None)
    if orig is None:
        return None
    return str(orig.pgerror or orig.args[0] if orig.args else None)


async def integrity_error_handler(request: Request, exc: IntegrityError):
    orig = getattr(exc, "orig", None)
    detail = _pg_error_detail(exc)

    if isinstance(orig, UniqueViolation):
        msg = "Ya existe un registro con esos valores únicos."
    elif isinstance(orig, ForeignKeyViolation):
        msg = "La referencia a otra tabla no existe."
    elif isinstance(orig, NotNullViolation):
        msg = "Un campo obligatorio está vacío."
    elif isinstance(orig, CheckViolation):
        msg = "Un valor no cumple la restricción CHECK de la base de datos."
    elif isinstance(orig, RaiseException):
        # Mensajes de triggers / funciones PL/pgSQL
        msg = detail or "Error de validación en la base de datos."
    else:
        msg = detail or "Error de integridad en la base de datos."

    logger.warning("IntegrityError en %s: %s", request.url, detail)
    return JSONResponse(status_code=422, content={"detail": msg})


async def operational_error_handler(request: Request, exc: OperationalError):
    logger.error("OperationalError en %s: %s", request.url, exc)
    return JSONResponse(
        status_code=503,
        content={"detail": "No se pudo conectar a la base de datos. Intenta más tarde."},
    )


async def programming_error_handler(request: Request, exc: ProgrammingError):
    detail = _pg_error_detail(exc)
    logger.error("ProgrammingError en %s: %s", request.url, detail)
    return JSONResponse(
        status_code=500,
        content={"detail": detail or "Error interno en la base de datos."},
    )


async def generic_error_handler(request: Request, exc: Exception):
    logger.exception("Error no manejado en %s", request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor."},
    )
