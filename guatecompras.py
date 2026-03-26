# dashboard_licitaciones.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Licitaciones - Guatemala",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Dashboard de Licitaciones Públicas")
st.markdown("---")

# ============================================
# CARGA DE DATOS
# ============================================
@st.cache_data
def load_data():
    """Carga los datos desde el archivo CSV"""
    df = pd.read_csv('licitaciones.csv', encoding='utf-8')
    
    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # Convertir columnas numéricas
    columnas_numericas = ['monto_adjudicado', 'fianza_sostenimiento', 'fianza_cumplimiento', 'numero_ofertas']
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Convertir fechas
    columnas_fechas = ['fecha_publicacion', 'fecha_presentacion', 'fecha_cierre', 'fecha_adjudicacion']
    for col in columnas_fechas:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Extraer año de adjudicación
    if 'fecha_adjudicacion' in df.columns:
        df['año_adjudicacion'] = df['fecha_adjudicacion'].dt.year
    
    return df

# Cargar datos
try:
    df = load_data()
    if df is not None and not df.empty:
        st.success(f"✅ Datos cargados correctamente: {len(df)} licitaciones")
    else:
        st.error("❌ No se encontraron datos en el archivo")
        st.stop()
except Exception as e:
    st.error(f"❌ Error al cargar datos: {e}")
    st.info("📝 Asegúrate de que el archivo 'licitaciones.csv' existe en el mismo directorio")
    st.stop()

# ============================================
# FILTROS
# ============================================
st.sidebar.header("🔍 Filtros")

# FILTRO 1: Año
st.sidebar.subheader("📅 1. Año de Adjudicación")
años_disponibles = sorted(df['año_adjudicacion'].dropna().unique().astype(int))
años_seleccionados = st.sidebar.multiselect(
    "Año",
    options=años_disponibles,
    default=años_disponibles
)

df_filtrado = df[df['año_adjudicacion'].isin(años_seleccionados)]

if df_filtrado.empty:
    st.warning("⚠️ No hay licitaciones en los años seleccionados.")
    st.stop()

# FILTRO 2: Región
st.sidebar.subheader("🗺️ 2. Región")
regiones_disponibles = sorted(df_filtrado['region'].dropna().unique())
regiones_seleccionadas = st.sidebar.multiselect(
    "Región",
    options=regiones_disponibles,
    default=regiones_disponibles
)

df_filtrado = df_filtrado[df_filtrado['region'].isin(regiones_seleccionadas)]

# FILTRO 3: Departamento
st.sidebar.subheader("📍 3. Departamento")
deptos_disponibles = sorted(df_filtrado['departamento'].dropna().unique())
deptos_seleccionados = st.sidebar.multiselect(
    "Departamento",
    options=deptos_disponibles,
    default=deptos_disponibles
)

df_filtrado = df_filtrado[df_filtrado['departamento'].isin(deptos_seleccionados)]

# FILTRO 4: Tipo de Proyecto
st.sidebar.subheader("🏗️ 4. Tipo de Proyecto")
tipos_disponibles = sorted(df_filtrado['tipo_proyecto'].dropna().unique())
tipos_seleccionados = st.sidebar.multiselect(
    "Tipo de Proyecto",
    options=tipos_disponibles,
    default=tipos_disponibles
)

df_filtrado = df_filtrado[df_filtrado['tipo_proyecto'].isin(tipos_seleccionados)]

# FILTRO 5: Estatus
st.sidebar.subheader("📌 5. Estatus")
estatus_disponibles = sorted(df_filtrado['estatus'].dropna().unique())
estatus_seleccionados = st.sidebar.multiselect(
    "Estatus",
    options=estatus_disponibles,
    default=estatus_disponibles
)

df_filtrado = df_filtrado[df_filtrado['estatus'].isin(estatus_seleccionados)]

# FILTRO 6: Rango de Monto
st.sidebar.subheader("💰 6. Rango de Monto")
monto_min = float(df_filtrado['monto_adjudicado'].min() if not df_filtrado['monto_adjudicado'].isna().all() else 0)
monto_max = float(df_filtrado['monto_adjudicado'].max() if not df_filtrado['monto_adjudicado'].isna().all() else 10000000)

