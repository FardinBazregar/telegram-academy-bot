# database.py
import sqlite3
import os

# Use project-relative data directory so DB is always in repo folder
BASE_DIR = os.path.dirname(__file__)
DB_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DB_DIR, "students.db")


def ensure_data_dir():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)


def connect():
    ensure_data_dir()
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        name TEXT,
        class_day TEXT,
        start_time TEXT,
        end_time TEXT,
        level TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level TEXT,
        content TEXT,
        tags TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_code TEXT,
        exercise_id INTEGER,
        status TEXT,
        date TEXT
    );
    """)

    conn.commit()
    conn.close()

# ----- Operations -----


def add_student(code, name, day, start, end, level="beginner"):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO students (code, name, class_day, start_time, end_time, level)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (code, name, day, start, end, level))
    conn.commit()
    conn.close()


def get_student_by_code(code):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, code, name, class_day, start_time, end_time, level FROM students WHERE code = ?", (code,))
    row = cur.fetchone()
    conn.close()
    return row


def get_students_by_day(day):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, code, name, class_day, start_time, end_time, level FROM students WHERE class_day = ?", (day,))
    rows = cur.fetchall()
    conn.close()
    return rows
