"""Repository wrapper that retains parsed domain entities in memory."""

from __future__ import annotations

from applehealth.db.repository import RecordRepository
from applehealth.models import HealthRecord
from applehealth.workout import WorkoutRecord


class CollectingRepository:
    """Retiene entidades de dominio mientras delega la persistencia en SQLite."""

    def __init__(self, repository: RecordRepository) -> None:
        self._repository = repository
        self.workouts: list[WorkoutRecord] = []
        self.records: list[HealthRecord] = []

    def add_quantity(self, table: str, record: HealthRecord) -> None:
        self.records.append(record)
        self._repository.add_quantity(table, record)

    def add_workout(self, record: WorkoutRecord) -> None:
        self.workouts.append(record)
        self._repository.add_workout(record)

    def flush_all(self) -> None:
        self._repository.flush_all()

    @property
    def counts(self) -> dict[str, int]:
        return self._repository.counts
