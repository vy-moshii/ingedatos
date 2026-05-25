import os
import pandas as pd
import numpy as np
import requests
import streamlit as st
from dotenv import load_dotenv
import data_mock as fallback

load_dotenv()

PAISES = ["Colombia", "Ecuador", "Paraguay"]

def set_page_style(page_id: str = "Home"):
    palettes = {
        "Home": {
            "bg1": "#103048",
            "bg2": "#1b4c5a",
            "accent": "#d9b770",
            "sidebar": "#23343f",
            "sidebar_text": "#f4ecd6",
            "hill": "#3c6b4f",
            "sun": "#f2c96c",
        },
        "Resumen": {
            "bg1": "#183044",
            "bg2": "#2f5e4c",
            "accent": "#d8b66b",
            "sidebar": "#2e2d22",
            "sidebar_text": "#f9f2dc",
            "hill": "#517459",
            "sun": "#ffd27f",
        },
        "Comparativo": {
            "bg1": "#1f2d44",
            "bg2": "#3c4f6b",
            "accent": "#f7c97f",
            "sidebar": "#2d303a",
            "sidebar_text": "#f6edde",
            "hill": "#4d6b5d",
            "sun": "#fcd17a",
        },
        "Colombia": {
            "bg1": "#143b52",
            "bg2": "#266276",
            "accent": "#f2c55d",
            "sidebar": "#2f3d4e",
            "sidebar_text": "#f2ebd9",
            "hill": "#4c755e",
            "sun": "#ffdb85",
        },
        "Ecuador": {
            "bg1": "#1e3342",
            "bg2": "#3a5a6f",
            "accent": "#e8b162",
            "sidebar": "#2f3b43",
            "sidebar_text": "#f1e7d2",
            "hill": "#5b7a62",
            "sun": "#f1ce7e",
        },
        "Paraguay": {
            "bg1": "#273b34",
            "bg2": "#435d59",
            "accent": "#d8a86f",
            "sidebar": "#2b3832",
            "sidebar_text": "#eee3c6",
            "hill": "#5a7c65",
            "sun": "#f3d18a",
        },
        "Diagnostico": {
            "bg1": "#1c2d33",
            "bg2": "#2f4d52",
            "accent": "#c2995b",
            "sidebar": "#243032",
            "sidebar_text": "#ede4cc",
            "hill": "#567065",
            "sun": "#d9b470",
        },
        "Datos": {
            "bg1": "#1a2c3b",
            "bg2": "#304c65",
            "accent": "#bfb06e",
            "sidebar": "#28313c",
            "sidebar_text": "#e7dfc7",
            "hill": "#4c715f",
            "sun": "#e2c478",
        },
    }
    style = palettes.get(page_id, palettes["Home"])
    css = f"""
    <style>
    body, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] .main {{
        background: linear-gradient(180deg, {style['bg1']} 0%, {style['bg2']} 60%, #102c3d 100%) !important;
        color: #f7f3e9;
    }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {style['sidebar']} 15%, #1c2730 100%) !important;
        color: {style['sidebar_text']} !important;
        border-right: 1px solid rgba(255,255,255,.08);
    }}
    [data-testid="stSidebar"] * {{ color: {style['sidebar_text']} !important; }}
    .css-18e3th9 {{ background: transparent !important; }}
    .css-1d391kg {{ background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.08) !important; }}
    .css-1d391kg, .css-1r6slb0, .css-1x8cf1d, .st-bb {{ box-shadow: 0 18px 45px -30px rgba(0,0,0,0.5) !important; }}
    .css-1wy0on6 {{ background: rgba(255,255,255,0.08) !important; }}
    .stButton button, .css-oy0x7s, .css-1iyw2u0, .css-1160xsj {{ background-color: rgba(255,255,255,0.12) !important; color: #f8f5ea !important; border-color: rgba(255,255,255,0.14) !important; }}
    .css-1f5u2kp, .css-1a7y5go {{ background: rgba(255,255,255,0.08) !important; }}
    .css-1vsu8ta, .css-13uwx2w {{ background: rgba(255,255,255,0.08) !important; }}
    .streamlit-expanderHeader, .css-1oe6wyh, .css-14xtw13, .css-1jnvc5b {{ color: #f7f3e9 !important; }}
    .css-10trblm.e16nr0p30, .css-1kyxreq, .css-1n0ewfb {{ background: rgba(255,255,255,0.08) !important; }}
    .stApp, .element-container {{ color: #f7f3e9 !important; }}
    .page-hero, .card, .section-label {{ border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 20px 40px rgba(0,0,0,0.18); }}
    .page-hero {{ background: rgba(255,255,255,0.06); backdrop-filter: blur(10px); }}
    .section-label {{ color: {style['accent']} !important; }}
    .card {{ background: rgba(255,255,255,0.08) !important; }}
    .css-1d391kg, .css-1v3fvcr, .css-18e3th9 {{ border-radius: 18px !important; }}
    .page-sun {{ position: fixed; top: 10vh; right: 10vw; width: 180px; height: 180px; border-radius: 50%; background: radial-gradient(circle, {style['sun']} 0%, transparent 60%); box-shadow: 0 0 70px rgba(255,215,115,0.35); pointer-events: none; z-index: 0; }}
    .page-hill {{ position: fixed; bottom: 0; left: 0; width: 120%; height: 28vh; background: radial-gradient(circle at 20% 0%, {style['hill']} 0%, transparent 60%); opacity: 0.85; transform: skewY(-7deg); pointer-events: none; z-index: 0; }}
    .page-field {{ position: fixed; bottom: 0; left: 0; width: 100%; height: 15vh; background: linear-gradient(180deg, transparent 0%, rgba(255,255,255,0.05) 30%, rgba(255,255,255,0.12) 100%); pointer-events: none; z-index: 0; }}
    .page-clouds {{ position: fixed; top: 12vh; left: -10%; width: 220%; height: 140px; background: radial-gradient(circle at 20% 40%, rgba(255,255,255,0.15) 0%, transparent 38%),
             radial-gradient(circle at 50% 20%, rgba(255,255,255,0.12) 0%, transparent 32%),
             radial-gradient(circle at 80% 35%, rgba(255,255,255,0.13) 0%, transparent 34%);
        opacity: 0.65; pointer-events: none; z-index: 0;
        animation: floatClouds 18s ease-in-out infinite;
    }}
    @keyframes floatClouds {{
        0%, 100% {{ transform: translateX(-10px); }}
        50% {{ transform: translateX(10px); }}
    }}
    .page-overlay {{ position: fixed; inset: 0; pointer-events: none; background: linear-gradient(180deg, rgba(255,255,255,0.03), transparent 30%, rgba(255,255,255,0.04)); z-index: 0; }}
    .page-content {{ position: relative; z-index: 1; }}
    </style>
    <div class="page-sun"></div>
    <div class="page-clouds"></div>
    <div class="page-hill"></div>
    <div class="page-field"></div>
    <div class="page-overlay"></div>
    """
    st.markdown(css, unsafe_allow_html=True)

