import pandas as pd
import streamlit as st
from datetime import datetime
import os

@st.cache_data
def load_produksi():
    """Load data produksi harian"""
    # Coba berbagai kemungkinan nama file
    possible_names = [
        'data/Produksi_UTSG_Harian.xlsx',
        'data/Produksi UTSG Harian.xlsx',
        'data/Produksi_UTSG_Harian .xlsx',  # dengan spasi di akhir
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
        st.info(f"File yang dicari: {', '.join(possible_names)}")
        return pd.DataFrame()
    
    try:
        # Clean kolom Date
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Remove header rows yang muncul di tengah data
        df = df[df['Shift'] != 'Shift']
        df = df[df['Date'].notna()]
        
        # Clean numeric columns
        numeric_cols = ['Rit', 'Tonnase']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with all NaN values
        df = df.dropna(how='all')
        
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
            
        # Clean data
        df = df[df['Row Labels'] != 'Row Labels']  # Remove header rows
        df['Frekuensi'] = pd.to_numeric(df['Frekuensi'], errors='coerce')
        df = df.dropna(subset=['Frekuensi'])
        
        return df
    except Exception as e:
        st.error(f"Error processing gangguan data: {e}")
        return pd.DataFrame()

@st.cache_data
def load_monitoring():
    """Load data monitoring produktivitas"""
    possible_names = [
        'data/Monitoring_2025_.xlsx',
        'data/Monitoring 2025_.xlsx',
        'data/Monitoring_2025.xlsx',
    ]
    
    for file_path in possible_names:
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path, sheet_name='Monitoring Januari', skiprows=2)
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
        
        # Clean kolom yang berisi mixed types (datetime + string)
        for col in df.columns:
            # Convert datetime objects to string
            if df[col].dtype == 'object':
                df[col] = df[col].apply(lambda x: str(x) if pd.notna(x) and not isinstance(x, str) else x)
        
        # Rename kolom jika baris pertama adalah header
        first_row = df.iloc[0]
        if 'Hari' in str(first_row.values):
            # Set kolom names dari baris pertama
            new_cols = []
            for i, val in enumerate(first_row):
                if pd.notna(val) and val != 'None':
                    new_cols.append(str(val))
                else:
                    new_cols.append(f'Col_{i}')
            
            df.columns = new_cols
            df = df[1:]  # Skip header row
            df = df.reset_index(drop=True)
        
        # Clean kolom Tanggal - convert to proper datetime
        if 'Tanggal' in df.columns:
            df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
            df['Tanggal'] = df['Tanggal'].dt.strftime('%Y-%m-%d')
        
        return df
    except Exception as e:
        st.error(f"Error loading daily plan: {e}")
        return pd.DataFrame()