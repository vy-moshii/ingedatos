"""
Router Sentinel Bank — REST + WebSocket.
"""
from __future__ import annotations
import json
import logging
from datetime import datetime
from bson import ObjectId

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from sentinel_session import get_db
from sentinel_schemas import (
    ClienteOut,
    TransaccionOut,
    AlertaOut,
    PanicoRequest,
    MensajeOut,
    DeteccionOut,
)
import sentinel_services as svc

logger = logging.getLogger(__name__)
router = APIRouter()

DbDep = AsyncIOMotorDatabase  # alias de tipo


def _validate_list(rows: list[dict], schema_cls):
    """Valida lista de dicts contra un schema Pydantic, serializa con alias."""
    result = []
    for r in rows:
        try:
            result.append(schema_cls.model_validate(r).model_dump(by_alias=True))
        except Exception as e:
            logger.warning("Validación fallida para doc %s: %s", r.get("_id"), e)
    return result


# ============================================================
# Clientes
# ============================================================

@router.get(
    "/clientes",
    response_model=list[ClienteOut],
    summary="Listar clientes (paginado)",
    tags=["Clientes"],
)
async def get_clientes(
    db: AsyncIOMotorDatabase = Depends(get_db),
    skip:  int = Query(0,  ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    rows = await svc.get_clientes(db, skip=skip, limit=limit)
    return _validate_list(rows, ClienteOut)


@router.get(
    "/clientes/{id}",
    response_model=ClienteOut,
    summary="Obtener cliente por ID",
    tags=["Clientes"],
)
async def get_cliente(id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    doc = await svc.get_cliente_by_id(db, id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cliente {id} no encontrado.")
    return ClienteOut.model_validate(doc).model_dump(by_alias=True)


# ============================================================
# Transacciones
# ============================================================

@router.get(
    "/transacciones",
    response_model=list[TransaccionOut],
    summary="Listar transacciones (paginado + filtros)",
    tags=["Transacciones"],
)
async def get_transacciones(
    db:         AsyncIOMotorDatabase = Depends(get_db),
    skip:       int        = Query(0, ge=0),
    limit:      int        = Query(20, ge=1, le=100),
    cliente_id: str | None = Query(None, alias="clienteId"),
    sospechosa: bool | None = Query(None),
):
    rows = await svc.get_transacciones(db, skip=skip, limit=limit, cliente_id=cliente_id, sospechosa=sospechosa)
    return _validate_list(rows, TransaccionOut)


# ============================================================
# Alertas
# ============================================================

@router.get(
    "/alertas",
    response_model=list[AlertaOut],
    summary="Listar alertas (paginado + filtro tipo)",
    tags=["Alertas"],
)
async def get_alertas(
    db:          AsyncIOMotorDatabase = Depends(get_db),
    skip:        int        = Query(0, ge=0),
    limit:       int        = Query(20, ge=1, le=100),
    tipo_alerta: str | None = Query(None, alias="tipoAlerta"),
):
    rows = await svc.get_alertas(db, skip=skip, limit=limit, tipo_alerta=tipo_alerta)
    return _validate_list(rows, AlertaOut)


# ============================================================
# Detección
# ============================================================

@router.post(
    "/deteccion/velocity",
    response_model=DeteccionOut,
    summary="Detectar Velocity Attack",
    tags=["Detección"],
)
async def deteccion_velocity(
    db:     AsyncIOMotorDatabase = Depends(get_db),
    umbral: int = Query(10, ge=1, description="Transacciones en 300 s para disparar alerta"),
):
    """
    Detecta clientes con más de `umbral` transacciones en una ventana de 300 segundos.
    Inserta una alerta tipo **velocity_attack** por cada cliente detectado.
    """
    alertas = await svc.detectar_velocity_attack(db, umbral=umbral)
    return DeteccionOut(alertas_generadas=len(alertas), detalle=alertas)


@router.post(
    "/deteccion/lavado",
    response_model=DeteccionOut,
    summary="Detectar redes de lavado",
    tags=["Detección"],
)
async def deteccion_lavado(
    db:        AsyncIOMotorDatabase = Depends(get_db),
    max_depth: int = Query(3, ge=1, le=10, description="Profundidad máxima del grafo"),
):
    """
    Recorre la red de transferencias con `$graphLookup` hasta `max_depth` niveles.
    Detecta ciclos y nodos con score_riesgo > 80. Alerta tipo **red_lavado**.
    """
    alertas = await svc.detectar_lavado(db, max_depth=max_depth)
    return DeteccionOut(alertas_generadas=len(alertas), detalle=alertas)


@router.post(
    "/deteccion/geo",
    response_model=DeteccionOut,
    summary="Detectar anomalías geográficas",
    tags=["Detección"],
)
async def deteccion_geo(
    db:          AsyncIOMotorDatabase = Depends(get_db),
    vel_max_kmh: float = Query(900.0, gt=0, description="Velocidad máxima razonable en km/h"),
):
    """
    Calcula la velocidad implícita entre transacciones consecutivas de cada cliente.
    Si supera `vel_max_kmh` → alerta tipo **anomalia_geografica**.
    """
    alertas = await svc.detectar_anomalia_geo(db, vel_max_kmh=vel_max_kmh)
    return DeteccionOut(alertas_generadas=len(alertas), detalle=alertas)


@router.post(
    "/panico",
    response_model=MensajeOut,
    summary="Botón de pánico — mover cliente a lista negra",
    tags=["Detección"],
)
async def boton_panico(payload: PanicoRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Mueve el cliente a la colección `lista_negra`, lo elimina de `clientes`
    y registra una alerta tipo **lista_negra**.
    """
    try:
        result = await svc.mover_a_lista_negra(db, cliente_id=payload.cliente_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return MensajeOut(mensaje=result["mensaje"], id=result.get("alerta_id"))


# ============================================================
# WebSocket — Change Stream en colección alertas
# ============================================================

def _make_serializable(doc: dict) -> dict:
    """Convierte ObjectId y datetime a str para json.dumps."""
    out = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat()
        elif isinstance(v, dict):
            out[k] = _make_serializable(v)
        elif isinstance(v, list):
            out[k] = [
                _make_serializable(i) if isinstance(i, dict)
                else (str(i) if isinstance(i, ObjectId) else i)
                for i in v
            ]
        else:
            out[k] = v
    return out


@router.websocket("/ws/alertas")
async def ws_alertas(websocket: WebSocket, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Escucha el Change Stream de la colección `alertas`.
    Envía cada INSERT nuevo como JSON al cliente WebSocket conectado.
    Cierra con código 1011 si el stream falla.
    """
    await websocket.accept()
    logger.info("WebSocket /ws/alertas: cliente conectado")

    try:
        async with db.alertas.watch(
            [{"$match": {"operationType": "insert"}}],
            full_document="updateLookup",
        ) as stream:
            async for change in stream:
                full_doc = change.get("fullDocument", {})
                serializable = _make_serializable(full_doc)
                await websocket.send_text(json.dumps(serializable))

    except WebSocketDisconnect:
        logger.info("WebSocket /ws/alertas: cliente desconectado")

    except Exception as e:
        logger.error("WebSocket /ws/alertas: error en stream — %s", e)
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
