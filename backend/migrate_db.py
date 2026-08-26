"""Database schema upgrade script to add new columns to reports table and create new tables."""
import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent.parent / "data" / "insightflow.db"
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get existing columns in reports table
cursor.execute("PRAGMA table_info(reports);")
columns = [row[1] for row in cursor.fetchall()]

new_columns = [
    ("reporting_period_name", "VARCHAR(100)"),
    ("version", "INTEGER DEFAULT 1"),
    ("parent_report_id", "INTEGER"),
    ("generated_by", "VARCHAR(100)"),
    ("generated_at", "DATETIME"),
    ("submitted_to", "VARCHAR(100)"),
    ("submitted_at", "DATETIME"),
    ("reviewed_by", "VARCHAR(100)"),
    ("reviewed_at", "DATETIME"),
    ("approved_by", "VARCHAR(100)"),
    ("approved_at", "DATETIME"),
    ("approval_comment", "TEXT"),
    ("rejected_by", "VARCHAR(100)"),
    ("rejected_at", "DATETIME"),
    ("rejection_reason", "TEXT"),
    ("rejection_feedback", "TEXT"),
    ("validation_status", "VARCHAR(30) DEFAULT 'PASS'"),
    ("validation_result", "JSON"),
    ("report_snapshot", "JSON"),
    ("kpi_snapshot", "JSON"),
    ("updated_at", "DATETIME"),
]

for col_name, col_type in new_columns:
    if col_name not in columns:
        print(f"Adding column {col_name} to reports table...")
        try:
            cursor.execute(f"ALTER TABLE reports ADD COLUMN {col_name} {col_type};")
        except Exception as e:
            print(f"Error adding {col_name}: {e}")

# Create notifications table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_role VARCHAR(50) NOT NULL,
    recipient_user_id INTEGER,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    report_id INTEGER,
    is_read BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    read_at DATETIME
);
""")

# Create audit_logs table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user VARCHAR(100) NOT NULL,
    role VARCHAR(50),
    report_id INTEGER,
    report_version INTEGER,
    action VARCHAR(100) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    comment TEXT,
    details TEXT,
    category VARCHAR(50) DEFAULT 'General'
);
""")

conn.commit()
conn.close()
print("Database schema successfully upgraded!")
