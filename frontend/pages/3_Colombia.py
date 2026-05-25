import streamlit as st
import plotly.express as px
from data_client import get_oferta, get_tipo_credito, get_findex, get_rural_urban, diagnosticar_pais, get_conceptos_clave, get_relaciones_tablas, descargar_csv, set_page_style

st.set_page_config(page_title="Colombia", page_icon="🇨🇴", layout="wide")
set_page_style("Colombia")

st.title("Colombia")
st.write("Colombia permite ver el desacople entre crecimiento absoluto de la oferta FINAGRO y baja participación relativa del pequeño productor frente al gran productor.")

with st.sidebar:
    st.header("Filtros Colombia")
    rango = st.slider("Rango de años", 2019, 2024, (2019, 2024))

st.info("Lectura del caso: si FINAGRO desembolsa más dinero total, pero el gran productor concentra la mayor parte, el aumento de oferta no necesariamente significa cierre de brecha para pequeños productores rurales.")

oferta = get_oferta()
oferta_col = oferta[(oferta["pais"] == "Colombia") & (oferta["anio"] >= rango[0]) & (oferta["anio"] <= rango[1])]
tipo = get_tipo_credito()
tipo_col = tipo[(tipo["pais"] == "Colombia") & (tipo["anio"] >= rango[0]) & (tipo["anio"] <= rango[1])]
findex = get_findex()
f_col = findex[findex["pais"] == "Colombia"]
diag = diagnosticar_pais("Colombia")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Nivel de brecha", diag["nivel"])
c2.metric("Cambio crédito formal", f"{diag['cambio_credito_formal_pp']:.1f} pp")
c3.metric("Brecha digital-crédito", f"{diag['brecha_digital_credito_pp']:.1f} pp")
c4.metric("Subsistencia/Productivo", f"{diag['ratio_subsistencia_productivo']:.1f}x")

st.info(diag["texto"])

with st.expander("Términos clave para entender Colombia"):
    conceptos = get_conceptos_clave()
    st.dataframe(conceptos[conceptos["concepto"].isin(["Crédito formal", "Crédito productivo", "Brecha de integración productiva", "Arquitectura institucional"])], use_container_width=True)

st.subheader("FINAGRO por tamaño de productor")
st.write("La tabla `cartera_anual` guarda los montos por año y tipo de productor. En Colombia, el segmento `pequenio` aproxima al productor de menor escala; `mediano` y `grande` ayudan a ver concentración del crédito.")
fig = px.line(oferta_col, x="anio", y="valor_millones_usd", color="segmento", markers=True, labels={"valor_millones_usd": "Millones USD", "anio": "Año", "segmento": "Tamaño de productor"}, title="Monto desembolsado por segmento")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Participación del pequeño productor")
st.write("Esta gráfica no mira solo cuánto creció el monto del pequeño productor, sino cuánto pesa dentro del total. Es importante porque el sistema puede crecer y aun así concentrarse en grandes productores.")
pivot = oferta_col.pivot_table(index="anio", columns="segmento", values="valor_millones_usd", aggfunc="sum").reset_index()
for col in ["grande", "mediano", "pequenio"]:
    if col not in pivot.columns:
        pivot[col] = 0
pivot["total"] = pivot[["grande", "mediano", "pequenio"]].sum(axis=1)
pivot["pct_pequenio"] = pivot["pequenio"] / pivot["total"] * 100
fig2 = px.bar(pivot, x="anio", y="pct_pequenio", labels={"pct_pequenio": "% del total FINAGRO", "anio": "Año"}, title="Participación del pequeño productor en el total")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Líneas de crédito del pequeño productor")
st.write("La tabla `tipo_credito` desagrega el crédito del pequeño productor por uso. `Capital de trabajo` ayuda a operar la actividad; `inversión` puede mejorar capacidad productiva; `normalización de cartera` está más relacionada con reorganizar deuda existente.")
fig3 = px.area(tipo_col, x="anio", y="valor_millones_usd", color="categoria", labels={"valor_millones_usd": "Millones USD", "anio": "Año", "categoria": "Línea"}, title="Capital de trabajo, inversión y normalización de cartera")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Demanda Findex Colombia")
st.write("Esta gráfica cambia de mirada: ya no muestra cuánto desembolsó FINAGRO, sino qué reportan las personas adultas en Findex. Por eso sirve para contrastar oferta institucional con acceso percibido a crédito formal.")
fig4 = px.line(f_col, x="anio", y=["cuenta_financiera", "pago_digital", "prestamo_banco_formal"], markers=True, labels={"value": "% adultos", "variable": "Indicador", "anio": "Año"}, title="Inclusión transaccional vs. crédito formal")
st.plotly_chart(fig4, use_container_width=True)

st.subheader("Rural vs. urbano 2024")
st.write("La comparación territorial muestra si la brecha se profundiza en zonas rurales. En el artículo, esta dimensión es clave porque la investigación se enfoca en financiamiento rural y pequeños productores.")
rural = get_rural_urban()
rural_col = rural[rural["pais"] == "Colombia"]
st.dataframe(rural_col, use_container_width=True)

with st.expander("Relación de tablas usadas en esta pantalla"):
    relaciones = get_relaciones_tablas()
    st.dataframe(relaciones[relaciones["tabla_o_dataset"].isin(["paises", "cartera_anual", "tipo_credito", "indicadores_findex", "indicadores_rural_urbano"])], use_container_width=True)

st.subheader("Datos usados")
st.dataframe(oferta_col, use_container_width=True)
st.download_button("Descargar Colombia CSV", data=descargar_csv(oferta_col), file_name="colombia_finagro.csv", mime="text/csv")
