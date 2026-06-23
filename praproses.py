# praproses.py
import pandas as pd
import numpy as np

def bersihkan_dan_transformasi(df):
    """
    Memproses dataframe untuk hanya mengambil kolom capaian nilai riil siswa (Rata_*)
    dan membuang kolom bobot/KKM kurikulum yang nilainya konstan.
    """
    df_clean = df.copy()
    
    # 1. Standarisasi nama kolom target yang valid
    pemetaan_nama = {
        'rata_algor': 'Rata_Algoritma',
        'rata_algoritma': 'Rata_Algoritma',
        'rata_pola': 'Rata_Pola',
        'rata_perulangan': 'Rata_Perulangan'
    }
    
    kolom_baru = {}
    for col in df_clean.columns:
        col_norm = str(col).strip().lower()
        if col_norm in pemetaan_nama:
            kolom_baru[col] = pemetaan_nama[col_norm]
            
    if kolom_baru:
        df_clean = df_clean.rename(columns=kolom_baru)

    kolom_target = ['Rata_Algoritma', 'Rata_Pola', 'Rata_Perulangan']

    # 2. Paksa tipe data menjadi numerik dan isi data kosong dengan rata-rata
    for col in kolom_target:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            df_clean[col] = df_clean[col].fillna(df_clean[col].mean() if not pd.isna(df_clean[col].mean()) else 0)
        else:
            df_clean[col] = 0.0
            
    # 3. KUNCI UTAMA: Buang kolom bobot master ('Algoritma', 'Pola', 'Perulangan') agar tidak double
    kolom_yang_dibuang = ['Algoritma', 'Pola', 'Perulangan', 'Total', 'Unnamed: 0']
    for col in kolom_yang_dibuang:
        if col in df_clean.columns:
            df_clean = df_clean.drop(columns=[col])
            
    # Ambil matriks nilai murni untuk clustering
    X = df_clean[kolom_target].values
    
    # Normalisasi Min-Max Scaler (0-1)
    min_val = X.min(axis=0)
    max_val = X.max(axis=0)
    range_val = max_val - min_val
    range_val[range_val == 0] = 1.0
    
    X_scaled = (X - min_val) / range_val
    X_scaled_df = pd.DataFrame(X_scaled, columns=kolom_target)
    
    return df_clean, X_scaled_df