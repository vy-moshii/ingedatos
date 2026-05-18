import os
from io import StringIO
import pandas as pd
import numpy as np
import requests
try:
    from sqlalchemy import create_engine
except ImportError:
    create_engine = None

PAISES = ["Colombia", "Ecuador", "Paraguay"]
CODIGOS_PAIS = {"Colombia": "COL", "Ecuador": "ECU", "Paraguay": "PRY"}
CODIGO_A_PAIS = {v: k for k, v in CODIGOS_PAIS.items()}
ANIOS_OFERTA = list(range(2019, 2025))
ANIOS_FINDEX = [2021, 2024]

NARRATIVA = {
    "titulo": "Entre la cuenta y el crédito",
    "subtitulo": "Brechas de integración productiva en el financiamiento rural de Colombia, Ecuador y Paraguay",
    "tesis": "La digitalización financiera amplía la inclusión transaccional, pero no garantiza acceso al crédito productivo si el diseño institucional no incorpora al pequeño productor rural como sujeto de crédito.",
    "pregunta": "¿Por qué el avance digital no se tradujo en mayor crédito productivo formal en Colombia y Ecuador, mientras Paraguay mostró crecimiento del crédito formal?",
    "hipotesis": "La diferencia no se explica por conectividad digital, sino por arquitectura institucional del financiamiento rural."
}

FUENTES = [
    {"fuente": "Global Findex", "pais": "Colombia, Ecuador y Paraguay", "periodo": "2021 y 2024", "uso": "Demanda: cuentas, pagos, crédito formal, préstamo para negocio, subsistencia, pagos agrícolas y brecha rural-urbana", "estado": "Base principal"},
    {"fuente": "FINAGRO", "pais": "Colombia", "periodo": "2019-2024", "uso": "Oferta: crédito agropecuario por pequeño, mediano y gran productor", "estado": "Disponible en el SQL"},
    {"fuente": "BCE", "pais": "Ecuador", "periodo": "2019-2024", "uso": "Oferta: crédito productivo, microcrédito y segmentos del sistema financiero", "estado": "Disponible en el SQL"},
    {"fuente": "SEPS", "pais": "Ecuador", "periodo": "2021-2024", "uso": "Oferta: microcrédito y crédito productivo cooperativo", "estado": "Disponible parcial"},
    {"fuente": "BCP", "pais": "Paraguay", "periodo": "2019-2024", "uso": "Oferta: bancos, financieras y cooperativas tipo A", "estado": "Disponible parcial"},
    {"fuente": "CAH", "pais": "Paraguay", "periodo": "Por recolectar", "uso": "Oferta: crédito directo a pequeño productor rural", "estado": "Faltante crítico"}
]