rango_monto = st.sidebar.slider(
    "Monto Adjudicado (Q)",
    min_value=monto_min,
    max_value=monto_max,
    value=(monto_min, monto_max),
    format="Q%.2f"
)

df_filtrado = df_filtrado[
    df_filtrado['monto_adjudicado'].between(rango_monto[0], rango_monto[1])
]

# Resumen de filtros
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Resumen")
st.sidebar.info(f"""
**Años:** {len(años_seleccionados)}  
**Regiones:** {len(regiones_seleccionadas)}  
**Departamentos:** {len(deptos_seleccionados)}  
**Tipos:** {len(tipos_seleccionados)}  
**Estatus:** {len(estatus_seleccionados)}  
**Licitaciones:** {len(df_filtrado)}
""")

# ============================================
# MÉTRICAS PRINCIPALES
# ============================================
st.header("📈 Indicadores Clave")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Licitaciones", len(df_filtrado))

with col2:
    monto_total = df_filtrado['monto_adjudicado'].sum()
    st.metric("Monto Total Adjudicado", f"Q{monto_total:,.2f}")

with col3:
    monto_promedio = df_filtrado['monto_adjudicado'].mean()
    st.metric("Monto Promedio", f"Q{monto_promedio:,.2f}")

with col4:
    proveedores = df_filtrado['proveedor_ganador'].nunique()
    st.metric("Proveedores Distintos", proveedores)

st.markdown("---")

# ============================================
# GRÁFICOS PRINCIPALES
# ============================================

# Gráfico 1: Evolución por año
st.subheader("📅 Evolución de Licitaciones por Año")
licitaciones_por_año = df_filtrado.groupby('año_adjudicacion').size().reset_index(name='Cantidad')
fig_temporal = px.line(
    licitaciones_por_año,
    x='año_adjudicacion',
    y='Cantidad',
    markers=True,
    line_shape='linear'
)
fig_temporal.update_traces(line=dict(width=3), marker=dict(size=10))
st.plotly_chart(fig_temporal, use_container_width=True)

# Gráficos en dos columnas
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Licitaciones por Tipo de Proyecto")
    licitaciones_por_tipo = df_filtrado.groupby('tipo_proyecto').size().reset_index(name='Cantidad')
    licitaciones_por_tipo = licitaciones_por_tipo.sort_values('Cantidad', ascending=False).head(10)
    fig_tipo = px.bar(
        licitaciones_por_tipo,
        x='tipo_proyecto',
        y='Cantidad',
        title="Top 10 Tipos de Proyecto",
        color='Cantidad',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig_tipo, use_container_width=True)

with col2:
    st.subheader("💰 Monto por Región")
    monto_por_region = df_filtrado.groupby('region')['monto_adjudicado'].sum().reset_index()
    monto_por_region = monto_por_region.sort_values('monto_adjudicado', ascending=True)
    fig_region = px.bar(
        monto_por_region,
        x='monto_adjudicado',
        y='region',
        orientation='h',
        title="Monto Total por Región",
        labels={'monto_adjudicado': 'Monto (Q)', 'region': 'Región'},
        color='monto_adjudicado',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_region, use_container_width=True)

# Gráfico 3: Top Proveedores
st.subheader("🏢 Top 10 Proveedores por Monto Adjudicado")
top_proveedores = df_filtrado.groupby('proveedor_ganador')['monto_adjudicado'].sum().reset_index()
top_proveedores = top_proveedores.sort_values('monto_adjudicado', ascending=False).head(10)
fig_proveedores = px.bar(
    top_proveedores,
    x='monto_adjudicado',
    y='proveedor_ganador',
    orientation='h',
    title="Top 10 Proveedores",
    labels={'monto_adjudicado': 'Monto (Q)', 'proveedor_ganador': 'Proveedor'},
    color='monto_adjudicado',
    color_continuous_scale='Greens'
)
st.plotly_chart(fig_proveedores, use_container_width=True)

# Gráfico 4: Estatus
st.subheader("📌 Distribución por Estatus")
estatus_count = df_filtrado['estatus'].value_counts().reset_index()
estatus_count.columns = ['Estatus', 'Cantidad']
fig_estatus = px.pie(
    estatus_count,
    values='Cantidad',
    names='Estatus',
    title="Proporción de Licitaciones por Estatus",
    hole=0.3
)
st.plotly_chart(fig_estatus, use_container_width=True)

