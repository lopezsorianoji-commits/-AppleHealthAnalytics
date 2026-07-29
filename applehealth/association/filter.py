"""Filtrado de elegibilidad para el proceso de asociación."""

from __future__ import annotations

from collections.abc import Sequence

from applehealth.models import HealthRecord
from applehealth.workout import WorkoutRecord


class EligibilityFilter:
    """Descarta entidades sin ``fecha_inicio`` y ``fecha_fin`` definidos.

    Excluye entidades con fechas ausentes antes de evaluar asociaciones.
    No infiere ni completa fechas faltantes.
    """


def _overlap(
    workout: WorkoutRecord,
    record: HealthRecord,
) -> bool:
    return (
        record.fecha_fin >= workout.fecha_inicio
        and record.fecha_inicio <= workout.fecha_fin
    )


class TemporalFilter:
    """Filtra mediciones de salud respecto al intervalo temporal de un entrenamiento.

    Recibe un ``WorkoutRecord`` y una lista de ``HealthRecord``, y devuelve
    únicamente las mediciones elegibles para asociarse con ese entrenamiento
    según el criterio temporal del módulo v0.1.
    """

    def filter(
        self,
        workout: WorkoutRecord,
        records: list[HealthRecord],
    ) -> list[HealthRecord]:
        return [
            record
            for record in records
            if _overlap(workout, record)
        ]


def filter_eligible_workouts(
    workouts: Sequence[WorkoutRecord],
) -> list[WorkoutRecord]:
    """Devuelve workouts con ``fecha_inicio`` y ``fecha_fin`` definidos."""
    raise NotImplementedError


def filter_eligible_records(
    records: Sequence[HealthRecord],
) -> list[HealthRecord]:
    """Devuelve ``HealthRecord`` con ``fecha_inicio`` y ``fecha_fin`` definidos."""
    raise NotImplementedError
