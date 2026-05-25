import streamlit as st
import plotly.express as px
from data_client import get_narrativa, get_findex, get_kpis, diagnosticos, get_sources, get_conceptos_clave, get_flujo_analitico, descargar_csv, PAISES, set_page_style

st.set_page_config(page_title="AgroCredit Insight", page_icon="🌱", layout="wide")
set_page_style("Home")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
  position: relative;
  overflow: hidden;
  background: radial-gradient(circle at top center, rgba(255,248,208,0.18), transparent 18%),
              linear-gradient(180deg, #0b1f12 0%, #123523 35%, #1b5a30 60%, #133b21 100%);
  color: white;
}
[data-testid="stAppViewContainer"]::before {
  content: "";
  position: absolute;
  top: -22%;
  left: 50%;
  width: 180%;
  height: 130%;
  background: radial-gradient(circle at 50% 50%, rgba(255,244,174,0.36), transparent 32%);
  transform: translateX(-50%);
  z-index: 0;
}
[data-testid="stAppViewContainer"]::after {
  content: "";
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(115deg, rgba(255,255,255,0.06), rgba(255,255,255,0.06) 1px, transparent 1px, transparent 42px);
  opacity: 0.18;
  animation: field-move 18s linear infinite;
  z-index: 0;
}
@keyframes field-move {
  0% { transform: translateX(0); }
  100% { transform: translateX(-80px); }
}
[data-testid="stAppViewContainer"] > div {
  position: relative;
  z-index: 1;
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
  position: relative;
  padding: 2.5rem;
  border-radius: 34px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: linear-gradient(180deg, rgba(18, 43, 26, 0.95), rgba(16, 39, 31, 1));
  backdrop-filter: blur(8px);
  color: white;
  margin-bottom: 1.6rem;
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.22);
  overflow: hidden;
}
.hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 20% 20%, rgba(255, 242, 181, 0.14), transparent 18%),
              radial-gradient(circle at 75% 15%, rgba(255, 214, 116, 0.11), transparent 16%),
              linear-gradient(180deg, rgba(255, 235, 180, 0.04), transparent 28%, transparent 100%);
  opacity: 0.55;
  pointer-events: none;
}
.hero::after {
  content: "";
  position: absolute;
  left: -10%;
  bottom: 0;
  width: 120%;
  height: 90%;
  background: radial-gradient(circle at 50% 20%, rgba(255, 241, 189, 0.1), transparent 24%),
              linear-gradient(100deg, rgba(85, 140, 72, 0.68) 0%, rgba(109, 150, 96, 0.68) 42%, rgba(146, 117, 53, 0.14) 100%);
  mask-image: radial-gradient(circle at 50% 30%, rgba(0,0,0,1) 25%, rgba(0,0,0,0) 62%);
  opacity: 0.7;
  filter: blur(1px);
  pointer-events: none;
}
.hero h1 {font-size: 3rem; margin-bottom: .4rem; text-transform: uppercase; letter-spacing: 0.03em; text-shadow: 0 2px 10px rgba(0,0,0,0.35);}
.hero p {font-size: 1.14rem; max-width: 900px; line-height: 1.75;}
.section-label {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.72rem 1.3rem;
  border-radius: 999px;
  background: linear-gradient(135deg, #89622c 0%, #cb9b5f 100%);
  color: #111111;
  font-size: 1.05rem;
  font-weight: 700;
  margin-bottom: 1rem;
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.18);
}
.card {
  background: linear-gradient(145deg, #3b4c33 0%, #5c6f45 48%, #b69d6c 100%);
  border: 1px solid rgba(255, 255, 255, 0.14);
  padding: 1.15rem;
  border-radius: 20px;
  box-shadow: 0 8px 22px rgba(11, 30, 15, 0.14);
  min-height: 170px;
  color: white;
}
.card h3,
.card p {
  color: white;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.24);
}
.badge {
  display: inline-block;
  padding: .35rem .7rem;
  border-radius: 999px;
  background: rgba(255, 244, 205, 0.14);
  color: #f4f1e7;
  font-weight: 700;
  margin-bottom: .5rem;
  border: 1px solid rgba(255, 255, 255, 0.16);
}
</style>
""", unsafe_allow_html=True)

narrativa = get_narrativa()
if not isinstance(narrativa, dict):
    narrativa = narrativa.iloc[0].to_dict() if len(narrativa) > 0 else {}

titulo = narrativa.get("titulo", "AgroCredit Insight")
subtitulo = narrativa.get("subtitulo", "Análisis de brechas de crédito y digitalización")
tesis = narrativa.get("tesis", "Exploramos cómo la inclusión financiera digital no siempre se traduce en acceso a crédito productivo.")

st.markdown(f"""
<div class="hero">
  <div class="badge">Dashboard de investigación aplicada</div>
  <h1>AgroCredit Insight</h1>
  <p><b>{titulo}:</b> {subtitulo}</p>
  <p>{tesis}</p>
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
