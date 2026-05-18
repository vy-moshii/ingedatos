import streamlit as st
import plotly.express as px
from data_mock import get_findex, segmento_menor_escala, get_oferta, get_rural_urban, get_conceptos_clave, get_relaciones_tablas, descargar_csv, PAISES

st.set_page_config(page_title="Comparativo", page_icon="🌎", layout="wide")

st.title("Comparativo entre países")
st.write("Esta pantalla une demanda y oferta. Findex explica lo que reportan las personas; las fuentes institucionales explican cómo se comporta la oferta oficial de crédito agropecuario.")

with st.sidebar:
    st.header("Filtros")
    paises = st.multiselect("País", PAISES, default=PAISES)
    rango = st.slider("Rango de años oferta", 2019, 2024, (2019, 2024))

st.info("La comparación no busca decir solamente qué país presta más dinero. Busca responder algo más profundo: si el sistema financiero convierte la inclusión digital en crédito productivo para el sector rural.")

with st.expander("Qué significa cruzar demanda y oferta"):
    st.write("Demanda financiera significa lo que las personas tienen o usan: cuentas, pagos digitales, préstamos y barreras. Oferta institucional significa lo que las entidades registran: montos, operaciones y segmentos de crédito. El dashboard necesita ambas porque puede crecer la oferta total y aun así no llegar al pequeño productor.")
    conceptos = get_conceptos_clave()
    st.dataframe(conceptos[conceptos["concepto"].isin(["Oferta de crédito", "Demanda financiera", "Arquitectura institucional", "Brecha de integración productiva"])], use_container_width=True)

findex = get_findex()
oferta = get_oferta()
menor = segmento_menor_escala()
menor = menor[(menor["pais"].isin(paises)) & (menor["anio"] >= rango[0]) & (menor["anio"] <= rango[1])]

st.subheader("Segmentos de menor escala usados como proxy de inclusión productiva")
st.write("Esta gráfica toma el segmento más cercano al pequeño productor en cada país: pequeño productor en Colombia, microcrédito en Ecuador y cooperativas en Paraguay. No son exactamente lo mismo, pero sirven como aproximación para observar si la oferta institucional llega a segmentos de menor escala.")
fig = px.line(menor, x="anio", y="valor_millones_usd", color="pais", line_dash="segmento", markers=True, labels={"valor_millones_usd": "Millones USD", "anio": "Año", "pais": "País", "segmento": "Segmento"}, title="Oferta institucional relacionada con productores de menor escala")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Mapa conceptual en forma de dispersión")
st.write("Cada punto resume un país en 2024. Lo ideal sería ver países con alta cuenta digital y alto crédito formal. Cuando la cuenta digital sube pero el crédito formal queda bajo, aparece la brecha.")
f2024 = findex[(findex["anio"] == 2024) & (findex["pais"].isin(paises))]
fig2 = px.scatter(
    f2024,
    x="cuenta_digital",
    y="prestamo_banco_formal",
    size="ratio_subsistencia_productivo",
    color="pais",
    hover_data=["internet", "prestamo_negocio", "credito_subsistencia", "efectivo_agricola_pct"],
    labels={"cuenta_digital": "Cuenta digital 2024 (%)", "prestamo_banco_formal": "Crédito formal 2024 (%)", "ratio_subsistencia_productivo": "Subsistencia/Productivo"},
    title="Si la digitalización fuera suficiente, los puntos deberían subir con claridad en crédito formal"
)
st.plotly_chart(fig2, use_container_width=True)
st.caption("El tamaño del punto representa el ratio subsistencia/productivo: mientras más grande, más pesa el endeudamiento para sobrevivir frente al endeudamiento para producir.")

st.subheader("Brecha rural-urbana 2024")
st.write("La comparación rural-urbana muestra si el problema es territorial. Si el crédito formal rural es menor o la subsistencia rural es mayor, la brecha no es solo financiera: también es de acceso territorial.")
rural = get_rural_urban()
rural = rural[rural["pais"].isin(paises)]
fig3 = px.bar(rural, x="pais", y="prestamo_banco_formal", color="zona", barmode="group", labels={"prestamo_banco_formal": "% adultos", "pais": "País", "zona": "Zona"}, title="Crédito formal rural vs. urbano")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Relación entre tablas que alimentan este comparativo")
relaciones = get_relaciones_tablas()
st.dataframe(relaciones[relaciones["tabla_o_dataset"].isin(["paises", "cartera_anual", "tipo_credito", "indicadores_findex", "indicadores_rural_urbano", "metadatos"])], use_container_width=True)

st.subheader("Tabla comparativa consolidada")
base = f2024[["pais", "cuenta_financiera", "cuenta_digital", "internet", "prestamo_banco_formal", "prestamo_negocio", "credito_subsistencia", "ratio_subsistencia_productivo", "efectivo_agricola_pct"]].copy()
st.dataframe(base, use_container_width=True)
st.download_button("Descargar comparativo CSV", data=descargar_csv(base), file_name="comparativo_paises.csv", mime="text/csv")

st.subheader("Oferta institucional completa")
oferta_filtrada = oferta[(oferta["pais"].isin(paises)) & (oferta["anio"] >= rango[0]) & (oferta["anio"] <= rango[1])]
st.dataframe(oferta_filtrada, use_container_width=True)
st.download_button("Descargar oferta CSV", data=descargar_csv(oferta_filtrada), file_name="oferta_institucional.csv", mime="text/csv")
