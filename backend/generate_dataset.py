import os
import random
from datetime import datetime, timedelta

import pandas as pd


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "data")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "raw_transactions.csv")
RANDOM_SEED = 2026
DEFAULT_USER_COUNT = 500


PROFILES = {
    "low_spender": {
        "amount_range": (40, 280),
        "transaction_count_range": (30, 40),
        "merchants": ["Local Shop", "Grocery", "Coffee"],
        "transaction_types": ["debit", "debit", "debit", "credit"],
        "fraud_chance": 0.01,
    },
    "food_lover": {
        "amount_range": (120, 850),
        "transaction_count_range": (24, 36),
        "merchants": ["Swiggy", "Zomato"],
        "transaction_types": ["debit", "debit", "debit", "credit"],
        "fraud_chance": 0.02,
    },
    "traveler": {
        "amount_range": (250, 6500),
        "transaction_count_range": (20, 32),
        "merchants": ["Uber", "Train", "Flight"],
        "transaction_types": ["debit", "debit", "debit", "credit"],
        "fraud_chance": 0.03,
    },
    "high_spender": {
        "amount_range": (4000, 32000),
        "transaction_count_range": (20, 30),
        "merchants": ["Amazon", "Electronics"],
        "transaction_types": ["debit", "debit", "credit"],
        "fraud_chance": 0.08,
    },
}


def build_users(rng):
    user_count = DEFAULT_USER_COUNT
    profile_names = list(PROFILES.keys())
    cities = ["Delhi", "Mumbai", "Bhopal", "Indore", "Pune", "Bengaluru", "Hyderabad"]
    users = []

    for index in range(1, user_count + 1):
        profile_name = profile_names[(index - 1) % len(profile_names)]
        users.append(
            {
                "name": f"user_{index:03d}",
                "profile": profile_name,
                "account_number": str(rng.randint(100000000000, 999999999999)),
                "location": rng.choice(cities),
            }
        )

    rng.shuffle(users)
    return users


def generate_dataset():
    rng = random.Random(RANDOM_SEED)
    users = build_users(rng)
    now = datetime.now()
    rows = []
    transaction_number = 1

    for user in users:
        profile = PROFILES[user["profile"]]
        transaction_total = rng.randint(*profile["transaction_count_range"])

        for _ in range(transaction_total):
            timestamp = now - timedelta(
                days=rng.randint(0, 120),
                hours=rng.randint(0, 23),
                minutes=rng.randint(0, 59),
            )
            amount = round(rng.uniform(*profile["amount_range"]), 2)
            merchant = rng.choice(profile["merchants"])
            transaction_type = rng.choice(profile["transaction_types"])
            is_fraud = int(rng.random() < profile["fraud_chance"])

            rows.append(
                [
                    f"TXN{transaction_number:05d}",
                    user["name"],
                    user["account_number"],
                    user["location"],
                    timestamp.isoformat(sep=" "),
                    amount,
                    transaction_type,
                    merchant,
                    is_fraud,
                    user["profile"],
                ]
            )
            transaction_number += 1

    df = pd.DataFrame(
        rows,
        columns=[
            "transaction_id",
            "name",
            "account_number",
            "location",
            "timestamp",
            "amount",
            "transaction_type",
            "merchant",
            "is_fraud",
            "behavior_profile",
        ],
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(
        f"Generated {len(df)} transactions for {df['name'].nunique()} users at {OUTPUT_PATH}"
    )
    print(df["behavior_profile"].value_counts().sort_index().to_string())
    return df


if __name__ == "__main__":
    generate_dataset()
