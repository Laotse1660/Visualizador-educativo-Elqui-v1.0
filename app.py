import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Monitor Educativo Coquimbo 2024", layout="wide")

# 2. CARGA DE DATOS
@st.cache_data # Esto hace que la app sea rápida al no recargar el CSV cada vez
def load_data():
    df = pd.read_csv('tabla_integral_criticos_2024.csv')
    return df

df = load_data()

# 3. INTERFAZ: Título y Filtros
st.title("📊 Seguimiento de Establecimientos Críticos (2019-2024)")
st.markdown("Análisis de resultados Simce e Indicadores de Desarrollo Personal y Social (IDPS)")

with st.sidebar:
    st.header("Filtros de Búsqueda")
    comuna_sel = st.multiselect("Selecciona Comuna(s):", 
                               options=df['Comuna'].unique(), 
                               default=df['Comuna'].unique())
    
    nivel_2019 = st.selectbox("Filtrar por Categoría 2019:", 
                             ["Todos", "INSUFICIENTE", "MEDIO-BAJO"])

# Aplicar Filtros
df_filtered = df[df['Comuna'].isin(comuna_sel)]
if nivel_2019 != "Todos":
    # Filtramos si fue crítico en básica o media
    df_filtered = df_filtered[(df_filtered['Cat_2019_Basica'] == nivel_2019) | 
                              (df_filtered['Cat_2019_Media'] == nivel_2019)]

# 4. VISUALIZACIONES PRINCIPALES
# =========================================================
# BLOQUE DE GRÁFICOS (VISUALIZACIONES PRINCIPALES)
# =========================================================

# 1. Preparación de datos (Limpieza para evitar errores de puntos vacíos)
# Filtramos solo los colegios que tengan puntajes y IDPS válidos para graficar
df_grafico_4b = df_filtered.dropna(subset=["Simce_Lect_4B", "Simce_Mate_4B", "Autoestima_4B"])
df_grafico_2m = df_filtered.dropna(subset=["Simce_Lect_2M", "Simce_Mate_2M", "Autoestima_2M"])

# 2. Creamos dos columnas en la web para poner los gráficos lado a lado
col1, col2 = st.columns(2)

with col1:
    st.subheader("📌 4° Básico: Rendimiento vs Autoestima")
    if not df_grafico_4b.empty:
        # Creamos el gráfico de burbujas (Scatter Plot)
        fig_4b = px.scatter(
            df_grafico_4b, 
            x="Simce_Lect_4B",      # Eje Horizontal
            y="Simce_Mate_4B",      # Eje Vertical
            size="Autoestima_4B",   # El tamaño de la burbuja es la Autoestima
            color="Comuna",         # Cada color representa una comuna
            hover_name="Nombre Establecimiento", # Lo que sale al pasar el mouse
            template="plotly_white",
            title="Puntajes 2024 (4° Básico)"
        )
        # Mostramos el gráfico en la web
        st.plotly_chart(fig_4b, use_container_width=True)
    else:
        st.info("No hay datos de 4° Básico para los filtros seleccionados.")

with col2:
    st.subheader("📌 II Medio: Rendimiento vs Autoestima")
    if not df_grafico_2m.empty:
        # Repetimos la lógica para Educación Media
        fig_2m = px.scatter(
            df_grafico_2m, 
            x="Simce_Lect_2M", 
            y="Simce_Mate_2M",
            size="Autoestima_2M", 
            color="Comuna",
            hover_name="Nombre Establecimiento",
            template="plotly_white",
            title="Puntajes 2024 (II Medio)"
        )
        st.plotly_chart(fig_2m, use_container_width=True)
    else:
        st.info("No hay datos de II Medio para los filtros seleccionados.")

# 5. TABLA DE DATOS DETALLADA
st.subheader("Detalle General de Establecimientos")
st.dataframe(df_filtered)

# 6. BOTÓN DE DESCARGA
csv = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Descargar Reporte Filtrado",
    data=csv,
    file_name='reporte_educativo_filtrado.csv',
    mime='text/csv',
)

