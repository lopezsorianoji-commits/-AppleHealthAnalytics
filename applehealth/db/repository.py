"""Batch insert operations for parsed health records."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any

from applehealth.models import HealthRecord
from applehealth.workout import WorkoutRecord

QUANTITY_COLUMNS = (
    "source_name",
    "source_version",
    "device",
    "creation_date",
    "start_date",
    "end_date",
    "value",
    "unit",
)

WORKOUT_COLUMNS = (
    "workout_activity_type",
    "duration",
    "duration_unit",
    "source_name",
    "source_version",
    "device",
    "creation_date",
    "start_date",
    "end_date",
    "total_distance",
    "total_distance_unit",
    "total_energy_burned",
    "total_energy_burned_unit",
)

_QUANTITY_ATTR_MAP: dict[str, str] = {
    "source_name": "fuente_origen",
    "device": "dispositivo",
    "creation_date": "fecha_creacion",
    "start_date": "fecha_inicio",
    "end_date": "fecha_fin",
    "value": "valor",
    "unit": "unidad_medida",
}


def _quantity_column_value(record: HealthRecord, column: str) -> Any:
    attr = _QUANTITY_ATTR_MAP.get(column)
    if attr is not None:
        value = getattr(record, attr)
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S %z")
        return value
    return getattr(record, column, record.metadatos.get(column))


_WORKOUT_ATTR_MAP: dict[str, str] = {
    "workout_activity_type": "tipo_actividad",
    "duration": "duracion",
    "duration_unit": "unidad_duracion",
    "source_name": "fuente_origen",
    "device": "dispositivo",
    "creation_date": "fecha_creacion",
    "start_date": "fecha_inicio",
    "end_date": "fecha_fin",
    "total_distance": "distancia_total",
    "total_distance_unit": "unidad_distancia",
    "total_energy_burned": "energia_total",
    "total_energy_burned_unit": "unidad_energia",
}


def _workout_column_value(record: WorkoutRecord, column: str) -> Any:
    attr = _WORKOUT_ATTR_MAP.get(column)
    if attr is not None:
        value = getattr(record, attr)
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S %z")
        return value
    meta_key = "sourceVersion" if column == "source_version" else column
    return getattr(record, column, record.metadatos.get(meta_key))


class RecordRepository:
    """Accumulates records and flushes them to SQLite in batches."""

    def __init__(self, connection: sqlite3.Connection, batch_size: int = 5_000) -> None:
        self._connection = connection
        self._batch_size = batch_size
        self._buffers: dict[str, list[tuple[Any, ...]]] = {
            "heart_rate": [],
            "hrv": [],
            "step_count": [],
            "active_energy": [],
            "workouts": [],
        }
        self.counts: dict[str, int] = {key: 0 for key in self._buffers}

    def add_quantity(self, table: str, record: HealthRecord) -> None:
        """Queue a quantity record (heart rate, HRV, steps, energy)."""
        row = tuple(
            _quantity_column_value(record, column)
            for column in QUANTITY_COLUMNS
        )
        self._buffers[table].append(row)
        self.counts[table] += 1
        if len(self._buffers[table]) >= self._batch_size:
            self._flush_table(table)

    def add_workout(self, record: WorkoutRecord) -> None:
        """Queue a workout record."""
        row = tuple(
            _workout_column_value(record, column)
            for column in WORKOUT_COLUMNS
        )
        self._buffers["workouts"].append(row)
        self.counts["workouts"] += 1
        if len(self._buffers["workouts"]) >= self._batch_size:
            self._flush_table("workouts")

    def flush_all(self) -> None:
        """Persist all buffered records in a single transaction."""
        for table in self._buffers:
            self._flush_table(table)
        self._connection.commit()

    def _flush_table(self, table: str) -> None:
        buffer = self._buffers[table]
        if not buffer:
            return
        if table == "workouts":
            columns = ", ".join(WORKOUT_COLUMNS)
            placeholders = ", ".join("?" for _ in WORKOUT_COLUMNS)
        else:
            columns = ", ".join(QUANTITY_COLUMNS)
            placeholders = ", ".join("?" for _ in QUANTITY_COLUMNS)
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self._connection.executemany(sql, buffer)
        buffer.clear()
