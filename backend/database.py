# backend/database.py
# COMPLETE & RUNNABLE - Creates SQLite database + sample privacy-preserved data
# Step 6 (now fixing the "Load Transactions" button)

import sqlite3

DB_NAME = 'database.db'

def init_database():
    """Create database, table, and insert sample noisy transactions"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create table (if not exists)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anonymous_id TEXT NOT NULL,
            noisy_amount REAL NOT NULL,
            category TEXT NOT NULL,
            cluster INTEGER,
            is_positive INTEGER
        )
    ''')
    
    # Clear old data and insert fresh sample data (privacy-preserved)
    cursor.execute("DELETE FROM transactions")
    
    sample_data = [
        ("anon_7f3k9p", 142.3, "groceries", 1, 1),
        ("anon_9x2m4q", -189.7, "rent", 0, 0),
        ("anon_a1b2c3", 75.4, "salary", 2, 1),
        ("anon_d4e5f6", 320.1, "bonus", 2, 1),
        ("anon_g7h8i9", -45.8, "transport", 0, 0),
        ("anon_j0k1l2", 12.9, "coffee", 1, 1),
        ("anon_m3n4o5", 850.0, "investment", 2, 1),
        ("anon_p6q7r8", -120.5, "shopping", 0, 0)
    ]
    
    cursor.executemany('''
        INSERT INTO transactions 
        (anonymous_id, noisy_amount, category, cluster, is_positive)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_data)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized: {DB_NAME}")
    print(f"✅ {len(sample_data)} privacy-preserved transactions loaded!")

# Run this file directly to create the database
if __name__ == "__main__":
    init_database()