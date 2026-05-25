import os
import sqlite3
from config import DB_PATH, DEFAULT_CATEGORIES


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'INR',
            amount_in_inr REAL NOT NULL,
            description TEXT,
            category_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)

    # Migration: add currency and amount_in_inr columns if missing
    columns = [row[1] for row in cursor.execute("PRAGMA table_info(expenses)").fetchall()]
    if "currency" not in columns:
        cursor.execute("ALTER TABLE expenses ADD COLUMN currency TEXT NOT NULL DEFAULT 'INR'")
    if "amount_in_inr" not in columns:
        cursor.execute("ALTER TABLE expenses ADD COLUMN amount_in_inr REAL")
        cursor.execute("UPDATE expenses SET amount_in_inr = amount WHERE amount_in_inr IS NULL")

    for cat in DEFAULT_CATEGORIES:
        cursor.execute(
            "INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,)
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_db()
    print("Database initialized successfully.")
