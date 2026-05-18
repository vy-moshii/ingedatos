import streamlit as st
from data_mock import get_sources, get_dictionary, get_missing_data, get_findex, get_oferta, get_tipo_credito, get_rural_urban, get_conceptos_clave, get_relaciones_tablas, get_guia_lectura_graficas, get_flujo_analitico, descargar_csv

st.set_page_config(page_title="Datos y fuentes", page_icon="🗂️", layout="wide")

st.title("Datos y fuentes")
st.write("Esta pantalla documenta qué datos usa el prototipo, cómo se relacionan las tablas, qué significa cada concepto y cuáles son los vacíos que deben resolverse para una versión final conectada a PostgreSQL o FastAPI.")

st.subheader("Flujo analítico del dashboard")
st.write(" Sigue una ruta: primero demanda, luego oferta, después cruce de brecha, diagnóstico y datos faltantes.")
st.dataframe(get_flujo_analitico(), use_container_width=True)

st.subheader("Fuentes del proyecto")
st.write("Las fuentes se dividen en dos grupos. Findex mide demanda financiera de adultos; FINAGRO, BCE, SEPS y BCP miden oferta institucional de crédito. Esa separación es importante porque una fuente puede mostrar más crédito en el sistema mientras otra muestra que las personas no acceden a crédito formal.")
sources = get_sources()
st.dataframe(sources, use_container_width=True)
st.download_button("Descargar fuentes CSV", data=descargar_csv(sources), file_name="fuentes.csv", mime="text/csv")

st.subheader("Relación entre tablas y datasets")
relaciones = get_relaciones_tablas()
st.dataframe(relaciones, use_container_width=True)
st.download_button("Descargar relación de tablas CSV", data=descargar_csv(relaciones), file_name="relacion_tablas.csv", mime="text/csv")

st.subheader("Glosario del artículo convertido a lenguaje de dashboard")
st.write("Estos conceptos son los que el público necesita entender para leer el dashboard sin conocer previamente el artículo.")
conceptos = get_conceptos_clave()
st.dataframe(conceptos, use_container_width=True)
st.download_button("Descargar glosario CSV", data=descargar_csv(conceptos), file_name="glosario_agrocredit.csv", mime="text/csv")

st.subheader("Diccionario de indicadores Findex")
st.write("Este diccionario conecta los nombres amigables del dashboard con los indicadores usados para representar cuenta, digitalización, crédito, barreras y resiliencia.")
dictionary = get_dictionary()
st.dataframe(dictionary, use_container_width=True)

st.subheader("Cómo leer las gráficas")
st.dataframe(get_guia_lectura_graficas(), use_container_width=True)

st.subheader("Datos faltantes")
st.write("Los datos faltantes no son un error del dashboard: son parte de la transparencia del análisis. Sirven para mostrar qué información falta para que la conclusión sea más fuerte, especialmente en Paraguay con el CAH.")
missing = get_missing_data()
st.dataframe(missing, use_container_width=True)

st.subheader("Vista previa de datasets")
st.write("Estas tablas son las que hoy alimentan el prototipo. Cuando haya PostgreSQL o FastAPI, las pantallas deberían consultar vistas o endpoints con estos mismos nombres lógicos.")
tabs = st.tabs(["Findex", "Oferta", "Tipo crédito", "Rural urbano"])
with tabs[0]:
    df = get_findex()
    st.write("Findex representa la demanda: lo que las personas reportan sobre cuentas, pagos, préstamos y barreras.")
    st.dataframe(df, use_container_width=True)
    st.download_button("Descargar Findex mock CSV", data=descargar_csv(df), file_name="findex_mock.csv", mime="text/csv")
with tabs[1]:
    df = get_oferta()
    st.write("Oferta representa registros institucionales: montos, operaciones y segmentos de crédito por país y año.")
    st.dataframe(df, use_container_width=True)
    st.download_button("Descargar oferta mock CSV", data=descargar_csv(df), file_name="oferta_mock.csv", mime="text/csv")
with tabs[2]:
    df = get_tipo_credito()
    st.write("Tipo crédito desagrega la oferta por líneas, categorías o entidades, lo que permite ver concentración y orientación productiva.")
    st.dataframe(df, use_container_width=True)
    st.download_button("Descargar tipo crédito mock CSV", data=descargar_csv(df), file_name="tipo_credito_mock.csv", mime="text/csv")
with tabs[3]:
    df = get_rural_urban()
    st.write("Rural urbano permite comparar si la brecha se profundiza en el campo frente a las ciudades.")
    st.dataframe(df, use_container_width=True)
    st.download_button("Descargar rural urbano mock CSV", data=descargar_csv(df), file_name="rural_urbano_mock.csv", mime="text/csv")

