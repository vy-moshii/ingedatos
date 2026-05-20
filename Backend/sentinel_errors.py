import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError, OperationFailure

logger = logging.getLogger(__name__)


async def duplicate_key_handler(request: Request, exc: DuplicateKeyError):
    logger.warning("DuplicateKeyError en %s: %s", request.url, exc.details)
    return JSONResponse(
        status_code=422,
        content={"detail": "Ya existe un documento con esa clave única.", "error": str(exc)},
    )


async def operation_failure_handler(request: Request, exc: OperationFailure):
    logger.error("OperationFailure en %s: %s", request.url, exc.details)
    return JSONResponse(
        status_code=500,
        content={"detail": exc.details or str(exc)},
    )


async def generic_error_handler(request: Request, exc: Exception):
    logger.exception("Error no manejado en %s", request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor."},
    )
