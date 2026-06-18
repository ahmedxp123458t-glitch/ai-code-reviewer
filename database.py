import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "reviews.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id TEXT PRIMARY KEY,
            language TEXT NOT NULL,
            code TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_review(review_id: str, language: str, code: str, result: dict):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO reviews (id, language, code, result) VALUES (?, ?, ?, ?)",
        (review_id, language, code, json.dumps(result)),
    )
    conn.commit()
    conn.close()


def get_review(review_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT id, language, code, result, created_at FROM reviews WHERE id = ?",
        (review_id,),
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "id": row["id"],
        "language": row["language"],
        "code": row["code"],
        "result": json.loads(row["result"]),
        "created_at": row["created_at"],
    }
