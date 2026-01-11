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
        font-size: 1.8rem;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        padding: 0.5rem;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #81C784;
        border-left: 4px solid #4CAF50;
        padding-left: 10px;
        margin: 1rem 0;
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

# ============================================================
# HALAMAN OVERVIEW
# ============================================================
if page == "🏠 Overview":
    st.markdown('<p class="main-header">🏭 Overview Produksi Tambang</p>', unsafe_allow_html=True)
    
    with st.spinner('Memuat data...'):
        df_prod = load_produksi()
    
    if df_prod.empty:
        st.warning("⚠️ Data produksi tidak ditemukan")
        st.stop()
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_rit = df_prod['Rit'].sum() if 'Rit' in df_prod.columns else 0
        st.metric("🚛 Total Ritase", f"{total_rit:,.0f}", "Rit")
    
    with col2:
        total_ton = df_prod['Tonnase'].sum() if 'Tonnase' in df_prod.columns else 0
        st.metric("⚖️ Total Tonase", f"{total_ton:,.0f}", "Ton")
    
    with col3:
        avg_ton = df_prod['Tonnase'].mean() if 'Tonnase' in df_prod.columns else 0
        st.metric("📊 Rata-rata", f"{avg_ton:.1f}", "Ton/Rit")
    
    with col4:
        total_exc = df_prod['Excavator'].nunique() if 'Excavator' in df_prod.columns else 0
        st.metric("🏗️ Excavator", f"{total_exc}", "Unit")
    
    st.markdown("---")
    
    # Tren Produksi Harian
    st.markdown('<p class="sub-header">📈 Tren Produksi Harian</p>', unsafe_allow_html=True)
    
    if 'Date' in df_prod.columns and 'Tonnase' in df_prod.columns:
        daily = df_prod.groupby('Date')['Tonnase'].sum().reset_index()
        fig = px.area(daily, x='Date', y='Tonnase', 
                      title='Produksi Harian (Tonase)',
                      color_discrete_sequence=['#4CAF50'])
        fig.update_layout(xaxis_title="Tanggal", yaxis_title="Tonase (Ton)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 2: Shift, Excavator, Material
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<p class="sub-header">🕐 Per Shift</p>', unsafe_allow_html=True)
        if 'Shift' in df_prod.columns:
            shift_prod = df_prod.groupby('Shift')['Tonnase'].sum().reset_index()
            fig = px.pie(shift_prod, values='Tonnase', names='Shift',
                        color_discrete_sequence=px.colors.sequential.Greens_r)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<p class="sub-header">🏗️ Per Excavator</p>', unsafe_allow_html=True)
        if 'Excavator' in df_prod.columns:
            exc_prod = df_prod.groupby('Excavator')['Tonnase'].sum().reset_index()
            exc_prod = exc_prod.sort_values('Tonnase', ascending=True)
            fig = px.bar(exc_prod, x='Tonnase', y='Excavator', orientation='h',
                        color='Tonnase', color_continuous_scale='Greens')
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown('<p class="sub-header">📦 Per Material</p>', unsafe_allow_html=True)
        if 'Commudity' in df_prod.columns:
            mat_data = df_prod.groupby('Commudity')['Tonnase'].sum().reset_index()
            fig = px.pie(mat_data, values='Tonnase', names='Commudity',
                        color_discrete_sequence=px.colors.sequential.Teal)
            st.plotly_chart(fig, use_container_width=True)


# ============================================================
# HALAMAN PRODUKSI
# ============================================================
elif page == "⚙️ Produksi":
    st.markdown('<p class="main-header">⚙️ Analisa Produksi Detail</p>', unsafe_allow_html=True)
    
    df_prod = load_produksi()
    
    if df_prod.empty:
        st.warning("⚠️ Data tidak tersedia")
        st.stop()
    
    # Filter
    st.markdown('<p class="sub-header">🔍 Filter Data</p>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        shifts = st.multiselect("Shift", options=df_prod['Shift'].unique(), 
                                default=df_prod['Shift'].unique())
    with col2:
        excavators = st.multiselect("Excavator", options=df_prod['Excavator'].unique(),
                                    default=df_prod['Excavator'].unique())
    with col3:
        commodities = st.multiselect("Material", options=df_prod['Commudity'].dropna().unique(),
                                     default=df_prod['Commudity'].dropna().unique())
    with col4:
        min_date = df_prod['Date'].min().date()
        max_date = df_prod['Date'].max().date()
        date_range = st.date_input("Range Tanggal", value=(min_date, max_date))
    
    # Apply filter
    df_filtered = df_prod.copy()
    if shifts:
        df_filtered = df_filtered[df_filtered['Shift'].isin(shifts)]
    if excavators:
        df_filtered = df_filtered[df_filtered['Excavator'].isin(excavators)]
    if commodities:
        df_filtered = df_filtered[df_filtered['Commudity'].isin(commodities)]
    if len(date_range) == 2:
        df_filtered = df_filtered[(df_filtered['Date'].dt.date >= date_range[0]) & 
                                   (df_filtered['Date'].dt.date <= date_range[1])]
    
    # KPI filtered
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Ritase", f"{df_filtered['Rit'].sum():,.0f}")
    col2.metric("Total Tonase", f"{df_filtered['Tonnase'].sum():,.0f}")
    col3.metric("Jumlah Record", f"{len(df_filtered):,}")
    
    st.markdown("---")
    
    # Visualisasi
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="sub-header">🏗️ Per Excavator</p>', unsafe_allow_html=True)
        exc_data = df_filtered.groupby('Excavator')['Tonnase'].sum().reset_index()
        exc_data = exc_data.sort_values('Tonnase', ascending=True)
        fig = px.bar(exc_data, x='Tonnase', y='Excavator', orientation='h',
                    color='Tonnase', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<p class="sub-header">🚛 Top 10 Dump Truck</p>', unsafe_allow_html=True)
        dt_data = df_filtered.groupby('Dump Truck')['Tonnase'].sum().reset_index()
        dt_data = dt_data.sort_values('Tonnase', ascending=False).head(10)
        fig = px.bar(dt_data, x='Dump Truck', y='Tonnase',
                    color='Tonnase', color_continuous_scale='Oranges')
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="sub-header">📦 Per Material</p>', unsafe_allow_html=True)
        mat_data = df_filtered.groupby('Commudity')['Tonnase'].sum().reset_index()
        mat_data = mat_data.sort_values('Tonnase', ascending=False)
        fig = px.bar(mat_data, x='Commudity', y='Tonnase',
                    color='Tonnase', color_continuous_scale='Teal')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<p class="sub-header">📍 Per Front</p>', unsafe_allow_html=True)
        if 'Front' in df_filtered.columns:
            front_data = df_filtered.groupby('Front')['Tonnase'].sum().reset_index()
            front_data = front_data.sort_values('Tonnase', ascending=False).head(10)
            fig = px.bar(front_data, x='Front', y='Tonnase',
                        color='Tonnase', color_continuous_scale='Purples')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap
    st.markdown('<p class="sub-header">🗓️ Heatmap Produksi</p>', unsafe_allow_html=True)
    df_filtered['DayOfWeek'] = df_filtered['Date'].dt.day_name()
    heatmap_data = df_filtered.groupby(['DayOfWeek', 'Shift'])['Tonnase'].sum().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='Shift', columns='DayOfWeek', values='Tonnase')
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_pivot = heatmap_pivot.reindex(columns=[d for d in day_order if d in heatmap_pivot.columns])
    fig = px.imshow(heatmap_pivot, color_continuous_scale='Greens', aspect='auto')
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabel
    st.markdown('<p class="sub-header">📋 Data Detail</p>', unsafe_allow_html=True)
    cols_show = ['Date', 'Time', 'Shift', 'Front', 'Commudity', 'Excavator', 'Dump Truck', 'Rit', 'Tonnase']
    available = [c for c in cols_show if c in df_filtered.columns]
    st.dataframe(df_filtered[available].sort_values('Date', ascending=False), 
                 use_container_width=True, height=400)
    
    csv = df_filtered[available].to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, f'produksi_{datetime.now().strftime("%Y%m%d")}.csv')