CODIGOS_PAIS = {
    "Colombia": "COL",
    "Ecuador": "ECU",
    "Paraguay": "PRY"
}

CODIGO_A_PAIS = {
    "COL": "Colombia",
    "ECU": "Ecuador",
    "PRY": "Paraguay"
}


def base_url():
    url = os.getenv("AGROCREDIT_API_URL", "http://127.0.0.1:8000/api/v1")
    return url.strip().rstrip("/")


def cargar_api(endpoint):
    url = f"{base_url()}/{endpoint.lstrip('/')}"
    response = requests.get(url, timeout=20)

    if response.status_code != 200:
        raise RuntimeError(f"Error al consultar {url}. Código: {response.status_code}. Respuesta: {response.text}")

    return pd.DataFrame(response.json())


def agregar_nombre_pais(df):
    if "pais" not in df.columns and "pais_id" in df.columns:
        df["pais"] = df["pais_id"].map(CODIGO_A_PAIS)

    return df


def convertir_numericas(df, columnas):
    for columna in columnas:
        if columna in df.columns:
            df[columna] = pd.to_numeric(df[columna], errors="coerce")

    return df


def asegurar_columnas(df, columnas):
    for columna in columnas:
        if columna not in df.columns:
            df[columna] = np.nan

    return df


def normalizar_findex(df):
    df = agregar_nombre_pais(df)

    if "movil_info_agricola" in df.columns and "info_agricola_digital" not in df.columns:
        df["info_agricola_digital"] = df["movil_info_agricola"]

    columnas = [
        "cuenta_financiera",
        "cuenta_banco_formal",
        "cuenta_dinero_movil",
        "cuenta_digital",
        "cuenta_inactiva",
        "pago_digital",
        "ahorro_formal_movil",
        "smartphone",
        "internet",
        "info_agricola_digital",
        "prestamo_cualquier_fuente",
        "prestamo_banco_formal",
        "prestamo_proveedor_movil",
        "prestamo_familia_amigos",
        "prestamo_negocio",
        "credito_subsistencia",
        "prestamo_recibido_movil",
        "pagos_agricolas_total",
        "pagos_agricolas_cuenta",
        "pagos_agricolas_banco",
        "pagos_agricolas_efectivo",
        "brecha_digital_credito_pp",
        "ratio_subsistencia_productivo",
        "efectivo_agricola_pct"
    ]

    df = asegurar_columnas(df, ["pais", "pais_id", "anio"] + columnas)
    df = convertir_numericas(df, ["anio"] + columnas)

    if "ratio_subsistencia_productivo" in df.columns:
        mask = df["ratio_subsistencia_productivo"].isna()
        df.loc[mask, "ratio_subsistencia_productivo"] = (
            df.loc[mask, "credito_subsistencia"] / df.loc[mask, "prestamo_negocio"]
        )

    if "brecha_digital_credito_pp" in df.columns:
        mask = df["brecha_digital_credito_pp"].isna()
        df.loc[mask, "brecha_digital_credito_pp"] = (
            df.loc[mask, "cuenta_digital"] - df.loc[mask, "prestamo_banco_formal"]
        )

    if "efectivo_agricola_pct" in df.columns:
        mask = df["efectivo_agricola_pct"].isna()
        df.loc[mask, "efectivo_agricola_pct"] = (
            df.loc[mask, "pagos_agricolas_efectivo"] / df.loc[mask, "pagos_agricolas_total"] * 100
        )

    variaciones = {}

    for pais in df["pais"].dropna().unique():
        datos_pais = df[df["pais"] == pais]
        base = datos_pais[datos_pais["anio"] == 2021]
        actual = datos_pais[datos_pais["anio"] == 2024]

        if not base.empty and not actual.empty:
            variaciones[pais] = (
                actual.iloc[0]["prestamo_banco_formal"] -
                base.iloc[0]["prestamo_banco_formal"]
            )

    df["variacion_credito_formal_pp"] = df["pais"].map(variaciones).fillna(0)

    return df


