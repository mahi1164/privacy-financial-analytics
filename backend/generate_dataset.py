import pandas as pd
import random
from datetime import datetime, timedelta

names = ["Rahul Sharma", "Priya Verma", "Amit Singh", "Sneha Patel", "Arjun Mehta"]
cities = ["Delhi", "Mumbai", "Bhopal", "Indore", "Pune"]
merchants = ["Amazon", "Flipkart", "Swiggy", "Zomato", "Uber", "ATM"]

data = []

for i in range(3000):
    name = random.choice(names)
    account_number = str(random.randint(100000000000, 999999999999))
    location = random.choice(cities)
    
    timestamp = datetime.now() - timedelta(days=random.randint(0, 365))
    
    amount = round(random.uniform(10, 50000), 2)
    transaction_type = random.choice(["debit", "credit"])
    merchant = random.choice(merchants)

    # Simple fraud logic
    is_fraud = 1 if amount > 20000 and random.random() > 0.7 else 0

    data.append([
        f"TXN{i+1}",
        name,
        account_number,
        location,
        timestamp,
        amount,
        transaction_type,
        merchant,
        is_fraud
    ])

df = pd.DataFrame(data, columns=[
    "transaction_id",
    "name",
    "account_number",
    "location",
    "timestamp",
    "amount",
    "transaction_type",
    "merchant",
    "is_fraud"
])

df.to_csv("../data/raw_transactions.csv", index=False)

print("✅ Raw dataset created (no Faker needed)")