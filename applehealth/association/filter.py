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
