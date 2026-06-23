import streamlit as st

def tampilkan_header_halaman(judul_halaman, deskripsi_halaman):
    # Menggunakan container bawaan Streamlit
    with st.container():
        st.markdown(f"""
            <div class='hero-box'>
                <h1 style='margin-bottom:0; font-size: 1.8rem; font-weight:700; color: white;'>
                    {judul_halaman}
                </h1>
                <p style='opacity:0.9; margin-top:8px; font-size:1rem; color: white;'>
                    {deskripsi_halaman}
                </p>
            </div>
        """, unsafe_allow_html=True)

def ringkas_arti(cluster_name):
    if "Tinggi" in cluster_name or "Sangat Baik" in cluster_name:
        return "🟢 Mandiri (Bisa diberi tantangan logika baru)"

    elif "Sedang" in cluster_name or "Baik" in cluster_name or "Cukup" in cluster_name:
        return "🟡 Berkembang Sesuai Harapan (Pertahankan)"

    else:
        return "🔴 Butuh Pendampingan (Perlu stimulasi alat peraga fisik)"
    