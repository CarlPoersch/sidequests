import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("sidequests.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            token TEXT NOT NULL UNIQUE,
            points INTEGER NOT NULL DEFAULT 10
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bar_id INTEGER NOT NULL,
            checked_in_at TEXT NOT NULL,
            UNIQUE(user_id, bar_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (bar_id) REFERENCES bars(id)
        )
    """)

    conn.commit()
    conn.close()


def seed_bars():
    bars = [
        ("Heart Regensburg", "heart123", 10),
        ("Murphy's Law", "murphys123", 10),
        ("Barock", "barock123", 10),
        ("Alte Filmbühne", "film123", 10),
        ("Banane", "banane123", 10),
    ]

    conn = get_connection()
    cur = conn.cursor()

    for name, token, points in bars:
        cur.execute("""
            INSERT OR IGNORE INTO bars (name, token, points)
            VALUES (?, ?, ?)
        """, (name, token, points))

    conn.commit()
    conn.close()


def get_or_create_user(username: str):
    username = username.strip()

    if not username:
        return None

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()

    if user:
        conn.close()
        return dict(user)

    created_at = datetime.utcnow().isoformat()
    cur.execute("""
        INSERT INTO users (username, created_at)
        VALUES (?, ?)
    """, (username, created_at))
    conn.commit()

    user_id = cur.lastrowid
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()

    conn.close()
    return dict(user)


def get_user_by_username(username: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()
    return dict(user) if user else None


def get_all_bars():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bars ORDER BY name")
    bars = cur.fetchall()
    conn.close()
    return [dict(bar) for bar in bars]


def create_checkin(user_id: int, bar_id: int):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO checkins (user_id, bar_id, checked_in_at)
            VALUES (?, ?, ?)
        """, (user_id, bar_id, datetime.utcnow().isoformat()))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False

    conn.close()
    return success


def get_bar_by_token(token: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bars WHERE token = ?", (token,))
    bar = cur.fetchone()
    conn.close()
    return dict(bar) if bar else None


def get_checked_in_bar_ids_for_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT bar_id
        FROM checkins
        WHERE user_id = ?
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [row["bar_id"] for row in rows]


def get_score_for_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COALESCE(SUM(b.points), 0) AS total_score
        FROM checkins c
        JOIN bars b ON c.bar_id = b.id
        WHERE c.user_id = ?
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    return row["total_score"] if row else 0


def get_leaderboard():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            u.username,
            COALESCE(SUM(b.points), 0) AS score,
            COUNT(c.id) AS bars_visited
        FROM users u
        LEFT JOIN checkins c ON u.id = c.user_id
        LEFT JOIN bars b ON c.bar_id = b.id
        GROUP BY u.id, u.username
        ORDER BY score DESC, bars_visited DESC, u.username ASC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]