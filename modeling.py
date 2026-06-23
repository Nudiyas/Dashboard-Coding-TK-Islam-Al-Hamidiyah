# modeling.py
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score


def jalankan_kmeans(df_clean, X_scaled, n_clusters=3):

    model = KMeans(
        n_clusters=n_clusters,
        init="k-means++",
        n_init=10,
        random_state=42
    )

    model.fit(X_scaled)
    print(model.cluster_centers_)

    df_hasil = df_clean.copy()

    df_hasil["Cluster"] = [
        f"Cluster {i+1}"
        for i in model.labels_
    ]

    centroid = pd.DataFrame(
        model.cluster_centers_,
        columns=X_scaled.columns,
        index=[
            f"Cluster {i+1}"
            for i in range(n_clusters)
        ]
    )

    return df_hasil, centroid, model


def hitung_db_index(X_scaled):

    hasil = []

    for k in range(2, 9):

        model = KMeans(
            n_clusters=k,
            init="k-means++",
            n_init=10,
            random_state=42
        )

        labels = model.fit_predict(X_scaled)

        hasil.append({
            "Jumlah Cluster (K)": k,
            "Davies-Bouldin Index":
                round(
                    davies_bouldin_score(
                        X_scaled,
                        labels
                    ),
                    4
                )
        })

    return pd.DataFrame(hasil)