# Gráfico 5: Número de Ofertas vs Monto
st.subheader("📊 Relación: Número de Ofertas vs Monto Adjudicado")
df_ofertas = df_filtrado.dropna(subset=['numero_ofertas', 'monto_adjudicado'])
if not df_ofertas.empty:
    fig_ofertas = px.scatter(
        df_ofertas,
        x='numero_ofertas',
        y='monto_adjudicado',
        color='tipo_proyecto',
        size='monto_adjudicado',
        hover_data=['proveedor_ganador', 'departamento', 'descripcion'],
        title="Número de Ofertas vs Monto Adjudicado",
        labels={'numero_ofertas': 'Número de Ofertas', 'monto_adjudicado': 'Monto (Q)'}
    )
    st.plotly_chart(fig_ofertas, use_container_width=True)

# ============================================
# TABLA DE DATOS
# ============================================
st.subheader("📋 Detalle de Licitaciones")

columnas_mostrar = [
    'nog', 'descripcion', 'region', 'departamento', 'municipio',
    'tipo_proyecto', 'estatus', 'monto_adjudicado', 'proveedor_ganador',
    'numero_ofertas', 'fecha_adjudicacion'
]

columnas_existentes = [col for col in columnas_mostrar if col in df_filtrado.columns]

busqueda = st.text_input("🔍 Buscar por descripción o NOG:", "")
if busqueda:
    df_filtrado = df_filtrado[
        df_filtrado['descripcion'].str.contains(busqueda, case=False, na=False) |
        df_filtrado['nog'].astype(str).str.contains(busqueda, case=False, na=False)
    ]

st.dataframe(
    df_filtrado[columnas_existentes].style.format({
        'monto_adjudicado': 'Q{:,.2f}',
        'numero_ofertas': '{:.0f}'
    }),
    use_container_width=True,
    height=400
)

# ============================================
# ALERTAS
# ============================================
st.subheader("⚠️ Alertas")

# Licitaciones con una sola oferta
ofertas_unicas = df_filtrado[df_filtrado['numero_ofertas'] == 1]
if len(ofertas_unicas) > 0:
    st.warning(f"🚨 {len(ofertas_unicas)} licitaciones con solo una oferta")
    with st.expander("Ver detalles"):
        st.dataframe(ofertas_unicas[['nog', 'descripcion', 'monto_adjudicado', 'proveedor_ganador']])

# Licitaciones con estatus "Evaluacion" o "En Proceso" antiguas
fecha_limite = datetime.now() - pd.Timedelta(days=90)
licitaciones_pendientes = df_filtrado[
    (df_filtrado['estatus'].isin(['Evaluacion', 'En Proceso'])) &
    (df_filtrado['fecha_adjudicacion'] < fecha_limite)
]
if len(licitaciones_pendientes) > 0:
    st.info(f"📋 {len(licitaciones_pendientes)} licitaciones en proceso por más de 90 días")

# ============================================
# EXPORTAR
# ============================================
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Exportar")

if st.sidebar.button("Exportar a CSV"):
    csv = df_filtrado.to_csv(index=False)
    st.sidebar.download_button(
        label="Descargar",
        data=csv,
        file_name=f"licitaciones_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# ============================================
# INFORMACIÓN
# ============================================
with st.expander("ℹ️ Información del Dashboard"):
    st.markdown(f"""
    **Resumen General:**
    - Total licitaciones: {len(df_filtrado)}
    - Monto total: Q{df_filtrado['monto_adjudicado'].sum():,.2f}
    - Monto promedio: Q{df_filtrado['monto_adjudicado'].mean():,.2f}
    - Proveedores distintos: {df_filtrado['proveedor_ganador'].nunique()}
    - Departamentos: {df_filtrado['departamento'].nunique()}
    - Regiones: {df_filtrado['region'].nunique()}
    
    **Columnas disponibles:**
    - NOG, Descripción, Región, Departamento, Municipio
    - Tipo de Proyecto, Estatus, Monto Adjudicado
    - Proveedor Ganador, Número de Ofertas, Fechas
    """)

st.markdown("---")
st.markdown(f"📅 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