def normalizar_oferta(df):
    df = agregar_nombre_pais(df)

    if "valor_miles_usd" in df.columns and "valor_millones_usd" not in df.columns:
        df["valor_millones_usd"] = df["valor_miles_usd"]

    if "tipo_productor" in df.columns and "segmento" not in df.columns:
        df["segmento"] = df["tipo_productor"]

    if "categoria" in df.columns and "segmento" not in df.columns:
        df["segmento"] = df["categoria"]

    if "fuente" not in df.columns:
        df["fuente"] = "PostgreSQL"

    if "n_operaciones" not in df.columns:
        df["n_operaciones"] = np.nan

    if "unidad_medida" not in df.columns:
        df["unidad_medida"] = "Millones USD"

    if "tipo_dato" not in df.columns:
        df["tipo_dato"] = "Oferta institucional"

    df = asegurar_columnas(
        df,
        [
            "pais",
            "pais_id",
            "anio",
            "fuente",
            "segmento",
            "n_operaciones",
            "valor_millones_usd",
            "unidad_medida",
            "tipo_dato"
        ]
    )

    df = convertir_numericas(df, ["anio", "n_operaciones", "valor_millones_usd"])

    return df


def normalizar_tipo_credito(df):
    df = agregar_nombre_pais(df)

    if "valor_miles_usd" in df.columns and "valor_millones_usd" not in df.columns:
        df["valor_millones_usd"] = df["valor_miles_usd"]

    if "tipo_productor" in df.columns and "segmento" not in df.columns:
        df["segmento"] = df["tipo_productor"]

    if "fuente" not in df.columns:
        df["fuente"] = "PostgreSQL"

    if "categoria" not in df.columns:
        df["categoria"] = "sin_categoria"

    if "n_operaciones" not in df.columns:
        df["n_operaciones"] = np.nan

    df = asegurar_columnas(
        df,
        [
            "pais",
            "pais_id",
            "anio",
            "fuente",
            "categoria",
            "segmento",
            "n_operaciones",
            "valor_millones_usd"
        ]
    )

    df = convertir_numericas(df, ["anio", "n_operaciones", "valor_millones_usd"])

    return df