# ============================================================
# HALAMAN GANGGUAN
# ============================================================
elif page == "🚨 Gangguan":
    st.markdown('<p class="main-header">🚨 Analisa Gangguan Produksi</p>', unsafe_allow_html=True)
    
    bulan = st.selectbox("📅 Pilih Bulan", 
                         ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                          "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
    
    df_gang = load_gangguan(bulan)
    
    if df_gang.empty:
        st.warning(f"⚠️ Data gangguan {bulan} tidak tersedia")
        st.stop()
    
    df_clean = df_gang[['Row Labels', 'Frekuensi']].copy()
    df_clean = df_clean.sort_values('Frekuensi', ascending=False)
    
    # KPI
    col1, col2, col3 = st.columns(3)
    col1.metric("Jenis Gangguan", len(df_clean))
    col2.metric("Total Frekuensi", f"{df_clean['Frekuensi'].sum():,.0f}")
    col3.metric("Gangguan Terbesar", df_clean.iloc[0]['Row Labels'] if len(df_clean) > 0 else "-")
    
    st.markdown("---")
    
    # Pareto Chart
    st.markdown(f'<p class="sub-header">📊 Pareto Chart - {bulan}</p>', unsafe_allow_html=True)
    
    df_plot = df_clean.head(10).copy()
    df_plot['Kumulatif'] = df_plot['Frekuensi'].cumsum()
    df_plot['Persen_Kum'] = (df_plot['Kumulatif'] / df_clean['Frekuensi'].sum()) * 100
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_plot['Row Labels'], y=df_plot['Frekuensi'], 
                         name='Frekuensi', marker_color='#EF5350'))
    fig.add_trace(go.Scatter(x=df_plot['Row Labels'], y=df_plot['Persen_Kum'],
                             name='Kumulatif (%)', yaxis='y2', 
                             marker_color='#42A5F5', mode='lines+markers'))
    fig.update_layout(
        yaxis2=dict(title='%', overlaying='y', side='right', range=[0, 105]),
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(df_clean.head(5), values='Frekuensi', names='Row Labels',
                    title='Top 5 Gangguan', color_discrete_sequence=px.colors.sequential.Reds_r)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(df_clean.head(10), x='Frekuensi', y='Row Labels', orientation='h',
                    title='Top 10 Gangguan', color='Frekuensi', color_continuous_scale='Reds')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<p class="sub-header">📋 Detail Gangguan</p>', unsafe_allow_html=True)
    st.dataframe(df_clean, use_container_width=True, height=400)


# ============================================================
# HALAMAN MONITORING
# ============================================================
elif page == "📈 Monitoring":
    st.markdown('<p class="main-header">📈 Monitoring Operasional</p>', unsafe_allow_html=True)
    
    mon_tab = st.radio("Pilih Data", ["⛽ BBM", "📊 Plan vs Aktual", "🚛 Ritase"], horizontal=True)
    st.markdown("---")
    
    # =============== TAB BBM ===============
    if mon_tab == "⛽ BBM":
        st.markdown('<p class="sub-header">⛽ Konsumsi BBM per Alat</p>', unsafe_allow_html=True)
        
        df_bbm = load_bbm()
        
        if df_bbm.empty:
            st.warning("⚠️ Data BBM tidak tersedia")
        else:
            # KPI
            col1, col2, col3 = st.columns(3)
            total_bbm = df_bbm['Total'].sum() if 'Total' in df_bbm.columns else 0
            col1.metric("Total BBM", f"{total_bbm:,.0f} L")
            col2.metric("Total Unit", len(df_bbm))
            avg_bbm = df_bbm['Total'].mean() if 'Total' in df_bbm.columns else 0
            col3.metric("Rata-rata/Unit", f"{avg_bbm:,.0f} L")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Alat Berat' in df_bbm.columns:
                    bbm_type = df_bbm.groupby('Alat Berat')['Total'].sum().reset_index()
                    fig = px.pie(bbm_type, values='Total', names='Alat Berat',
                                title='BBM per Tipe Alat', 
                                color_discrete_sequence=px.colors.sequential.Oranges_r)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'Tipe Alat' in df_bbm.columns:
                    bbm_unit = df_bbm[['Tipe Alat', 'Total']].sort_values('Total', ascending=True).tail(15)
                    fig = px.bar(bbm_unit, x='Total', y='Tipe Alat', orientation='h',
                                title='Top 15 Konsumsi BBM', color='Total', 
                                color_continuous_scale='YlOrRd')
                    st.plotly_chart(fig, use_container_width=True)
            
            # Tabel
            st.dataframe(df_bbm[['No', 'Alat Berat', 'Tipe Alat', 'Total']].sort_values('Total', ascending=False),
                        use_container_width=True)
    
    # =============== TAB PLAN VS AKTUAL ===============
    elif mon_tab == "📊 Plan vs Aktual":
        st.markdown('<p class="sub-header">📊 Analisa Plan vs Aktual</p>', unsafe_allow_html=True)
        
        bulan_ap = st.selectbox("Pilih Bulan", ["Januari", "Februari"])
        
        df_ap = load_analisa_produksi(bulan_ap)
        
        if df_ap.empty:
            st.warning(f"⚠️ Data {bulan_ap} tidak tersedia")
        else:
            # KPI
            col1, col2, col3, col4 = st.columns(4)
            total_plan = df_ap['Plan'].sum()
            total_aktual = df_ap['Aktual'].sum()
            achievement = (total_aktual / total_plan * 100) if total_plan > 0 else 0
            gap = total_aktual - total_plan
            
            col1.metric("Total Plan", f"{total_plan:,.0f}")
            col2.metric("Total Aktual", f"{total_aktual:,.0f}")
            col3.metric("Achievement", f"{achievement:.1f}%")
            col4.metric("Gap", f"{gap:,.0f}", delta=f"{gap:,.0f}")
            
            st.markdown("---")
            
            # Chart Plan vs Aktual
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_ap['Tanggal'], y=df_ap['Plan'], name='Plan', marker_color='#90CAF9'))
            fig.add_trace(go.Bar(x=df_ap['Tanggal'], y=df_ap['Aktual'], name='Aktual', marker_color='#4CAF50'))
            fig.update_layout(title=f'Plan vs Aktual - {bulan_ap}', barmode='group', 
                             xaxis_title='Tanggal', yaxis_title='Tonase')
            st.plotly_chart(fig, use_container_width=True)
            
            # Achievement line
            col1, col2 = st.columns(2)
            
            with col1:
                df_ap['Achievement_Pct'] = (df_ap['Aktual'] / df_ap['Plan'] * 100).round(1)
                fig = px.line(df_ap, x='Tanggal', y='Achievement_Pct', 
                             title='Achievement Harian (%)', markers=True)
                fig.add_hline(y=100, line_dash="dash", line_color="red")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                df_ap['Status'] = df_ap['Achievement_Pct'].apply(
                    lambda x: '✅ Tercapai' if x >= 100 else '⚠️ Belum')
                status = df_ap['Status'].value_counts().reset_index()
                status.columns = ['Status', 'Jumlah']
                fig = px.pie(status, values='Jumlah', names='Status', title='Status Pencapaian')
                st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_ap, use_container_width=True)
    
    # =============== TAB RITASE ===============
    elif mon_tab == "🚛 Ritase":
        st.markdown('<p class="sub-header">🚛 Monitoring Ritase per Front</p>', unsafe_allow_html=True)
        
        df_rit = load_ritase()
        
        if df_rit.empty:
            st.warning("⚠️ Data ritase tidak tersedia")
        else:
            # Kolom ritase (numeric)
            rit_cols = [c for c in df_rit.columns if c not in ['Tanggal', 'Shift', 'Pengawasan']]
            
            # Total per front
            st.markdown("**Total Ritase per Front**")
            front_totals = df_rit[rit_cols].sum().reset_index()
            front_totals.columns = ['Front', 'Total Ritase']
            front_totals = front_totals.sort_values('Total Ritase', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(front_totals, x='Front', y='Total Ritase', 
                            title='Total Ritase per Front', color='Total Ritase',
                            color_continuous_scale='Blues')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.pie(front_totals.head(6), values='Total Ritase', names='Front',
                            title='Top 6 Front', color_discrete_sequence=px.colors.sequential.Blues_r)
                st.plotly_chart(fig, use_container_width=True)
            
            # Tren per front
            st.markdown("**Tren Ritase Harian**")
            selected_front = st.selectbox("Pilih Front", rit_cols)
            
            if selected_front:
                df_trend = df_rit.groupby('Tanggal')[selected_front].sum().reset_index()
                fig = px.line(df_trend, x='Tanggal', y=selected_front, 
                             title=f'Tren Ritase - {selected_front}', markers=True)
                st.plotly_chart(fig, use_container_width=True)
            
            # Per Shift
            st.markdown("**Ritase per Shift**")
            shift_data = df_rit.groupby('Shift')[rit_cols].sum().T.reset_index()
            shift_data.columns = ['Front'] + [f'Shift {s}' for s in shift_data.columns[1:]]
            st.dataframe(shift_data, use_container_width=True)
            
            # Raw data
            st.markdown("**Data Lengkap**")
            st.dataframe(df_rit, use_container_width=True, height=300)


# ============================================================
# HALAMAN PLAN VS REALISASI
# ============================================================
elif page == "📋 Plan vs Realisasi":
    st.markdown('<p class="main-header">📋 Plan vs Realisasi</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 Daily Plan", "✅ Realisasi", "📊 Perbandingan"])
    
    # =============== TAB DAILY PLAN ===============
    with tab1:
        st.markdown('<p class="sub-header">📅 Daily Plan (Scheduling)</p>', unsafe_allow_html=True)
        
        df_plan = load_daily_plan()
        
        if df_plan.empty:
            st.warning("⚠️ Data plan tidak tersedia")
        else:
            # Summary
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Record", len(df_plan))
            if 'Keterangan' in df_plan.columns:
                col2.metric("Jenis Material", df_plan['Keterangan'].nunique())
            if 'Alat Muat' in df_plan.columns:
                col3.metric("Alat Muat", df_plan['Alat Muat'].nunique())
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Keterangan' in df_plan.columns:
                    ket_count = df_plan['Keterangan'].value_counts().reset_index()
                    ket_count.columns = ['Keterangan', 'Jumlah']
                    fig = px.pie(ket_count, values='Jumlah', names='Keterangan',
                                title='Distribusi per Keterangan')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'Alat Muat' in df_plan.columns:
                    alat_count = df_plan['Alat Muat'].value_counts().reset_index()
                    alat_count.columns = ['Alat Muat', 'Jumlah']
                    fig = px.bar(alat_count, x='Alat Muat', y='Jumlah',
                                title='Distribusi Alat Muat', color='Jumlah',
                                color_continuous_scale='Greens')
                    st.plotly_chart(fig, use_container_width=True)
            
            # Grid untuk peta
            if 'Grid' in df_plan.columns and 'Blok' in df_plan.columns:
                st.markdown("**📍 Distribusi Grid & Blok (untuk Peta)**")
                col1, col2 = st.columns(2)
                
                with col1:
                    grid_count = df_plan['Grid'].value_counts().reset_index().head(15)
                    grid_count.columns = ['Grid', 'Jumlah']
                    fig = px.bar(grid_count, x='Grid', y='Jumlah', title='Top 15 Grid')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    blok_count = df_plan['Blok'].value_counts().reset_index().head(10)
                    blok_count.columns = ['Blok', 'Jumlah']
                    fig = px.pie(blok_count, values='Jumlah', names='Blok', title='Distribusi Blok')
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("**Data Detail**")
            st.dataframe(df_plan, use_container_width=True, height=400)
            
            csv = df_plan.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Plan CSV", csv, 'daily_plan.csv')
    
    # =============== TAB REALISASI ===============
    with tab2:
        st.markdown('<p class="sub-header">✅ Data Realisasi</p>', unsafe_allow_html=True)
        
        df_real = load_realisasi()
        
        if df_real.empty:
            st.warning("⚠️ Data realisasi tidak tersedia")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Record", len(df_real))
            if 'Week' in df_real.columns:
                col2.metric("Jumlah Week", df_real['Week'].nunique())
            if 'Alat Muat' in df_real.columns:
                col3.metric("Alat Muat", df_real['Alat Muat'].nunique())
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Keterangan' in df_real.columns:
                    ket_count = df_real['Keterangan'].value_counts().reset_index()
                    ket_count.columns = ['Keterangan', 'Jumlah']
                    fig = px.pie(ket_count, values='Jumlah', names='Keterangan',
                                title='Realisasi per Keterangan')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'Shift' in df_real.columns:
                    shift_count = df_real['Shift'].value_counts().reset_index()
                    shift_count.columns = ['Shift', 'Jumlah']
                    fig = px.bar(shift_count, x='Shift', y='Jumlah',
                                title='Realisasi per Shift', color='Jumlah')
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("**Data Detail Realisasi**")
            st.dataframe(df_real, use_container_width=True, height=400)
            
            csv = df_real.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Realisasi CSV", csv, 'realisasi.csv')
    
    # =============== TAB PERBANDINGAN ===============
    with tab3:
        st.markdown('<p class="sub-header">📊 Perbandingan Plan vs Realisasi</p>', unsafe_allow_html=True)
        
        df_plan = load_daily_plan()
        df_real = load_realisasi()
        
        if df_plan.empty or df_real.empty:
            st.warning("⚠️ Data tidak lengkap untuk perbandingan")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📅 Summary Plan**")
                st.metric("Total Plan", len(df_plan))
                if 'Keterangan' in df_plan.columns:
                    plan_ket = df_plan['Keterangan'].value_counts()
                    st.write(plan_ket)
            
            with col2:
                st.markdown("**✅ Summary Realisasi**")
                st.metric("Total Realisasi", len(df_real))
                if 'Keterangan' in df_real.columns:
                    real_ket = df_real['Keterangan'].value_counts()
                    st.write(real_ket)
            
            # Perbandingan per Keterangan
            if 'Keterangan' in df_plan.columns and 'Keterangan' in df_real.columns:
                st.markdown("---")
                st.markdown("**Perbandingan per Keterangan**")
                
                plan_summary = df_plan['Keterangan'].value_counts().reset_index()
                plan_summary.columns = ['Keterangan', 'Plan']
                
                real_summary = df_real['Keterangan'].value_counts().reset_index()
                real_summary.columns = ['Keterangan', 'Realisasi']
                
                compare = pd.merge(plan_summary, real_summary, on='Keterangan', how='outer').fillna(0)
                compare['Selisih'] = compare['Realisasi'] - compare['Plan']
                
                fig = go.Figure()
                fig.add_trace(go.Bar(x=compare['Keterangan'], y=compare['Plan'], name='Plan', marker_color='#90CAF9'))
                fig.add_trace(go.Bar(x=compare['Keterangan'], y=compare['Realisasi'], name='Realisasi', marker_color='#4CAF50'))
                fig.update_layout(barmode='group', title='Plan vs Realisasi per Keterangan')
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(compare, use_container_width=True)