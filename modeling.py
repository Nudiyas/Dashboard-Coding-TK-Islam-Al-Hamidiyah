import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score

import pandas as pd
from sklearn.cluster import KMeans

# modeling.py
import pandas as pd
from sklearn.cluster import KMeans

def jalankan_kmeans(df_clean, X_scaled, n_clusters=3):
    # 1. Inisialisasi
    init_model = KMeans(n_clusters=n_clusters, init="random", n_init=1, max_iter=1, random_state=1)
    init_model.fit(X_scaled)
    init_df = pd.DataFrame(init_model.cluster_centers_, columns=X_scaled.columns)
    
    # 2. Model Utama
    model_kmeans = KMeans(n_clusters=n_clusters, init="k-means++", n_init=10, random_state=42)
    model_kmeans.fit(X_scaled)
    
    # 3. Persiapan Hasil
    centroid = pd.DataFrame(model_kmeans.cluster_centers_, columns=X_scaled.columns)
    df_hasil_raw = df_clean.copy()
    df_hasil_raw['Cluster'] = model_kmeans.labels_
    
    # --- INI WAJIB ADA ---
    return df_hasil_raw, centroid, model_kmeans, init_df

def hitung_db_index(X_scaled):
    hasil = []
    for k in range(2, 9):
        model = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=42)
        labels = model.fit_predict(X_scaled)
        hasil.append({"Jumlah Cluster (K)": k, "Davies-Bouldin Index": round(davies_bouldin_score(X_scaled, labels), 4)})
    return pd.DataFrame(hasil)