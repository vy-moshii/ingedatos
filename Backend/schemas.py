"""
Schemas Pydantic para AgroCredit Insight.
Los alias (by_alias=True en los routers) aseguran que el JSON
devuelto use camelCase compatible con el frontend.
"""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class CamelModel(BaseModel):
    """Base con alias camelCase auto-generados."""
    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def _to_camel(cls, name: str) -> str:
        parts = name.split("_")
        return parts[0] + "".join(p.capitalize() for p in parts[1:])


# ---------------------------------------------------------------------------
# Países
# ---------------------------------------------------------------------------

class PaisOut(CamelModel):
    pais_id: int     = Field(alias="paisId")
    nombre:  str
    codigo:  str | None = None
    region:  str | None = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


# ---------------------------------------------------------------------------
# Indicadores Findex
# ---------------------------------------------------------------------------

class IndicadorFindexBase(CamelModel):
    pais_id:                        int          = Field(alias="paisId")
    anio:                           int
    cuenta_bancaria_pct:            float | None = Field(None, alias="cuentaBancariaPct")
    credito_formal_pct:             float | None = Field(None, alias="creditoFormalPct")
    ahorro_formal_pct:              float | None = Field(None, alias="ahorroFormalPct")
    uso_movil_financiero_pct:       float | None = Field(None, alias="usoMovilFinancieroPct")
    brecha_genero_cuenta_pct:       float | None = Field(None, alias="brechaGeneroCuentaPct")
    poblacion_rural_sin_cuenta_pct: float | None = Field(None, alias="poblacionRuralSinCuentaPct")

    model_config = ConfigDict(populate_by_name=True)


class IndicadorFindexCreate(IndicadorFindexBase):
    pass


class IndicadorFindexUpdate(CamelModel):
    """Todos los campos opcionales para actualizaciones parciales."""
    cuenta_bancaria_pct:            float | None = Field(None, alias="cuentaBancariaPct")
    credito_formal_pct:             float | None = Field(None, alias="creditoFormalPct")
    ahorro_formal_pct:              float | None = Field(None, alias="ahorroFormalPct")
    uso_movil_financiero_pct:       float | None = Field(None, alias="usoMovilFinancieroPct")
    brecha_genero_cuenta_pct:       float | None = Field(None, alias="brechaGeneroCuentaPct")
    poblacion_rural_sin_cuenta_pct: float | None = Field(None, alias="poblacionRuralSinCuentaPct")

    model_config = ConfigDict(populate_by_name=True)


class IndicadorFindexOut(IndicadorFindexBase):
    id: int

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


# ---------------------------------------------------------------------------
# Oferta de crédito
# ---------------------------------------------------------------------------

class OfertaCreditoOut(CamelModel):
    id:                  int
    pais_id:             int          = Field(alias="paisId")
    anio:                int
    institucion:         str | None   = None
    tipo_institucion:    str | None   = Field(None, alias="tipoInstitucion")
    cartera_agricola_mn: float | None = Field(None, alias="carteraAgricolaMn")
    num_creditos:        int   | None = Field(None, alias="numCreditos")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


# ---------------------------------------------------------------------------
# Tipo de crédito
# ---------------------------------------------------------------------------

class TipoCreditoOut(CamelModel):
    id:                int
    pais_id:           int          = Field(alias="paisId")
    anio:              int
    tipo_credito:      str | None   = Field(None, alias="tipoCredito")
    monto_promedio_mn: float | None = Field(None, alias="montoPromedioMn")
    participacion_pct: float | None = Field(None, alias="participacionPct")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


# ---------------------------------------------------------------------------
# Rural / Urbano
# ---------------------------------------------------------------------------

class RuralUrbanoOut(CamelModel):
    id:                         int
    pais_id:                    int          = Field(alias="paisId")
    anio:                       int
    zona:                       str | None   = None
    acceso_credito_formal_pct:  float | None = Field(None, alias="accesoCreditoFormalPct")
    uso_credito_informal_pct:   float | None = Field(None, alias="usoCreditoInformalPct")
    tasa_bancarizacion_pct:     float | None = Field(None, alias="tasaBancarizacionPct")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


# ---------------------------------------------------------------------------
# Diagnóstico  (resultado de función SQL)
# ---------------------------------------------------------------------------

class DiagnosticoOut(CamelModel):
    pais_id:                    int          = Field(alias="paisId")
    anio:                       int
    nivel_inclusion:            str | None   = Field(None, alias="nivelInclusion")
    score_inclusion:            float | None = Field(None, alias="scoreInclusion")
    brecha_genero:              str | None   = Field(None, alias="brechaGenero")
    acceso_rural:               str | None   = Field(None, alias="accesRural")
    oferta_credito_agricola:    str | None   = Field(None, alias="ofertaCreditoAgricola")
    resumen:                    str | None   = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


# ---------------------------------------------------------------------------
# Recomendaciones  (resultado de función SQL)
# ---------------------------------------------------------------------------

class RecomendacionOut(CamelModel):
    orden:          int
    categoria:      str | None = None
    recomendacion:  str | None = None
    prioridad:      str | None = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


# ---------------------------------------------------------------------------
# Datos faltantes
# ---------------------------------------------------------------------------

class DatoFaltanteOut(CamelModel):
    pais_id:    int   = Field(alias="paisId")
    pais:       str | None = None
    anio:       int | None = None
    tabla:      str | None = None
    campo:      str | None = None
    total_nulos: int | None = Field(None, alias="totalNulos")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


# ---------------------------------------------------------------------------
# Metadatos
# ---------------------------------------------------------------------------

class MetadatoOut(CamelModel):
    tabla:       str | None = None
    campo:       str | None = None
    descripcion: str | None = None
    unidad:      str | None = None
    fuente:      str | None = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


# ---------------------------------------------------------------------------
# Respuestas genéricas
# ---------------------------------------------------------------------------

class MensajeOut(BaseModel):
    mensaje: str
    id:      int | None = None
