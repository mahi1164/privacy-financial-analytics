import pandas as pd
import random
import sqlite3
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(BASE_DIR, '..', 'data', 'raw_transactions.csv')
db_path = os.path.join(BASE_DIR, 'database.db')

# Load raw data
df = pd.read_csv(input_path)

processed_data = []

for _, row in df.iterrows():
    
    # 🔐 Remove name completely
    anonymous_id = f"anon_{random.randint(100000,999999)}"
    
    # 🔐 Mask account number (keep last 4 digits)
    account = str(row['account_number'])
    masked_account = "XXXX-XXXX-" + account[-4:]
    
    # 🔐 Add noise to amount
    noisy_amount = round(row['amount'] + random.uniform(-10, 10), 2)
    
    category = row['merchant']
    cluster = None
    is_positive = row['is_fraud']

    processed_data.append((
        anonymous_id,
        noisy_amount,
        category,
        cluster,
        is_positive
    ))

# Store in database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("DELETE FROM transactions")

cursor.executemany('''
    INSERT INTO transactions 
    (anonymous_id, noisy_amount, category, cluster, is_positive)
    VALUES (?, ?, ?, ?, ?)
''', processed_data)

conn.commit()
conn.close()

print(f"✅ Privacy-preserved dataset stored! Total: {len(processed_data)} rows")