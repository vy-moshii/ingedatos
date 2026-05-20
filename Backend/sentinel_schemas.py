"""
Schemas Pydantic para Sentinel Bank.
ObjectId de MongoDB se serializa siempre como str.
populate_by_name=True permite usar tanto el nombre del campo como su alias.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from bson import ObjectId


# ---------------------------------------------------------------------------
# Helper: convierte ObjectId → str al validar desde un documento Mongo
# ---------------------------------------------------------------------------

def _oid_to_str(v: Any) -> str:
    if isinstance(v, ObjectId):
        return str(v)
    return str(v)


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class SentinelModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


# ---------------------------------------------------------------------------
# Cliente
# ---------------------------------------------------------------------------

class ClienteOut(SentinelModel):
    id:           str        = Field(alias="_id")
    nombre:       str
    email:        str
    score_riesgo: float | None = Field(None, alias="scoreRiesgo")
    ips_conocidas: list[str] = Field(default_factory=list, alias="ipsConocidas")

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id(cls, v):
        return _oid_to_str(v)

    @field_validator("score_riesgo", mode="before")
    @classmethod
    def coerce_score(cls, v):
        return float(v) if v is not None else None

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


# ---------------------------------------------------------------------------
# Transacción
# ---------------------------------------------------------------------------

class TransaccionOut(SentinelModel):
    id:         str      = Field(alias="_id")
    cliente_id: str      = Field(alias="clienteId")
    monto:      float
    fecha:      datetime
    categoria:  str | None = None
    ip:         str | None = None
    sospechosa: bool     = False

    @field_validator("id", "cliente_id", mode="before")
    @classmethod
    def coerce_oids(cls, v):
        return _oid_to_str(v)

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


# ---------------------------------------------------------------------------
# Alerta
# ---------------------------------------------------------------------------

class AlertaOut(SentinelModel):
    id:          str      = Field(alias="_id")
    tipo_alerta: str      = Field(alias="tipoAlerta")
    cliente_id:  str      = Field(alias="clienteId")
    timestamp:   datetime
    detalle:     dict | str | None = None

    @field_validator("id", "cliente_id", mode="before")
    @classmethod
    def coerce_oids(cls, v):
        return _oid_to_str(v)

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


class AlertaCreate(SentinelModel):
    tipo_alerta: str  = Field(alias="tipoAlerta")
    cliente_id:  str  = Field(alias="clienteId")
    detalle:     dict | str | None = None

    model_config = ConfigDict(populate_by_name=True)


# ---------------------------------------------------------------------------
# Pánico
# ---------------------------------------------------------------------------

class PanicoRequest(SentinelModel):
    cliente_id: str = Field(alias="clienteId")

    model_config = ConfigDict(populate_by_name=True)


# ---------------------------------------------------------------------------
# Respuesta genérica
# ---------------------------------------------------------------------------

class MensajeOut(BaseModel):
    mensaje: str
    id:      str | None = None


class DeteccionOut(BaseModel):
    alertas_generadas: int
    detalle:           list[dict]
