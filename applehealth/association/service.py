"""Orquestación del proceso de asociación WorkoutRecord ↔ HealthRecord."""

from __future__ import annotations

from collections.abc import Sequence

from applehealth.association.filter import TemporalFilter
from applehealth.association.result import AssociationResult
from applehealth.models import HealthRecord
from applehealth.workout import WorkoutRecord


class AssociationService:
    """Orquestador del proceso de asociación entre un entrenamiento y mediciones de salud."""

    def __init__(self, temporal_filter: TemporalFilter) -> None:
        self._temporal_filter = temporal_filter

    def associate(
        self,
        workout: WorkoutRecord,
        records: list[HealthRecord],
    ) -> AssociationResult:
        filtered_records = self._temporal_filter.filter(workout, records)
        return AssociationResult(workout=workout, records=filtered_records)


def associate(
    workouts: Sequence[WorkoutRecord],
    records: Sequence[HealthRecord],
) -> AssociationResult:
    """Ejecuta el proceso completo de asociación v0.1 y devuelve el resultado."""
    raise NotImplementedError
