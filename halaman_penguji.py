# halaman_penguji.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils import tampilkan_header_halaman


def tampilkan_halaman_penguji(
        df_hasil_final,
        kolom_fitur_scaled,
        X_scaled,
        centroid,
        model_kmeans,
        hitung_db_index
):

    tampilkan_header_halaman(
        "🔬 Perspektif Penguji (Validasi)",
        "Pembuktian matematis proses K-Means menggunakan Min-Max Scaling, Euclidean Distance, dan Davies-Bouldin Index."
    )

    # ===================================================
    # CENTROID
    # ===================================================
    st.markdown("## 📊 Matriks Centroid Hasil Normalisasi Min-Max")

    st.dataframe(
        centroid.round(4),
        use_container_width=True
    )

    st.info(
        "💡 Setiap baris merupakan titik pusat (centroid) masing-masing cluster. "
        "Nilai mendekati 1 menunjukkan kemampuan semakin tinggi, sedangkan mendekati 0 menunjukkan kemampuan semakin rendah."
    )

    st.divider()

    # ===================================================
    # EUCLIDEAN DISTANCE
    # ===================================================
    st.markdown("## 📐 Contoh Perhitungan Euclidean Distance")

    st.latex(
        r'''
        d=\sqrt{
        (x_1-c_1)^2+
        (x_2-c_2)^2+
        (x_3-c_3)^2
        }
        '''
    )

    idx = 0
    nama_siswa = df_hasil_final.iloc[idx]["Nama"]
    contoh_scaled = X_scaled.iloc[idx]

    st.write(f"Contoh menggunakan siswa: **{nama_siswa}**")

    df_contoh = pd.DataFrame({
        "Variabel": kolom_fitur_scaled,
        "Nilai Normalisasi": contoh_scaled.round(4).values
    })

    col_data_1, col_data_2 = st.columns(2, gap="medium")

    with col_data_1:
        st.caption("🔹 Nilai Normalisasi Siswa")
        st.dataframe(df_contoh, use_container_width=True, hide_index=True)

    jarak = []
    for i in range(len(centroid)):
        d = np.sqrt(
            np.sum(
                (contoh_scaled.values - centroid.iloc[i].values) ** 2
            )
        )
        jarak.append(round(d, 4))

    df_jarak = pd.DataFrame({
        "Cluster": centroid.index,
        "Jarak Euclidean": jarak
    })

    with col_data_2:
        st.caption("🔹 Hasil Jarak ke Setiap Centroid")
        st.dataframe(df_jarak, use_container_width=True, hide_index=True)

    cluster_idx = df_jarak["Jarak Euclidean"].idxmin()
    cluster_terdekat = df_jarak.loc[cluster_idx, "Cluster"]

    c = centroid.iloc[cluster_idx]
    x1, x2, x3 = contoh_scaled.iloc[0], contoh_scaled.iloc[1], contoh_scaled.iloc[2]
    c1, c2, c3 = c.iloc[0], c.iloc[1], c.iloc[2]

    hasil = np.sqrt((x1-c1)**2 + (x2-c2)**2 + (x3-c3)**2)

    st.markdown("#### Substitusi Angka")
    st.latex(
        fr'''
        d = \sqrt{{ ({x1:.4f}-{c1:.4f})^2 + ({x2:.4f}-{c2:.4f})^2 + ({x3:.4f}-{c3:.4f})^2 }} = {hasil:.4f}
        '''
    )

    st.success(
        f"Siswa ditempatkan pada **{cluster_terdekat}** "
        f"karena memiliki jarak Euclidean paling kecil yaitu **{hasil:.4f}**."
    )

    st.divider()

    # ===================================================
    # DBI + ITERASI + SSE
    # ===================================================
    st.markdown("## 📈 Evaluasi Davies-Bouldin Index (DBI)")

    df_dbi = hitung_db_index(X_scaled)

    col1, col2 = st.columns([1.2, 2], gap="medium")

    with col1:
        st.dataframe(df_dbi, use_container_width=True, hide_index=True)

    with col2:
        fig = px.line(
            df_dbi,
            x="Jumlah Cluster (K)",
            y="Davies-Bouldin Index",
            markers=True
        )
        fig.update_layout(
            template="plotly_white",
            height=280,  
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.metric("Jumlah Iterasi K-Means", model_kmeans.n_iter_)

    with col_b:
        st.metric("Nilai SSE (Inertia)", round(model_kmeans.inertia_, 4))

    k_terbaik = df_dbi.loc[
        df_dbi["Davies-Bouldin Index"].idxmin(),
        "Jumlah Cluster (K)"
    ]
    dbi_terbaik = df_dbi["Davies-Bouldin Index"].min()

    st.info(
        f"💡 Secara matematis DBI terbaik diperoleh pada "
        f"K={k_terbaik} dengan nilai {dbi_terbaik:.4f}. "
        f"Penelitian ini menggunakan K={len(centroid)} "
        f"karena pertimbangan interpretasi pedagogis untuk guru TK."
    )

    st.divider()

    # ===================================================
    # SCATTER
    # ===================================================
    st.markdown("## 🌌 Sebaran Cluster pada Euclidean Space")

    col_x, col_y = st.columns(2)

    with col_x:
        sx = st.selectbox("Sumbu X", kolom_fitur_scaled, index=0)

    with col_y:
        sy = st.selectbox("Sumbu Y", kolom_fitur_scaled, index=1)

    fig = px.scatter(
        df_hasil_final,
        x=sx,
        y=sy,
        color="Keterangan_Cluster",
        hover_data=["Nama"],
        color_discrete_sequence=["#22c55e", "#f59e0b", "#ef4444"]
    )
    fig.update_layout(
        template="plotly_white",
        height=380,  
        margin=dict(t=20, b=20, l=10, r=10),
        legend=dict(
            orientation="h",
            y=-0.18,
            x=0.5,
            xanchor="center"
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    st.success(f"""
📌 **Kesimpulan Pengujian**

1. Seluruh variabel telah dinormalisasi menggunakan **Min-Max Scaling** sehingga berada pada rentang 0–1.
2. Pengelompokan dilakukan menggunakan algoritma **K-Means** berdasarkan kedekatan jarak Euclidean terhadap centroid.
3. Nilai DBI terkecil diperoleh pada **K={k_terbaik}** dengan nilai **{dbi_terbaik:.4f}**.
4. Nilai SSE sebesar **{model_kmeans.inertia_:.4f}** menunjukkan tingkat kekompakan anggota cluster terhadap centroid.
5. Algoritma mencapai kondisi konvergen setelah **{model_kmeans.n_iter_}** iterasi.
""")