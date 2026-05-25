from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.database import get_db
from app import models, schemas

router = APIRouter()

# Mapeo de código de país a nombre para uso interno
CODIGO_A_PAIS = {"COL": "Colombia", "ECU": "Ecuador", "PRY": "Paraguay"}

# ---------------------------
# Endpoints existentes (catálogos)
# ---------------------------
@router.get("/paises", response_model=List[schemas.PaisOut])
def get_paises(db: Session = Depends(get_db)):
    return db.query(models.Pais).all()

@router.get("/cartera/{pais_id}", response_model=List[schemas.CarteraAnualOut])
def get_cartera(pais_id: str, anio: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(models.CarteraAnual).filter(models.CarteraAnual.pais_id == pais_id)
    if anio:
        q = q.filter(models.CarteraAnual.anio == anio)
    return q.all()

@router.get("/tipo_credito/{pais_id}", response_model=List[schemas.TipoCreditoResponse])
def get_tipo_credito_por_pais(pais_id: str, anio: Optional[int] = None, db: Session = Depends(get_db)):
    sql_base = """
        SELECT 
            p.nombre AS pais,
            tc.pais_id,
            tc.anio,
            tc.fuente,
            tc.categoria,
            tc.tipo_productor,
            tc.n_operaciones,
            tc.valor_miles_usd,
            tc.notas
        FROM tipo_credito tc
        JOIN paises p ON p.pais_id = tc.pais_id
        WHERE tc.pais_id = :pais_id
    """

    params = {"pais_id": pais_id}

    if anio is not None:
        sql_base += " AND tc.anio = :anio"
        params["anio"] = anio

    sql_base += " ORDER BY tc.anio, tc.categoria, tc.tipo_productor"

    result = db.execute(text(sql_base), params).mappings().all()
    return result

# ---------------------------
# Nuevos endpoints que requiere el frontend (modo API)
# ---------------------------

@router.get("/findex", response_model=List[schemas.FindexResponse])
def get_findex(db: Session = Depends(get_db)):
    sql = text("""
        SELECT 
            p.nombre AS pais,
            f.pais_id,
            f.anio,
            f.cuenta_financiera,
            f.cuenta_banco_formal,
            f.cuenta_dinero_movil,
            f.cuenta_digital,
            f.cuenta_inactiva,
            f.pago_digital,
            f.ahorro_formal_movil,
            f.smartphone,
            f.internet,
            f.movil_info_agricola,
            f.prestamo_cualquier_fuente,
            f.prestamo_banco_formal,
            f.prestamo_proveedor_movil,
            f.prestamo_familia_amigos,
            f.prestamo_negocio,
            f.credito_subsistencia,
            f.prestamo_recibido_movil,
            f.pagos_agricolas_total,
            f.pagos_agricolas_cuenta,
            f.pagos_agricolas_banco,
            f.pagos_agricolas_efectivo,
            fn_calcular_brecha_digital_credito(f.pais_id, f.anio) AS brecha_digital_credito_pp,
            fn_calcular_ratio_subsistencia_productivo(f.pais_id, f.anio) AS ratio_subsistencia_productivo,
            fn_calcular_efectivo_agricola(f.pais_id, f.anio) AS efectivo_agricola_pct
        FROM indicadores_findex f
        JOIN paises p ON p.pais_id = f.pais_id
        ORDER BY p.nombre, f.anio
    """)
    result = db.execute(sql).mappings().all()
    return result

@router.get("/oferta", response_model=List[schemas.OfertaResponse])
def get_oferta(db: Session = Depends(get_db)):
    """
    Devuelve la cartera anual (cartera_anual) para todos los países
    """
    sql = text("""
        SELECT 
            p.nombre as pais,
            c.pais_id,
            c.anio,
            c.fuente,
            c.tipo_productor,
            c.n_operaciones,
            c.valor_miles_usd,
            c.moneda_original,
            c.notas
        FROM cartera_anual c
        JOIN paises p ON p.pais_id = c.pais_id
        ORDER BY p.nombre, c.anio, c.tipo_productor
    """)
    result = db.execute(sql).mappings().all()
    return result

@router.get("/tipo_credito/{pais_id}", response_model=List[schemas.TipoCreditoResponse])
def get_tipo_credito_por_pais(pais_id: str, anio: Optional[int] = None, db: Session = Depends(get_db)):
    sql_base = """
        SELECT 
            p.nombre AS pais,
            tc.pais_id,
            tc.anio,
            tc.fuente,
            tc.categoria,
            tc.tipo_productor,
            tc.n_operaciones,
            tc.valor_miles_usd,
            tc.notas
        FROM tipo_credito tc
        JOIN paises p ON p.pais_id = tc.pais_id
        WHERE tc.pais_id = :pais_id
    """

    params = {"pais_id": pais_id}

    if anio is not None:
        sql_base += " AND tc.anio = :anio"
        params["anio"] = anio

    sql_base += " ORDER BY tc.anio, tc.categoria"

    result = db.execute(text(sql_base), params).mappings().all()
    return result

@router.get("/rural_urban", response_model=List[schemas.RuralUrbanResponse])
def get_rural_urban(db: Session = Depends(get_db)):
    """
    Devuelve indicadores rural/urbano desde la tabla indicadores_rural_urbano
    """
    sql = text("""
        SELECT 
            p.nombre as pais,
            ru.pais_id,
            ru.anio,
            ru.zona,
            ru.cuenta_financiera,
            ru.cuenta_digital,
            ru.prestamo_banco_formal,
            ru.credito_subsistencia,
            ru.smartphone,
            ru.internet,
            ru.barrera_costo,
            ru.barrera_fondos,
            ru.barrera_distancia,
            ru.dificultad_emergencia
        FROM indicadores_rural_urbano ru
        JOIN paises p ON p.pais_id = ru.pais_id
        ORDER BY p.nombre, ru.anio, ru.zona
    """)
    result = db.execute(sql).mappings().all()
    return result

@router.get("/diagnosticos", response_model=List[schemas.DiagnosticoResponse])
def get_diagnosticos(db: Session = Depends(get_db)):
    """
    Devuelve la tabla diagnostico_brecha con el nivel de brecha por país y año
    """
    sql = text("""
        SELECT 
            p.nombre as pais,
            d.pais_id,
            d.anio,
            d.nivel_brecha,
            d.puntaje_brecha,
            d.brecha_digital_credito_pp,
            d.cambio_credito_formal_pp,
            d.ratio_subsistencia_productivo,
            d.efectivo_agricola_pct,
            d.texto_diagnostico
        FROM diagnostico_brecha d
        JOIN paises p ON p.pais_id = d.pais_id
        ORDER BY p.nombre, d.anio
    """)
    result = db.execute(sql).mappings().all()
    return result

@router.get("/recomendaciones", response_model=List[schemas.RecomendacionesResponse])
def get_recomendaciones(db: Session = Depends(get_db)):
    """
    Devuelve recomendaciones generadas según el diagnóstico automático y los niveles de brecha.
    """
    sql = text("""
        SELECT
            p.nombre AS pais,
            r.pais_id,
            r.anio,
            r.nivel_brecha,
            r.eje,
            r.recomendacion,
            r.accion,
            r.indicador_relacionado
        FROM recomendaciones r
        JOIN paises p ON p.pais_id = r.pais_id
        ORDER BY p.nombre, r.anio, r.eje
    """)
    result = db.execute(sql).mappings().all()
    return result

@router.get("/missing", response_model=List[schemas.MissingDataResponse])
def get_missing_data(db: Session = Depends(get_db)):
    """
    Devuelve los datos faltantes registrados en la tabla datos_faltantes
    """
    sql = text("""
        SELECT 
            COALESCE(p.nombre, 'Todos los países') as pais,
            df.fuente,
            df.dato_faltante,
            df.prioridad,
            df.justificacion as por_que_importa
        FROM datos_faltantes df
        LEFT JOIN paises p ON p.pais_id = df.pais_id
        ORDER BY df.prioridad, df.pais_id NULLS LAST
    """)
    result = db.execute(sql).mappings().all()
    return result

@router.get("/fuentes", response_model=List[schemas.FuenteResponse])
def get_fuentes(db: Session = Depends(get_db)):
    """
    Devuelve las fuentes de datos desde la tabla metadatos,
    formateadas como espera el frontend.
    """
    sql = text("""
        SELECT 
            m.fuente,
            p.nombre as pais,
            m.anios_cubiertos as periodo,
            m.observaciones as uso,
            'Disponible' as estado
        FROM metadatos m
        JOIN paises p ON p.pais_id = m.pais_id
        ORDER BY p.nombre, m.fuente
    """)
    result = db.execute(sql).mappings().all()
    return result

@router.get("/diccionario", response_model=List[schemas.DiccionarioResponse])
def get_diccionario():
    """
    Diccionario estático de indicadores Global Findex
    (coincide con el que usa el frontend en modo mock)
    """
    data = [
        {"grupo": "Inclusión transaccional", "indicador": "Cuenta financiera", "codigo": "account.t.d", "descripcion": "% adultos con cuenta en institución financiera o móvil"},
        {"grupo": "Inclusión transaccional", "indicador": "Cuenta banco formal", "codigo": "fin11a.t.d", "descripcion": "% adultos con cuenta en banco formal"},
        {"grupo": "Inclusión transaccional", "indicador": "Cuenta dinero móvil", "codigo": "mob.t.d", "descripcion": "% adultos con cuenta de dinero móvil"},
        {"grupo": "Inclusión transaccional", "indicador": "Cuenta habilitada digitalmente", "codigo": "dig.acc", "descripcion": "% adultos con cuenta digital activa"},
        {"grupo": "Digitalización", "indicador": "Pago digital", "codigo": "g20.any", "descripcion": "% realizó o recibió algún pago digital"},
        {"grupo": "Digitalización", "indicador": "Usó internet", "codigo": "internet", "descripcion": "% usó internet en los últimos 3 meses"},
        {"grupo": "Crédito", "indicador": "Préstamo banco formal", "codigo": "fin22a", "descripcion": "% adultos con préstamo vigente en banco formal"},
        {"grupo": "Crédito", "indicador": "Préstamo para negocio", "codigo": "fin22e", "descripcion": "% adultos cuyo último préstamo fue para negocio o actividad productiva"},
        {"grupo": "Crédito", "indicador": "Crédito de subsistencia", "codigo": "fin22f", "descripcion": "% adultos que compraron alimentos a crédito"},
        {"grupo": "Crédito", "indicador": "Pagos agrícolas en efectivo", "codigo": "fin43c", "descripcion": "% adultos que reciben pagos agrícolas exclusivamente en efectivo"},
        {"grupo": "Barreras", "indicador": "Banco muy lejos", "codigo": "fin11d", "descripcion": "% adultos sin cuenta que señalan distancia al banco"},
        {"grupo": "Resiliencia", "indicador": "Dificultad alta ante emergencia", "codigo": "fin24aVD", "descripcion": "% adultos con mucha dificultad para reunir fondos de emergencia"}
    ]
    return [schemas.DiccionarioResponse(**item) for item in data]

# ---------------------------
# Endpoints de microdatos FINAGRO (opcionales, si el frontend los usa)
# ---------------------------
@router.get("/finagro/departamento", response_model=List[schemas.FinagroDepartamentoOut])
def get_finagro_departamento(anio: Optional[int] = None, tipo: Optional[str] = None, db: Session = Depends(get_db)):
    sql_base = """
        SELECT
            anio,
            departamento,
            tipo_productor,
            n_operaciones,
            valor_mm_usd AS "valor_MM_usd"
        FROM finagro_departamento
    """

    condiciones = []
    params = {}

    if anio is not None:
        condiciones.append("anio = :anio")
        params["anio"] = anio

    if tipo:
        condiciones.append("tipo_productor = :tipo")
        params["tipo"] = tipo

    if condiciones:
        sql_base += " WHERE " + " AND ".join(condiciones)

    sql_base += " ORDER BY anio, departamento, tipo_productor"

    result = db.execute(text(sql_base), params).mappings().all()
    return result

@router.get("/finagro/cadena", response_model=List[schemas.FinagroCadenaOut])
def get_finagro_cadena(anio: Optional[int] = None, db: Session = Depends(get_db)):
    sql_base = """
        SELECT
            anio,
            cadena,
            tipo_productor,
            n_operaciones,
            valor_mm_usd AS "valor_MM_usd"
        FROM finagro_cadena
    """

    params = {}

    if anio is not None:
        sql_base += " WHERE anio = :anio"
        params["anio"] = anio

    sql_base += " ORDER BY anio, cadena, tipo_productor"

    result = db.execute(text(sql_base), params).mappings().all()
    return result

@router.get("/finagro/sexo", response_model=List[schemas.FinagroSexoOut])
def get_finagro_sexo(anio: Optional[int] = None, db: Session = Depends(get_db)):
    sql_base = """
        SELECT
            anio,
            sexo,
            tipo_productor,
            n_operaciones,
            valor_mm_usd AS "valor_MM_usd"
        FROM finagro_sexo
    """

    params = {}

    if anio is not None:
        sql_base += " WHERE anio = :anio"
        params["anio"] = anio

    sql_base += " ORDER BY anio, sexo, tipo_productor"

    result = db.execute(text(sql_base), params).mappings().all()
    return result

# ---------------------------
# Endpoint comparativo (opcional)
# ---------------------------
@router.get("/comparativo/{indicador}", response_model=List[schemas.ComparativoItem])
def get_comparativo(indicador: str, anios: Optional[str] = None, db: Session = Depends(get_db)):
    col_map = {
        "prestamo_banco_formal": models.IndicadoresFindex.prestamo_banco_formal,
        "cuenta_digital": models.IndicadoresFindex.cuenta_digital,
        "pagos_agricolas_efectivo": models.IndicadoresFindex.pagos_agricolas_efectivo
    }
    if indicador not in col_map:
        raise HTTPException(400, "Indicador no válido")
    
    anio_list = [int(a) for a in anios.split(",")] if anios else [2021, 2024]
    q = db.query(
        models.Pais.nombre.label("pais"),
        models.IndicadoresFindex.anio,
        col_map[indicador].label("valor")
    ).join(
        models.IndicadoresFindex,
        models.Pais.pais_id == models.IndicadoresFindex.pais_id
    ).filter(
        models.IndicadoresFindex.anio.in_(anio_list)
    ).order_by(models.Pais.nombre, models.IndicadoresFindex.anio)
    
    results = q.all()
    return [schemas.ComparativoItem(pais=r.pais, anio=r.anio, indicador=indicador, valor=r.valor) for r in results]