def normalizar_rural_urban(df):
    df = agregar_nombre_pais(df)

    renombres = {
        "Cuenta financiera": "cuenta_financiera",
        "Cuenta habilitada digitalmente": "cuenta_digital",
        "Préstamo banco formal": "prestamo_banco_formal",
        "Compró alimentos a crédito": "credito_subsistencia",
        "Smartphone": "smartphone",
        "Uso de internet": "internet",
        "Banco muy lejos": "barrera_distancia",
        "Servicios muy caros": "barrera_costo",
        "Fondos insuficientes": "barrera_fondos",
        "Muy difícil reunir fondos de emergencia": "resiliencia_dificil"
    }

    df = df.rename(columns=renombres)

    if {"indicador", "valor"}.issubset(df.columns):
        index_cols = [col for col in ["pais", "pais_id", "zona", "anio"] if col in df.columns]
        df = df.pivot_table(
            index=index_cols,
            columns="indicador",
            values="valor",
            aggfunc="first"
        ).reset_index()
        df.columns.name = None
        df = df.rename(columns=renombres)

    df = asegurar_columnas(
        df,
        [
            "pais",
            "pais_id",
            "zona",
            "anio",
            "cuenta_financiera",
            "cuenta_digital",
            "prestamo_banco_formal",
            "credito_subsistencia",
            "smartphone",
            "internet",
            "barrera_costo",
            "barrera_fondos",
            "barrera_distancia",
            "resiliencia_dificil"
        ]
    )

    df = convertir_numericas(
        df,
        [
            "anio",
            "cuenta_financiera",
            "cuenta_digital",
            "prestamo_banco_formal",
            "credito_subsistencia",
            "smartphone",
            "internet",
            "barrera_costo",
            "barrera_fondos",
            "barrera_distancia",
            "resiliencia_dificil"
        ]
    )

    return df


def get_findex():
    df = cargar_api("findex")
    return normalizar_findex(df)


def get_oferta():
    df = cargar_api("oferta")
    return normalizar_oferta(df)


def get_tipo_credito():
    try:
        partes = []

        for codigo in CODIGO_A_PAIS:
            df = cargar_api(f"tipo_credito/{codigo}")
            partes.append(df)

        df = pd.concat(partes, ignore_index=True)
        return normalizar_tipo_credito(df)
    except Exception as error:
        print(f"Error cargando tipo_credito desde API: {error}. Usando datos locales de respaldo.")
        return fallback.get_tipo_credito()


def get_rural_urban():
    df = cargar_api("rural_urban")
    return normalizar_rural_urban(df)


def get_missing_data():
    return cargar_api("missing")


def get_sources():
    return cargar_api("fuentes")


def get_dictionary():
    return cargar_api("diccionario")


