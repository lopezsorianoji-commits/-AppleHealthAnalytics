"""Database connection helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from applehealth.db.schema import create_schema


def open_database(db_path: Path) -> sqlite3.Connection:
    """Open (or create) the SQLite database with performance-oriented pragmas."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode = WAL;")
    connection.execute("PRAGMA synchronous = NORMAL;")
    connection.execute("PRAGMA temp_store = MEMORY;")
    connection.execute("PRAGMA cache_size = -64000;")
    connection.execute("PRAGMA foreign_keys = ON;")
    create_schema(connection)
    return connection
