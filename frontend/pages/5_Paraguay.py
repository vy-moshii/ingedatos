import streamlit as st
import plotly.express as px
from data_client import get_oferta, get_findex, get_rural_urban, diagnosticar_pais, get_missing_data, get_conceptos_clave, get_relaciones_tablas, descargar_csv, set_page_style

st.set_page_config(page_title="Paraguay", page_icon="🇵🇾", layout="wide")
set_page_style("Paraguay")

st.title("Paraguay")
st.write("Paraguay es el caso contrastante: el crédito formal crece en Findex, pero falta incorporar datos estructurados del CAH para confirmar la explicación desde la oferta institucional.")

with st.sidebar:
    st.header("Filtros Paraguay")
    rango = st.slider("Rango de años", 2019, 2024, (2019, 2024))

st.info("Lectura del caso: Paraguay no se interpreta como prueba cerrada, sino como caso sugerente. El artículo lo usa para discutir la importancia de una institución rural especializada como el CAH, pero el SQL todavía no trae esa fuente de forma estructurada.")

oferta = get_oferta()
oferta_pry = oferta[(oferta["pais"] == "Paraguay") & (oferta["anio"] >= rango[0]) & (oferta["anio"] <= rango[1])]
findex = get_findex()
f_pry = findex[findex["pais"] == "Paraguay"]
diag = diagnosticar_pais("Paraguay")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Nivel de brecha", diag["nivel"])
c2.metric("Cambio crédito formal", f"{diag['cambio_credito_formal_pp']:.1f} pp")
c3.metric("Brecha digital-crédito", f"{diag['brecha_digital_credito_pp']:.1f} pp")
c4.metric("Préstamo móvil 2024", "11.4%")

st.info(diag["texto"])

with st.expander("Términos clave para entender Paraguay"):
    conceptos = get_conceptos_clave()
    st.dataframe(conceptos[conceptos["concepto"].isin(["Arquitectura institucional", "Crédito formal", "Crédito productivo", "Pagos agrícolas en efectivo", "Oferta de crédito"])], use_container_width=True)

st.subheader("BCP: bancos/financieras vs. cooperativas tipo A")
st.write("La tabla `cartera_anual` contiene bancos, financieras y cooperativas tipo A del BCP. Estos datos muestran el sistema financiero formal, pero no reemplazan al CAH, que es la institución más importante para discutir crédito rural especializado en Paraguay.")
fig = px.line(oferta_pry, x="anio", y="valor_millones_usd", color="segmento", markers=True, labels={"valor_millones_usd": "Millones USD", "anio": "Año", "segmento": "Intermediario"}, title="Sistema financiero formal de Paraguay")
st.plotly_chart(fig, use_container_width=True)

st.warning("Dato faltante crítico: el SQL y el artículo no incluyen una tabla estructurada del CAH. Por eso esta pantalla deja explícito que Paraguay es un caso sugerente, no una prueba cerrada desde oferta.")

st.subheader("Demanda Findex Paraguay")
st.write("Aquí se ve la parte más fuerte del caso paraguayo: Findex registra crecimiento en crédito formal entre 2021 y 2024. Esa trayectoria es distinta a Colombia y Ecuador.")
fig2 = px.line(f_pry, x="anio", y=["cuenta_financiera", "pago_digital", "prestamo_banco_formal"], markers=True, labels={"value": "% adultos", "variable": "Indicador", "anio": "Año"}, title="Inclusión transaccional vs. crédito formal")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Pagos agrícolas: efectivo vs. cuenta")
st.write("Esta gráfica ayuda a entender si el ingreso agrícola deja trazabilidad. Cuando los pagos se reciben en cuenta, hay más posibilidades de construir historial; cuando dominan en efectivo, el productor queda menos visible para el sistema financiero.")
fig3 = px.bar(f_pry, x="anio", y=["pagos_agricolas_efectivo", "pagos_agricolas_cuenta", "pagos_agricolas_banco"], barmode="group", labels={"value": "% adultos", "variable": "Modalidad", "anio": "Año"}, title="Modalidad de pagos agrícolas")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Rural vs. urbano 2024")
st.write("Esta tabla permite observar que Paraguay tiene menor dificultad extrema para reunir fondos de emergencia que Colombia y Ecuador rural, aunque sigue mostrando alto crédito de subsistencia rural.")
rural = get_rural_urban()
rural_pry = rural[rural["pais"] == "Paraguay"]
st.dataframe(rural_pry, use_container_width=True)

st.subheader("Datos faltantes relacionados con Paraguay")
missing = get_missing_data()
st.dataframe(missing[missing["pais"].isin(["Paraguay", "Tres países"])], use_container_width=True)

with st.expander("Relación de tablas usadas en esta pantalla"):
    relaciones = get_relaciones_tablas()
    st.dataframe(relaciones[relaciones["tabla_o_dataset"].isin(["paises", "cartera_anual", "indicadores_findex", "indicadores_rural_urbano", "datos_faltantes", "metadatos"])], use_container_width=True)

st.subheader("Datos usados")
st.dataframe(oferta_pry, use_container_width=True)
st.download_button("Descargar Paraguay CSV", data=descargar_csv(oferta_pry), file_name="paraguay_bcp.csv", mime="text/csv")
