import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests
import json

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Guatecompras",
    page_icon="📋",
    layout="wide"
)

# Título principal
st.title("📋 Dashboard de Proyectos Guatecompras")
st.markdown("---")

# Función para cargar datos con caché
@st.cache_data
def cargar_datos():
    encodings = ['utf-8', 'latin-1', 'iso-8859-1']
    for enc in encodings:
        try:
            df = pd.read_csv('proyectos_guatecompras.csv', encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        st.error("No se pudo leer el archivo. Verifica la codificación.")
        return pd.DataFrame()

    # Convertir columnas de fecha
    fecha_cols = ['fecha_publicacion', 'fecha_presentacion', 'fecha_cierre', 'fecha_adjudicacion']
    for col in fecha_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Convertir montos a número
    df['monto_adjudicado'] = pd.to_numeric(df['monto_adjudicado'], errors='coerce')

    # 🆕 Convertir número de ofertas a número (coerce convierte errores a NaN)
    if 'numero_ofertas' in df.columns:
        df['numero_ofertas'] = pd.to_numeric(df['numero_ofertas'], errors='coerce')

    # Crear columna de año
    df['año_adjudicacion'] = df['fecha_adjudicacion'].dt.year

    return df

# Función para cargar GeoJSON de Guatemala (desde repositorio público)
@st.cache_data
def cargar_geojson_guatemala():
    url = "https://raw.githubusercontent.com/tierradenadies/guatemala-geojson/master/departamentos.geojson"
    try:
        response = requests.get(url)
        response.raise_for_status()
        geojson = response.json()
        return geojson
    except:
        st.warning("No se pudo cargar el mapa de departamentos. Verifica tu conexión.")
        return None

# Cargar datos
df = cargar_datos()
geojson = cargar_geojson_guatemala()

# Verificar que hay datos
if df.empty:
    st.stop()

# BARRA LATERAL - FILTROS
st.sidebar.header("🎯 Filtros")

# Filtro por región
regiones = ['Todas'] + sorted(df['region'].dropna().unique().tolist())
region_seleccionada = st.sidebar.selectbox("Región:", regiones)

# Filtro por departamento (dependiente de región)
if region_seleccionada != 'Todas':
    deptos_filtro = df[df['region'] == region_seleccionada]['departamento'].unique()
else:
    deptos_filtro = df['departamento'].unique()
departamento_seleccionado = st.sidebar.selectbox(
    "Departamento:",
    ['Todos'] + sorted(deptos_filtro)
)

# Filtro por tipo de proyecto
tipos = ['Todos'] + sorted(df['tipo_proyecto'].dropna().unique().tolist())
tipo_seleccionado = st.sidebar.selectbox("Tipo de proyecto:", tipos)

# Filtro por estatus
estatus_list = ['Todos'] + sorted(df['estatus'].dropna().unique().tolist())
estatus_seleccionado = st.sidebar.selectbox("Estatus:", estatus_list)

# Filtro por rango de montos (solo para proyectos adjudicados)
montos_validos = df['monto_adjudicado'].dropna()
if not montos_validos.empty:
    min_monto = float(montos_validos.min())
    max_monto = float(montos_validos.max())
    rango_monto = st.sidebar.slider(
        "Rango de monto adjudicado (Q)",
        min_value=min_monto,
        max_value=max_monto,
        value=(min_monto, max_monto)
    )
else:
    rango_monto = (0, 1)

# APLICAR FILTROS
df_filtrado = df.copy()

if region_seleccionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['region'] == region_seleccionada]

if departamento_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['departamento'] == departamento_seleccionado]

if tipo_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['tipo_proyecto'] == tipo_seleccionado]

if estatus_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['estatus'] == estatus_seleccionado]

# Filtro de montos (solo si hay adjudicados)
if not df_filtrado[df_filtrado['monto_adjudicado'].notna()].empty:
    df_filtrado = df_filtrado[
        (df_filtrado['monto_adjudicado'].isna()) |  # conserva los no adjudicados
        (df_filtrado['monto_adjudicado'].between(rango_monto[0], rango_monto[1]))
    ]

