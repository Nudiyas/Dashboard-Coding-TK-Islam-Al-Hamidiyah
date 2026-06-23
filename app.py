# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

from halaman_guru import tampilkan_halaman_guru
from halaman_penguji import tampilkan_halaman_penguji
from praproses import bersihkan_dan_transformasi
from modeling import hitung_db_index, jalankan_kmeans

# =========================================================================
# 1. KONFIGURASI HALAMAN UTAMA & PARAMETER
# =========================================================================
st.set_page_config(
    page_title="Dashboard Coding - TK Islam Al-Hamidiyah", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

query_params = st.query_params
is_admin = query_params.get("admin") == "true"

# Loader CSS Sentralisasi
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            st.html(f"<style>{f.read()}</style>")

load_css("style.css")

# Helper Tampilan Header Clean
def tampilkan_header_halaman(judul_halaman, deskripsi_halaman):
    st.markdown(f"""
        <div class='hero-box'>
            <h1>{judul_halaman}</h1>
            <p>{deskripsi_halaman}</p>
        </div>
    """, unsafe_allow_html=True)

# =========================================================================
# FUNGSI CACHE: Mengunci data agar tidak hilang saat pindah URL (?admin=true)
# =========================================================================
@st.cache_data
def proses_kolektif_file(file_names, file_contents):
    list_df = []
    for name, content in zip(file_names, file_contents):
        df_raw = pd.read_excel(content, header=None)

        idx_header = 0
        for idx, row in df_raw.iterrows():
            row_str = [str(val).lower().strip() for val in row.values]
            if any('algor' in s or 'nama' in s for s in row_str):
                idx_header = idx
                break

        # Reset pointer content excel untuk dibaca ulang
        content.seek(0)
        df_clean_file = pd.read_excel(content, skiprows=idx_header)
        df_clean_file.columns = df_clean_file.columns.astype(str).str.strip()
        df_clean_file['Asal_Kelas'] = name.split('.')[0].replace('TK ', '')
        list_df.append(df_clean_file)

    df_mentah = pd.concat(list_df, ignore_index=True)
    df_mentah = df_mentah.loc[:, df_mentah.columns.notna()]
    df_mentah = df_mentah.loc[:, ~df_mentah.columns.str.contains('^Unnamed', case=False)]
    
    return df_mentah

# =========================================================================
# 2. SIDEBAR PANEL KONTROL
# =========================================================================
with st.sidebar:
    if os.path.exists("logo.png"):
        col_logo_left, col_logo_center, col_logo_right = st.columns([1, 2, 1])
        with col_logo_center:
            st.image("logo.png", width=120) 
    
    st.markdown("### 📁 Menu Kendali Kontrol")
    
    uploaded_files = st.file_uploader(
        "Unggah File Excel Kelas (Bisa pilih banyak sekaligus):", 
        type=["xlsx", "xls"], 
        accept_multiple_files=True
    )

    st.write("---")
    
    opsi_menu = ["🏫 Pemahaman Guru"]
    if is_admin:
        opsi_menu.append("🔬 Perspektif Penguji (Validasi)")
        
    menu_halaman = st.radio("📌 Navigasi Halaman:", opsi_menu)


# =========================================================================
# 3. KONDISI UTAMA: JIKA FILE BELUM DIUNGGAH
# =========================================================================
if not uploaded_files:
    tampilkan_header_halaman(
        "📊 Dashboard Penerapan K-Means Clustering", 
        "Pengelompokan Hasil Pembelajaran Coding Anak Usia Dini di TK Islam Al-Hamidiyah Depok"
    )
    st.info("💡 **Petunjuk Awal:** Silakan pilih dan unggah file Excel data nilai kelas paralel Anda melalui panel berlogo folder di sebelah kiri untuk mengaktifkan seluruh halaman analisis sistem.")
    
    st.write("") 
    st.markdown("### 🎯 Fokus Kompetensi Coding Anak Usia Dini")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='pilar-box pilar-algoritma'><h4>🤖 1. Logika Algoritma</h4><p>Mengukur kemampuan anak mengurutkan langkah-langkah penyelesaian masalah sederhana.</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='pilar-box pilar-pola'><h4>🔍 2. Pengenalan Pola</h4><p>Mengukur ketelitian anak melihat kesamaan atau keteraturan visual dari objek.</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='pilar-box pilar-perulangan'><h4>🔄 3. Konsep Perulangan</h4><p>Mengukur pemahaman anak terhadap aktivitas yang dilakukan berulang secara efisien.</p></div>", unsafe_allow_html=True)
        
    st.write("---")
    with st.expander("📋 Lihat Aturan & Format Berkas Excel yang Didukung"):
        st.markdown("""
        * **Format File:** `.xlsx` atau `.xls`
        * **Kolom Identitas Wajib:** Memiliki kolom nama siswa.
        * **Kolom Nilai yang Dikenali:** Mengandung kata kunci **Algoritma**, **Pola**, dan **Perulangan**.
        """)

# =========================================================================
# 4. KONDISI UTAMA: JIKA FILE SUDAH DIUNGGAH
# =========================================================================
else:
    # Memproses file dan transformasi
    file_names = [f.name for f in uploaded_files]
    file_contents = [f for f in uploaded_files]
    df_mentah = proses_kolektif_file(file_names, file_contents)
    df_clean, X_scaled = bersihkan_dan_transformasi(df_mentah)
    kolom_fitur_scaled = X_scaled.columns.tolist()
    kolom_riil = ['Rata_Algoritma', 'Rata_Pola', 'Rata_Perulangan']
    
    # Pengaturan K
    k_pilihan = 3
    if menu_halaman == "🔬 Perspektif Penguji (Validasi)":
        with st.sidebar:
            st.write("---")
            k_pilihan = st.selectbox("Pilih Jumlah Kelompok (K):", [2, 3, 4, 5, 6, 7, 8], index=1)
    
    # Jalankan Modeling (Menerima 4 nilai: df_hasil_raw, centroid, model_kmeans, init_df)
    df_hasil_raw, centroid, model_kmeans, init_df = jalankan_kmeans(df_clean, X_scaled, n_clusters=k_pilihan)

    # Labeling Cluster
    df_hasil_raw['Skor_Total_Urut'] = X_scaled.sum(axis=1)
    urutan = df_hasil_raw.groupby('Cluster')['Skor_Total_Urut'].mean().sort_values(ascending=False).index
    label_map = {cluster: label for cluster, label in zip(urutan, ["Tingkat Pemahaman Tinggi (Sangat Baik)", "Tingkat Pemahaman Sedang (Cukup)", "Tingkat Pemahaman Rendah (Butuh Bimbingan)"])}
    
    df_hasil_final = df_hasil_raw.copy()
    df_hasil_final['Keterangan_Cluster'] = df_hasil_final['Cluster'].map(label_map)

    # Router Halaman
    if menu_halaman == "🏫 Pemahaman Guru":
        tampilkan_halaman_guru(df_hasil_final, df_mentah, kolom_riil)
    else:
        # Mengirimkan 7 parameter ke halaman penguji
        tampilkan_halaman_penguji(
            df_hasil_final, kolom_fitur_scaled, X_scaled, centroid, model_kmeans, hitung_db_index, init_df
        )