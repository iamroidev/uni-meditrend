import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, silhouette_score
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from generate_dataset import generate_dataset


RANDOM_STATE = 42
OUT_DIR = Path("report_assets")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_B_CLUSTER_LABELS = {
    0: "Tropical Illness",
    1: "Severe/Water-Borne",
    2: "Fresher Burnout",
    3: "Minor Ailments",
}


def make_eda_figures(df: pd.DataFrame) -> None:
    diagnosis_hostel = (
        df.groupby(["hostel", "diagnosis"]).size().reset_index(name="count")
    )

    top_hostels = (
        diagnosis_hostel.groupby("hostel")["count"].sum().sort_values(ascending=False).head(8).index
    )
    plot_df = diagnosis_hostel[diagnosis_hostel["hostel"].isin(top_hostels)].copy()

    pivot_df = plot_df.pivot(index="hostel", columns="diagnosis", values="count").fillna(0)
    pivot_df = pivot_df.loc[top_hostels]

    plt.figure(figsize=(12, 6))
    pivot_df.plot(kind="bar", stacked=True, figsize=(12, 6), colormap="tab20", ax=plt.gca())
    plt.title("Diagnosis Frequency by Hostel (Top 8 Hostels)")
    plt.xlabel("Hostel")
    plt.ylabel("Number of Visits")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "eda_diagnosis_by_hostel.png", dpi=200)
    plt.close()

    weekly = (
        df.set_index("visit_date").resample("W")
        .size()
        .reset_index(name="weekly_visits")
    )

    plt.figure(figsize=(12, 4.8))
    plt.plot(weekly["visit_date"], weekly["weekly_visits"], linewidth=1.8)
    plt.title("Weekly Clinic Visit Volume")
    plt.xlabel("Week")
    plt.ylabel("Visits")
    plt.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "eda_weekly_visits.png", dpi=200)
    plt.close()


def build_hostel_cluster(df: pd.DataFrame):
    total_by_hostel = df.groupby("hostel").size().rename("total")
    diag_mix = pd.crosstab(df["hostel"], df["diagnosis"])
    diag_mix = diag_mix.div(diag_mix.sum(axis=1), axis=0)
    avg_sev = df.groupby("hostel")["severity"].mean().rename("avg_severity")

    hostel_profile = pd.concat([diag_mix, avg_sev, total_by_hostel], axis=1).fillna(0)

    scaler = StandardScaler()
    X = scaler.fit_transform(hostel_profile)

    k = 3
    km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=20)
    labels = km.fit_predict(X)
    sil = silhouette_score(X, labels)

    hostel_profile["cluster"] = labels

    cluster_totals = (
        pd.DataFrame({"hostel": df["hostel"], "cluster": df["hostel"].map(hostel_profile["cluster"])})
        .groupby("cluster")
        .size()
        .sort_index()
    )

    return hostel_profile, float(sil), cluster_totals


def build_visit_cluster(df: pd.DataFrame):
    cat_cols = ["hostel", "diagnosis", "department", "gender", "level"]
    num_cols = ["severity"]

    enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    X_cat = enc.fit_transform(df[cat_cols])
    X_num = df[num_cols].to_numpy(dtype=float)
    X = np.hstack([X_cat, X_num])

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    X2 = pca.fit_transform(Xs)

    inertias = []
    silhouettes = []
    k_values = list(range(2, 9))

    for k in k_values:
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=20)
        lbl = km.fit_predict(Xs)
        inertias.append(float(km.inertia_))
        silhouettes.append(float(silhouette_score(Xs, lbl)))

    k_final = 4
    km4 = KMeans(n_clusters=k_final, random_state=RANDOM_STATE, n_init=20)
    labels4 = km4.fit_predict(Xs)
    sil4 = silhouette_score(Xs, labels4)
    label_names = np.array([MODEL_B_CLUSTER_LABELS[int(x)] for x in labels4])

    plt.figure(figsize=(10, 4.6))
    plt.plot(k_values, inertias, marker="o", label="Inertia (Elbow)")
    plt.plot(k_values, silhouettes, marker="s", label="Silhouette")
    plt.axvline(k_final, color="red", linestyle="--", linewidth=1.2, label="Chosen K=4")
    plt.title("K Selection Diagnostics for Visit-Level K-Means")
    plt.xlabel("Number of clusters (K)")
    plt.ylabel("Score")
    plt.grid(alpha=0.2)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "cluster_k_selection_curve.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8.4, 6.2))
    color_map = {
        0: "#1f77b4",
        1: "#d62728",
        2: "#2ca02c",
        3: "#9467bd",
    }
    for cluster_id in sorted(MODEL_B_CLUSTER_LABELS.keys()):
        mask = labels4 == cluster_id
        plt.scatter(
            X2[mask, 0],
            X2[mask, 1],
            s=13,
            alpha=0.55,
            color=color_map[cluster_id],
            label=f"{cluster_id} - {MODEL_B_CLUSTER_LABELS[cluster_id]}",
        )
    plt.title("Model B Clusters in PCA Space (K=4)")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.grid(alpha=0.15)
    plt.legend(loc="best", fontsize=8, frameon=True)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "cluster_model_b_pca_scatter.png", dpi=200)
    plt.close()

    cluster_counts = (
        pd.Series(label_names).value_counts().sort_index().to_dict()
    )

    return float(sil4), {k: int(v) for k, v in cluster_counts.items()}


