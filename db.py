import sqlite3
import csv
import pandas as pd
import os

DB_NAME = "database.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        group_name TEXT,
        dataset INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        block_id INTEGER,
        task_id INTEGER,
        answer TEXT,
        correct INTEGER,
        code TEXT,
        timestamp TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        selected_count INTEGER
    )
    """)

    conn.commit()
    conn.close()


# 🔥 FIX: гарантированная инициализация БД
def ensure_initialized():
    if not os.path.exists(DB_NAME):
        init_db()
        load_students_from_csv("data/students.csv")
        load_datasets()


def load_students_from_csv(file_path: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students")

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            cursor.execute("""
                INSERT INTO students (name, group_name, dataset)
                VALUES (?, ?, NULL)
            """, (row["name"], row["group_name"]))

    conn.commit()
    conn.close()


def get_all_students():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, group_name, dataset FROM students")
    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "name": row[1],
            "group": row[2],
            "dataset": row[3]
        }
        for row in rows
    ]


def load_datasets():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM datasets")

    datasets = [
        "dataset1.csv",
        "dataset2.csv",
        "dataset3.csv"
    ]

    for name in datasets:
        cursor.execute("""
            INSERT INTO datasets (name, selected_count)
            VALUES (?, 0)
        """, (name,))

    conn.commit()
    conn.close()


def get_all_datasets():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, selected_count FROM datasets")
    rows = cursor.fetchall()

    conn.close()

    return [
        {"id": r[0], "name": r[1], "count": r[2]}
        for r in rows
    ]


def assign_dataset(student_id: int, dataset_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    # проверка студента
    cursor.execute("SELECT dataset FROM students WHERE id=?", (student_id,))
    student_row = cursor.fetchone()

    if student_row is None:
        conn.close()
        return {"success": False, "error": "student not found"}

    if student_row[0] is not None:
        conn.close()
        return {"success": False, "error": "dataset already selected"}

    # проверка датасета
    cursor.execute("SELECT selected_count FROM datasets WHERE id=?", (dataset_id,))
    dataset_row = cursor.fetchone()

    if dataset_row is None:
        conn.close()
        return {"success": False, "error": "dataset not found"}

    if dataset_row[0] >= 5:
        conn.close()
        return {"success": False, "error": "limit reached"}

    # назначение датасета
    cursor.execute("""
        UPDATE students
        SET dataset = ?
        WHERE id = ?
    """, (dataset_id, student_id))

    cursor.execute("""
        UPDATE datasets
        SET selected_count = selected_count + 1
        WHERE id = ?
    """, (dataset_id,))

    conn.commit()
    conn.close()

    return {"success": True}


def get_student_dataset(student_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT dataset FROM students WHERE id=?", (student_id,))
    row = cursor.fetchone()

    if row is None or row[0] is None:
        conn.close()
        return None

    dataset_id = row[0]

    cursor.execute("SELECT name FROM datasets WHERE id=?", (dataset_id,))
    dataset_row = cursor.fetchone()

    conn.close()

    if dataset_row is None:
        return None

    dataset_name = dataset_row[0]
    file_path = f"data/{dataset_name}"

    try:
        df = pd.read_csv(file_path)
        return df
    except Exception:
        return None