"""Batch insert operations for parsed health records."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from applehealth.association.result import AssociationResult
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


@dataclass(frozen=True)
class HealthRecordReference:
    """Referencia persistida a una medición de salud en SQLite."""

    health_record_table: str
    health_record_id: int


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
        self._pending_workouts: list[WorkoutRecord] = []
        self._pending_quantity: dict[str, list[HealthRecord]] = {
            table: [] for table in ("heart_rate", "hrv", "step_count", "active_energy")
        }
        self._workout_db_ids: dict[int, int] = {}
        self._health_record_refs: dict[int, tuple[str, int]] = {}

    def add_quantity(self, table: str, record: HealthRecord) -> None:
        """Queue a quantity record (heart rate, HRV, steps, energy)."""
        self._pending_quantity[table].append(record)
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
        self._pending_workouts.append(record)
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

    def save_associations(self, associations: list[AssociationResult]) -> None:
        """Persist workout-to-health-record associations."""
        rows: list[tuple[int, str, int]] = []
        for association in associations:
            workout_id = self._workout_db_ids[id(association.workout)]
            for record in association.records:
                health_record_table, health_record_id = self._health_record_refs[id(record)]
                rows.append((workout_id, health_record_table, health_record_id))
        if not rows:
            return
        self._connection.executemany(
            "INSERT INTO workout_health_record "
            "(workout_id, health_record_table, health_record_id) VALUES (?, ?, ?)",
            rows,
        )
        self._connection.commit()

    def get_associated_health_records(
        self,
        workout_id: int,
    ) -> list[HealthRecordReference]:
        """Return persisted health record references associated with a workout."""
        rows = self._connection.execute(
            "SELECT health_record_table, health_record_id "
            "FROM workout_health_record "
            "WHERE workout_id = ? "
            "ORDER BY health_record_table, health_record_id",
            (workout_id,),
        ).fetchall()
        return [
            HealthRecordReference(
                health_record_table=row[0],
                health_record_id=row[1],
            )
            for row in rows
        ]

    def _flush_table(self, table: str) -> None:
        buffer = self._buffers[table]
        if not buffer:
            return
        row_count = len(buffer)
        if table == "workouts":
            entities = self._pending_workouts[:row_count]
            del self._pending_workouts[:row_count]
        else:
            entities = self._pending_quantity[table][:row_count]
            del self._pending_quantity[table][:row_count]
        if table == "workouts":
            columns = ", ".join(WORKOUT_COLUMNS)
            placeholders = ", ".join("?" for _ in WORKOUT_COLUMNS)
        else:
            columns = ", ".join(QUANTITY_COLUMNS)
            placeholders = ", ".join("?" for _ in QUANTITY_COLUMNS)
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        last_id = self._connection.execute(
            f"SELECT COALESCE(MAX(id), 0) FROM {table}"
        ).fetchone()[0]
        self._connection.executemany(sql, buffer)
        new_ids = self._connection.execute(
            f"SELECT id FROM {table} WHERE id > ? ORDER BY id",
            (last_id,),
        ).fetchall()
        if table == "workouts":
            for entity, (row_id,) in zip(entities, new_ids, strict=True):
                self._workout_db_ids[id(entity)] = row_id
        else:
            for entity, (row_id,) in zip(entities, new_ids, strict=True):
                self._health_record_refs[id(entity)] = (table, row_id)
        buffer.clear()
