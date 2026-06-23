# halaman_guru.py
import streamlit as st
import plotly.express as px
from utils import tampilkan_header_halaman, ringkas_arti


def tampilkan_halaman_guru(df_hasil_final, df_mentah, kolom_riil):

    # =====================
    # HEADER
    # =====================
    tampilkan_header_halaman(
        "🏫 Panel Evaluasi & Rekomendasi Belajar Kelas",
        "Menu khusus guru untuk melihat hasil clustering, kondisi pemahaman siswa, dan rekomendasi pembelajaran coding."
    )

    # =====================
    # KARTU METRIK
    # =====================
    jumlah_rendah = (
        df_hasil_final["Keterangan_Cluster"]
        .str.contains("Rendah", case=False)
        .sum()
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("👦 Total Siswa", f"{len(df_mentah)} Anak")
    c2.metric("📚 Materi Coding", "3 Materi")
    c3.metric("🔴 Perlu Pendampingan", f"{jumlah_rendah} Anak")

    st.divider()

    # =====================
    # FILTER KELAS
    # =====================
    pilih_kelas = st.selectbox(
        "🏫 Pilih Kelas",
        ["Semua"] + sorted(df_hasil_final["Asal_Kelas"].unique())
    )

    if pilih_kelas != "Semua":
        df_hasil_final = df_hasil_final[
            df_hasil_final["Asal_Kelas"] == pilih_kelas
        ]

    # =====================
    # DATA GRAFIK
    # =====================
    df_materi = (
        df_hasil_final[kolom_riil]
        .mean()
        .sort_values()
        .reset_index()
    )
    df_materi.columns = ["Materi", "Nilai"]
    df_materi["Materi"] = df_materi["Materi"].replace({
        "Rata_Algoritma": "Logika Algoritma",
        "Rata_Pola": "Pengenalan Pola",
        "Rata_Perulangan": "Konsep Perulangan"
    })

    materi_terendah = df_materi.iloc[0]["Materi"]

    df_pie = (
        df_hasil_final["Keterangan_Cluster"]
        .value_counts()
        .reset_index()
    )
    df_pie.columns = ["Kategori", "Jumlah"]
    kategori_terbesar = df_pie.iloc[0]["Kategori"]

    # =====================
    # GRAFIK
    # =====================
    st.markdown("### 📊 Evaluasi Pembelajaran Coding")
    st.write("")

    col1, col2 = st.columns([1, 1], gap="large")

    # ---------------------
    # DONUT CHART
    # ---------------------
    with col1:
        st.markdown("##### 👦 Distribusi Tingkat Pemahama n Anak")

        fig_donut = px.pie(
            df_pie,
            names="Kategori",
            values="Jumlah",
            hole=0.55,
            color="Kategori",
            color_discrete_map={
                "Tingkat Pemahaman Tinggi (Sangat Baik)": "#22c55e",
                "Tingkat Pemahaman Sedang (Cukup)": "#f59e0b",
                "Tingkat Pemahaman Rendah (Butuh Bimbingan)": "#ef4444"
            }
        )
        fig_donut.update_traces(
            textposition="inside",
            textinfo="percent"
        )
        fig_donut.add_annotation(
            text=f"<b>{len(df_hasil_final)}</b><br>Anak",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=18)
        )
        fig_donut.update_layout(
            template="plotly_white",
            height=380,
            margin=dict(t=40, b=60, l=20, r=20),
            legend=dict(
                orientation="h",
                y=-0.15,
                x=0.5,
                xanchor="center",
                font=dict(size=10)
            )
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.info(f"💡 Mayoritas siswa berada pada kategori **{kategori_terbesar}**.")

    # ---------------------
    # BAR CHART
    # ---------------------
    with col2:
        st.markdown("##### 📚 Materi Coding yang Perlu Ditingkatkan")

        fig_materi = px.bar(
            df_materi,
            x="Nilai",
            y="Materi",
            orientation="h",
            text="Nilai"
        )
        fig_materi.update_traces(
            marker_color=["#ef4444", "#f59e0b", "#22c55e"],
            texttemplate="%{text:.2f}",
            textposition="inside"
        )
        fig_materi.update_layout(
            template="plotly_white",
            height=380,
            margin=dict(t=40, b=40, l=20, r=20),
            showlegend=False,
            xaxis_title="Nilai Rata-rata",
            yaxis_title="Materi"
        )
        st.plotly_chart(fig_materi, use_container_width=True)
        st.info(f"💡 Materi **{materi_terendah}** memiliki rata-rata capaian terendah.")

    # =====================
    # INSIGHT GURU
    # =====================
    st.divider()
    st.markdown("##### 🎯 Insight & Rekomendasi Guru")
    st.success(f"""
• Mayoritas siswa berada pada kategori **{kategori_terbesar}**.

• Materi yang perlu diperkuat adalah **{materi_terendah}**.

• Guru dapat menambah kegiatan **unplugged coding** menggunakan kartu instruksi, balok pola, dan permainan langkah berurutan secara bertahap.
""")

    # =====================
    # ACUAN CLUSTER
    # =====================
    st.divider()
    st.markdown("###### 📋 Acuan Pembacaan Nomor Klaster")

    df_rujukan = (
        df_hasil_final
        .groupby("Cluster")["Keterangan_Cluster"]
        .first()
        .reset_index()
    )
    df_rujukan.columns = ["ID Cluster", "Tingkat Pemahaman"]
    df_rujukan["Kategori Tindakan Guru"] = df_rujukan["Tingkat Pemahaman"].apply(ringkas_arti)

    st.dataframe(df_rujukan, use_container_width=True, hide_index=True)

    # =====================
    # TABEL SISWA
    # =====================
    st.divider()
    st.markdown("###### 🔍 Filter & Daftar Hasil Belajar Siswa")

    df_tabel = df_hasil_final.copy()
    for c in kolom_riil:
        df_tabel[c] = df_tabel[c].round(2)

    df_tabel = df_tabel[["Asal_Kelas", "Nama"] + kolom_riil + ["Cluster"]]
    df_tabel.columns = ["Nama Kelas", "Nama Siswa", "Rata Algoritma", "Rata Pola", "Rata Perulangan", "Cluster"]

    pilih_siswa = st.selectbox(
        "👦 Pilih Nama Siswa",
        ["Semua"] + sorted(df_tabel["Nama Siswa"].unique())
    )

    if pilih_siswa != "Semua":
        df_tabel = df_tabel[df_tabel["Nama Siswa"] == pilih_siswa]

    st.dataframe(
        df_tabel.sort_values(["Nama Kelas", "Nama Siswa"]),
        use_container_width=True,
        hide_index=True
    )