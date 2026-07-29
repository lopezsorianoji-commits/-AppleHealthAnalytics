"""Export SQLite tables to CSV files."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

from applehealth.constants import (
    ACTIVE_ENERGY_CSV,
    HEART_RATE_CSV,
    HRV_CSV,
    STEPS_CSV,
    WORKOUTS_CSV,
)

EXPORTS: tuple[tuple[str, str], ...] = (
    ("heart_rate", HEART_RATE_CSV),
    ("hrv", HRV_CSV),
    ("workouts", WORKOUTS_CSV),
    ("step_count", STEPS_CSV),
    ("active_energy", ACTIVE_ENERGY_CSV),
)


def _export_table(
    connection: sqlite3.Connection,
    table: str,
    output_path: Path,
) -> int:
    cursor = connection.execute(f"SELECT * FROM {table} ORDER BY start_date, id")
    rows = cursor.fetchall()
    if not rows:
        output_path.write_text("", encoding="utf-8")
        return 0

    fieldnames = rows[0].keys()
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))
    return len(rows)


def export_all_csv(connection: sqlite3.Connection, output_dir: Path) -> dict[str, int]:
    """Write all metric tables to CSV and return row counts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for table, filename in EXPORTS:
        path = output_dir / filename
        counts[filename] = _export_table(connection, table, path)
    return counts