def get_recomendaciones():
    try:
        return cargar_api("recomendaciones")
    except Exception as error:
        print(f"Error al consultar recomendaciones desde API: {error}. Usando datos locales de respaldo.")
        return fallback.get_recomendaciones()


def get_finagro_sexo(anio=None):
    endpoint = "finagro/sexo"

    if anio is not None:
        endpoint += f"?anio={anio}"

    return cargar_api(endpoint)


def get_finagro_departamento(anio=None, tipo=None):
    params = []

    if anio is not None:
        params.append(f"anio={anio}")

    if tipo:
        params.append(f"tipo={tipo}")

    endpoint = "finagro/departamento"

    if params:
        endpoint += "?" + "&".join(params)

    return cargar_api(endpoint)


def get_finagro_cadena(anio=None):
    endpoint = "finagro/cadena"

    if anio is not None:
        endpoint += f"?anio={anio}"

    return cargar_api(endpoint)


def get_narrativa():
    return {
        "titulo": "Entre la cuenta y el crédito",
        "subtitulo": "Brechas de integración productiva en el financiamiento rural de Colombia, Ecuador y Paraguay",
        "pregunta": "¿Por qué la inclusión financiera digital no se traduce automáticamente en crédito productivo rural?",
        "hipotesis": "La diferencia no se explica solo por el nivel de digitalización, sino por la arquitectura institucional del financiamiento rural.",
        "descripcion": "La aplicación analiza si los avances en cuentas, pagos digitales e internet realmente se convierten en acceso a crédito productivo para pequeños productores rurales.",
        "resultado_principal": "Colombia y Ecuador retroceden en crédito formal, mientras Paraguay aparece como caso contrastante con crecimiento.",
        "mensaje_clave": "Tener cuenta o usar servicios digitales no significa necesariamente ser sujeto de crédito productivo."
    }

def get_conceptos_clave():
    data = [
        {
            "concepto": "Inclusión transaccional",
            "significado": "Capacidad de una persona para tener y usar servicios financieros básicos como cuenta, pagos, ahorro o transferencias.",
            "en_el_dashboard": "Se observa con cuenta financiera, cuenta digital, pago digital, internet y ahorro formal o móvil.",
            "por_que_importa": "El artículo muestra que tener cuenta o internet no significa automáticamente tener crédito para producir."
        },
        {
            "concepto": "Integración productiva",
            "significado": "Momento en que la inclusión financiera permite financiar una actividad económica real, por ejemplo sembrar, comprar insumos, invertir en maquinaria o sostener una unidad productiva rural.",
            "en_el_dashboard": "Se aproxima con préstamo para negocio, crédito formal y segmentos de menor escala de la oferta institucional.",
            "por_que_importa": "Es el centro del proyecto: pasar de estar dentro del sistema financiero a ser reconocido como sujeto de crédito productivo."
        },
        {
            "concepto": "Brecha de integración productiva",
            "significado": "Distancia entre estar incluido transaccionalmente y acceder de verdad a crédito productivo formal.",
            "en_el_dashboard": "Se calcula comparando cuenta digital con préstamo bancario formal y préstamo para negocio.",
            "por_que_importa": "Permite ver si la digitalización está ayudando a producir o solo a pagar, ahorrar o transferir."
        },
        {
            "concepto": "Circuito del efectivo",
            "significado": "Pagos agrícolas recibidos en efectivo que no generan trazabilidad financiera.",
            "en_el_dashboard": "Se observa como pagos agrícolas en efectivo y efectivo agrícola porcentual.",
            "por_que_importa": "Si el ingreso del productor queda en efectivo, no deja trazabilidad financiera y es más difícil construir historial crediticio."
        }
    ]

    return pd.DataFrame(data)


