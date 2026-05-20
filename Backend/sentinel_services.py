"""
Servicios de detección de fraude para Sentinel Bank.
Todas las funciones son async y reciben db (AsyncIOMotorDatabase).
"""
from __future__ import annotations
import logging
import math
from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _make_alerta(tipo: str, cliente_id, detalle: dict) -> dict:
    return {
        "tipo_alerta": tipo,
        "cliente_id": ObjectId(str(cliente_id)) if not isinstance(cliente_id, ObjectId) else cliente_id,
        "timestamp": _now(),
        "detalle": detalle,
    }


def _serialize(doc: dict) -> dict:
    """Convierte ObjectIds a str para serialización JSON."""
    out = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat()
        elif isinstance(v, dict):
            out[k] = _serialize(v)
        elif isinstance(v, list):
            out[k] = [_serialize(i) if isinstance(i, dict) else (str(i) if isinstance(i, ObjectId) else i) for i in v]
        else:
            out[k] = v
    return out


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia en km entre dos coordenadas (lat/lon en grados)."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


# ---------------------------------------------------------------------------
# Lectura genérica paginada
# ---------------------------------------------------------------------------

async def get_clientes(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 20) -> list[dict]:
    cursor = db.clientes.find({}, skip=skip, limit=limit)
    return [_serialize(doc) async for doc in cursor]


async def get_cliente_by_id(db: AsyncIOMotorDatabase, cliente_id: str) -> dict | None:
    try:
        oid = ObjectId(cliente_id)
    except Exception:
        return None
    doc = await db.clientes.find_one({"_id": oid})
    return _serialize(doc) if doc else None


async def get_transacciones(
    db: AsyncIOMotorDatabase,
    skip: int = 0,
    limit: int = 20,
    cliente_id: str | None = None,
    sospechosa: bool | None = None,
) -> list[dict]:
    filtro: dict = {}
    if cliente_id:
        try:
            filtro["cliente_id"] = ObjectId(cliente_id)
        except Exception:
            filtro["cliente_id"] = cliente_id
    if sospechosa is not None:
        filtro["sospechosa"] = sospechosa
    cursor = db.transacciones.find(filtro, skip=skip, limit=limit).sort("fecha", -1)
    return [_serialize(doc) async for doc in cursor]


async def get_alertas(
    db: AsyncIOMotorDatabase,
    skip: int = 0,
    limit: int = 20,
    tipo_alerta: str | None = None,
) -> list[dict]:
    filtro: dict = {}
    if tipo_alerta:
        filtro["tipo_alerta"] = tipo_alerta
    cursor = db.alertas.find(filtro, skip=skip, limit=limit).sort("timestamp", -1)
    return [_serialize(doc) async for doc in cursor]


# ---------------------------------------------------------------------------
# a) Velocity Attack
# Detecta clientes con más de `umbral` transacciones en ventana de 300 s.
# ---------------------------------------------------------------------------

async def detectar_velocity_attack(
    db: AsyncIOMotorDatabase,
    umbral: int = 10,
) -> list[dict]:
    pipeline = [
        # Agrupa transacciones por cliente en ventanas de 300 s
        {
            "$setWindowFields": {
                "partitionBy": "$cliente_id",
                "sortBy": {"fecha": 1},
                "output": {
                    "count_ventana": {
                        "$sum": 1,
                        "window": {"range": [-300, 0], "unit": "second"},
                    }
                },
            }
        },
        {"$match": {"count_ventana": {"$gte": umbral}}},
        {
            "$group": {
                "_id": "$cliente_id",
                "max_count": {"$max": "$count_ventana"},
                "transacciones": {"$push": "$_id"},
            }
        },
    ]

    alertas_insertadas: list[dict] = []

    async for doc in db.transacciones.aggregate(pipeline):
        alerta = _make_alerta(
            tipo="velocity_attack",
            cliente_id=doc["_id"],
            detalle={
                "max_transacciones_en_ventana": doc["max_count"],
                "umbral": umbral,
                "transacciones_ids": [str(t) for t in doc.get("transacciones", [])],
            },
        )
        result = await db.alertas.insert_one(alerta)
        alerta["_id"] = result.inserted_id
        alertas_insertadas.append(_serialize(alerta))

    logger.info("velocity_attack: %d alertas generadas", len(alertas_insertadas))
    return alertas_insertadas


# ---------------------------------------------------------------------------
# b) Redes de lavado
# Usa $graphLookup para recorrer la red de transferencias hasta max_depth.
# ---------------------------------------------------------------------------

