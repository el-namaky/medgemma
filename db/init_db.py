"""
init_db.py — Database schema for Gemma-Health Sentinel
Creates SQLite database with 8 tables for the hospital system.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "hospital.db")


def get_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database():
    """Create all tables in the database."""
    conn = get_connection()
    cursor = conn.cursor()

    # ── جدول المرضى ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            national_id TEXT UNIQUE,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            blood_type TEXT,
            phone TEXT,
            emergency_contact TEXT
        )
    """)

    # ── جدول الأمراض المزمنة ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chronic_diseases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            disease_name TEXT NOT NULL,
            diagnosed_date TEXT,
            severity TEXT,
            notes TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        )
    """)

    # ── جدول الحساسيات ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS allergies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            allergen TEXT NOT NULL,
            reaction_type TEXT,
            severity TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        )
    """)

    # ── جدول الأدوية الحالية ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS current_medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            drug_name TEXT NOT NULL,
            dose TEXT,
            frequency TEXT,
            reason TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        )
    """)

    # ── جدول العمليات السابقة ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS surgeries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            surgery_name TEXT NOT NULL,
            surgery_date TEXT,
            notes TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        )
    """)

    # ── جدول الزيارات السابقة ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            visit_date TEXT,
            department TEXT,
            reason TEXT,
            diagnosis TEXT,
            treatment TEXT,
            doctor_notes TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        )
    """)

    # ── جدول التحاليل ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lab_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            test_name TEXT NOT NULL,
            result_value TEXT,
            normal_range TEXT,
            test_date TEXT,
            is_abnormal BOOLEAN DEFAULT 0,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        )
    """)

    # ── جدول موانع الأدوية والتفاعلات ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contraindications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_name TEXT NOT NULL,
            contraindicated_substance TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            reason TEXT,
            source TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully at:", DB_PATH)


if __name__ == "__main__":
    init_database()