# ============================================
# MÉTRICAS CLAVE
# ============================================
st.subheader("📊 Métricas Generales")

total_proyectos = len(df_filtrado)
proyectos_adjudicados = df_filtrado[df_filtrado['estatus'] == 'Adjudicado'].shape[0]
monto_total = df_filtrado['monto_adjudicado'].sum()
monto_promedio = df_filtrado['monto_adjudicado'].mean()
proyectos_sin_adjudicar = df_filtrado[df_filtrado['estatus'] != 'Adjudicado'].shape[0]
ofertas_promedio = df_filtrado['numero_ofertas'].mean()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="📌 Total de proyectos",
        value=f"{total_proyectos:,}"
    )
with col2:
    st.metric(
        label="✅ Adjudicados",
        value=f"{proyectos_adjudicados:,}",
        delta=f"{proyectos_adjudicados/total_proyectos*100:.1f}% del total"
    )
with col3:
    st.metric(
        label="💰 Monto total adjudicado",
        value=f"Q{monto_total:,.0f}" if not pd.isna(monto_total) else "Q0"
    )
with col4:
    st.metric(
        label="📊 Promedio por proyecto",
        value=f"Q{monto_promedio:,.0f}" if not pd.isna(monto_promedio) else "Q0"
    )
with col5:
    st.metric(
        label="🔄 Ofertas promedio",
        value=f"{ofertas_promedio:.1f}" if not pd.isna(ofertas_promedio) else "0"
    )

st.markdown("---")

# ============================================
# GRÁFICOS PRINCIPALES
# ============================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Monto adjudicado por región")
    monto_region = df_filtrado.groupby('region')['monto_adjudicado'].sum().reset_index()
    monto_region = monto_region.sort_values('monto_adjudicado', ascending=True)
    fig_monto_region = px.bar(
        monto_region,
        x='monto_adjudicado',
        y='region',
        orientation='h',
        title='Inversión total por región',
        labels={'monto_adjudicado': 'Monto (Q)', 'region': ''},
        color='monto_adjudicado',
        color_continuous_scale='Blues'
    )
    fig_monto_region.update_layout(height=400)
    st.plotly_chart(fig_monto_region, use_container_width=True)

