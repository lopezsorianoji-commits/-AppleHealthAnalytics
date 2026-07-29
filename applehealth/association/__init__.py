"""Asociación temporal entre entrenamientos y mediciones de salud."""

from __future__ import annotations

from applehealth.association.filter import (
    EligibilityFilter,
    TemporalFilter,
    filter_eligible_records,
    filter_eligible_workouts,
)
from applehealth.association.matcher import AssociationMatcher, TemporalMatcher, is_contained
from applehealth.association.result import AssociationResult
from applehealth.association.selector import AssociationSelector, select_best_workout
from applehealth.association.service import AssociationService, associate
from applehealth.models import HealthRecord
from applehealth.workout import WorkoutRecord


class AssociationFacade:
    """Punto de entrada del módulo de asociación."""

    def __init__(self) -> None:
        temporal_filter = TemporalFilter()
        association_service = AssociationService(temporal_filter)
        association_selector = AssociationSelector()
        self._matcher = AssociationMatcher(association_service, association_selector)

    def associate(
        self,
        workouts: list[WorkoutRecord],
        records: list[HealthRecord],
    ) -> list[AssociationResult]:
        return self._matcher.match(workouts, records)


__all__ = [
    "AssociationFacade",
    "AssociationResult",
    "AssociationSelector",
    "AssociationService",
    "EligibilityFilter",
    "TemporalMatcher",
    "associate",
    "filter_eligible_records",
    "filter_eligible_workouts",
    "is_contained",
    "select_best_workout",
]
