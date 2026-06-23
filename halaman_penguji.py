import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils import tampilkan_header_halaman

def tampilkan_halaman_penguji(df_hasil_final, kolom_fitur_scaled, X_scaled, centroid, model_kmeans, hitung_db_index, init_df):
    tampilkan_header_halaman("🔬 Perspektif Penguji (Validasi)", "Pembuktian matematis proses K-Means dan analisis pergeseran centroid.")

    # 1. STATISTIK DESKRIPTIF
    st.markdown("## 📊 1. Statistik Deskriptif Data")
    st.dataframe(df_hasil_final[['Rata_Algoritma', 'Rata_Pola', 'Rata_Perulangan']].describe().round(2), use_container_width=True)
    st.divider()

# 2. ANALISIS PERGESERAN CENTROID (DELTA)
    st.markdown("## 🔄 2. Evolusi Centroid (Inisialisasi vs Konvergensi)")
    
    # Konversi ke array numpy untuk menghindari masalah index/nama kolom
    # Ini akan memaksa pengurangan numerik murni
    delta_values = np.abs(centroid.values - init_df.values)
    delta_df = pd.DataFrame(delta_values, columns=centroid.columns, index=centroid.index)
    
    c1, c2, c3 = st.columns(3)
    c1.caption("🔹 Centroid Awal (Inisialisasi)")
    c1.dataframe(init_df.round(4), use_container_width=True)
    
    c2.caption("🔹 Centroid Akhir (Hasil Konvergensi)")
    c2.dataframe(centroid.round(4), use_container_width=True)
    
    c3.caption("🔹 Delta (Pergeseran)")
    c3.dataframe(delta_df.round(4), use_container_width=True)
    
    st.info("""
    💡 **Analisis Iterasi:** Tabel di atas membuktikan terjadinya proses pembelajaran algoritma. 
    Perubahan nilai dari 'Inisialisasi' ke 'Konvergensi' adalah bukti matematis bahwa sistem 
    secara otomatis menggeser pusat cluster untuk mencari titik optimal (titik dengan total 
    jarak terkecil terhadap anggota kelompoknya).
    """)

    # 3. EUCLIDEAN DISTANCE
    st.markdown("## 📐 3. Contoh Perhitungan Euclidean Distance")
    idx = 0
    nama, contoh = df_hasil_final.iloc[idx]["Nama"], X_scaled.iloc[idx]
    st.write(f"Contoh perhitungan untuk siswa: **{nama}**")
    
    col1, col2 = st.columns(2)
    jarak = [round(np.sqrt(np.sum((contoh.values - centroid.iloc[i].values) ** 2)), 4) for i in range(len(centroid))]
    col1.dataframe(pd.DataFrame({"Variabel": kolom_fitur_scaled, "Nilai": contoh.round(4).values}), hide_index=True)
    col2.dataframe(pd.DataFrame({"Cluster": centroid.index, "Jarak": jarak}), hide_index=True)
    
    hasil = min(jarak)
    st.latex(fr'''d = \sqrt{{\sum(x_i-c_i)^2}} = {hasil:.4f}''')
    st.success(f"Siswa ditempatkan pada cluster dengan jarak terkecil: **{hasil:.4f}**.")
    st.divider()

    # 4. EVALUASI KINERJA
    st.markdown("## 📈 4. Evaluasi Kinerja Model")
    cols = st.columns(3)
    cols[0].metric("Jumlah Iterasi", model_kmeans.n_iter_)
    cols[1].metric("Nilai SSE", round(model_kmeans.inertia_, 4))
    cols[2].metric("DBI Optimal", round(hitung_db_index(X_scaled)['Davies-Bouldin Index'].min(), 4))

    df_dbi = hitung_db_index(X_scaled)
    c_left, c_right = st.columns([1, 2])
    c_left.dataframe(df_dbi, hide_index=True)
    fig = px.line(df_dbi, x="Jumlah Cluster (K)", y="Davies-Bouldin Index", markers=True)
    fig.update_layout(template="plotly_white", height=250, margin=dict(t=10, b=10, l=10, r=10))
    c_right.plotly_chart(fig, use_container_width=True)
    st.divider()

    # 5. SCATTER PLOT
    st.markdown("## 🌌 5. Sebaran Cluster")
    sx, sy = st.columns(2)
    x_axis = sx.selectbox("Sumbu X", kolom_fitur_scaled, index=0)
    y_axis = sy.selectbox("Sumbu Y", kolom_fitur_scaled, index=1)
    fig = px.scatter(df_hasil_final, x=x_axis, y=y_axis, color="Keterangan_Cluster", hover_data=["Nama"], color_discrete_sequence=["#22c55e", "#f59e0b", "#ef4444"])
    fig.update_layout(template="plotly_white", height=350, margin=dict(t=20, b=20), legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)

    st.success(f"""
               🎯 Kesimpulan & Validitas Model"
    * **Stabilitas Model:** Algoritma mencapai konvergensi dalam **{model_kmeans.n_iter_} iterasi**. Ini menunjukkan model sudah stabil dan data berhasil dikelompokkan sesuai pola karakteristiknya.
    * **Kualitas Cluster:** Dengan nilai **DBI sebesar {df_dbi['Davies-Bouldin Index'].min():.4f}**, model berhasil memisahkan tiap tingkat pemahaman siswa (Tinggi, Sedang, Rendah) dengan jarak antar-kelompok yang sangat tegas.
    * **Signifikansi Praktis:** Hasil clustering ini bersifat objektif karena murni berdasarkan distribusi nilai anak. Ini membantu guru untuk tidak lagi mengelompokkan siswa berdasarkan tebakan, melainkan berdasarkan data numerik yang akurat.
    """)