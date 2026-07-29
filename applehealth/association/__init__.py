"""Asociación temporal entre entrenamientos y mediciones de salud."""

from applehealth.association.filter import (
    EligibilityFilter,
    filter_eligible_records,
    filter_eligible_workouts,
)
from applehealth.association.matcher import TemporalMatcher, is_contained
from applehealth.association.result import AssociationResult
from applehealth.association.selector import AssociationSelector, select_best_workout
from applehealth.association.service import AssociationService, associate

__all__ = [
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
