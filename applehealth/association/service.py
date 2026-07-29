"""Orquestación del proceso de asociación WorkoutRecord ↔ HealthRecord."""

from __future__ import annotations

from collections.abc import Sequence

from applehealth.association.result import AssociationResult
from applehealth.models import HealthRecord
from applehealth.workout import WorkoutRecord


class AssociationService:
    """Orquestador principal del módulo de asociación.

    Recibe colecciones de entidades de dominio, coordina filtrado, matching,
    selección y construcción del resultado. Garantiza determinismo: misma
    entrada → misma salida. No accede a SQLite, parser ni repositorio.
    """


def associate(
    workouts: Sequence[WorkoutRecord],
    records: Sequence[HealthRecord],
) -> AssociationResult:
    """Ejecuta el proceso completo de asociación v0.1 y devuelve el resultado."""
    raise NotImplementedError
