import streamlit as st
import plotly.express as px
from data_mock import get_narrativa, get_findex, get_kpis, diagnosticos, get_sources, get_conceptos_clave, get_flujo_analitico, descargar_csv, PAISES

st.set_page_config(page_title="AgroCredit Insight", page_icon="🌱", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
  background: #0f1724;
  color: white;
}
[data-testid="stAppViewContainer"] * {
  color: white !important;
}
[data-testid="stMetric"] {
  background: linear-gradient(135deg, #143d2a 0%, #2e7d4f 55%, #9cc86a 100%);
  border: 1px solid rgba(255, 255, 255, 0.22);
  padding: 16px;
  border-radius: 18px;
  box-shadow: 0 8px 22px rgba(17, 67, 41, 0.06);
  color: white;
}
[data-testid="stMetric"] * {
  color: white !important;
}
.block-container {padding-top: 2rem;}
.hero {
  padding: 2rem;
  border-radius: 26px;
  border: 1px solid rgba(255, 255, 255, 0.22);
  background: linear-gradient(135deg, #143d2a 0%, #2e7d4f 55%, #9cc86a 100%);
  color: white;
  margin-bottom: 1.2rem;
}
.hero h1 {font-size: 3rem; margin-bottom: .2rem;}
.hero p {font-size: 1.12rem; max-width: 980px;}
.section-label {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.65rem 1.2rem;
  border-radius: 999px;
  background: linear-gradient(135deg, #143d2a 0%, #2e7d4f 55%, #9cc86a 100%);
  color: white;
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 1rem;
  box-shadow: 0 10px 25px rgba(17, 67, 41, 0.08);
}
.card {
  background: linear-gradient(135deg, #143d2a 0%, #2e7d4f 55%, #9cc86a 100%);
  border: 1px solid rgba(255, 255, 255, 0.22);
  padding: 1.15rem;
  border-radius: 20px;
  box-shadow: 0 8px 22px rgba(17, 67, 41, 0.06);
  min-height: 170px;
  color: white;
}
.card h3,
.card p {
  color: white;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.35);
}
.badge {
  display: inline-block;
  padding: .35rem .7rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.18);
  color: white;
  font-weight: 700;
  margin-bottom: .5rem;
  border: 1px solid rgba(255, 255, 255, 0.24);
}
</style>
""", unsafe_allow_html=True)

narrativa = get_narrativa()

st.markdown(f"""
<div class="hero">
  <div class="badge">Dashboard de investigación aplicada</div>
  <h1>AgroCredit Insight</h1>
  <p><b>{narrativa['titulo']}:</b> {narrativa['subtitulo']}</p>
  <p>{narrativa['tesis']}</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("AgroCredit Insight")
st.sidebar.write("Usa las páginas del menú para navegar por el análisis.")
paises = st.sidebar.multiselect("Países visibles", PAISES, default=PAISES)

st.markdown('<div class="section-label">Cómo leer este dashboard</div>', unsafe_allow_html=True)
st.write("La app está pensada para un público que quiere entender el problema sin perderse entre tablas. La idea central es comparar lo que las personas ya pueden hacer con el sistema financiero, como tener cuenta o pagar digitalmente, contra lo que todavía no logran hacer de forma suficiente: acceder a crédito productivo formal.")
with st.expander("Ver flujo de lectura de la investigación"):
    flujo = get_flujo_analitico()
    st.dataframe(flujo, use_container_width=True)

kpis = get_kpis(paises, 2024)

st.markdown('<div class="section-label">Lectura ejecutiva</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="card">
      <div class="badge">Problema</div>
      <h3>La cuenta no equivale a crédito</h3>
      <p>Una persona puede estar bancarizada, pagar digitalmente o usar internet, pero aun así no ser aceptada como sujeto de crédito productivo.</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="card">
      <div class="badge">Mecanismo</div>
      <h3>El efectivo vuelve invisible al productor</h3>
      <p>Cuando el pago agrícola no pasa por una cuenta, el sistema financiero no ve ingresos estables ni historial transaccional útil para evaluar riesgo.</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="card">
      <div class="badge">Comparación</div>
      <h3>Paraguay es el contraste</h3>
      <p>El caso paraguayo permite discutir el papel de instituciones rurales especializadas, aunque falta incorporar datos estructurados del CAH.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-label">KPIs 2024</div>', unsafe_allow_html=True)
met1, met2, met3, met4 = st.columns(4)
met1.metric("Cuenta financiera", f"{kpis.get('cuenta_financiera', 0):.1f}%")
met2.metric("Cuenta digital", f"{kpis.get('cuenta_digital', 0):.1f}%")
met3.metric("Crédito formal", f"{kpis.get('prestamo_banco_formal', 0):.1f}%")
met4.metric("Brecha digital-crédito", f"{kpis.get('brecha_digital_credito_pp', 0):.1f} pp")

met5, met6, met7, met8 = st.columns(4)
met5.metric("Préstamo para negocio", f"{kpis.get('prestamo_negocio', 0):.1f}%")
met6.metric("Crédito de subsistencia", f"{kpis.get('credito_subsistencia', 0):.1f}%")
met7.metric("Subsistencia/Productivo", f"{kpis.get('ratio_subsistencia_productivo', 0):.1f}x")
met8.metric("Pagos agrícolas en efectivo", f"{kpis.get('efectivo_agricola_pct', 0):.1f}%")

with st.expander("Qué significa cada KPI principal"):
    conceptos = get_conceptos_clave()
    st.dataframe(conceptos[["concepto", "significado", "en_el_dashboard", "por_que_importa"]], use_container_width=True)

findex = get_findex()
findex_2024 = findex[(findex["anio"] == 2024) & (findex["pais"].isin(paises))]
fig = px.bar(
    findex_2024,
    x="pais",
    y=["cuenta_digital", "prestamo_banco_formal", "prestamo_negocio", "credito_subsistencia"],
    barmode="group",
    title="La brecha central: inclusión digital vs. crédito productivo",
    labels={"value": "% de adultos", "variable": "Indicador", "pais": "País"}
)
fig.update_layout(
    plot_bgcolor="#0f1724",
    paper_bgcolor="#0f1724",
    font_color="#ffffff",
    legend_bgcolor="#0f1724",
    title_font_color="#ffffff",
    xaxis=dict(color="#ffffff", gridcolor="rgba(255,255,255,0.08)"),
    yaxis=dict(color="#ffffff", gridcolor="rgba(255,255,255,0.08)")
)
st.plotly_chart(fig, use_container_width=True)
st.caption("Lectura: si cuenta digital es alta pero crédito formal o préstamo para negocio son bajos, la inclusión existe como uso transaccional, pero no como integración productiva.")

st.subheader("Diagnóstico automático resumido")
diag = diagnosticos()
diag = diag[diag["pais"].isin(paises)]
st.dataframe(diag[["pais", "nivel", "brecha_digital_credito_pp", "cambio_credito_formal_pp", "ratio_subsistencia_productivo", "efectivo_agricola_pct"]], use_container_width=True)
st.download_button("Descargar diagnóstico CSV", data=descargar_csv(diag), file_name="diagnostico_agrocredit.csv", mime="text/csv")

st.subheader("Fuentes que sostienen la lectura")
st.write("El dashboard cruza dos familias de datos: Findex describe la demanda, es decir, lo que reportan las personas; las fuentes institucionales describen la oferta, es decir, el crédito que registran entidades como FINAGRO, BCE, SEPS y BCP.")
sources = get_sources()
st.dataframe(sources, use_container_width=True)

st.info("Cuando tus compañeros tengan API o PostgreSQL, este frontend puede cambiar de datos simulados a datos reales usando variables de entorno sin rediseñar las pantallas.")
