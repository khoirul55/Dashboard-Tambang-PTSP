import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
sys.path.append('.')
from utils.data_loader import *

# ============= CONFIG =============
st.set_page_config(
    page_title="Dashboard Tambang Semen Padang",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============= CUSTOM CSS =============
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============= SIDEBAR =============
st.sidebar.title("⛏️ Dashboard Tambang")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "📊 Menu Navigasi",
    ["🏠 Overview", "⚙️ Produksi", "🚨 Gangguan", "📋 Plan vs Realisasi"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Dashboard Tambang**  
Semen Padang  
Version 1.0
""")

# ============= HALAMAN OVERVIEW =============
if page == "🏠 Overview":
    st.markdown('<p class="main-header">🏭 Overview Produksi Tambang</p>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Memuat data...'):
        df_prod = load_produksi()
    
    if df_prod.empty:
        st.warning("⚠️ Data produksi tidak ditemukan. Pastikan file Excel ada di folder 'data/'")
        st.stop()
    
    # ============= KPI CARDS =============
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_rit = df_prod['Rit'].sum() if 'Rit' in df_prod.columns else 0
        st.metric(
            label="🚛 Total Ritase",
            value=f"{total_rit:,.0f}",
            delta="Rit"
        )
    
    with col2:
        total_ton = df_prod['Tonnase'].sum() if 'Tonnase' in df_prod.columns else 0
        st.metric(
            label="⚖️ Total Tonase",
            value=f"{total_ton:,.0f}",
            delta="Ton"
        )
    
    with col3:
        avg_ton = df_prod['Tonnase'].mean() if 'Tonnase' in df_prod.columns else 0
        st.metric(
            label="📊 Rata-rata Tonase",
            value=f"{avg_ton:.1f}",
            delta="Ton/Rit"
        )
    
    with col4:
        total_exc = df_prod['Excavator'].nunique() if 'Excavator' in df_prod.columns else 0
        st.metric(
            label="🏗️ Total Excavator",
            value=f"{total_exc}",
            delta="Unit"
        )
    
    st.markdown("---")
    
    # ============= GRAFIK TREN PRODUKSI =============
    st.subheader("📈 Tren Produksi Harian")
    
    if 'Date' in df_prod.columns and 'Tonnase' in df_prod.columns:
        daily = df_prod.groupby('Date')['Tonnase'].sum().reset_index()
        
        fig = px.line(
            daily, 
            x='Date', 
            y='Tonnase',
            title='Produksi Harian (Tonase)',
            markers=True
        )
        fig.update_layout(
            xaxis_title="Tanggal",
            yaxis_title="Tonase (Ton)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ============= PRODUKSI PER SHIFT =============
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🕐 Produksi per Shift")
        if 'Shift' in df_prod.columns and 'Tonnase' in df_prod.columns:
            shift_prod = df_prod.groupby('Shift')['Tonnase'].sum().reset_index()
            fig = px.pie(
                shift_prod,
                values='Tonnase',
                names='Shift',
                title='Distribusi Produksi per Shift'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏗️ Top 5 Excavator")
        if 'Excavator' in df_prod.columns and 'Tonnase' in df_prod.columns:
            exc_prod = df_prod.groupby('Excavator')['Tonnase'].sum().reset_index()
            exc_prod = exc_prod.sort_values('Tonnase', ascending=False).head(5)
            fig = px.bar(
                exc_prod,
                x='Excavator',
                y='Tonnase',
                title='Top 5 Excavator Berdasarkan Tonase'
            )
            st.plotly_chart(fig, use_container_width=True)

# ============= HALAMAN PRODUKSI =============
elif page == "⚙️ Produksi":
    st.markdown('<p class="main-header">⚙️ Analisa Produksi Detail</p>', unsafe_allow_html=True)
    
    df_prod = load_produksi()
    
    if df_prod.empty:
        st.warning("⚠️ Data tidak tersedia")
        st.stop()
    
    # ============= FILTER =============
    st.subheader("🔍 Filter Data")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'Shift' in df_prod.columns:
            shifts = st.multiselect(
                "Pilih Shift",
                options=df_prod['Shift'].unique(),
                default=df_prod['Shift'].unique()
            )
        else:
            shifts = []
    
    with col2:
        if 'Excavator' in df_prod.columns:
            excavators = st.multiselect(
                "Pilih Excavator",
                options=df_prod['Excavator'].unique()
            )
        else:
            excavators = []
    
    with col3:
        if 'Date' in df_prod.columns:
            date_range = st.date_input(
                "Pilih Range Tanggal",
                value=(df_prod['Date'].min(), df_prod['Date'].max())
            )
        else:
            date_range = None
    
    # Apply filters
    df_filtered = df_prod.copy()
    if shifts and 'Shift' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['Shift'].isin(shifts)]
    if excavators and 'Excavator' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['Excavator'].isin(excavators)]
    
    st.markdown("---")
    
    # ============= VISUALISASI =============
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Produksi per Excavator")
        if 'Excavator' in df_filtered.columns and 'Tonnase' in df_filtered.columns:
            exc_data = df_filtered.groupby('Excavator')['Tonnase'].sum().reset_index()
            exc_data = exc_data.sort_values('Tonnase', ascending=True)
            fig = px.bar(
                exc_data,
                x='Tonnase',
                y='Excavator',
                orientation='h',
                title='Total Tonase per Excavator'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🚛 Produksi per Dump Truck")
        if 'Dump Truck' in df_filtered.columns and 'Tonnase' in df_filtered.columns:
            dt_data = df_filtered.groupby('Dump Truck')['Tonnase'].sum().reset_index()
            dt_data = dt_data.sort_values('Tonnase', ascending=False).head(10)
            fig = px.bar(
                dt_data,
                x='Dump Truck',
                y='Tonnase',
                title='Top 10 Dump Truck'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ============= TABEL DETAIL =============
    st.subheader("📋 Data Detail Produksi")
    
    columns_to_show = ['Date', 'Time', 'Shift', 'Front', 'Excavator', 
                       'Dump Truck', 'Rit', 'Tonnase']
    available_cols = [col for col in columns_to_show if col in df_filtered.columns]
    
    st.dataframe(
        df_filtered[available_cols].sort_values('Date', ascending=False),
        use_container_width=True,
        height=400
    )
    
    # Download button
    csv = df_filtered[available_cols].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data CSV",
        data=csv,
        file_name=f'produksi_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv'
    )

# ============= HALAMAN GANGGUAN =============
elif page == "🚨 Gangguan":
    st.markdown('<p class="main-header">🚨 Analisa Gangguan Produksi</p>', unsafe_allow_html=True)
    
    # Pilih bulan
    bulan = st.selectbox(
        "📅 Pilih Bulan",
        ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
         "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    )
    
    df_gang = load_gangguan(bulan)
    
    if df_gang.empty:
        st.warning(f"⚠️ Data gangguan untuk {bulan} tidak tersedia")
        st.stop()
    
    # Clean data
    if 'Row Labels' in df_gang.columns and 'Frekuensi' in df_gang.columns:
        df_clean = df_gang[['Row Labels', 'Frekuensi']].copy()
        df_clean = df_clean.dropna()
        df_clean = df_clean[df_clean['Row Labels'] != 'Grand Total']
        df_clean = df_clean[df_clean['Frekuensi'] > 0]
        df_clean = df_clean.sort_values('Frekuensi', ascending=False)
        
        # ============= PARETO CHART =============
        st.subheader(f"📊 Pareto Chart Gangguan - {bulan}")
        
        df_plot = df_clean.head(10).copy()
        df_plot['Kumulatif'] = df_plot['Frekuensi'].cumsum()
        df_plot['Persentase_Kumulatif'] = (df_plot['Kumulatif'] / df_plot['Frekuensi'].sum()) * 100
        
        fig = go.Figure()
        
        # Bar chart
        fig.add_trace(go.Bar(
            x=df_plot['Row Labels'],
            y=df_plot['Frekuensi'],
            name='Frekuensi',
            marker_color='indianred'
        ))
        
        # Line chart
        fig.add_trace(go.Scatter(
            x=df_plot['Row Labels'],
            y=df_plot['Persentase_Kumulatif'],
            name='Kumulatif (%)',
            yaxis='y2',
            marker_color='blue',
            mode='lines+markers'
        ))
        
        fig.update_layout(
            title=f'Top 10 Gangguan - {bulan}',
            xaxis_title='Jenis Gangguan',
            yaxis_title='Frekuensi',
            yaxis2=dict(
                title='Persentase Kumulatif (%)',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ============= SUMMARY TABLE =============
        st.subheader("📋 Detail Gangguan")
        st.dataframe(df_clean, use_container_width=True, height=400)

# ============= HALAMAN PLAN VS REALISASI =============
elif page == "📋 Plan vs Realisasi":
    st.markdown('<p class="main-header">📋 Plan vs Realisasi</p>', unsafe_allow_html=True)
    
    df_plan = load_daily_plan()
    
    if df_plan.empty:
        st.warning("⚠️ Data plan tidak tersedia")
        st.stop()
    
    st.subheader("📅 Data Daily Plan")
    st.dataframe(df_plan, use_container_width=True, height=500)
    
    # Download
    csv = df_plan.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Plan CSV",
        data=csv,
        file_name=f'daily_plan_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv'
    )