INDICADORES_FINDEX = [
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

def _maybe_number(value):
    if value is None:
        return np.nan
    return value

def get_findex():
    rows = []
    data = {
        "Colombia": {
            2021: {"cuenta_financiera": 59.7, "cuenta_banco_formal": 55.9, "cuenta_dinero_movil": 21.8, "cuenta_digital": None, "cuenta_inactiva": 4.6, "pago_digital": 52.1, "ahorro_formal_movil": 13.5, "smartphone": None, "internet": None, "info_agricola_digital": None, "prestamo_cualquier_fuente": 48.2, "prestamo_banco_formal": 18.1, "prestamo_proveedor_movil": 2.3, "prestamo_familia_amigos": 29.1, "prestamo_negocio": None, "credito_subsistencia": None, "prestamo_recibido_movil": None, "pagos_agricolas_total": 4.5, "pagos_agricolas_cuenta": 1.1, "pagos_agricolas_banco": 1.0, "pagos_agricolas_efectivo": 2.6},
            2024: {"cuenta_financiera": 57.1, "cuenta_banco_formal": 43.4, "cuenta_dinero_movil": 39.1, "cuenta_digital": 46.0, "cuenta_inactiva": 2.5, "pago_digital": 49.2, "ahorro_formal_movil": 25.0, "smartphone": 73.3, "internet": 80.7, "info_agricola_digital": 1.4, "prestamo_cualquier_fuente": 46.3, "prestamo_banco_formal": 12.4, "prestamo_proveedor_movil": 3.0, "prestamo_familia_amigos": 19.4, "prestamo_negocio": 7.6, "credito_subsistencia": 21.3, "prestamo_recibido_movil": 3.7, "pagos_agricolas_total": 2.1, "pagos_agricolas_cuenta": 0.7, "pagos_agricolas_banco": 0.4, "pagos_agricolas_efectivo": 1.2}
        },
        "Ecuador": {
            2021: {"cuenta_financiera": 64.2, "cuenta_banco_formal": 64.2, "cuenta_dinero_movil": None, "cuenta_digital": None, "cuenta_inactiva": 10.2, "pago_digital": 46.9, "ahorro_formal_movil": 13.1, "smartphone": None, "internet": None, "info_agricola_digital": None, "prestamo_cualquier_fuente": 47.1, "prestamo_banco_formal": 23.2, "prestamo_proveedor_movil": None, "prestamo_familia_amigos": 28.8, "prestamo_negocio": None, "credito_subsistencia": None, "prestamo_recibido_movil": None, "pagos_agricolas_total": 10.4, "pagos_agricolas_cuenta": 1.9, "pagos_agricolas_banco": 1.8, "pagos_agricolas_efectivo": 7.2},
            2024: {"cuenta_financiera": 64.5, "cuenta_banco_formal": 63.9, "cuenta_dinero_movil": 10.1, "cuenta_digital": 38.4, "cuenta_inactiva": 5.6, "pago_digital": 43.3, "ahorro_formal_movil": 22.3, "smartphone": 64.6, "internet": 82.8, "info_agricola_digital": 2.8, "prestamo_cualquier_fuente": 48.0, "prestamo_banco_formal": 16.1, "prestamo_proveedor_movil": 0.8, "prestamo_familia_amigos": 18.6, "prestamo_negocio": 8.9, "credito_subsistencia": 19.4, "prestamo_recibido_movil": 3.8, "pagos_agricolas_total": 5.6, "pagos_agricolas_cuenta": 1.5, "pagos_agricolas_banco": 1.5, "pagos_agricolas_efectivo": 4.0}
        },
        "Paraguay": {
            2021: {"cuenta_financiera": 54.4, "cuenta_banco_formal": 27.1, "cuenta_dinero_movil": 37.7, "cuenta_digital": None, "cuenta_inactiva": 2.0, "pago_digital": 51.2, "ahorro_formal_movil": 7.4, "smartphone": None, "internet": None, "info_agricola_digital": None, "prestamo_cualquier_fuente": 34.8, "prestamo_banco_formal": 12.4, "prestamo_proveedor_movil": 1.9, "prestamo_familia_amigos": 22.2, "prestamo_negocio": None, "credito_subsistencia": None, "prestamo_recibido_movil": None, "pagos_agricolas_total": 7.5, "pagos_agricolas_cuenta": 0.9, "pagos_agricolas_banco": 0.3, "pagos_agricolas_efectivo": 6.4},
            2024: {"cuenta_financiera": 60.9, "cuenta_banco_formal": 45.5, "cuenta_dinero_movil": 35.9, "cuenta_digital": 47.3, "cuenta_inactiva": 0.6, "pago_digital": 55.5, "ahorro_formal_movil": 19.6, "smartphone": 82.6, "internet": 83.8, "info_agricola_digital": 3.9, "prestamo_cualquier_fuente": 54.8, "prestamo_banco_formal": 17.6, "prestamo_proveedor_movil": 7.9, "prestamo_familia_amigos": 23.0, "prestamo_negocio": 7.2, "credito_subsistencia": 24.8, "prestamo_recibido_movil": 11.4, "pagos_agricolas_total": 8.8, "pagos_agricolas_cuenta": 2.3, "pagos_agricolas_banco": 1.9, "pagos_agricolas_efectivo": 6.1}
        }
    }
    for pais, years in data.items():
        for anio, values in years.items():
            row = {"pais": pais, "pais_id": CODIGOS_PAIS[pais], "anio": anio}
            row.update({k: _maybe_number(v) for k, v in values.items()})
            rows.append(row)
    df = pd.DataFrame(rows)
    df["variacion_credito_formal_pp"] = df.groupby("pais")["prestamo_banco_formal"].transform(lambda s: s - s.iloc[0])
    df["ratio_subsistencia_productivo"] = df["credito_subsistencia"] / df["prestamo_negocio"]
    df["brecha_digital_credito_pp"] = df["cuenta_digital"] - df["prestamo_banco_formal"]
    df["efectivo_agricola_pct"] = np.where(df["pagos_agricolas_total"] > 0, df["pagos_agricolas_efectivo"] / df["pagos_agricolas_total"] * 100, np.nan)
    return df

def get_rural_urban():
    rows = [
        ["Colombia", "Rural", 2024, 51.5, 38.3, 10.9, 24.3, 65.9, 77.8, 39.3, 25.9, 26.4, 45.8],
        ["Colombia", "Urbano", 2024, 60.5, 50.8, 13.3, 19.5, 77.9, 82.5, 34.4, 14.8, 19.8, 31.6],
        ["Ecuador", "Rural", 2024, 62.6, 32.3, 15.0, 19.9, 60.8, 81.9, 26.9, 11.1, 21.2, 49.1],
        ["Ecuador", "Urbano", 2024, 66.3, 43.8, 17.0, 18.9, 68.0, 83.5, 24.3, 12.6, 18.0, 35.3],
        ["Paraguay", "Rural", 2024, 57.6, 43.6, 16.4, 30.0, 80.0, 80.4, 26.3, 28.3, 25.8, 28.0],
        ["Paraguay", "Urbano", 2024, 65.8, 52.6, 19.3, 17.2, 86.4, 88.9, 23.7, 25.3, 9.2, 22.9]
    ]
    columns = ["pais", "zona", "anio", "cuenta_financiera", "cuenta_digital", "prestamo_banco_formal", "credito_subsistencia", "smartphone", "internet", "barrera_costo", "barrera_fondos", "barrera_distancia", "resiliencia_dificil"]
    df = pd.DataFrame(rows, columns=columns)
    df["pais_id"] = df["pais"].map(CODIGOS_PAIS)
    return df

def get_oferta():
    rows = []
    col = {
        2019: {"grande": [11098, 4144.9], "mediano": [58805, 959.2], "pequenio": [343830, 763.0]},
        2020: {"grande": [11758, 4632.1], "mediano": [61733, 969.6], "pequenio": [439746, 950.9]},
        2021: {"grande": [11752, 5369.6], "mediano": [66667, 1035.8], "pequenio": [437375, 1066.5]},
        2022: {"grande": [14552, 4684.2], "mediano": [63929, 942.7], "pequenio": [453805, 1063.1]},
        2023: {"grande": [22864, 3495.7], "mediano": [63413, 783.9], "pequenio": [445879, 1021.7]},
        2024: {"grande": [25689, 6914.3], "mediano": [62672, 906.5], "pequenio": [434701, 1117.0]}
    }
    for anio, vals in col.items():
        for segmento, datos in vals.items():
            rows.append(["Colombia", "COL", anio, "FINAGRO", segmento, datos[0], datos[1], "Flujo desembolsado", "Oferta institucional"])
    ecu = {
        2019: {"productivo": 15245, "microcredito": 5202, "consumo": 7310},
        2020: {"productivo": 15281, "microcredito": 3816, "consumo": 6905},
        2021: {"productivo": 15255, "microcredito": 6230, "consumo": 7801},
        2022: {"productivo": 18757, "microcredito": 7761, "consumo": 8560},
        2023: {"productivo": 19263, "microcredito": 7321, "consumo": 9050},
        2024: {"productivo": 22216, "microcredito": 6385, "consumo": 9460}
    }
    for anio, vals in ecu.items():
        for segmento, monto in vals.items():
            rows.append(["Ecuador", "ECU", anio, "BCE", segmento, np.nan, monto, "Operaciones activas", "Oferta institucional"])
    pry = {
        2019: {"bancos_financieras": 14706, "cooperativas": 2110},
        2020: {"bancos_financieras": 14870, "cooperativas": 2123},
        2021: {"bancos_financieras": 16504, "cooperativas": 2324},
        2022: {"bancos_financieras": 17305, "cooperativas": 2385},
        2023: {"bancos_financieras": 19238, "cooperativas": 2540},
        2024: {"bancos_financieras": np.nan, "cooperativas": 2514}
    }
    for anio, vals in pry.items():
        for segmento, monto in vals.items():
            rows.append(["Paraguay", "PRY", anio, "BCP", segmento, np.nan, monto, "Saldo de cartera", "Oferta institucional parcial"])
    df = pd.DataFrame(rows, columns=["pais", "pais_id", "anio", "fuente", "segmento", "n_operaciones", "valor_millones_usd", "unidad_medida", "tipo_dato"])
    return df

def get_tipo_credito():
    rows = []
    col = {
        2019: {"capital_trabajo": [165300, 218.2], "inversion": [140703, 466.0], "normalizacion_cartera": [37827, 78.9]},
        2020: {"capital_trabajo": [172550, 280.0], "inversion": [124124, 405.6], "normalizacion_cartera": [143072, 265.3]},
        2021: {"capital_trabajo": [185223, 319.1], "inversion": [131289, 476.3], "normalizacion_cartera": [120863, 271.1]},
        2022: {"capital_trabajo": [181234, 290.1], "inversion": [136921, 479.7], "normalizacion_cartera": [135650, 293.4]},
        2023: {"capital_trabajo": [185672, 264.4], "inversion": [140289, 489.4], "normalizacion_cartera": [119918, 267.9]},
        2024: {"capital_trabajo": [192341, 298.4], "inversion": [144892, 521.3], "normalizacion_cartera": [97468, 297.2]}
    }
    for anio, vals in col.items():
        for categoria, datos in vals.items():
            rows.append(["Colombia", "COL", anio, "FINAGRO", categoria, "pequenio", datos[0], datos[1]])
    ecu_prod = {
        2021: {"bancos_privados": 14860, "cooperativas": 285, "banca_publica": 95, "mutualistas": 15},
        2022: {"bancos_privados": 18475, "cooperativas": 210, "banca_publica": 55, "mutualistas": 17},
        2023: {"bancos_privados": 18990, "cooperativas": 165, "banca_publica": 88, "mutualistas": 20},
        2024: {"bancos_privados": 22216, "cooperativas": 103, "banca_publica": 111, "mutualistas": 22}
    }
    for anio, vals in ecu_prod.items():
        for entidad, monto in vals.items():
            rows.append(["Ecuador", "ECU", anio, "BCE", "productivo", entidad, np.nan, monto])
    ecu_seps = {
        2019: {"microcredito_seps": 2831},
        2020: {"microcredito_seps": 2429},
        2021: {"microcredito_seps": 2749},
        2022: {"microcredito_seps": 4951},
        2023: {"microcredito_seps": 4526},
        2024: {"microcredito_seps": 3786}
    }
    for anio, vals in ecu_seps.items():
        for categoria, monto in vals.items():
            rows.append(["Ecuador", "ECU", anio, "SEPS", categoria, "cooperativas_mutualistas", np.nan, monto])
    return pd.DataFrame(rows, columns=["pais", "pais_id", "anio", "fuente", "categoria", "segmento", "n_operaciones", "valor_millones_usd"])

def get_missing_data():
    rows = [
        ["Paraguay", "CAH", "Desembolsos por pequeño productor, cobertura territorial y morosidad", "Crítico", "Permitiría comprobar si el crecimiento formal de Paraguay se explica por banca pública rural"],
        ["Colombia", "FINAGRO", "Desagregación rural/urbana de crédito por municipio y tamaño de productor", "Alto", "Ayudaría a medir si el pequeño productor rural recibe crédito o solo aparece agregado"],
        ["Ecuador", "SEPS", "Crédito productivo cooperativo completo 2019-2020", "Alto", "El artículo advierte que el desglose cooperativo no está completo para esos años"],
        ["Tres países", "Global Findex", "Datos por tipo de productor específico", "Medio", "Findex mide adultos y usa proxies rurales, no pequeños productores agrícolas directamente"],
        ["Tres países", "Cadenas de valor", "Pagos digitales comprador-productor por producto agrícola", "Alto", "Sirve para medir trazabilidad del ingreso agropecuario"],
        ["Tres países", "Garantías", "Uso de garantías alternativas, seguros paramétricos y contratos de venta", "Medio", "Permite conectar diagnóstico con rediseño institucional del crédito"],
        ["Tres países", "Territorio", "Departamentos, provincias o distritos con mayor brecha rural", "Medio", "Ayuda a que el dashboard pase de país a focalización territorial"]
    ]
    return pd.DataFrame(rows, columns=["pais", "fuente", "dato_faltante", "prioridad", "por_que_importa"])

def get_recomendaciones():
    rows = [
        ["Trazabilidad", "Digitalizar primero el pago por la producción agrícola", "Promover pagos digitales entre compradores, asociaciones, cooperativas y productores", "pagos_agricolas_efectivo"],
        ["Crédito productivo", "Diseñar crédito según ciclo agropecuario", "Usar plazos estacionales, periodos de gracia, garantías de cosecha, contratos de venta y seguros paramétricos", "prestamo_negocio"],
        ["Arquitectura institucional", "Fortalecer instituciones con mandato rural explícito", "Evitar que la oferta se concentre en banca privada o gran productor", "prestamo_banco_formal"],
        ["Datos", "Construir historial alternativo con transacciones rurales", "Integrar pagos, compras de insumos, asociaciones, facturas y producción esperada", "cuenta_digital"],
        ["Territorio", "Priorizar zonas rurales con distancia bancaria y baja resiliencia", "Cruzar brecha rural-urbana con barreras de costo, fondos insuficientes y distancia", "barrera_distancia"]
    ]
    return pd.DataFrame(rows, columns=["eje", "recomendacion", "accion", "indicador_relacionado"])

def get_sources():
    return pd.DataFrame(FUENTES)

def get_dictionary():
    return pd.DataFrame(INDICADORES_FINDEX)

def get_narrativa():
    return NARRATIVA

def filtrar_paises(df, paises):
    if not paises:
        return df.iloc[0:0]
    return df[df["pais"].isin(paises)].copy()

def filtrar_anios(df, rango):
    if "anio" not in df.columns:
        return df.copy()
    return df[(df["anio"] >= rango[0]) & (df["anio"] <= rango[1])].copy()

def get_kpis(paises=None, anio=2024):
    df = get_findex()
    if paises:
        df = df[df["pais"].isin(paises)]
    df = df[df["anio"] == anio]
    if df.empty:
        return {}
    return {
        "cuenta_financiera": df["cuenta_financiera"].mean(),
        "cuenta_digital": df["cuenta_digital"].mean(),
        "internet": df["internet"].mean(),
        "prestamo_banco_formal": df["prestamo_banco_formal"].mean(),
        "prestamo_negocio": df["prestamo_negocio"].mean(),
        "credito_subsistencia": df["credito_subsistencia"].mean(),
        "ratio_subsistencia_productivo": df["ratio_subsistencia_productivo"].mean(),
        "brecha_digital_credito_pp": df["brecha_digital_credito_pp"].mean(),
        "efectivo_agricola_pct": df["efectivo_agricola_pct"].mean()
    }

def diagnosticar_pais(pais):
    df = get_findex()
    actual = df[(df["pais"] == pais) & (df["anio"] == 2024)].iloc[0]
    base = df[(df["pais"] == pais) & (df["anio"] == 2021)].iloc[0]
    brecha = actual["cuenta_digital"] - actual["prestamo_banco_formal"]
    cambio = actual["prestamo_banco_formal"] - base["prestamo_banco_formal"]
    ratio = actual["ratio_subsistencia_productivo"]
    efectivo = actual["efectivo_agricola_pct"]
    puntaje = 0
    if brecha >= 30:
        puntaje += 3
    elif brecha >= 20:
        puntaje += 2
    else:
        puntaje += 1
    if cambio < -5:
        puntaje += 3
    elif cambio < 0:
        puntaje += 2
    else:
        puntaje += 0
    if ratio >= 3:
        puntaje += 3
    elif ratio >= 2:
        puntaje += 2
    else:
        puntaje += 1
    if efectivo >= 70:
        puntaje += 3
    elif efectivo >= 55:
        puntaje += 2
    else:
        puntaje += 1
    if puntaje >= 10:
        nivel = "Crítica"
    elif puntaje >= 7:
        nivel = "Alta"
    elif puntaje >= 5:
        nivel = "Media"
    else:
        nivel = "Moderada"
    texto = f"{pais} presenta una brecha {nivel.lower()} porque la cuenta digital alcanza {actual['cuenta_digital']:.1f}%, el crédito bancario formal llega a {actual['prestamo_banco_formal']:.1f}% y el crédito de subsistencia equivale a {ratio:.1f} veces el préstamo para negocio."
    return {
        "pais": pais,
        "nivel": nivel,
        "puntaje": puntaje,
        "brecha_digital_credito_pp": brecha,
        "cambio_credito_formal_pp": cambio,
        "ratio_subsistencia_productivo": ratio,
        "efectivo_agricola_pct": efectivo,
        "texto": texto
    }

def diagnosticos():
    return pd.DataFrame([diagnosticar_pais(p) for p in PAISES])

def segmento_menor_escala():
    df = get_oferta()
    condiciones = ((df["pais"] == "Colombia") & (df["segmento"] == "pequenio")) | ((df["pais"] == "Ecuador") & (df["segmento"] == "microcredito")) | ((df["pais"] == "Paraguay") & (df["segmento"] == "cooperativas"))
    return df[condiciones].copy()

def descargar_csv(df):
    return df.to_csv(index=False).encode("utf-8-sig")

def cargar_desde_fastapi(endpoint):
    base_url = os.getenv("AGROCREDIT_API_URL", "").strip()
    if not base_url:
        return None
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return pd.DataFrame(response.json())

def cargar_tabla_postgresql(tabla):
    url = os.getenv("AGROCREDIT_DATABASE_URL", "").strip()
    if not url:
        return None
    if create_engine is None:
        return None
    engine = create_engine(url)
    return pd.read_sql_table(tabla, engine)

def obtener_dataset(nombre):
    modo = os.getenv("AGROCREDIT_DATA_MODE", "mock").lower().strip()
    if modo == "api":
        data = cargar_desde_fastapi(nombre)
        if data is not None:
            return data
    if modo == "postgresql":
        data = cargar_tabla_postgresql(nombre)
        if data is not None:
            return data
    datasets = {
        "findex": get_findex,
        "oferta": get_oferta,
        "tipo_credito": get_tipo_credito,
        "rural_urban": get_rural_urban,
        "missing": get_missing_data,
        "fuentes": get_sources,
        "diccionario": get_dictionary,
        "diagnosticos": diagnosticos
    }
    return datasets[nombre]()


CONCEPTOS_CLAVE = [
    {"concepto": "Inclusión transaccional", "significado": "Capacidad de una persona para tener y usar servicios financieros básicos como cuenta, pagos, ahorro o transferencias.", "en_el_dashboard": "Se observa con cuenta financiera, cuenta digital, pago digital, internet y ahorro formal o móvil.", "por_que_importa": "El artículo muestra que tener cuenta o internet no significa automáticamente tener crédito para producir."},
    {"concepto": "Integración productiva", "significado": "Momento en que la inclusión financiera permite financiar una actividad económica real, por ejemplo sembrar, comprar insumos, invertir en maquinaria o sostener una unidad productiva rural.", "en_el_dashboard": "Se aproxima con préstamo para negocio, crédito formal y segmentos de menor escala de la oferta institucional.", "por_que_importa": "Es el centro del proyecto: pasar de estar dentro del sistema financiero a ser reconocido como sujeto de crédito productivo."},
    {"concepto": "Brecha de integración productiva", "significado": "Distancia entre estar incluido transaccionalmente y acceder de verdad a crédito productivo formal.", "en_el_dashboard": "Se calcula comparando cuenta digital con préstamo bancario formal y préstamo para negocio.", "por_que_importa": "Permite ver si la digitalización está ayudando a producir o solo a pagar, ahorrar o transferir."},
    {"concepto": "Crédito formal", "significado": "Préstamo recibido desde una institución financiera regulada, como banco, cooperativa supervisada o entidad formal.", "en_el_dashboard": "Aparece como préstamo banco formal en Findex y como cartera institucional en las fuentes de oferta.", "por_que_importa": "Si cae mientras sube la digitalización, hay una señal de desconexión entre acceso financiero y financiamiento productivo."},
    {"concepto": "Crédito productivo", "significado": "Crédito usado para financiar negocio, producción, capital de trabajo, inversión o actividad agropecuaria.", "en_el_dashboard": "Aparece como préstamo para negocio en Findex y como líneas productivas, microcrédito o cartera por productor en las fuentes nacionales.", "por_que_importa": "Es el tipo de crédito que puede mejorar producción e ingresos, no solo cubrir necesidades inmediatas."},
    {"concepto": "Crédito de subsistencia", "significado": "Endeudamiento para cubrir necesidades básicas, especialmente comprar alimentos a crédito.", "en_el_dashboard": "Aparece como crédito de subsistencia y como ratio subsistencia/productivo.", "por_que_importa": "Cuando supera al crédito productivo, la deuda está ayudando a sobrevivir, no necesariamente a invertir."},
    {"concepto": "Pagos agrícolas en efectivo", "significado": "Pagos recibidos por productos agrícolas sin pasar por cuenta bancaria o digital.", "en_el_dashboard": "Aparece como pagos agrícolas en efectivo y efectivo agrícola porcentual.", "por_que_importa": "Si el ingreso del productor queda en efectivo, no deja trazabilidad financiera y es más difícil construir historial crediticio."},
    {"concepto": "Arquitectura institucional", "significado": "Conjunto de entidades, reglas, garantías, líneas de crédito y cobertura territorial que definen quién puede acceder al financiamiento.", "en_el_dashboard": "Se interpreta con FINAGRO, BCE, SEPS, BCP, cooperativas y el dato faltante del CAH.", "por_que_importa": "La investigación sostiene que la diferencia entre países no depende solo de internet, sino de cómo está diseñado el financiamiento rural."},
    {"concepto": "Oferta de crédito", "significado": "Datos de instituciones que entregan o registran crédito: montos, operaciones, segmentos y fuentes oficiales.", "en_el_dashboard": "Se observa en cartera anual, tipo de crédito y fuentes como FINAGRO, BCE, SEPS y BCP.", "por_que_importa": "Sirve para contrastar si el sistema financiero realmente está canalizando recursos hacia productores pequeños o rurales."},
    {"concepto": "Demanda financiera", "significado": "Datos de personas encuestadas sobre uso de cuentas, pagos, préstamos y barreras de acceso.", "en_el_dashboard": "Se observa en Global Findex 2021 y 2024.", "por_que_importa": "Muestra si los adultos rurales y vinculados al sector agrícola están usando crédito formal o siguen dependiendo de efectivo y subsistencia."}
]

RELACIONES_TABLAS = [
    {"tabla_o_dataset": "paises", "que_guarda": "Catálogo maestro de Colombia, Ecuador y Paraguay.", "llave_principal": "pais_id", "se_relaciona_con": "cartera_anual, tipo_credito, zona_residencia, metadatos, indicadores_findex, indicadores_rural_urbano", "lectura_publico": "Es la tabla base: cada registro de crédito o indicador se conecta a un país para que el dashboard pueda filtrar y comparar."},
    {"tabla_o_dataset": "cartera_anual", "que_guarda": "Montos y operaciones anuales de crédito por país y segmento institucional.", "llave_principal": "id", "se_relaciona_con": "paises mediante pais_id", "lectura_publico": "Responde cuánto crédito reportan las instituciones oficiales cada año y en qué segmento se concentra."},
    {"tabla_o_dataset": "tipo_credito", "que_guarda": "Desglose de la cartera por línea o categoría: inversión, capital de trabajo, microcrédito, productivo, bancos, cooperativas.", "llave_principal": "id", "se_relaciona_con": "paises mediante pais_id y complementa cartera_anual", "lectura_publico": "Permite saber si el crédito sirve para invertir, operar, refinanciar deuda o si está concentrado en bancos o cooperativas."},
    {"tabla_o_dataset": "zona_residencia", "que_guarda": "Información rural, rural dispersa o urbana cuando la fuente de oferta lo permite.", "llave_principal": "id", "se_relaciona_con": "paises mediante pais_id", "lectura_publico": "Ayuda a mirar si el crédito llega al territorio rural o se queda en zonas más integradas al sistema financiero."},
    {"tabla_o_dataset": "metadatos", "que_guarda": "Origen, formato, fecha y observaciones de cada fuente.", "llave_principal": "id", "se_relaciona_con": "paises mediante pais_id", "lectura_publico": "Sirve para transparencia: permite explicar de dónde salió cada dato y qué limitaciones tiene."},
    {"tabla_o_dataset": "indicadores_findex", "que_guarda": "Indicadores de demanda financiera: cuenta, internet, pagos digitales, crédito formal, préstamo para negocio, subsistencia y pagos agrícolas.", "llave_principal": "pais_id + anio", "se_relaciona_con": "paises y diagnostico_brecha", "lectura_publico": "Muestra qué hacen las personas con el sistema financiero, no solo cuánto dinero prestan las instituciones."},
    {"tabla_o_dataset": "indicadores_rural_urbano", "que_guarda": "Indicadores Findex 2024 separados entre zona rural y urbana.", "llave_principal": "pais_id + anio + zona", "se_relaciona_con": "paises", "lectura_publico": "Permite ver si la brecha es más fuerte en el campo que en la ciudad."},
    {"tabla_o_dataset": "diagnostico_brecha", "que_guarda": "Resultado calculado del nivel de brecha, puntaje, ratio y texto explicativo.", "llave_principal": "pais_id + anio", "se_relaciona_con": "indicadores_findex", "lectura_publico": "Resume los indicadores en una lectura entendible: moderada, media, alta o crítica."},
    {"tabla_o_dataset": "datos_faltantes", "que_guarda": "Información que falta para mejorar el análisis, como datos estructurados del CAH o ruralidad detallada.", "llave_principal": "id", "se_relaciona_con": "paises y fuentes", "lectura_publico": "Aclara qué tan completo es el análisis y qué se necesita conseguir para hacerlo más sólido."},
    {"tabla_o_dataset": "recomendaciones", "que_guarda": "Acciones sugeridas según el tipo de brecha detectada.", "llave_principal": "id", "se_relaciona_con": "diagnostico_brecha", "lectura_publico": "Convierte los resultados en propuestas: digitalizar pagos agrícolas, adaptar garantías o fortalecer instituciones rurales."}
]

GUIA_LECTURA_GRAFICAS = [
    {"grafica": "Cuenta digital vs. crédito formal", "como_leerla": "Si la cuenta digital es mucho mayor que el crédito formal, hay inclusión para operar dinero, pero no necesariamente para financiar producción.", "pregunta_que_responde": "¿La digitalización se está convirtiendo en crédito?"},
    {"grafica": "Préstamo para negocio vs. crédito de subsistencia", "como_leerla": "Si subsistencia supera a negocio, la deuda está más ligada a sobrevivir que a invertir.", "pregunta_que_responde": "¿El endeudamiento impulsa producción o cubre necesidades básicas?"},
    {"grafica": "Pagos agrícolas en efectivo vs. cuenta", "como_leerla": "Si domina el efectivo, el ingreso agrícola no deja huella en el sistema financiero.", "pregunta_que_responde": "¿El productor genera trazabilidad financiera?"},
    {"grafica": "Oferta institucional por segmento", "como_leerla": "Si el segmento grande o la banca privada concentra el monto, el sistema puede crecer sin cerrar la brecha del pequeño productor.", "pregunta_que_responde": "¿A quién está llegando la oferta de crédito?"},
    {"grafica": "Rural vs. urbano", "como_leerla": "Si la zona rural tiene menos crédito formal y más subsistencia, la brecha tiene una dimensión territorial.", "pregunta_que_responde": "¿El campo está en desventaja frente a la ciudad?"}
]

FLUJO_ANALITICO = [
    {"paso": 1, "nombre": "Demanda financiera", "explicacion": "Primero se mira qué usan las personas: cuentas, internet, pagos digitales, préstamos y crédito de subsistencia."},
    {"paso": 2, "nombre": "Oferta institucional", "explicacion": "Después se mira qué reportan las instituciones: montos, operaciones, segmentos y fuentes oficiales de crédito."},
    {"paso": 3, "nombre": "Cruce interpretativo", "explicacion": "La brecha aparece al comparar mucha inclusión transaccional con poco crédito formal o productivo."},
    {"paso": 4, "nombre": "Diagnóstico", "explicacion": "El sistema resume la evidencia en nivel de brecha, puntaje y recomendaciones."},
    {"paso": 5, "nombre": "Datos faltantes", "explicacion": "Finalmente se muestran vacíos que limitan la conclusión, como la ausencia de datos estructurados del CAH."}
]

def get_conceptos_clave():
    return pd.DataFrame(CONCEPTOS_CLAVE)

def get_relaciones_tablas():
    return pd.DataFrame(RELACIONES_TABLAS)

def get_guia_lectura_graficas():
    return pd.DataFrame(GUIA_LECTURA_GRAFICAS)

def get_flujo_analitico():
    return pd.DataFrame(FLUJO_ANALITICO)
