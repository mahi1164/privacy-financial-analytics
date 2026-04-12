import hashlib
import os
import random

import pandas as pd

try:
    from .database import get_connection, init_database
except ImportError:
    from database import get_connection, init_database


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(BASE_DIR, "..", "data", "raw_transactions.csv")


def build_anonymous_id(name, account_number):
    digest = hashlib.sha256(f"{name}|{account_number}".encode("utf-8")).hexdigest()
    return f"anon_{digest[:10]}"


def build_noise(transaction_id):
    seed = int(hashlib.sha256(str(transaction_id).encode("utf-8")).hexdigest()[:12], 16)
    rng = random.Random(seed)
    return round(rng.uniform(-12, 12), 2)


def run_privacy_pipeline():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"Raw dataset not found at {INPUT_PATH}")

    raw_df = pd.read_csv(INPUT_PATH)
    init_database(reset=True)

    processed_rows = []
    for _, row in raw_df.iterrows():
        anonymous_id = build_anonymous_id(row["name"], row["account_number"])
        noisy_amount = max(1.0, round(float(row["amount"]) + build_noise(row["transaction_id"]), 2))
        category = row["merchant"]
        cluster = "Unclustered"
        is_positive = int(row.get("is_fraud", 0))

        processed_rows.append(
            (
                anonymous_id,
                noisy_amount,
                category,
                cluster,
                is_positive,
            )
        )

    connection = get_connection()
    cursor = connection.cursor()
    cursor.executemany(
        """
        INSERT INTO transactions (
            anonymous_id,
            noisy_amount,
            category,
            cluster,
            is_positive
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        processed_rows,
    )
    connection.commit()
    connection.close()

    print(
        "Stored privacy-preserved transactions:",
        f"rows={len(processed_rows)}",
        f"users={raw_df['name'].nunique()}",
        f"categories={raw_df['merchant'].nunique()}",
    )
    return len(processed_rows)


if __name__ == "__main__":
    run_privacy_pipeline()