def build_forecast(df: pd.DataFrame):
    weekly = (
        df.set_index("visit_date").resample("W")
        .size()
        .reset_index(name="total_visits")
    )

    weekly["lag_1"] = weekly["total_visits"].shift(1)
    weekly["lag_2"] = weekly["total_visits"].shift(2)
    weekly["lag_3"] = weekly["total_visits"].shift(3)
    weekly["rolling_mean_4"] = weekly["total_visits"].rolling(4).mean()

    weekly["month"] = weekly["visit_date"].dt.month
    weekly["weekofyear"] = weekly["visit_date"].dt.isocalendar().week.astype(int)

    weekly["month_sin"] = np.sin(2 * np.pi * weekly["month"] / 12)
    weekly["month_cos"] = np.cos(2 * np.pi * weekly["month"] / 12)
    weekly["week_sin"] = np.sin(2 * np.pi * weekly["weekofyear"] / 52)
    weekly["week_cos"] = np.cos(2 * np.pi * weekly["weekofyear"] / 52)

    model_df = weekly.dropna().reset_index(drop=True)

    feature_cols = [
        "lag_1", "lag_2", "lag_3", "rolling_mean_4",
        "month_sin", "month_cos", "week_sin", "week_cos",
    ]

    X = model_df[feature_cols]
    y = model_df["total_visits"]

    split_idx = int(len(model_df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    d_test = model_df["visit_date"].iloc[split_idx:]

    sc = StandardScaler()
    X_train_sc = sc.fit_transform(X_train)
    X_test_sc = sc.transform(X_test)

    lr = LinearRegression()
    lr.fit(X_train_sc, y_train)
    pred_lr = lr.predict(X_test_sc)

    rf = RandomForestRegressor(
        n_estimators=250,
        max_depth=10,
        min_samples_split=4,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)
    pred_rf = rf.predict(X_test)

    metrics = {
        "lr": {
            "mae": float(mean_absolute_error(y_test, pred_lr)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, pred_lr))),
            "r2": float(r2_score(y_test, pred_lr)),
        },
        "rf": {
            "mae": float(mean_absolute_error(y_test, pred_rf)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, pred_rf))),
            "r2": float(r2_score(y_test, pred_rf)),
        },
        "rows": int(len(model_df)),
        "split_train": int(split_idx),
        "split_test": int(len(model_df) - split_idx),
    }

    tscv = TimeSeriesSplit(n_splits=5)
    cv_mae = -cross_val_score(rf, X, y, cv=tscv, scoring="neg_mean_absolute_error")
    cv_rmse = -cross_val_score(rf, X, y, cv=tscv, scoring="neg_root_mean_squared_error")
    cv_r2 = cross_val_score(rf, X, y, cv=tscv, scoring="r2")

    metrics["rf_cv"] = {
        "mae_mean": float(cv_mae.mean()),
        "mae_std": float(cv_mae.std()),
        "rmse_mean": float(cv_rmse.mean()),
        "rmse_std": float(cv_rmse.std()),
        "r2_mean": float(cv_r2.mean()),
        "r2_std": float(cv_r2.std()),
    }

    plt.figure(figsize=(12, 4.8))
    plt.plot(d_test, y_test.values, marker="o", linewidth=1.6, label="Actual")
    plt.plot(d_test, pred_rf, marker="s", linewidth=1.6, label="Predicted (Random Forest)")
    plt.title("Actual vs Predicted Weekly Visits (Holdout)")
    plt.xlabel("Week")
    plt.ylabel("Weekly Visits")
    plt.grid(alpha=0.2)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "forecast_actual_vs_predicted_rf.png", dpi=200)
    plt.close()

    return metrics


def main() -> None:
    df = generate_dataset().copy()
    df["visit_date"] = pd.to_datetime(df["visit_date"])

    make_eda_figures(df)

    _, hostel_sil, cluster_counts = build_hostel_cluster(df)
    visit_sil, visit_cluster_counts = build_visit_cluster(df)
    forecast_metrics = build_forecast(df)

    summary = {
        "record_count": int(len(df)),
        "weekly_periods": int(df.set_index("visit_date").resample("W").size().shape[0]),
        "model_a": {
            "k": 3,
            "silhouette": hostel_sil,
            "cluster_counts": {str(k): int(v) for k, v in cluster_counts.to_dict().items()},
        },
        "model_b": {
            "k": 4,
            "silhouette": visit_sil,
            "cluster_label_map": {str(k): v for k, v in MODEL_B_CLUSTER_LABELS.items()},
            "cluster_counts": visit_cluster_counts,
        },
        "forecast": forecast_metrics,
        "library_versions": {
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "scikit_learn": __import__("sklearn").__version__,
            "matplotlib": __import__("matplotlib").__version__,
        },
    }

    with open(OUT_DIR / "metrics_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Report assets generated in:", OUT_DIR.resolve())
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