async def detectar_lavado(
    db: AsyncIOMotorDatabase,
    max_depth: int = 3,
) -> list[dict]:
    # Solo transacciones con destino_id definido
    pipeline = [
        {"$match": {"destino_id": {"$exists": True, "$ne": None}}},
        {
            "$graphLookup": {
                "from": "transacciones",
                "startWith": "$destino_id",
                "connectFromField": "destino_id",
                "connectToField": "cliente_id",
                "as": "red",
                "maxDepth": max_depth,
                "depthField": "profundidad",
            }
        },
        # Filtra nodos que forman ciclo (origen aparece en la red) o score alto
        {
            "$lookup": {
                "from": "clientes",
                "localField": "cliente_id",
                "foreignField": "_id",
                "as": "cliente_info",
            }
        },
        {"$unwind": {"path": "$cliente_info", "preserveNullAndEmptyArrays": True}},
        {
            "$match": {
                "$or": [
                    # Ciclo: cliente_id aparece como destino_id en algún nodo de la red
                    {"$expr": {"$in": ["$cliente_id", "$red.destino_id"]}},
                    # Cliente de alto riesgo
                    {"cliente_info.score_riesgo": {"$gt": 80}},
                ]
            }
        },
        {
            "$group": {
                "_id": "$cliente_id",
                "nodos_red": {"$sum": {"$size": "$red"}},
                "score_riesgo": {"$first": "$cliente_info.score_riesgo"},
            }
        },
    ]

    alertas_insertadas: list[dict] = []

    async for doc in db.transacciones.aggregate(pipeline):
        alerta = _make_alerta(
            tipo="red_lavado",
            cliente_id=doc["_id"],
            detalle={
                "nodos_en_red": doc.get("nodos_red", 0),
                "score_riesgo": doc.get("score_riesgo"),
                "max_depth": max_depth,
            },
        )
        result = await db.alertas.insert_one(alerta)
        alerta["_id"] = result.inserted_id
        alertas_insertadas.append(_serialize(alerta))

    logger.info("red_lavado: %d alertas generadas", len(alertas_insertadas))
    return alertas_insertadas


# ---------------------------------------------------------------------------
# c) Anomalía geográfica
# Compara ubicaciones consecutivas de cada cliente y calcula velocidad.
# ---------------------------------------------------------------------------

async def detectar_anomalia_geo(
    db: AsyncIOMotorDatabase,
    vel_max_kmh: float = 900.0,
) -> list[dict]:
    pipeline = [
        # Solo transacciones con ubicación GeoJSON tipo Point
        {"$match": {"ubicacion.type": "Point", "ubicacion.coordinates": {"$size": 2}}},
        {"$sort": {"cliente_id": 1, "fecha": 1}},
        {
            "$group": {
                "_id": "$cliente_id",
                "puntos": {
                    "$push": {
                        "fecha": "$fecha",
                        "coords": "$ubicacion.coordinates",
                        "tx_id": "$_id",
                    }
                },
            }
        },
    ]

    alertas_insertadas: list[dict] = []

    async for doc in db.transacciones.aggregate(pipeline):
        puntos = doc["puntos"]
        cliente_id = doc["_id"]

        for i in range(1, len(puntos)):
            p_prev = puntos[i - 1]
            p_curr = puntos[i]

            coords_prev = p_prev["coords"]   # [lon, lat]
            coords_curr = p_curr["coords"]

            # MongoDB GeoJSON: [longitud, latitud]
            lon1, lat1 = coords_prev[0], coords_prev[1]
            lon2, lat2 = coords_curr[0], coords_curr[1]

            distancia_km = _haversine_km(lat1, lon1, lat2, lon2)

            dt = p_curr["fecha"] - p_prev["fecha"]
            dt_horas = dt.total_seconds() / 3600.0

            if dt_horas <= 0:
                continue

            velocidad_kmh = distancia_km / dt_horas

            if velocidad_kmh > vel_max_kmh:
                alerta = _make_alerta(
                    tipo="anomalia_geografica",
                    cliente_id=cliente_id,
                    detalle={
                        "velocidad_kmh": round(velocidad_kmh, 2),
                        "vel_max_kmh": vel_max_kmh,
                        "distancia_km": round(distancia_km, 2),
                        "tx_anterior": str(p_prev["tx_id"]),
                        "tx_actual": str(p_curr["tx_id"]),
                        "coords_anterior": coords_prev,
                        "coords_actual": coords_curr,
                    },
                )
                result = await db.alertas.insert_one(alerta)
                alerta["_id"] = result.inserted_id
                alertas_insertadas.append(_serialize(alerta))

    logger.info("anomalia_geografica: %d alertas generadas", len(alertas_insertadas))
    return alertas_insertadas


# ---------------------------------------------------------------------------
# d) Botón de pánico → lista negra
# ---------------------------------------------------------------------------

async def mover_a_lista_negra(
    db: AsyncIOMotorDatabase,
    cliente_id: str,
) -> dict:
    try:
        oid = ObjectId(cliente_id)
    except Exception:
        raise ValueError(f"cliente_id inválido: {cliente_id}")

    cliente = await db.clientes.find_one({"_id": oid})
    if cliente is None:
        raise LookupError(f"Cliente {cliente_id} no encontrado.")

    # Mover a lista_negra
    cliente["fecha_bloqueo"] = _now()
    cliente["motivo"] = "panico_manual"
    await db.lista_negra.insert_one(cliente)

    # Eliminar de clientes
    await db.clientes.delete_one({"_id": oid})

    # Registrar alerta
    alerta = _make_alerta(
        tipo="lista_negra",
        cliente_id=oid,
        detalle={"motivo": "panico_manual", "fecha_bloqueo": cliente["fecha_bloqueo"].isoformat()},
    )
    result = await db.alertas.insert_one(alerta)

    logger.warning("Cliente %s movido a lista negra", cliente_id)
    return {"mensaje": f"Cliente {cliente_id} movido a lista negra.", "alerta_id": str(result.inserted_id)}