with col2:
    st.subheader("📁 Proyectos por tipo")
    tipo_counts = df_filtrado['tipo_proyecto'].value_counts().reset_index()
    tipo_counts.columns = ['tipo_proyecto', 'cantidad']
    fig_tipo = px.pie(
        tipo_counts,
        values='cantidad',
        names='tipo_proyecto',
        title='Distribución por tipo de proyecto',
        hole=0.4
    )
    fig_tipo.update_layout(height=400)
    st.plotly_chart(fig_tipo, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Evolución de adjudicaciones por año")
    adjudicados_por_año = df_filtrado[df_filtrado['estatus'] == 'Adjudicado']
    if not adjudicados_por_año.empty:
        año_counts = adjudicados_por_año['año_adjudicacion'].value_counts().sort_index().reset_index()
        año_counts.columns = ['año', 'cantidad']
        fig_evol = px.line(
            año_counts,
            x='año',
            y='cantidad',
            markers=True,
            title='Proyectos adjudicados por año',
            labels={'cantidad': 'N° de proyectos', 'año': 'Año'}
        )
        st.plotly_chart(fig_evol, use_container_width=True)
    else:
        st.info("No hay datos de adjudicaciones para el período seleccionado.")

with col2:
    st.subheader("🏆 Top 5 departamentos por inversión")
    top_deptos = df_filtrado.groupby('departamento')['monto_adjudicado'].sum().nlargest(5).reset_index()
    fig_top = px.bar(
        top_deptos,
        x='departamento',
        y='monto_adjudicado',
        title='Departamentos con mayor inversión',
        labels={'monto_adjudicado': 'Monto (Q)', 'departamento': ''},
        color='monto_adjudicado',
        color_continuous_scale='Greens'
    )
    st.plotly_chart(fig_top, use_container_width=True)

# ============================================
# NUEVAS VISUALIZACIONES: MAPA Y TOP PROVEEDORES
# ============================================
st.markdown("---")
st.subheader("🗺️ Mapa de inversión por departamento")

if geojson is not None:
    # Agrupar datos por departamento
    monto_por_depto = df_filtrado.groupby('departamento')['monto_adjudicado'].sum().reset_index()
    # Asegurar que los nombres coincidan con el GeoJSON (puede haber diferencias)
    # El GeoJSON usa nombres como "Guatemala", "Alta Verapaz", etc.
    # Hacemos un merge aproximado: convertimos a mayúsculas y quitamos espacios extra
    monto_por_depto['depto_norm'] = monto_por_depto['departamento'].str.strip().str.upper()
    
    # Crear el mapa coroplético
    fig_mapa = px.choropleth(
        monto_por_depto,
        geojson=geojson,
        locations='depto_norm',
        featureidkey="properties.DEPARTAMENTO",  # ajusta según la estructura del GeoJSON
        color='monto_adjudicado',
        color_continuous_scale='Viridis',
        range_color=(monto_por_depto['monto_adjudicado'].min(), monto_por_depto['monto_adjudicado'].max()),
        labels={'monto_adjudicado': 'Monto (Q)'},
        title='Inversión total por departamento'
    )
    fig_mapa.update_geos(fitbounds="locations", visible=False)
    fig_mapa.update_layout(height=500, margin={"r":0,"t":30,"l":0,"b":0})
    st.plotly_chart(fig_mapa, use_container_width=True)
else:
    st.warning("No se pudo cargar el mapa. Mostrando datos en tabla.")
    monto_por_depto = df_filtrado.groupby('departamento')['monto_adjudicado'].sum().reset_index()
    st.dataframe(monto_por_depto.sort_values('monto_adjudicado', ascending=False))

# TOP PROVEEDORES
st.subheader("🏢 Top proveedores por monto adjudicado")
# Filtrar solo proyectos adjudicados con proveedor no nulo
proveedores_df = df_filtrado[df_filtrado['estatus'] == 'Adjudicado']
proveedores_df = proveedores_df[proveedores_df['proveedor_ganador'].notna()]

if not proveedores_df.empty:
    # Agrupar por proveedor: sumar montos y contar proyectos
    top_proveedores = proveedores_df.groupby('proveedor_ganador').agg(
        monto_total=('monto_adjudicado', 'sum'),
        cantidad_proyectos=('nog', 'count')
    ).reset_index().sort_values('monto_total', ascending=False).head(10)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig_prov = px.bar(
            top_proveedores,
            x='monto_total',
            y='proveedor_ganador',
            orientation='h',
            title='Top 10 proveedores por monto',
            labels={'monto_total': 'Monto (Q)', 'proveedor_ganador': ''},
            color='monto_total',
            color_continuous_scale='Oranges',
            text='cantidad_proyectos'  # mostrar número de proyectos
        )
        fig_prov.update_traces(texttemplate='%{text} proyectos', textposition='inside')
        fig_prov.update_layout(height=400)
        st.plotly_chart(fig_prov, use_container_width=True)
    with col2:
        st.subheader("📋 Detalle")
        st.dataframe(top_proveedores[['proveedor_ganador', 'monto_total', 'cantidad_proyectos']].head(5))
else:
    st.info("No hay datos de proveedores para los filtros seleccionados.")

# Tabla final de proyectos
st.subheader("📋 Últimos proyectos")
columnas_mostrar = ['nog', 'descripcion', 'departamento', 'tipo_proyecto', 'monto_adjudicado', 'estatus', 'proveedor_ganador']
df_display = df_filtrado[columnas_mostrar].sort_values('nog', ascending=False).head(10)
st.dataframe(df_display, use_container_width=True)

# Pie de página
st.markdown("---")
st.caption(f"📌 Mostrando {len(df_filtrado)} de {len(df)} proyectos totales")
