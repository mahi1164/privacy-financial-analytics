import os
import sqlite3


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database(reset=False):
    connection = get_connection()
    cursor = connection.cursor()

    if reset:
        cursor.execute("DROP TABLE IF EXISTS transactions")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anonymous_id TEXT NOT NULL,
            noisy_amount REAL NOT NULL,
            category TEXT NOT NULL,
            cluster TEXT,
            is_positive INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    connection.commit()
    connection.close()
    return DB_PATH


if __name__ == "__main__":
    path = init_database(reset=True)
    print(f"Initialized database at {path}")
