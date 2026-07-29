"""Evaluación de contención temporal entre entidades de dominio."""

from __future__ import annotations

from applehealth.association.result import AssociationResult
from applehealth.association.selector import AssociationSelector
from applehealth.association.service import AssociationService
from applehealth.models import HealthRecord
from applehealth.workout import WorkoutRecord


class AssociationMatcher:
    """Asocia entrenamientos con mediciones de salud mediante ``AssociationService``."""

    def __init__(
        self,
        association_service: AssociationService,
        selector: AssociationSelector,
    ) -> None:
        self._association_service = association_service
        self._selector = selector

    def match(
        self,
        workouts: list[WorkoutRecord],
        records: list[HealthRecord],
    ) -> list[AssociationResult]:
        results: list[AssociationResult] = []
        for workout in workouts:
            results.append(self._association_service.associate(workout, records))
        return self._selector.select(results)


class TemporalMatcher:
    """Evalúa si un ``HealthRecord`` está contenido temporalmente dentro de un ``WorkoutRecord``.

    Aplica la regla v0.1 de contención total con límites inclusivos. No usa
    solapamiento parcial, heurísticas ni ``metadatos``.
    """


def is_contained(
    record: HealthRecord,
    workout: WorkoutRecord,
) -> bool:
    """True si el intervalo completo del ``HealthRecord`` está contenido en el ``WorkoutRecord`` (inclusivo)."""
    raise NotImplementedError
