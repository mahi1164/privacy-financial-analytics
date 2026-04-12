import os

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

import pandas as pd
from flask import Blueprint, jsonify, request
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder, StandardScaler

try:
    from .database import DB_PATH, get_connection
    from .generate_dataset import generate_dataset
    from .privacy_pipeline import run_privacy_pipeline
except ImportError:
    from database import DB_PATH, get_connection
    from generate_dataset import generate_dataset
    from privacy_pipeline import run_privacy_pipeline


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "..", "data", "raw_transactions.csv")

FOOD_CATEGORIES = {"Swiggy", "Zomato"}
TRAVEL_CATEGORIES = {"Uber", "Train", "Flight"}
HIGH_SPEND_CATEGORIES = {"Amazon", "Electronics"}

routes = Blueprint("routes", __name__)


def bootstrap_pipeline(force_refresh=False):
    if force_refresh or not os.path.exists(DATASET_PATH):
        print("[PIPELINE] Generating raw behavior dataset")
        generate_dataset()

    dataset_is_newer = os.path.exists(DATASET_PATH) and (
        not os.path.exists(DB_PATH)
        or os.path.getmtime(DATASET_PATH) > os.path.getmtime(DB_PATH)
    )

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'"
    )
    table_exists = cursor.fetchone() is not None
    row_count = 0
    if table_exists:
        cursor.execute("SELECT COUNT(*) FROM transactions")
        row_count = cursor.fetchone()[0]
    connection.close()

    if force_refresh or dataset_is_newer or not table_exists or row_count == 0:
        print("[PIPELINE] Running privacy pipeline")
        run_privacy_pipeline()


def fetch_user_level_features(cursor):
    cursor.execute(
        """
        SELECT
            t.anonymous_id,
            AVG(t.noisy_amount) AS avg_amount,
            COUNT(*) AS transaction_count,
            (
                SELECT t2.category
                FROM transactions t2
                WHERE t2.anonymous_id = t.anonymous_id
                GROUP BY t2.category
                ORDER BY COUNT(*) DESC, t2.category ASC
                LIMIT 1
            ) AS top_category
        FROM transactions t
        GROUP BY t.anonymous_id
        ORDER BY t.anonymous_id
        """
    )
    rows = cursor.fetchall()
    return pd.DataFrame(
        rows,
        columns=["anonymous_id", "avg_amount", "transaction_count", "top_category"],
    )


def label_cluster(dominant_category, avg_amount):
    if dominant_category in FOOD_CATEGORIES:
        return "Food Lover"
    if dominant_category in TRAVEL_CATEGORIES:
        return "Traveler"
    if dominant_category in HIGH_SPEND_CATEGORIES or avg_amount >= 2500:
        return "High Spender"
    return "Low Spender"


@routes.route("/test", methods=["GET"])
def test():
    return jsonify(
        {
            "status": "healthy",
            "message": "PrivacyGuard Backend is running",
            "port": 5000,
        }
    )


@routes.route("/api/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "version": "1.0",
            "privacy": "differential-privacy-enabled",
        }
    )


@routes.route("/api/transactions", methods=["GET"])
def get_transactions():
    try:
        bootstrap_pipeline()

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT id, anonymous_id, noisy_amount, category, cluster, is_positive
            FROM transactions
            ORDER BY anonymous_id ASC, id ASC
            """
        )
        rows = [dict(row) for row in cursor.fetchall()]
        connection.close()

        return jsonify(rows)
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@routes.route("/api/analyze", methods=["POST"])
def run_analysis():
    try:
        bootstrap_pipeline()

        connection = get_connection()
        cursor = connection.cursor()
        user_df = fetch_user_level_features(cursor)

        if user_df.empty:
            connection.close()
            return jsonify({"error": "No transactions available for clustering"}), 400

        print("[CLUSTER] Clustering started")
        print(f"[CLUSTER] Users clustered: {len(user_df)}")

        encoder = LabelEncoder()
        user_df["encoded_category"] = encoder.fit_transform(user_df["top_category"])

        feature_matrix = user_df[["avg_amount", "transaction_count", "encoded_category"]]
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(feature_matrix)

        n_clusters = min(4, len(user_df))
        if n_clusters < 2:
            user_df["cluster"] = "Low Spender"
        else:
            model = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
            user_df["cluster_id"] = model.fit_predict(scaled_features)

            cluster_summary = (
                user_df.groupby("cluster_id")
                .agg(
                    avg_amount=("avg_amount", "mean"),
                    transaction_count=("transaction_count", "mean"),
                    dominant_category=("top_category", lambda values: values.mode().iloc[0]),
                )
                .reset_index()
            )
            cluster_summary["cluster_label"] = cluster_summary.apply(
                lambda row: label_cluster(row["dominant_category"], row["avg_amount"]),
                axis=1,
            )
            cluster_map = dict(
                zip(cluster_summary["cluster_id"], cluster_summary["cluster_label"])
            )
            user_df["cluster"] = user_df["cluster_id"].map(cluster_map)

        cluster_counts = user_df["cluster"].value_counts().to_dict()
        print(f"[CLUSTER] Cluster distribution: {cluster_counts}")

        for _, row in user_df.iterrows():
            cursor.execute(
                "UPDATE transactions SET cluster = ? WHERE anonymous_id = ?",
                (row["cluster"], row["anonymous_id"]),
            )

        connection.commit()
        connection.close()

        return jsonify(
            {
                "status": "success",
                "message": "User-level clustering completed",
                "users_clustered": int(len(user_df)),
                "cluster_distribution": cluster_counts,
            }
        )
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@routes.route("/api/transaction", methods=["POST"])
def add_transaction():
    data = request.get_json()
    return (
        jsonify(
            {
                "status": "added",
                "anonymous_id": "anon_" + str(hash(str(data)))[-6:],
            }
        ),
        201,
    )
