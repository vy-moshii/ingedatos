from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.database import get_db
from app import models, schemas

router = APIRouter()

# ---------------------------
# 1. Endpoints generales por país
# ---------------------------
@router.get("/paises", response_model=List[schemas.PaisBase])
def get_paises(db: Session = Depends(get_db)):
    return db.query(models.Pais).all()

@router.get("/cartera/{pais_id}", response_model=List[schemas.CarteraAnualOut])
def get_cartera(pais_id: str, anio: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(models.CarteraAnual).filter(models.CarteraAnual.pais_id == pais_id)
    if anio:
        q = q.filter(models.CarteraAnual.anio == anio)
    return q.all()

@router.get("/tipo_credito/{pais_id}", response_model=List[schemas.TipoCreditoOut])
def get_tipo_credito(pais_id: str, anio: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(models.TipoCredito).filter(models.TipoCredito.pais_id == pais_id)
    if anio:
        q = q.filter(models.TipoCredito.anio == anio)
    return q.all()

# ---------------------------
# 2. Endpoints de Findex (incluye brecha calculada)
# ---------------------------
@router.get("/findex/{pais_id}", response_model=List[schemas.FindexOut])
def get_findex(pais_id: str, anio: Optional[int] = None, db: Session = Depends(get_db)):
    # Usamos la vista v_findex definida en el script SQL
    sql = text("""
        SELECT pais_id, anio, cuenta_digital, prestamo_banco_formal,
               brecha_digital_credito_pp, ratio_subsistencia_productivo
        FROM v_findex
        WHERE pais_id = :pais_id
        {filtro_anio}
        ORDER BY anio
    """.format(filtro_anio = "AND anio = :anio" if anio else ""))
    params = {"pais_id": pais_id}
    if anio:
        params["anio"] = anio
    result = db.execute(sql, params).mappings().all()
    return result

# ---------------------------
# 3. Endpoints de diagnóstico (usando tabla diagnostico_brecha)
# ---------------------------
@router.get("/diagnostico/{pais_id}", response_model=schemas.DiagnosticoOut)
def get_diagnostico(pais_id: str, anio: int, db: Session = Depends(get_db)):
    # Primero intentamos obtener de la tabla
    diag = db.query(models.DiagnosticoBrecha).filter(
        models.DiagnosticoBrecha.pais_id == pais_id,
        models.DiagnosticoBrecha.anio == anio
    ).first()
    if not diag:
        # Si no existe, llamamos a la función PL/pgSQL que lo genera
        sql = text("SELECT * FROM fn_generar_diagnostico_brecha(:pais_id, :anio)")
        result = db.execute(sql, {"pais_id": pais_id, "anio": anio}).mappings().first()
        if not result:
            raise HTTPException(404, "No se pudo generar diagnóstico")
        # Guardamos en la tabla (el trigger lo haría, pero lo hacemos explícito)
        nuevo = models.DiagnosticoBrecha(
            pais_id=pais_id,
            anio=anio,
            nivel_brecha=result["nivel"],
            puntaje_brecha=result["puntaje"],
            texto_diagnostico=result["diagnostico"]
        )
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        diag = nuevo
    # Obtener ejes de recomendación
    ejes = db.query(models.Recomendaciones.eje).filter(
        models.Recomendaciones.pais_id == pais_id,
        models.Recomendaciones.anio == anio,
        models.Recomendaciones.nivel_brecha == diag.nivel_brecha
    ).distinct().all()
    ejes_str = " | ".join([e[0] for e in ejes]) if ejes else None
    return schemas.DiagnosticoOut(
        pais_id=diag.pais_id,
        anio=diag.anio,
        nivel_brecha=diag.nivel_brecha,
        puntaje_brecha=diag.puntaje_brecha,
        texto_diagnostico=diag.texto_diagnostico,
        ejes_recomendacion=ejes_str
    )

@router.get("/recomendaciones/{pais_id}", response_model=List[schemas.RecomendacionOut])
def get_recomendaciones(pais_id: str, anio: int, db: Session = Depends(get_db)):
    # Primero obtenemos el nivel de brecha para ese año
    diag = db.query(models.DiagnosticoBrecha).filter(
        models.DiagnosticoBrecha.pais_id == pais_id,
        models.DiagnosticoBrecha.anio == anio
    ).first()
    if not diag:
        raise HTTPException(404, "Diagnóstico no encontrado")
    recs = db.query(models.Recomendaciones).filter(
        models.Recomendaciones.pais_id == pais_id,
        models.Recomendaciones.anio == anio,
        models.Recomendaciones.nivel_brecha == diag.nivel_brecha
    ).all()
    return recs

# ---------------------------
# 4. Endpoints de microdatos FINAGRO (Colombia)
# ---------------------------
@router.get("/finagro/departamento", response_model=List[schemas.FinagroDepartamentoOut])
def get_finagro_departamento(anio: Optional[int] = None, tipo: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.FinagroDepartamento)
    if anio:
        q = q.filter(models.FinagroDepartamento.anio == anio)
    if tipo:
        q = q.filter(models.FinagroDepartamento.tipo_productor == tipo)
    return q.all()

@router.get("/finagro/cadena", response_model=List[schemas.FinagroCadenaOut])
def get_finagro_cadena(anio: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(models.FinagroCadena)
    if anio:
        q = q.filter(models.FinagroCadena.anio == anio)
    return q.all()

@router.get("/finagro/sexo", response_model=List[schemas.FinagroSexoOut])
def get_finagro_sexo(anio: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(models.FinagroSexo)
    if anio:
        q = q.filter(models.FinagroSexo.anio == anio)
    return q.all()

# ---------------------------
# 5. Endpoint comparativo entre países
# ---------------------------
@router.get("/comparativo/{indicador}", response_model=List[schemas.ComparativoItem])
def get_comparativo(indicador: str, anios: Optional[str] = None, db: Session = Depends(get_db)):
    """
    indicador puede ser: 'prestamo_banco_formal', 'cuenta_digital', 'pagos_agricolas_efectivo'
    anios: separados por coma, ej. '2021,2024'
    """
    # Mapeo de indicador a columna
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

# ---------------------------
# 6. Endpoint de datos faltantes
# ---------------------------
@router.get("/datos_faltantes", response_model=List[schemas.DatosFaltantes])
def get_datos_faltantes(db: Session = Depends(get_db)):
    return db.query(models.DatosFaltantes).all()

# Nota: Falta crear el esquema DatosFaltantes en schemas, similar a los demás.