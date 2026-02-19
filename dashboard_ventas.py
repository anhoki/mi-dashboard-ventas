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
    # Intentar cargar el CSV, si no existe crear datos de ejemplo
    try:
        df = pd.read_csv('datos_ventas.csv', parse_dates=['Fecha'])
    except:
        # Crear datos de ejemplo
        np.random.seed(42)
        df = pd.DataFrame({
            'Fecha': pd.date_range('2024-01-01', periods=200, freq='D'),
            'Ventas': np.random.randint(50, 500, 200),
            'Producto': np.random.choice(['Smartphone', 'Laptop', 'Tablet', 'Auriculares'], 200),
            'Region': np.random.choice(['Norte', 'Sur', 'Este', 'Oeste'], 200)
        })
        # Guardar para próxima vez
        df.to_csv('datos_ventas.csv', index=False)
    return df

# Cargar los datos
df = cargar_datos()

# BARRA LATERAL - FILTROS
st.sidebar.header("🎯 Filtros")

# Filtro de producto
productos = ['Todos'] + sorted(list(df['Producto'].unique()))
producto_seleccionado = st.sidebar.selectbox("Selecciona Producto:", productos)

# Filtro de región
regiones = ['Todas'] + sorted(list(df['Region'].unique()))
region_seleccionada = st.sidebar.selectbox("Selecciona Región:", regiones)

# Filtro de fechas
fecha_min = df['Fecha'].min().date()
fecha_max = df['Fecha'].max().date()
rango_fechas = st.sidebar.date_input(
    "Rango de Fechas:",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

# APLICAR FILTROS
df_filtrado = df.copy()

if producto_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Producto'] == producto_seleccionado]

if region_seleccionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['Region'] == region_seleccionada]

if len(rango_fechas) == 2:
    df_filtrado = df_filtrado[
        (df_filtrado['Fecha'] >= pd.to_datetime(rango_fechas[0])) &
        (df_filtrado['Fecha'] <= pd.to_datetime(rango_fechas[1]))
    ]

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