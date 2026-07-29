"""SQLite schema definitions."""

from __future__ import annotations

import sqlite3

QUANTITY_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS {table} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT,
    source_version TEXT,
    device TEXT,
    creation_date TEXT,
    start_date TEXT,
    end_date TEXT,
    value REAL,
    unit TEXT
);
"""

WORKOUTS_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_activity_type TEXT,
    duration REAL,
    duration_unit TEXT,
    source_name TEXT,
    source_version TEXT,
    device TEXT,
    creation_date TEXT,
    start_date TEXT,
    end_date TEXT,
    total_distance REAL,
    total_distance_unit TEXT,
    total_energy_burned REAL,
    total_energy_burned_unit TEXT
);
"""

WORKOUT_HEALTH_RECORD_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS workout_health_record (
    workout_id INTEGER NOT NULL,
    health_record_id INTEGER NOT NULL,
    PRIMARY KEY (workout_id, health_record_id)
);
"""

QUANTITY_TABLES = ("heart_rate", "hrv", "step_count", "active_energy")
DATE_INDEX_COLUMNS = ("start_date", "end_date", "creation_date")


def _create_date_indexes(cursor: sqlite3.Cursor, table: str) -> None:
    for column in DATE_INDEX_COLUMNS:
        cursor.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{table}_{column} ON {table}({column});"
        )


def create_schema(connection: sqlite3.Connection) -> None:
    """Create all required tables and indexes."""
    cursor = connection.cursor()
    for table in QUANTITY_TABLES:
        cursor.execute(QUANTITY_TABLE_DDL.format(table=table))
        _create_date_indexes(cursor, table)
    cursor.execute(WORKOUTS_TABLE_DDL)
    _create_date_indexes(cursor, "workouts")
    cursor.execute(WORKOUT_HEALTH_RECORD_TABLE_DDL)
    connection.commit()
