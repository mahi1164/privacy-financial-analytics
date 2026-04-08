import pandas as pd
import sqlite3
import random
import os

# Step 1: Get file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, '..', 'data', 'creditcard.csv')
db_path = os.path.join(BASE_DIR, 'database.db')

# Step 2: Load CSV
df = pd.read_csv(csv_path)

# Step 3: Take sample (IMPORTANT - keeps project fast)
df = df.sample(2000, random_state=42)

# Step 4: Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Step 5: Clear old data
cursor.execute("DELETE FROM transactions")

# Step 6: Convert data
converted_data = []

for _, row in df.iterrows():
    anonymous_id = f"anon_{random.randint(100000,999999)}"
    
    # Add small noise (privacy)
    noisy_amount = round(row['Amount'] + random.uniform(-5, 5), 2)
    
    category = "transaction"
    cluster = None
    is_positive = int(row['Class'])  # fraud = 1

    converted_data.append((
        anonymous_id,
        noisy_amount,
        category,
        cluster,
        is_positive
    ))

# Step 7: Insert into database
cursor.executemany('''
    INSERT INTO transactions 
    (anonymous_id, noisy_amount, category, cluster, is_positive)
    VALUES (?, ?, ?, ?, ?)
''', converted_data)

conn.commit()
conn.close()

print(f"✅ Successfully loaded {len(converted_data)} real transactions into database!")