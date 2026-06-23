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

# 1. KONFIGURASI HALAMAN UTAMA
st.set_page_config(
    page_title="Dashboard Coding - TK Islam Al-Hamidiyah", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. PEMBACA EXTERNAL CSS (Sentralisasi Desain)
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            st.html(f"<style>{f.read()}</style>")

load_css("style.css")


# 3. HELPER UTAMA: MENAMPILKAN HEADER CLEAN (CSS Pindah ke style.css)
def tampilkan_header_halaman(judul_halaman, deskripsi_halaman):
    st.markdown(f"""
        <div class='hero-box'>
            <h1>{judul_halaman}</h1>
            <p>{deskripsi_halaman}</p>
        </div>
    """, unsafe_allow_html=True)
# ==========================================
# 4. SIDEBAR PANEL KONTROL
# ==========================================
with st.sidebar:
    if os.path.exists("logo.png"):
        col_logo_left, col_logo_center, col_logo_right = st.columns([1, 2, 1])
        with col_logo_center:
            st.image("logo.png", width=120) 
    
    st.markdown("### 📁 Menu Kendali Kontrol")
    
    # PASTIKAN BARIS INI ADA DAN NAMA VARIABELNYA SAMA PERSIS
    uploaded_files = st.file_uploader(
        "Unggah File Excel Kelas (Bisa pilih banyak sekaligus):", 
        type=["xlsx", "xls"], 
        accept_multiple_files=True
    )

# 5. PERKONDISIAN UTAMA: JIKA FILE BELUM DIUNGGAH
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
        st.markdown("""
        <div class='pilar-box pilar-algoritma'>
            <h4>🤖 1. Logika Algoritma</h4>
            <p>Mengukur kemampuan anak mengurutkan langkah-langkah penyelesaian masalah sederhana.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class='pilar-box pilar-pola'>
            <h4>🔍 2. Pengenalan Pola</h4>
            <p>Mengukur ketelitian anak melihat kesamaan atau keteraturan visual dari objek.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class='pilar-box pilar-perulangan'>
            <h4>🔄 3. Konsep Perulangan</h4>
            <p>Mengukur pemahaman anak terhadap aktivitas yang dilakukan berulang secara efisien.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("---")
    
    with st.expander("📋 Lihat Aturan & Format Berkas Excel yang Didukung"):
        st.markdown("""
        Untuk memastikan komputasi klaster berjalan lancar, pastikan file Excel kelas Anda memenuhi kriteria berikut:
        * **Format File:** `.xlsx` atau `.xls`
        * **Kolom Identitas Wajib:** Memiliki kolom nama siswa (Contoh: `Nama` atau `Nama Siswa`).
        * **Kolom Nilai yang Dikenali:** Sistem akan mendeteksi otomatis kolom yang mengandung kata kunci **Algoritma**, **Pola**, dan **Perulangan**.
        * **Tips Tambahan:** Anda dapat mengunggah beberapa berkas kelas sekaligus secara bersamaan (misal: data Kelas A dan Kelas B) untuk dianalisis secara kolektif.
        """)
    
else:
    list_df = []

    for file in uploaded_files:
        df_raw = pd.read_excel(file, header=None)

        idx_header = 0
        for idx, row in df_raw.iterrows():
            row_str = [str(val).lower().strip() for val in row.values]
            if any('algor' in s or 'nama' in s for s in row_str):
                idx_header = idx
                break

        df_clean_file = pd.read_excel(file, skiprows=idx_header)
        df_clean_file.columns = (
            df_clean_file.columns.astype(str).str.strip()
        )

        df_clean_file['Asal_Kelas'] = (
            file.name.split('.')[0].replace('TK ', '')
        )

        list_df.append(df_clean_file)

    df_mentah = pd.concat(list_df, ignore_index=True)
    df_mentah = df_mentah.loc[:, df_mentah.columns.notna()]
    df_mentah = df_mentah.loc[
        :, ~df_mentah.columns.str.contains('^Unnamed', case=False)
    ]

    # Praproses data
    df_clean, X_scaled = bersihkan_dan_transformasi(df_mentah)
    kolom_fitur_scaled = X_scaled.columns.tolist()
    
    # ==========================
    # SIDEBAR NAVIGASI HALAMAN
    # ==========================
    with st.sidebar:
        st.write("---")
        menu_halaman = st.radio(
            "📌 Navigasi Halaman:",
            [
                "🏫 Pemahaman Guru",
                "🔬 Perspektif Penguji (Validasi)"
            ]
        )

    # ==========================
    # MENENTUKAN NILAI K
    # ==========================
    if menu_halaman == "🏫 Pemahaman Guru":
        k_pilihan = 3
    else:
        with st.sidebar:
            st.write("---")
            st.markdown("### ⚙️ Konfigurasi Parameter")
            k_pilihan = st.selectbox(
                "Pilih Jumlah Kelompok (K):",
                options=[2, 3, 4, 5, 6, 7, 8],
                index=1
            )
            st.caption(f"ℹ️ K = {k_pilihan} digunakan untuk evaluasi pengelompokan.")
    
    # ==========================
    # MENJALANKAN K-MEANS
    # ==========================
    df_hasil_raw, centroid, model_kmeans = jalankan_kmeans(
        df_clean,
        X_scaled,
        n_clusters=k_pilihan
    )

    # ==========================
    # PEMETAAN LABEL CLUSTER
    # ==========================
    df_hasil_raw['Skor_Total_Urut'] = X_scaled.sum(axis=1)

    urutan_cluster = (
        df_hasil_raw
        .groupby('Cluster')['Skor_Total_Urut']
        .mean()
        .sort_values(ascending=False)
        .index
    )

    pemetaan_status = {}
    label_status = [
        "Tingkat Pemahaman Tinggi (Sangat Baik)",
        "Tingkat Pemahaman Sedang (Cukup)",
        "Tingkat Pemahaman Rendah (Butuh Bimbingan)"
    ]

    for i, cluster_name in enumerate(urutan_cluster):
        pemetaan_status[cluster_name] = (
            label_status[min(i, len(label_status) - 1)]
        )

    df_hasil_final = df_hasil_raw.copy()
    df_hasil_final['Keterangan_Cluster'] = (
        df_hasil_final['Cluster'].map(pemetaan_status)
    )

    kolom_riil = [
        'Rata_Algoritma',
        'Rata_Pola',
        'Rata_Perulangan'
    ]
    
    # ==========================
    # MENAMPILKAN HALAMAN
    # ==========================
    if menu_halaman == "🏫 Pemahaman Guru":
        tampilkan_halaman_guru(
            df_hasil_final,
            df_mentah,
            kolom_riil
        )
    else:
        tampilkan_halaman_penguji(
            df_hasil_final,
            kolom_fitur_scaled,
            X_scaled,
            centroid,
            model_kmeans,
            hitung_db_index
        )