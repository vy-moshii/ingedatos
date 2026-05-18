import streamlit as st
import plotly.express as px
from data_mock import get_oferta, get_tipo_credito, get_findex, get_rural_urban, diagnosticar_pais, get_conceptos_clave, get_relaciones_tablas, descargar_csv

st.set_page_config(page_title="Ecuador", page_icon="🇪🇨", layout="wide")

st.title("Ecuador")
st.write("Ecuador permite analizar una tensión importante: existe un sistema financiero amplio, pero el crédito productivo aparece muy concentrado en la banca privada y el microcrédito cae después de 2022.")

with st.sidebar:
    st.header("Filtros Ecuador")
    rango = st.slider("Rango de años", 2019, 2024, (2019, 2024))

st.info("Lectura del caso: el problema no es solo si hay crédito en el sistema, sino qué tipo de entidad lo entrega y si los segmentos cercanos al pequeño productor tienen peso real.")

oferta = get_oferta()
oferta_ecu = oferta[(oferta["pais"] == "Ecuador") & (oferta["anio"] >= rango[0]) & (oferta["anio"] <= rango[1])]
tipo = get_tipo_credito()
tipo_ecu = tipo[(tipo["pais"] == "Ecuador") & (tipo["anio"] >= rango[0]) & (tipo["anio"] <= rango[1])]
findex = get_findex()
f_ecu = findex[findex["pais"] == "Ecuador"]
diag = diagnosticar_pais("Ecuador")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Nivel de brecha", diag["nivel"])
c2.metric("Cambio crédito formal", f"{diag['cambio_credito_formal_pp']:.1f} pp")
c3.metric("Brecha digital-crédito", f"{diag['brecha_digital_credito_pp']:.1f} pp")
c4.metric("Subsistencia/Productivo", f"{diag['ratio_subsistencia_productivo']:.1f}x")

st.info(diag["texto"])

with st.expander("Términos clave para entender Ecuador"):
    conceptos = get_conceptos_clave()
    st.dataframe(conceptos[conceptos["concepto"].isin(["Crédito formal", "Crédito productivo", "Crédito de subsistencia", "Arquitectura institucional", "Oferta de crédito"])], use_container_width=True)

st.subheader("Sistema financiero BCE por segmento")
st.write("La tabla `cartera_anual` resume los segmentos reportados por el sistema financiero: productivo, microcrédito, consumo e inmobiliario. Para esta investigación, productivo y microcrédito son los más relevantes porque se acercan más a actividades económicas y unidades pequeñas.")
fig = px.line(oferta_ecu, x="anio", y="valor_millones_usd", color="segmento", markers=True, labels={"valor_millones_usd": "Millones USD", "anio": "Año", "segmento": "Segmento"}, title="Crédito productivo, microcrédito y consumo")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Crédito productivo por tipo de entidad")
st.write("Esta gráfica usa `tipo_credito` para separar bancos privados y cooperativas. La lectura importante es si el crédito productivo está distribuido entre actores cercanos a pequeños productores o si se concentra casi totalmente en banca privada.")
prod = tipo_ecu[tipo_ecu["categoria"] == "productivo"]
fig2 = px.bar(prod, x="anio", y="valor_millones_usd", color="segmento", labels={"valor_millones_usd": "Millones USD", "anio": "Año", "segmento": "Entidad"}, title="Concentración del crédito productivo")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Microcrédito cooperativo SEPS")
st.write("La SEPS es relevante porque supervisa cooperativas del sector popular y solidario. En el enfoque del artículo, las cooperativas pueden estar más cerca de productores de menor escala que la banca privada tradicional.")
seps = tipo_ecu[tipo_ecu["categoria"] == "microcredito_seps"]
fig3 = px.line(seps, x="anio", y="valor_millones_usd", markers=True, labels={"valor_millones_usd": "Millones USD", "anio": "Año"}, title="Microcrédito SEPS cooperativas y mutualistas")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Demanda Findex Ecuador")
st.write("Findex permite revisar si la población adulta reporta acceso a cuenta, pagos y préstamo formal. La caída del préstamo formal es relevante porque ocurre aunque el uso de internet sea alto.")
fig4 = px.line(f_ecu, x="anio", y=["cuenta_financiera", "pago_digital", "prestamo_banco_formal"], markers=True, labels={"value": "% adultos", "variable": "Indicador", "anio": "Año"}, title="Inclusión transaccional vs. crédito formal")
st.plotly_chart(fig4, use_container_width=True)

st.subheader("Rural vs. urbano 2024")
st.write("La comparación rural-urbana muestra si la brecha es más severa en el campo. En Ecuador, la resiliencia financiera rural y el acceso digital ayudan a interpretar por qué la inclusión transaccional no basta.")
rural = get_rural_urban()
rural_ecu = rural[rural["pais"] == "Ecuador"]
st.dataframe(rural_ecu, use_container_width=True)

with st.expander("Relación de tablas usadas en esta pantalla"):
    relaciones = get_relaciones_tablas()
    st.dataframe(relaciones[relaciones["tabla_o_dataset"].isin(["paises", "cartera_anual", "tipo_credito", "indicadores_findex", "indicadores_rural_urbano", "metadatos"])], use_container_width=True)

st.subheader("Datos usados")
st.dataframe(oferta_ecu, use_container_width=True)
st.download_button("Descargar Ecuador CSV", data=descargar_csv(oferta_ecu), file_name="ecuador_credito.csv", mime="text/csv")
