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
        font-size: 2rem;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        padding: 0.5rem;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #81C784;
        border-left: 4px solid #4CAF50;
        padding-left: 10px;
        margin: 1rem 0;
    }
    .metric-container {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# ============= SIDEBAR =============
st.sidebar.title("⛏️ Dashboard Tambang")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "📊 Menu Navigasi",
    ["🏠 Overview", "⚙️ Produksi", "🚨 Gangguan", "📈 Monitoring", "📋 Plan vs Realisasi"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Dashboard Tambang**  
Semen Padang  
Version 2.0
""")

# ============= HALAMAN OVERVIEW =============
if page == "🏠 Overview":
    st.markdown('<p class="main-header">🏭 Overview Produksi Tambang</p>', unsafe_allow_html=True)
    
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
    st.markdown('<p class="sub-header">📈 Tren Produksi Harian</p>', unsafe_allow_html=True)
    
    if 'Date' in df_prod.columns and 'Tonnase' in df_prod.columns:
        daily = df_prod.groupby('Date')['Tonnase'].sum().reset_index()
        
        fig = px.area(
            daily, 
            x='Date', 
            y='Tonnase',
            title='Produksi Harian (Tonase)',
            color_discrete_sequence=['#4CAF50']
        )
        fig.update_layout(
            xaxis_title="Tanggal",
            yaxis_title="Tonase (Ton)",
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ============= ROW 2: SHIFT + EXCAVATOR + COMMODITY =============
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<p class="sub-header">🕐 Produksi per Shift</p>', unsafe_allow_html=True)
        if 'Shift' in df_prod.columns and 'Tonnase' in df_prod.columns:
            shift_prod = df_prod.groupby('Shift')['Tonnase'].sum().reset_index()
            fig = px.pie(
                shift_prod,
                values='Tonnase',
                names='Shift',
                title='Distribusi per Shift',
                color_discrete_sequence=px.colors.sequential.Greens_r
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<p class="sub-header">🏗️ Top Excavator</p>', unsafe_allow_html=True)
        if 'Excavator' in df_prod.columns and 'Tonnase' in df_prod.columns:
            exc_prod = df_prod.groupby('Excavator')['Tonnase'].sum().reset_index()
            exc_prod = exc_prod.sort_values('Tonnase', ascending=True)
            fig = px.bar(
                exc_prod,
                x='Tonnase',
                y='Excavator',
                orientation='h',
                title='Tonase per Excavator',
                color='Tonnase',
                color_continuous_scale='Greens'
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown('<p class="sub-header">📦 Produksi per Material</p>', unsafe_allow_html=True)
        if 'Commudity' in df_prod.columns and 'Tonnase' in df_prod.columns:
            mat_data = df_prod.groupby('Commudity')['Tonnase'].sum().reset_index()
            mat_data = mat_data.sort_values('Tonnase', ascending=False)
            fig = px.pie(
                mat_data,
                values='Tonnase',
                names='Commudity',
                title='Distribusi Material',
                color_discrete_sequence=px.colors.sequential.Teal
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
    st.markdown('<p class="sub-header">🔍 Filter Data</p>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
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
                options=df_prod['Excavator'].unique(),
                default=df_prod['Excavator'].unique()
            )
        else:
            excavators = []
    
    with col3:
        if 'Commudity' in df_prod.columns:
            commodities = st.multiselect(
                "Pilih Material",
                options=df_prod['Commudity'].unique(),
                default=df_prod['Commudity'].unique()
            )
        else:
            commodities = []
    
    with col4:
        if 'Date' in df_prod.columns:
            min_date = df_prod['Date'].min().date()
            max_date = df_prod['Date'].max().date()
            date_range = st.date_input(
                "Range Tanggal",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
        else:
            date_range = None
    
    # Apply filters
    df_filtered = df_prod.copy()
    if shifts and 'Shift' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['Shift'].isin(shifts)]
    if excavators and 'Excavator' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['Excavator'].isin(excavators)]
    if commodities and 'Commudity' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['Commudity'].isin(commodities)]
    if date_range and len(date_range) == 2 and 'Date' in df_filtered.columns:
        df_filtered = df_filtered[
            (df_filtered['Date'].dt.date >= date_range[0]) & 
            (df_filtered['Date'].dt.date <= date_range[1])
        ]
    
    # KPI setelah filter
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Ritase (Filtered)", f"{df_filtered['Rit'].sum():,.0f}")
    with col2:
        st.metric("Total Tonase (Filtered)", f"{df_filtered['Tonnase'].sum():,.0f}")
    with col3:
        st.metric("Jumlah Record", f"{len(df_filtered):,}")
    
    st.markdown("---")
    
    # ============= VISUALISASI =============
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="sub-header">🏗️ Produksi per Excavator</p>', unsafe_allow_html=True)
        if 'Excavator' in df_filtered.columns and 'Tonnase' in df_filtered.columns:
            exc_data = df_filtered.groupby('Excavator')['Tonnase'].sum().reset_index()
            exc_data = exc_data.sort_values('Tonnase', ascending=True)
            fig = px.bar(
                exc_data,
                x='Tonnase',
                y='Excavator',
                orientation='h',
                title='Total Tonase per Excavator',
                color='Tonnase',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<p class="sub-header">🚛 Top 10 Dump Truck</p>', unsafe_allow_html=True)
        if 'Dump Truck' in df_filtered.columns and 'Tonnase' in df_filtered.columns:
            dt_data = df_filtered.groupby('Dump Truck')['Tonnase'].sum().reset_index()
            dt_data = dt_data.sort_values('Tonnase', ascending=False).head(10)
            fig = px.bar(
                dt_data,
                x='Dump Truck',
                y='Tonnase',
                title='Top 10 Dump Truck',
                color='Tonnase',
                color_continuous_scale='Oranges'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ============= ROW 2: COMMODITY =============
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="sub-header">📦 Produksi per Material</p>', unsafe_allow_html=True)
        if 'Commudity' in df_filtered.columns and 'Tonnase' in df_filtered.columns:
            mat_data = df_filtered.groupby('Commudity')['Tonnase'].sum().reset_index()
            mat_data = mat_data.sort_values('Tonnase', ascending=False)
            fig = px.bar(
                mat_data,
                x='Commudity',
                y='Tonnase',
                title='Total Tonase per Material',
                color='Tonnase',
                color_continuous_scale='Teal'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<p class="sub-header">📍 Produksi per Front</p>', unsafe_allow_html=True)
        if 'Front' in df_filtered.columns and 'Tonnase' in df_filtered.columns:
            front_data = df_filtered.groupby('Front')['Tonnase'].sum().reset_index()
            front_data = front_data.sort_values('Tonnase', ascending=False).head(10)
            fig = px.bar(
                front_data,
                x='Front',
                y='Tonnase',
                title='Top 10 Front Area',
                color='Tonnase',
                color_continuous_scale='Purples'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    # ============= HEATMAP PRODUKSI =============
    st.markdown('<p class="sub-header">🗓️ Heatmap Produksi (Shift x Hari)</p>', unsafe_allow_html=True)
    if 'Date' in df_filtered.columns and 'Shift' in df_filtered.columns:
        df_filtered['DayOfWeek'] = df_filtered['Date'].dt.day_name()
        heatmap_data = df_filtered.groupby(['DayOfWeek', 'Shift'])['Tonnase'].sum().reset_index()
        heatmap_pivot = heatmap_data.pivot(index='Shift', columns='DayOfWeek', values='Tonnase')
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_pivot = heatmap_pivot.reindex(columns=[d for d in day_order if d in heatmap_pivot.columns])
        
        fig = px.imshow(
            heatmap_pivot,
            title='Heatmap Produksi per Shift dan Hari',
            color_continuous_scale='Greens',
            aspect='auto'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ============= TABEL DETAIL =============
    st.markdown('<p class="sub-header">📋 Data Detail Produksi</p>', unsafe_allow_html=True)
    
    columns_to_show = ['Date', 'Time', 'Shift', 'Front', 'Commudity', 'Excavator', 
                       'Dump Truck', 'Dump Loc', 'Rit', 'Tonnase']
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
    
    bulan = st.selectbox(
        "📅 Pilih Bulan",
        ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
         "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    )
    
    df_gang = load_gangguan(bulan)
    
    if df_gang.empty:
        st.warning(f"⚠️ Data gangguan untuk {bulan} tidak tersedia")
        st.stop()
    
    if 'Row Labels' in df_gang.columns and 'Frekuensi' in df_gang.columns:
        df_clean = df_gang[['Row Labels', 'Frekuensi']].copy()
        df_clean = df_clean.sort_values('Frekuensi', ascending=False)
        
        # KPI
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Jenis Gangguan", len(df_clean))
        with col2:
            st.metric("Total Frekuensi", f"{df_clean['Frekuensi'].sum():,.0f}")
        with col3:
            st.metric("Gangguan Terbesar", df_clean.iloc[0]['Row Labels'] if len(df_clean) > 0 else "-")
        
        st.markdown("---")
        
        # ============= PARETO CHART =============
        st.markdown(f'<p class="sub-header">📊 Pareto Chart Gangguan - {bulan}</p>', unsafe_allow_html=True)
        
        df_plot = df_clean.head(10).copy()
        df_plot['Kumulatif'] = df_plot['Frekuensi'].cumsum()
        df_plot['Persentase_Kumulatif'] = (df_plot['Kumulatif'] / df_clean['Frekuensi'].sum()) * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df_plot['Row Labels'],
            y=df_plot['Frekuensi'],
            name='Frekuensi',
            marker_color='#EF5350'
        ))
        
        fig.add_trace(go.Scatter(
            x=df_plot['Row Labels'],
            y=df_plot['Persentase_Kumulatif'],
            name='Kumulatif (%)',
            yaxis='y2',
            marker_color='#42A5F5',
            mode='lines+markers',
            line=dict(width=3)
        ))
        
        fig.update_layout(
            title=f'Top 10 Gangguan - {bulan}',
            xaxis_title='Jenis Gangguan',
            yaxis_title='Frekuensi',
            yaxis2=dict(
                title='Persentase Kumulatif (%)',
                overlaying='y',
                side='right',
                range=[0, 105]
            ),
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ============= PIE CHART =============
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<p class="sub-header">🥧 Distribusi Top 5 Gangguan</p>', unsafe_allow_html=True)
            fig = px.pie(
                df_clean.head(5),
                values='Frekuensi',
                names='Row Labels',
                title='Top 5 Gangguan',
                color_discrete_sequence=px.colors.sequential.Reds_r
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('<p class="sub-header">📊 Bar Chart Gangguan</p>', unsafe_allow_html=True)
            fig = px.bar(
                df_clean.head(10),
                x='Frekuensi',
                y='Row Labels',
                orientation='h',
                title='Top 10 Gangguan',
                color='Frekuensi',
                color_continuous_scale='Reds'
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        # ============= SUMMARY TABLE =============
        st.markdown('<p class="sub-header">📋 Detail Gangguan</p>', unsafe_allow_html=True)
        st.dataframe(df_clean, use_container_width=True, height=400)

# ============= HALAMAN MONITORING (BARU) =============
elif page == "📈 Monitoring":
    st.markdown('<p class="main-header">📈 Monitoring Operasional</p>', unsafe_allow_html=True)
    
    # Sub-menu monitoring
    mon_tab = st.radio(
        "Pilih Data Monitoring",
        ["⛽ BBM", "📊 Analisa Produksi", "🚛 Ritase"],
        horizontal=True
    )
    
    st.markdown("---")
    
    # ============= TAB BBM =============
    if mon_tab == "⛽ BBM":
        st.markdown('<p class="sub-header">⛽ Konsumsi BBM per Alat</p>', unsafe_allow_html=True)
        
        df_bbm = load_bbm()
        
        if df_bbm.empty:
            st.warning("⚠️ Data BBM tidak tersedia")
        else:
            # Filter valid data
            df_bbm = df_bbm[df_bbm['No'].notna()]
            df_bbm = df_bbm[df_bbm['Alat Berat'].notna()]
            
            # FIX: Pastikan kolom Total numerik
            if 'Total' in df_bbm.columns:
                df_bbm['Total'] = pd.to_numeric(df_bbm['Total'], errors='coerce').fillna(0)
            
            # KPI
            col1, col2, col3 = st.columns(3)
            with col1:
                total_bbm = df_bbm['Total'].sum() if 'Total' in df_bbm.columns else 0
                st.metric("Total Konsumsi BBM", f"{total_bbm:,.0f} L")
            with col2:
                total_unit = len(df_bbm)
                st.metric("Total Unit", f"{total_unit}")
            with col3:
                avg_bbm = df_bbm['Total'].mean() if 'Total' in df_bbm.columns else 0
                st.metric("Rata-rata per Unit", f"{avg_bbm:,.0f} L")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # BBM per tipe alat
                if 'Alat Berat' in df_bbm.columns and 'Total' in df_bbm.columns:
                    bbm_type = df_bbm.groupby('Alat Berat')['Total'].sum().reset_index()
                    fig = px.pie(
                        bbm_type,
                        values='Total',
                        names='Alat Berat',
                        title='Distribusi BBM per Tipe Alat',
                        color_discrete_sequence=px.colors.sequential.Oranges_r
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # BBM per unit
                if 'Tipe Alat' in df_bbm.columns and 'Total' in df_bbm.columns:
                    bbm_unit = df_bbm[['Tipe Alat', 'Total']].sort_values('Total', ascending=True).tail(15)
                    fig = px.bar(
                        bbm_unit,
                        x='Total',
                        y='Tipe Alat',
                        orientation='h',
                        title='Top 15 Konsumsi BBM per Unit',
                        color='Total',
                        color_continuous_scale='YlOrRd'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Tabel detail
            st.markdown('<p class="sub-header">📋 Detail Konsumsi BBM</p>', unsafe_allow_html=True)
            cols_show = ['No', 'Alat Berat', 'Tipe Alat', 'Total']
            available = [c for c in cols_show if c in df_bbm.columns]
            st.dataframe(df_bbm[available].sort_values('Total', ascending=False), use_container_width=True)
    
    # ============= TAB ANALISA PRODUKSI =============
    elif mon_tab == "📊 Analisa Produksi":
        st.markdown('<p class="sub-header">📊 Plan vs Aktual Produksi</p>', unsafe_allow_html=True)
        
        try:
            df_ap = pd.read_excel('data/Monitoring_2025_.xlsx', sheet_name='Analisa Produksi')
            
            # Parse data Januari
            df_jan = df_ap.iloc[1:32, 0:3].copy()
            df_jan.columns = ['Tanggal', 'Plan', 'Aktual']
            df_jan['Tanggal'] = pd.to_numeric(df_jan['Tanggal'], errors='coerce')
            df_jan['Plan'] = pd.to_numeric(df_jan['Plan'], errors='coerce')
            df_jan['Aktual'] = pd.to_numeric(df_jan['Aktual'], errors='coerce')
            df_jan = df_jan.dropna()
            df_jan['Bulan'] = 'Januari'
            
            # KPI
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Plan", f"{df_jan['Plan'].sum():,.0f}")
            with col2:
                st.metric("Total Aktual", f"{df_jan['Aktual'].sum():,.0f}")
            with col3:
                achievement = (df_jan['Aktual'].sum() / df_jan['Plan'].sum() * 100) if df_jan['Plan'].sum() > 0 else 0
                st.metric("Achievement", f"{achievement:.1f}%")
            with col4:
                gap = df_jan['Aktual'].sum() - df_jan['Plan'].sum()
                st.metric("Gap", f"{gap:,.0f}", delta=f"{gap:,.0f}")
            
            st.markdown("---")
            
            # Chart Plan vs Aktual
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_jan['Tanggal'],
                y=df_jan['Plan'],
                name='Plan',
                marker_color='#90CAF9'
            ))
            fig.add_trace(go.Bar(
                x=df_jan['Tanggal'],
                y=df_jan['Aktual'],
                name='Aktual',
                marker_color='#4CAF50'
            ))
            fig.update_layout(
                title='Plan vs Aktual Produksi Harian - Januari 2025',
                xaxis_title='Tanggal',
                yaxis_title='Tonase',
                barmode='group',
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Achievement per hari
            df_jan['Achievement'] = (df_jan['Aktual'] / df_jan['Plan'] * 100).round(1)
            df_jan['Status'] = df_jan['Achievement'].apply(
                lambda x: '✅ Tercapai' if x >= 100 else '⚠️ Belum Tercapai'
            )
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.line(
                    df_jan,
                    x='Tanggal',
                    y='Achievement',
                    title='Achievement Harian (%)',
                    markers=True
                )
                fig.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Target 100%")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                status_count = df_jan['Status'].value_counts().reset_index()
                status_count.columns = ['Status', 'Jumlah']
                fig = px.pie(
                    status_count,
                    values='Jumlah',
                    names='Status',
                    title='Status Pencapaian Target',
                    color_discrete_sequence=['#4CAF50', '#FFC107']
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Tabel
            st.dataframe(df_jan, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading analisa produksi: {e}")
    
    # ============= TAB RITASE =============
    elif mon_tab == "🚛 Ritase":
        st.markdown('<p class="sub-header">🚛 Monitoring Ritase</p>', unsafe_allow_html=True)
        
        df_rit = load_ritase()
        
        if df_rit.empty:
            st.warning("⚠️ Data ritase tidak tersedia")
        else:
            # Clean data
            df_rit = df_rit.loc[:, ~df_rit.columns.str.contains('^Unnamed')]
            
            st.dataframe(df_rit.head(20), use_container_width=True)
            
            if 'Tanggal' in df_rit.columns and 'Shift' in df_rit.columns:
                # Cari kolom numerik untuk visualisasi
                numeric_cols = df_rit.select_dtypes(include=['number']).columns.tolist()
                
                if numeric_cols:
                    selected_col = st.selectbox("Pilih Kolom untuk Visualisasi", numeric_cols)
                    
                    fig = px.line(
                        df_rit,
                        x='Tanggal',
                        y=selected_col,
                        color='Shift' if 'Shift' in df_rit.columns else None,
                        title=f'Tren {selected_col}',
                        markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)

# ============= HALAMAN PLAN VS REALISASI =============
elif page == "📋 Plan vs Realisasi":
    st.markdown('<p class="main-header">📋 Plan vs Realisasi</p>', unsafe_allow_html=True)
    
    df_plan = load_daily_plan()
    
    if df_plan.empty:
        st.warning("⚠️ Data plan tidak tersedia")
        st.stop()
    
    st.markdown('<p class="sub-header">📅 Data Daily Plan</p>', unsafe_allow_html=True)
    st.dataframe(df_plan, use_container_width=True, height=500)
    
    # Summary jika ada kolom yang bisa diagregasi
    if 'Keterangan' in df_plan.columns:
        st.markdown("---")
        st.markdown('<p class="sub-header">📊 Ringkasan Plan</p>', unsafe_allow_html=True)
        
        summary = df_plan['Keterangan'].value_counts().reset_index()
        summary.columns = ['Keterangan', 'Jumlah']
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(
                summary,
                values='Jumlah',
                names='Keterangan',
                title='Distribusi Rencana per Keterangan'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                summary,
                x='Keterangan',
                y='Jumlah',
                title='Jumlah Plan per Keterangan',
                color='Jumlah',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Download
    csv = df_plan.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Plan CSV",
        data=csv,
        file_name=f'daily_plan_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv'
    )