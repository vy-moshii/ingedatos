import streamlit as st
import plotly.express as px
from data_mock import get_findex, get_kpis, get_conceptos_clave, get_guia_lectura_graficas, descargar_csv, PAISES

st.set_page_config(page_title="Resumen general", page_icon="📌", layout="wide")

st.title("Resumen general")
st.write("Esta pantalla resume el argumento de la investigación: los países pueden tener conectividad, cuentas y pagos digitales, pero eso no significa que la población rural acceda a crédito productivo formal.")

with st.sidebar:
    st.header("Filtros")
    paises = st.multiselect("País", PAISES, default=PAISES)
    anio = st.selectbox("Año Findex", [2024, 2021], index=0)

findex = get_findex()
df = findex[(findex["pais"].isin(paises)) & (findex["anio"] == anio)]
kpis = get_kpis(paises, anio)

st.info("Lee esta pantalla de izquierda a derecha: primero mira si la gente tiene acceso transaccional, luego mira si ese acceso se convierte en crédito formal o en préstamo para negocio. La diferencia entre esas dos cosas es la brecha que estudia el artículo.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Cuenta financiera", f"{kpis.get('cuenta_financiera', 0):.1f}%")
c2.metric("Cuenta digital", f"{kpis.get('cuenta_digital', 0):.1f}%" if anio == 2024 else "n/d")
c3.metric("Crédito formal", f"{kpis.get('prestamo_banco_formal', 0):.1f}%")
c4.metric("Internet", f"{kpis.get('internet', 0):.1f}%" if anio == 2024 else "n/d")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Préstamo negocio", f"{kpis.get('prestamo_negocio', 0):.1f}%" if anio == 2024 else "n/d")
c6.metric("Subsistencia", f"{kpis.get('credito_subsistencia', 0):.1f}%" if anio == 2024 else "n/d")
c7.metric("Subsistencia/Productivo", f"{kpis.get('ratio_subsistencia_productivo', 0):.1f}x" if anio == 2024 else "n/d")
c8.metric("Efectivo agrícola", f"{kpis.get('efectivo_agricola_pct', 0):.1f}%")

with st.expander("Explicación de los indicadores para público general"):
    conceptos = get_conceptos_clave()
    st.dataframe(conceptos[conceptos["concepto"].isin(["Inclusión transaccional", "Integración productiva", "Brecha de integración productiva", "Crédito formal", "Crédito productivo", "Crédito de subsistencia", "Pagos agrícolas en efectivo"])], use_container_width=True)

st.subheader("Lectura visual de la brecha")
fig = px.bar(
    df,
    x="pais",
    y=["cuenta_financiera", "cuenta_digital", "internet", "prestamo_banco_formal", "prestamo_negocio", "credito_subsistencia"],
    barmode="group",
    labels={"value": "% de adultos", "variable": "Indicador", "pais": "País"},
    title=f"Indicadores principales {anio}"
)
st.plotly_chart(fig, use_container_width=True)
st.caption("La gráfica junta indicadores que normalmente se mirarían por separado. Así se ve si el avance digital llega al crédito o si se queda en el nivel de cuenta, pagos e internet.")

st.subheader("Cambio del crédito formal 2021 → 2024")
trend = findex[findex["pais"].isin(paises)]
fig2 = px.line(trend, x="anio", y="prestamo_banco_formal", color="pais", markers=True, labels={"prestamo_banco_formal": "% adultos", "anio": "Año", "pais": "País"}, title="Préstamo en banco formal")
st.plotly_chart(fig2, use_container_width=True)
st.caption("Esta línea es clave porque muestra la trayectoria: Colombia y Ecuador retroceden en préstamo bancario formal, mientras Paraguay aumenta.")

with st.expander("Cómo interpretar las gráficas"):
    st.dataframe(get_guia_lectura_graficas(), use_container_width=True)

st.subheader("Tabla base")
cols = ["pais", "anio", "cuenta_financiera", "cuenta_digital", "internet", "pago_digital", "prestamo_banco_formal", "prestamo_negocio", "credito_subsistencia", "ratio_subsistencia_productivo", "efectivo_agricola_pct"]
st.dataframe(df[cols], use_container_width=True)
st.download_button("Descargar resumen CSV", data=descargar_csv(df[cols]), file_name="resumen_general.csv", mime="text/csv")

st.success("La pantalla funciona como portada analítica: primero muestra el tamaño de la inclusión transaccional y luego evidencia si esa inclusión llega o no al crédito productivo.")
