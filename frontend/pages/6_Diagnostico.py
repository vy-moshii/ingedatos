import streamlit as st
import plotly.express as px
from data_mock import diagnosticos, diagnosticar_pais, get_recomendaciones, get_missing_data, get_findex, get_conceptos_clave, get_relaciones_tablas, descargar_csv, PAISES

st.set_page_config(page_title="Diagnóstico automático", page_icon="🧭", layout="wide")

st.title("Diagnóstico automático de brecha")
st.write("El diagnóstico traduce muchos indicadores en una lectura sencilla: qué tan grave es la distancia entre inclusión financiera transaccional y acceso a crédito productivo formal.")

with st.sidebar:
    st.header("Parámetros")
    pais = st.selectbox("País", PAISES)

resultado = diagnosticar_pais(pais)

st.info("El diagnóstico cruza cuatro señales: brecha cuenta digital-crédito formal, cambio del crédito formal, peso de la subsistencia y pagos agrícolas en efectivo. En una versión conectada a PostgreSQL, este cálculo debería vivir en una función SQL y actualizarse con trigger cuando cambien los indicadores.")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Nivel", resultado["nivel"])
c2.metric("Puntaje", f"{resultado['puntaje']}/12")
c3.metric("Brecha digital-crédito", f"{resultado['brecha_digital_credito_pp']:.1f} pp")
c4.metric("Cambio crédito formal", f"{resultado['cambio_credito_formal_pp']:.1f} pp")
c5.metric("Efectivo agrícola", f"{resultado['efectivo_agricola_pct']:.1f}%")

st.info(resultado["texto"])

with st.expander("Qué significa cada parte del diagnóstico"):
    st.markdown("""
| Señal | Qué mide | Cómo se interpreta |
|---|---|---|
| Brecha digital-crédito | Cuenta digital menos préstamo bancario formal | Si es alta, hay uso digital pero poco crédito formal |
| Cambio crédito formal | Diferencia entre 2021 y 2024 | Si es negativa, el acceso a crédito formal retrocedió |
| Ratio subsistencia/productivo | Crédito de subsistencia dividido entre préstamo para negocio | Si supera 1, pesa más endeudarse para sobrevivir que para producir |
| Efectivo agrícola | Pagos agrícolas en efectivo sobre pagos agrícolas totales | Si es alto, el circuito productivo queda poco visible para el sistema financiero |
""")
    conceptos = get_conceptos_clave()
    st.dataframe(conceptos[conceptos["concepto"].isin(["Brecha de integración productiva", "Crédito de subsistencia", "Pagos agrícolas en efectivo", "Arquitectura institucional"])], use_container_width=True)

all_diag = diagnosticos()
fig = px.bar(all_diag, x="pais", y="puntaje", color="nivel", labels={"puntaje": "Puntaje de brecha", "pais": "País", "nivel": "Nivel"}, title="Comparación del diagnóstico automático")
st.plotly_chart(fig, use_container_width=True)
st.caption("El puntaje no pretende reemplazar el análisis académico. Sirve para convertir señales dispersas en una alerta fácil de leer dentro del dashboard.")

st.subheader("Cómo se construye la lectura")
findex = get_findex()
base = findex[(findex["pais"] == pais) & (findex["anio"] == 2024)][["pais", "anio", "cuenta_digital", "prestamo_banco_formal", "prestamo_negocio", "credito_subsistencia", "ratio_subsistencia_productivo", "pagos_agricolas_total", "pagos_agricolas_efectivo", "efectivo_agricola_pct"]]
st.write("Esta tabla muestra los campos mínimos que alimentan el diagnóstico. En PostgreSQL, estos datos deberían salir de `indicadores_findex` y el resultado debería guardarse en `diagnostico_brecha`.")
st.dataframe(base, use_container_width=True)

with st.expander("Relación de tablas para el diagnóstico"):
    relaciones = get_relaciones_tablas()
    st.dataframe(relaciones[relaciones["tabla_o_dataset"].isin(["indicadores_findex", "diagnostico_brecha", "recomendaciones", "datos_faltantes", "paises"])], use_container_width=True)

st.subheader("Recomendaciones automáticas")
st.write("Las recomendaciones no salen de la nada: responden a los mecanismos de la investigación. Si el problema es efectivo, la acción debe mejorar trazabilidad; si el problema es subsistencia, la acción debe orientar crédito hacia inversión productiva; si el problema es institucional, la acción debe ajustar garantías, mandato y cobertura territorial.")
recs = get_recomendaciones()
for _, row in recs.iterrows():
    st.markdown(f"**{row['eje']}** — {row['recomendacion']}")
    st.write(row["accion"])

st.subheader("Datos faltantes que mejorarían el diagnóstico")
missing = get_missing_data()
missing_view = missing[missing["pais"].isin([pais, "Tres países"])]
st.dataframe(missing_view, use_container_width=True)

st.download_button("Descargar diagnóstico completo CSV", data=descargar_csv(all_diag), file_name="diagnostico_automatico.csv", mime="text/csv")
