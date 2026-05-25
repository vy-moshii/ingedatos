from pydantic import BaseModel
from typing import Optional, List

# Esquemas base
class PaisBase(BaseModel):
    pais_id: str
    nombre: str

class CarteraAnualOut(BaseModel):
    pais_id: str
    anio: int
    tipo_productor: Optional[str]
    n_operaciones: Optional[int]
    valor_miles_usd: Optional[float]
    moneda_original: Optional[str]

class TipoCreditoOut(BaseModel):
    pais_id: str
    anio: int
    categoria: str
    tipo_productor: Optional[str]
    n_operaciones: Optional[int]
    valor_miles_usd: Optional[float]

class FindexOut(BaseModel):
    pais_id: str
    anio: int
    cuenta_digital: Optional[float]
    prestamo_banco_formal: Optional[float]
    brecha_digital_credito_pp: Optional[float]
    ratio_subsistencia_productivo: Optional[float]

class RuralUrbanoOut(BaseModel):
    pais_id: str
    anio: int
    zona: str
    cuenta_digital: Optional[float]
    prestamo_banco_formal: Optional[float]
    barrera_distancia: Optional[float]

class DiagnosticoOut(BaseModel):
    pais_id: str
    anio: int
    nivel_brecha: str
    puntaje_brecha: float
    texto_diagnostico: str
    ejes_recomendacion: Optional[str]

class RecomendacionOut(BaseModel):
    eje: str
    recomendacion: str
    accion: Optional[str]
    indicador_relacionado: Optional[str]

class FinagroDepartamentoOut(BaseModel):
    anio: int
    departamento: str
    tipo_productor: str
    n_operaciones: Optional[int]
    valor_MM_usd: Optional[float]

class FinagroCadenaOut(BaseModel):
    anio: int
    cadena: str
    tipo_productor: str
    n_operaciones: Optional[int]
    valor_MM_usd: Optional[float]

class FinagroSexoOut(BaseModel):
    anio: int
    sexo: str
    tipo_productor: str
    n_operaciones: Optional[int]
    valor_MM_usd: Optional[float]

class ComparativoItem(BaseModel):
    pais: str
    anio: int
    indicador: str
    valor: Optional[float]