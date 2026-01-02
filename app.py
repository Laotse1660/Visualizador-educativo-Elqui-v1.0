import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN Y CARGA
st.set_page_config(page_title="Monitor Educativo 2024", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('tabla_integral_criticos_2024.csv')

df = load_data()

# 2. FILTROS EN LA BARRA LATERAL
with st.sidebar:
    st.header("🔍 Filtros y Búsqueda")
    comuna_sel = st.multiselect("Selecciona Comuna(s):", 
                               options=sorted(df['Comuna'].unique()), 
                               default=df['Comuna'].unique())
    
    # Filtro para la Ficha Individual
    df_comuna_f = df[df['Comuna'].isin(comuna_sel)]
    colegio_sel = st.selectbox("🎯 Ver Ficha de un Colegio:", 
                              options=sorted(df_comuna_f['Nombre Establecimiento'].unique()))

# Aplicamos el filtro general a la base
df_filtered = df[df['Comuna'].isin(comuna_sel)]

# =========================================================
# 3. BLOQUE DE ANÁLISIS ESTADÍSTICO (VA AQUÍ) <<<
# =st.subheader("📈 Análisis de Relación: Autoestima vs. Resultados (Grupo Seleccionado)")

col_corr1, col_corr2 = st.columns(2)
# Calculamos correlación de Pearson (r)
r_lect = df_filtered['Autoestima_4B'].corr(df_filtered['Simce_Lect_4B'])
r_mate = df_filtered['Autoestima_4B'].corr(df_filtered['Simce_Mate_4B'])

with col_corr1:
    st.metric("Vínculo Autoestima-Lectura (r)", f"{r_lect:.2f}" if pd.notnull(r_lect) else "N/A")
with col_corr2:
    st.metric("Vínculo Autoestima-Matemática (r)", f"{r_mate:.2f}" if pd.notnull(r_mate) else "N/A")
# =========================================================

# 4. GRÁFICOS GENERALES (Burbujas)
st.divider()
st.subheader("📌 Comparativa General: Rendimiento vs Autoestima")
col1, col2 = st.columns(2)
# (Aquí va el código de los gráficos px.scatter que ya tienes)
# ...

# 5. FICHA TÉCNICA INDIVIDUAL
st.divider()
df_unitario = df[df['Nombre Establecimiento'] == colegio_sel].iloc[0]
st.header(f"🏫 Ficha Individual: {colegio_sel}")

# AQUI INSERTAS EL GRÁFICO DE BARRAS APILADAS (EDA) <<<
st.subheader("📊 Distribución por Estándares de Aprendizaje (%)")
# (Aquí va el código de px.bar con color_discrete_map que te pasé antes)
# ...

# 6. TABLA FINAL
st.subheader("📋 Datos en Crudo")
st.dataframe(df_filtered)

