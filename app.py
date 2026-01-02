import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Generador de Reportes Educativos", layout="wide")

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    # Usamos la base consolidada que creamos anteriormente
    df = pd.read_csv('tabla_integral_criticos_2024.csv')
    return df

df = load_data()

# --- LÓGICA DE PDF (Clase FPDF) ---
class ReportePDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Ficha de Síntesis de Resultados 2024', 0, 1, 'C')
        self.ln(5)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, title, 0, 1, 'L', 1)
        self.ln(4)

    def create_table(self, header, data):
        self.set_font('Arial', 'B', 10)
        for h in header:
            self.cell(45, 7, h, 1)
        self.ln()
        self.set_font('Arial', '', 10)
        for row in data:
            for item in row:
                self.cell(45, 7, str(item), 1)
            self.ln()

# --- INTERFAZ DE FILTROS ---
st.sidebar.header("🎯 Selector de Establecimiento")
comuna_sel = st.sidebar.selectbox("Comuna:", sorted(df['Comuna'].unique()))
df_comuna = df[df['Comuna'] == comuna_sel]
colegio_sel = st.sidebar.selectbox("Nombre del Colegio:", sorted(df_comuna['Nombre Establecimiento'].unique()))

# Obtener datos del colegio
row = df[df['Nombre Establecimiento'] == colegio_sel].iloc[0]

# --- CUERPO DEL REPORTE WEB ---
st.title(f"🏫 Reporte Institucional: {colegio_sel}")
st.markdown(f"**Comuna:** {row['Comuna']} | **RBD:** {int(row['RBD'])}")

# BLOQUE 1: INDICADORES SOCIOEMOCIONALES (IDPS)
st.header("1. Bienestar y Desarrollo Social (IDPS)")
col_idps1, col_idps2 = st.columns(2)

with col_idps1:
    st.subheader("4° Básico")
    fig4 = px.bar(x=["Autoestima", "Convivencia", "Participación", "Hábitos"],
                  y=[row['Autoestima_4B'], row['Convivencia_4B'], row['Participacion_4B'], row['Habitos_Vida_4B']],
                  range_y=[0,100], color_discrete_sequence=['#1f77b4'])
    st.plotly_chart(fig4, use_container_width=True)

with col_idps2:
    st.subheader("II Medio")
    fig2 = px.bar(x=["Autoestima", "Convivencia", "Participación", "Hábitos"],
                  y=[row['Autoestima_2M'], row['Convivencia_2M'], row['Participacion_2M'], row['Habitos_Vida_2M']],
                  range_y=[0,100], color_discrete_sequence=['#ff7f0e'])
    st.plotly_chart(fig2, use_container_width=True)

# BLOQUE 2: ACADÉMICO Y ESTÁNDARES (EDA)
st.header("2. Resultados Académicos y Estándares de Aprendizaje")

def plot_eda(nivel_label, lect_ins, lect_ele, lect_ade, mate_ins, mate_ele, mate_ade):
    data = [
        {"Evaluación": "Lectura", "Nivel": "Insuficiente", "Val": row[lect_ins]},
        {"Evaluación": "Lectura", "Nivel": "Elemental", "Val": row[lect_ele]},
        {"Evaluación": "Lectura", "Nivel": "Adecuado", "Val": row[lect_ade]},
        {"Evaluación": "Matemática", "Nivel": "Insuficiente", "Val": row[mate_ins]},
        {"Evaluación": "Matemática", "Nivel": "Elemental", "Val": row[mate_ele]},
        {"Evaluación": "Matemática", "Nivel": "Adecuado", "Val": row[mate_ade]}
    ]
    df_plot = pd.DataFrame(data)
    fig = px.bar(df_plot, x="Evaluación", y="Val", color="Nivel",
                 color_discrete_map={"Insuficiente": "#E63946", "Elemental": "#FFB703", "Adecuado": "#2A9D8F"},
                 category_orders={"Nivel": ["Adecuado", "Elemental", "Insuficiente"]},
                 barmode="stack", text_auto='.1f', title=f"Estándares {nivel_label}")
    return fig

t1, t2 = st.tabs(["Resultados 4° Básico", "Resultados II Medio"])
with t1:
    st.plotly_chart(plot_eda("4B", 'EDA_Lect_Ins_4B', 'EDA_Lect_Ele_4B', 'EDA_Lect_Ade_4B', 'EDA_Mate_Ins_4B', 'EDA_Mate_Ele_4B', 'EDA_Mate_Ade_4B'))
with t2:
    st.plotly_chart(plot_eda("2M", 'EDA_Lect_Ins_2M', 'EDA_Lect_Ele_2M', 'EDA_Lect_Ade_2M', 'EDA_Mate_Ins_2M', 'EDA_Mate_Ele_2M', 'EDA_Mate_Ade_2M'))

# --- BOTÓN GENERADOR DE PDF ---
if st.button("📄 Generar Ficha PDF para Impresión"):
    pdf = ReportePDF()
    pdf.add_page()
    
    # Datos Institucionales
    pdf.chapter_title("I. Identificación")
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 7, f"Establecimiento: {row['Nombre Establecimiento']}", 0, 1)
    pdf.cell(0, 7, f"Comuna: {row['Comuna']} | RBD: {int(row['RBD'])}", 0, 1)
    pdf.ln(5)
    
    # Tabla Simce
    pdf.chapter_title("II. Resultados Académicos Simce 2024")
    header = ['Nivel', 'Lectura', 'Matemática']
    data = [
        ['4to Basico', str(row['Simce_Lect_4B']), str(row['Simce_Mate_4B'])],
        ['2do Medio', str(row['Simce_Lect_2M']), str(row['Simce_Mate_2M'])]
    ]
    pdf.create_table(header, data)
    pdf.ln(5)
    
    # Tabla IDPS
    pdf.chapter_title("III. Indicadores de Desarrollo Personal y Social")
    header_idps = ['Nivel', 'Autoestima', 'Convivencia', 'Habitos']
    data_idps = [
        ['4B', str(row['Autoestima_4B']), str(row['Convivencia_4B']), str(row['Habitos_Vida_4B'])],
        ['2M', str(row['Autoestima_2M']), str(row['Convivencia_2M']), str(row['Habitos_Vida_2M'])]
    ]
    pdf.create_table(header_idps, data_idps)
    
    # Descarga
    pdf_output = pdf.output(dest='S').encode('latin-1')
    b64 = base64.b64encode(pdf_output).decode('latin-1')
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Reporte_{row["RBD"]}.pdf">Haga clic aquí para descargar el PDF</a>'
    st.markdown(href, unsafe_allow_html=True)
