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
# MÉTRICAS PRINCIPALES
st.subheader("📈 Métricas Clave")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💰 Ventas Totales",
        value=f"${df_filtrado['Ventas'].sum():,.0f}"
    )

with col2:
    st.metric(
        label="📦 Venta Promedio",
        value=f"${df_filtrado['Ventas'].mean():,.1f}"
    )

with col3:
    st.metric(
        label="📊 Total Transacciones",
        value=len(df_filtrado)
    )

with col4:
    st.metric(
        label="🏷️ Productos Únicos",
        value=df_filtrado['Producto'].nunique()
    )

st.markdown("---")

# GRÁFICOS - PRIMERA FILA
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Evolución de Ventas")
    fig_linea = px.line(
        df_filtrado,
        x='Fecha',
        y='Ventas',
        color='Producto' if producto_seleccionado == 'Todos' else None,
        title='Ventas Diarias',
        template='plotly_white'
    )
    fig_linea.update_layout(height=400)
    st.plotly_chart(fig_linea, use_container_width=True)

with col2:
    st.subheader("🥧 Distribución por Producto")
    ventas_producto = df_filtrado.groupby('Producto')['Ventas'].sum().reset_index()
    fig_pie = px.pie(
        ventas_producto,
        values='Ventas',
        names='Producto',
        title='% de Ventas por Producto',
        template='plotly_white'
    )
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

# GRÁFICOS - SEGUNDA FILA
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Ventas por Región")
    ventas_region = df_filtrado.groupby('Region')['Ventas'].sum().reset_index()
    fig_barras = px.bar(
        ventas_region,
        x='Region',
        y='Ventas',
        color='Region',
        title='Ventas Totales por Región',
        template='plotly_white'
    )
    fig_barras.update_layout(height=400)
    st.plotly_chart(fig_barras, use_container_width=True)

with col2:
    st.subheader("📋 Datos Filtrados")
    st.dataframe(
        df_filtrado.sort_values('Fecha', ascending=False).head(10),
        use_container_width=True,
        height=400
    )

# PIE DE PÁGINA
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"📅 Período: {df_filtrado['Fecha'].min().date()} - {df_filtrado['Fecha'].max().date()}")
with col2:
    st.caption(f"📌 Registros mostrados: {len(df_filtrado)}")
with col3:
    st.caption(f"🔄 Actualizado: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")