def get_relaciones_tablas():
    data = [
        {"tabla_o_dataset": "paises", "relacion": "Tabla base para relacionar todos los indicadores por país."},
        {"tabla_o_dataset": "cartera_anual", "relacion": "Oferta institucional de crédito agropecuario."},
        {"tabla_o_dataset": "tipo_credito", "relacion": "Detalle por categoría, línea o tipo de crédito."},
        {"tabla_o_dataset": "indicadores_findex", "relacion": "Demanda financiera, digitalización y crédito formal."},
        {"tabla_o_dataset": "indicadores_rural_urbano", "relacion": "Brechas por zona de residencia."},
        {"tabla_o_dataset": "diagnostico_brecha", "relacion": "Resultado calculado del análisis por país."},
        {"tabla_o_dataset": "recomendaciones", "relacion": "Sugerencias generadas desde el diagnóstico."}
    ]

    return pd.DataFrame(data)


def get_guia_lectura_graficas():
    data = [
        {"grafica": "Findex 2024", "lectura": "Compara digitalización y crédito productivo."},
        {"grafica": "Oferta 2019-2024", "lectura": "Permite ver tendencias internas por país."},
        {"grafica": "Rural vs urbano", "lectura": "Muestra si la brecha se intensifica en zonas rurales."},
        {"grafica": "Diagnóstico", "lectura": "Resume el nivel de brecha según indicadores clave."}
    ]

    return pd.DataFrame(data)


def get_flujo_analitico():
    data = [
        {"paso": 1, "nombre": "Inclusión transaccional", "descripcion": "Se revisan cuentas, pagos digitales e internet."},
        {"paso": 2, "nombre": "Crédito formal", "descripcion": "Se observa el acceso a préstamo bancario y préstamo para negocio."},
        {"paso": 3, "nombre": "Circuito productivo", "descripcion": "Se analiza si los pagos agrícolas pasan por cuenta o efectivo."},
        {"paso": 4, "nombre": "Brecha", "descripcion": "Se compara digitalización con acceso efectivo al crédito."},
        {"paso": 5, "nombre": "Recomendación", "descripcion": "Se genera una salida orientada a política pública."}
    ]

    return pd.DataFrame(data)


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

    actual = df[(df["pais"] == pais) & (df["anio"] == 2024)]
    base = df[(df["pais"] == pais) & (df["anio"] == 2021)]

    if actual.empty or base.empty:
        raise RuntimeError(f"No hay datos suficientes para diagnosticar {pais}")

    actual = actual.iloc[0]
    base = base.iloc[0]

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

    texto = (
        f"{pais} presenta una brecha {nivel.lower()} porque la cuenta digital alcanza "
        f"{actual['cuenta_digital']:.1f}%, el crédito bancario formal llega a "
        f"{actual['prestamo_banco_formal']:.1f}% y el crédito de subsistencia equivale a "
        f"{ratio:.1f} veces el préstamo para negocio."
    )

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
    return pd.DataFrame([diagnosticar_pais(pais) for pais in PAISES])


def segmento_menor_escala():
    df = get_oferta()
    segmento = df["segmento"].astype(str).str.lower()

    condiciones = (
        ((df["pais"] == "Colombia") & segmento.str.contains("pequenio|pequeño", regex=True)) |
        ((df["pais"] == "Ecuador") & segmento.str.contains("microcredito|microcrédito", regex=True)) |
        ((df["pais"] == "Paraguay") & segmento.str.contains("cooperativa", regex=True))
    )

    return df[condiciones].copy()


def descargar_csv(df):
    return df.to_csv(index=False).encode("utf-8")


def obtener_dataset(nombre):
    datasets = {
        "findex": get_findex,
        "oferta": get_oferta,
        "tipo_credito": get_tipo_credito,
        "rural_urban": get_rural_urban,
        "missing": get_missing_data,
        "fuentes": get_sources,
        "diccionario": get_dictionary,
        "diagnosticos": diagnosticos,
        "recomendaciones": get_recomendaciones,
        "finagro_sexo": get_finagro_sexo,
        "finagro_departamento": get_finagro_departamento,
        "finagro_cadena": get_finagro_cadena
    }

    if nombre not in datasets:
        raise ValueError(f"No existe el dataset {nombre}")

    return datasets[nombre]()