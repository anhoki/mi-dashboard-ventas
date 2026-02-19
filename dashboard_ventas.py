import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Configuración de la página (debe ser el primer comando)
st.set_page_config(
    page_title="Dashboard de Ventas",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Dashboard de Ventas Interactivo")
st.markdown("---")

# Cargar datos con caché para mejor rendimiento
@st.cache_data
def cargar_datos():
    # Cargar el archivo CSV con los datos reales
    df = pd.read_csv('proyectos_guatecompras.csv')
    
    # Convertir columnas de fecha
    fecha_cols = ['fecha_publicacion', 'fecha_presentacion', 'fecha_cierre', 'fecha_adjudicacion']
    for col in fecha_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Convertir montos a número
    df['monto_adjudicado'] = pd.to_numeric(df['monto_adjudicado'], errors='coerce')
    
    return df
# Cargar los datos
df = cargar_datos()

# BARRA LATERAL - FILTROS
st.sidebar.header("🎯 Filtros")

# Filtro de producto
productos = ['Todos'] + sorted(list(df['Producto'].unique()))
producto_seleccionado = st.sidebar.selectbox("Selecciona Producto:", productos)

# Filtros actualizados para los nuevos datos
st.sidebar.header("🎯 Filtros")

# Filtro por región
regiones = ['Todas'] + sorted(df['region'].dropna().unique().tolist())
region_seleccionada = st.sidebar.selectbox("Selecciona Región:", regiones)

# Filtro por departamento (se actualizará según la región)
if region_seleccionada != 'Todas':
    deptos_disponibles = df[df['region'] == region_seleccionada]['departamento'].unique()
else:
    deptos_disponibles = df['departamento'].unique()
departamento_seleccionado = st.sidebar.selectbox(
    "Selecciona Departamento:", 
    ['Todos'] + sorted(deptos_disponibles)
)

# Filtro por tipo de proyecto
tipos_proyecto = ['Todos'] + sorted(df['tipo_proyecto'].dropna().unique().tolist())
tipo_seleccionado = st.sidebar.selectbox("Tipo de Proyecto:", tipos_proyecto)

# Filtro por estatus
estatus_list = ['Todos'] + sorted(df['estatus'].dropna().unique().tolist())
estatus_seleccionado = st.sidebar.selectbox("Estatus:", estatus_list)

# Rango de montos
min_monto = float(df['monto_adjudicado'].min() or 0)
max_monto = float(df['monto_adjudicado'].max() or 5000000)
rango_monto = st.sidebar.slider(
    "Rango de Monto (Q)",
    min_value=min_monto,
    max_value=max_monto,
    value=(min_monto, max_monto)
)
