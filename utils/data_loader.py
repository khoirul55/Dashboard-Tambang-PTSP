import pandas as pd
import streamlit as st
from datetime import datetime
import os

@st.cache_data
def load_produksi():
    """Load data produksi harian"""
    possible_names = [
        'data/Produksi_UTSG_Harian.xlsx',
        'data/Produksi UTSG Harian.xlsx',
        'data/Produksi_UTSG_Harian .xlsx',
    ]
    
    df = None
    for file_path in possible_names:
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path, sheet_name='Tahun 2025')
                st.success(f"✅ Loaded: {file_path}")
                break
            except Exception as e:
                st.error(f"Error reading {file_path}: {e}")
                continue
    
    if df is None:
        st.error(f"❌ File produksi tidak ditemukan. Cek nama file di folder 'data/'")
        return pd.DataFrame()
    
    try:
        # ============ FIX: HAPUS KOLOM UNNAMED ============
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # ============ FIX: HAPUS HEADER BERULANG ============
        # Filter rows yang bukan header (Shift != 'Shift')
        df = df[df['Shift'] != 'Shift']
        
        # ============ FIX: VALIDASI EXCAVATOR ============
        # Hanya ambil excavator yang valid (mulai dengan "PC")
        df = df[df['Excavator'].astype(str).str.startswith('PC', na=False)]
        
        # ============ FIX: VALIDASI SHIFT ============
        valid_shifts = ['Shift 1', 'Shift 2', 'Shift 3']
        df = df[df['Shift'].isin(valid_shifts)]
        
        # ============ CLEAN DATE ============
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df[df['Date'].notna()]
        
        # ============ CLEAN NUMERIC COLUMNS ============
        numeric_cols = ['Rit', 'Tonnase']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # ============ FIX: DUMP TRUCK SEBAGAI STRING ============
        if 'Dump Truck' in df.columns:
            df['Dump Truck'] = df['Dump Truck'].astype(str)
            # Filter hanya yang berupa angka (bukan nama excavator)
            df = df[df['Dump Truck'].str.match(r'^\d+$', na=False)]
        
        # Remove rows with all NaN values
        df = df.dropna(how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
        
    except Exception as e:
        st.error(f"Error processing produksi data: {e}")
        return pd.DataFrame()


@st.cache_data
def load_gangguan(bulan):
    """Load data gangguan per bulan"""
    possible_names = [
        'data/Gangguan_Produksi_2025_baru.xlsx',
        'data/Gangguan Produksi 2025 baru.xlsx',
        'data/Gangguan_Produksi_2025_baru .xlsx',
    ]
    
    df = None
    sheet = f'Monitoring {bulan}'
    
    for file_path in possible_names:
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path, sheet_name=sheet, skiprows=1)
                break
            except Exception as e:
                continue
    
    if df is None:
        st.error(f"❌ File gangguan tidak ditemukan atau sheet '{sheet}' tidak ada")
        return pd.DataFrame()
    
    try:
        # Rename kolom
        if len(df.columns) >= 3:
            df.columns = ['Row Labels', 'Frekuensi', 'Persentase']
        
        # ============ FIX: HAPUS HEADER BERULANG ============
        df = df[df['Row Labels'] != 'Row Labels']
        df = df[df['Row Labels'] != 'Grand Total']
        
        # Clean data
        df['Frekuensi'] = pd.to_numeric(df['Frekuensi'], errors='coerce')
        df = df.dropna(subset=['Frekuensi'])
        df = df[df['Frekuensi'] > 0]
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
        
    except Exception as e:
        st.error(f"Error processing gangguan data: {e}")
        return pd.DataFrame()


@st.cache_data
def load_monitoring(sheet_name='Monitoring Januari'):
    """Load data monitoring produktivitas"""
    possible_names = [
        'data/Monitoring_2025_.xlsx',
        'data/Monitoring 2025_.xlsx',
        'data/Monitoring_2025.xlsx',
    ]
    
    for file_path in possible_names:
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=2)
                
                # Clean unnamed columns
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                
                return df
            except Exception as e:
                continue
    
    st.error("❌ File monitoring tidak ditemukan")
    return pd.DataFrame()


@st.cache_data
def load_daily_plan():
    """Load data daily plan"""
    try:
        df = pd.read_excel('data/DAILY_PLAN.xlsx', sheet_name='W22 Scheduling', skiprows=1)
        
        # ============ FIX: RENAME KOLOM DARI BARIS PERTAMA ============
        first_row = df.iloc[0]
        new_cols = []
        for i, val in enumerate(first_row):
            if pd.notna(val) and str(val) != 'None':
                new_cols.append(str(val))
            else:
                new_cols.append(f'Col_{i}')
        
        df.columns = new_cols
        df = df[1:]  # Skip header row
        df = df.reset_index(drop=True)
        
        # ============ FIX: CLEAN TANGGAL ============
        if 'Tanggal' in df.columns:
            df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
            df['Tanggal'] = df['Tanggal'].dt.strftime('%Y-%m-%d')
        
        # ============ FIX: HAPUS KOLOM YANG TIDAK PERLU ============
        cols_to_keep = ['Hari', 'Tanggal', 'Shift', 'Batu Kapur', 'Silika', 
                        'Clay', 'Alat Muat', 'Alat Angkut', 'Blok', 'Grid', 
                        'ROM', 'Keterangan']
        available_cols = [col for col in cols_to_keep if col in df.columns]
        
        if available_cols:
            df = df[available_cols]
        
        # Hapus rows yang semua nilainya None/NaN
        df = df.dropna(how='all')
        
        return df
        
    except Exception as e:
        st.error(f"Error loading daily plan: {e}")
        return pd.DataFrame()


@st.cache_data  
def load_produktivitas():
    """Load data produktivitas dari Monitoring_2025_"""
    possible_names = [
        'data/Monitoring_2025_.xlsx',
        'data/Monitoring 2025_.xlsx',
    ]
    
    for file_path in possible_names:
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path, sheet_name='Produktivitas')
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                return df
            except Exception as e:
                continue
    
    return pd.DataFrame()


@st.cache_data
def load_bbm():
    """Load data BBM dari Monitoring_2025_"""
    possible_names = [
        'data/Monitoring_2025_.xlsx',
        'data/Monitoring 2025_.xlsx',
    ]
    
    for file_path in possible_names:
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path, sheet_name='BBM')
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                
                # FIX: Hapus baris header yang ikut terbaca
                if 'Total' in df.columns:
                    df = df[df['Total'] != 'Total']
                    df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(0)
                
                # FIX: Convert semua kolom numerik (tanggal 1-31)
                for col in df.columns:
                    if col not in ['No', 'Alat Berat', 'Tipe Alat', 'Total']:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
                return df
            except Exception as e:
                continue
    
    return pd.DataFrame()


@st.cache_data
def load_ritase():
    """Load data ritase dari Monitoring_2025_"""
    possible_names = [
        'data/Monitoring_2025_.xlsx',
        'data/Monitoring 2025_.xlsx',
    ]
    
    for file_path in possible_names:
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path, sheet_name='Ritase')
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                
                # FIX: Convert Tanggal
                if 'Tanggal' in df.columns:
                    df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
                    df = df[df['Tanggal'].notna()]
                
                # FIX: Convert kolom numerik
                for col in df.columns:
                    if col not in ['Tanggal', 'Shift', 'Pengawasan']:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
                return df
            except Exception as e:
                continue
    
    return pd.DataFrame()