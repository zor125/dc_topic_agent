import sqlite3
from typing import Iterable

DB_PATH = "data/cache.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS seen_posts(
        doc_id INTEGER PRIMARY KEY,
        first_seen_at TEXT,
        last_seen_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def is_seen(doc_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM seen_posts WHERE doc_id=?", (doc_id,))
    row = cur.fetchone()
    conn.close()
    return row is not None

def mark_seen(doc_ids: Iterable[int], now_iso: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for doc_id in doc_ids:
        cur.execute("""
        INSERT INTO seen_posts(doc_id, first_seen_at, last_seen_at)
        VALUES(?,?,?)
        ON CONFLICT(doc_id) DO UPDATE SET last_seen_at=excluded.last_seen_at
        """, (doc_id, now_iso, now_iso))
    conn.commit()
    conn.close()
