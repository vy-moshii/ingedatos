from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# Esquemas base para catálogos
class PaisBase(BaseModel):
    pais_id: str
    nombre: str

class PaisOut(PaisBase):
    fuente_oferta: Optional[str] = None
    url_fuente: Optional[str] = None

# Esquemas para cartera_anual (oferta)
class CarteraAnualOut(BaseModel):
    pais_id: str
    anio: int
    tipo_productor: Optional[str]
    n_operaciones: Optional[int]
    valor_miles_usd: Optional[float]
    moneda_original: Optional[str]
    tasa_cambio: Optional[float]
    fuente: Optional[str]
    notas: Optional[str]

# Esquema para /oferta (con nombre de país)
class OfertaResponse(BaseModel):
    pais: str
    pais_id: str
    anio: int
    fuente: str
    tipo_productor: Optional[str] = None
    n_operaciones: Optional[int] = None
    valor_miles_usd: Optional[float] = None
    moneda_original: Optional[str] = None
    notas: Optional[str] = None

# Esquema para /tipo_credito
class TipoCreditoResponse(BaseModel):
    pais: str
    pais_id: str
    anio: int
    fuente: str
    categoria: str
    tipo_productor: Optional[str] = None
    n_operaciones: Optional[int] = None
    valor_miles_usd: Optional[float] = None
    notas: Optional[str] = None

# Esquema para /findex (vista v_findex)
class FindexResponse(BaseModel):
    pais: str
    pais_id: str
    anio: int
    cuenta_financiera: Optional[float] = None
    cuenta_banco_formal: Optional[float] = None
    cuenta_digital: Optional[float] = None
    prestamo_banco_formal: Optional[float] = None
    prestamo_negocio: Optional[float] = None
    credito_subsistencia: Optional[float] = None
    brecha_digital_credito_pp: Optional[float] = None
    ratio_subsistencia_productivo: Optional[float] = None
    efectivo_agricola_pct: Optional[float] = None
    pagos_agricolas_efectivo: Optional[float] = None
    internet: Optional[float] = None
    smartphone: Optional[float] = None
    # otros campos opcionales
    cuenta_dinero_movil: Optional[float] = None
    cuenta_inactiva: Optional[float] = None
    pago_digital: Optional[float] = None
    ahorro_formal_movil: Optional[float] = None
    movil_info_agricola: Optional[float] = None
    prestamo_cualquier_fuente: Optional[float] = None
    prestamo_proveedor_movil: Optional[float] = None
    prestamo_familia_amigos: Optional[float] = None
    prestamo_recibido_movil: Optional[float] = None
    pagos_agricolas_total: Optional[float] = None
    pagos_agricolas_cuenta: Optional[float] = None
    pagos_agricolas_banco: Optional[float] = None

# Esquema para /rural_urban
class RuralUrbanResponse(BaseModel):
    pais: str
    pais_id: str
    anio: int
    zona: str
    cuenta_financiera: Optional[float] = None
    cuenta_digital: Optional[float] = None
    prestamo_banco_formal: Optional[float] = None
    credito_subsistencia: Optional[float] = None
    smartphone: Optional[float] = None
    internet: Optional[float] = None
    barrera_costo: Optional[float] = None
    barrera_fondos: Optional[float] = None
    barrera_distancia: Optional[float] = None
    dificultad_emergencia: Optional[float] = None

# Esquema para /diagnosticos
class DiagnosticoResponse(BaseModel):
    pais: str
    pais_id: str
    anio: int
    nivel_brecha: str
    puntaje_brecha: float
    brecha_digital_credito_pp: Optional[float] = None
    cambio_credito_formal_pp: Optional[float] = None
    ratio_subsistencia_productivo: Optional[float] = None
    efectivo_agricola_pct: Optional[float] = None
    texto_diagnostico: Optional[str] = None

# Esquema para /missing
class MissingDataResponse(BaseModel):
    pais: Optional[str]
    fuente: str
    dato_faltante: str
    prioridad: str
    por_que_importa: str

# Esquema para /fuentes
class FuenteResponse(BaseModel):
    fuente: str
    pais: str
    periodo: str
    uso: str
    estado: str

# Esquema para /diccionario
class DiccionarioResponse(BaseModel):
    grupo: str
    indicador: str
    codigo: str
    descripcion: str

# Esquemas para microdatos FINAGRO (opcionales, por si se usan)
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

# Esquema comparativo (si se requiere)
class ComparativoItem(BaseModel):
    pais: str
    anio: int
    indicador: str
    valor: Optional[float]