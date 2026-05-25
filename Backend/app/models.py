from sqlalchemy import Column, Integer, String, Float, Date, Text, JSON
from sqlalchemy.sql.schema import ForeignKey
from app.database import Base

class Pais(Base):
    __tablename__ = "paises"
    pais_id = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    fuente_oferta = Column(String, nullable=False)
    url_fuente = Column(String)

class CarteraAnual(Base):
    __tablename__ = "cartera_anual"
    id = Column(Integer, primary_key=True)
    pais_id = Column(String, ForeignKey("paises.pais_id"))
    anio = Column(Integer)
    tipo_productor = Column(String)
    n_operaciones = Column(Integer)
    valor_miles_usd = Column(Float)
    tasa_cambio = Column(Float)
    moneda_original = Column(String)
    fuente = Column(String)
    notas = Column(String)

class TipoCredito(Base):
    __tablename__ = "tipo_credito"
    id = Column(Integer, primary_key=True)
    pais_id = Column(String, ForeignKey("paises.pais_id"))
    anio = Column(Integer)
    categoria = Column(String)
    tipo_productor = Column(String)
    n_operaciones = Column(Integer)
    valor_miles_usd = Column(Float)
    fuente = Column(String)
    notas = Column(String)

class Metadatos(Base):
    __tablename__ = "metadatos"
    id = Column(Integer, primary_key=True)
    pais_id = Column(String, ForeignKey("paises.pais_id"))
    fuente = Column(String)
    url = Column(String)
    fecha_descarga = Column(Date)
    formato_original = Column(String)
    anios_cubiertos = Column(String)
    observaciones = Column(Text)

# Tablas FINAGRO
class FinagroDepartamento(Base):
    __tablename__ = "finagro_departamento"
    id = Column(Integer, primary_key=True)
    pais_id = Column(String, ForeignKey("paises.pais_id"))
    anio = Column(Integer)
    departamento = Column(String)
    tipo_productor = Column(String)
    n_operaciones = Column(Integer)
    valor_MM_usd = Column(Float)
    valor_MM_cop = Column(Float)
    tasa_cambio = Column(Float)

class FinagroCadena(Base):
    __tablename__ = "finagro_cadena"
    id = Column(Integer, primary_key=True)
    pais_id = Column(String, ForeignKey("paises.pais_id"))
    anio = Column(Integer)
    cadena = Column(String)
    tipo_productor = Column(String)
    n_operaciones = Column(Integer)
    valor_MM_usd = Column(Float)
    valor_MM_cop = Column(Float)
    tasa_cambio = Column(Float)

class FinagroSexo(Base):
    __tablename__ = "finagro_sexo"
    id = Column(Integer, primary_key=True)
    pais_id = Column(String, ForeignKey("paises.pais_id"))
    anio = Column(Integer)
    sexo = Column(String)
    tipo_productor = Column(String)
    n_operaciones = Column(Integer)
    valor_MM_usd = Column(Float)
    valor_MM_cop = Column(Float)
    tasa_cambio = Column(Float)

# Global Findex
class IndicadoresFindex(Base):
    __tablename__ = "indicadores_findex"
    id = Column(Integer, primary_key=True)
    pais_id = Column(String, ForeignKey("paises.pais_id"))
    anio = Column(Integer)
    cuenta_financiera = Column(Float)
    cuenta_banco_formal = Column(Float)
    cuenta_digital = Column(Float)
    prestamo_banco_formal = Column(Float)
    prestamo_negocio = Column(Float)
    credito_subsistencia = Column(Float)
    pagos_agricolas_efectivo = Column(Float)
    # ... otros campos (se pueden agregar si se necesitan)

class IndicadoresRuralUrbano(Base):
    __tablename__ = "indicadores_rural_urbano"
    id = Column(Integer, primary_key=True)
    pais_id = Column(String, ForeignKey("paises.pais_id"))
    anio = Column(Integer)
    zona = Column(String)
    cuenta_financiera = Column(Float)
    cuenta_digital = Column(Float)
    prestamo_banco_formal = Column(Float)
    credito_subsistencia = Column(Float)
    barrera_distancia = Column(Float)

class DiagnosticoBrecha(Base):
    __tablename__ = "diagnostico_brecha"
    id = Column(Integer, primary_key=True)
    pais_id = Column(String, ForeignKey("paises.pais_id"))
    anio = Column(Integer)
    nivel_brecha = Column(String)
    puntaje_brecha = Column(Float)
    texto_diagnostico = Column(Text)

class Recomendaciones(Base):
    __tablename__ = "recomendaciones"
    id = Column(Integer, primary_key=True)
    pais_id = Column(String, ForeignKey("paises.pais_id"))
    anio = Column(Integer)
    nivel_brecha = Column(String)
    eje = Column(String)
    recomendacion = Column(String)
    accion = Column(String)
    indicador_relacionado = Column(String)

class DatosFaltantes(Base):
    __tablename__ = "datos_faltantes"
    id = Column(Integer, primary_key=True)
    pais_id = Column(String, ForeignKey("paises.pais_id"), nullable=True)
    fuente = Column(String)
    dato_faltante = Column(String)
    prioridad = Column(String)
    justificacion = Column(Text)
    estado = Column(String)

# Nota: Las vistas no se modelan como tablas, se consultan con texto SQL.