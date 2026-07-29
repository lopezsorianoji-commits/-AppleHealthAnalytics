"""Resolución de conflictos entre múltiples entrenamientos candidatos."""

from __future__ import annotations

from collections.abc import Sequence

from applehealth.association.result import AssociationResult
from applehealth.models import HealthRecord
from applehealth.workout import WorkoutRecord


class AssociationSelector:
    """Resuelve conflictos cuando un ``HealthRecord`` coincide con más de un ``WorkoutRecord``.

    Garantiza como máximo una asociación por ``HealthRecord``. Ante múltiples
    candidatos, selecciona la coincidencia más específica según criterio temporal.
    """

    def select(
        self,
        associations: list[AssociationResult],
    ) -> list[AssociationResult]:
        return associations


def select_best_workout(
    record: HealthRecord,
    candidates: Sequence[WorkoutRecord],
) -> WorkoutRecord | None:
    """Elige el ``WorkoutRecord`` más específico entre candidatos válidos; ``None`` si la secuencia está vacía."""
    raise NotImplementedError
