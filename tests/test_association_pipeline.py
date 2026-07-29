"""Tests for the association module end-to-end flow."""

from __future__ import annotations

from datetime import datetime

from applehealth.association.filter import TemporalFilter
from applehealth.association.matcher import AssociationMatcher
from applehealth.association.selector import AssociationSelector
from applehealth.association.service import AssociationService
from applehealth.models import HealthRecord
from applehealth.workout import WorkoutRecord


def test_association_pipeline_filters_records_by_temporal_overlap() -> None:
    workout = WorkoutRecord(
        fecha_inicio=datetime(2026, 7, 1, 8, 0),
        fecha_fin=datetime(2026, 7, 1, 8, 30),
    )
    record_inside = HealthRecord(
        fecha_inicio=datetime(2026, 7, 1, 8, 10),
        fecha_fin=datetime(2026, 7, 1, 8, 15),
    )
    record_outside = HealthRecord(
        fecha_inicio=datetime(2026, 7, 1, 9, 0),
        fecha_fin=datetime(2026, 7, 1, 9, 5),
    )

    temporal_filter = TemporalFilter()
    association_service = AssociationService(temporal_filter)
    association_selector = AssociationSelector()
    association_matcher = AssociationMatcher(association_service, association_selector)

    results = association_matcher.match(
        [workout],
        [record_inside, record_outside],
    )

    assert len(results) == 1
    assert results[0].workout is workout
    assert results[0].records == [record_inside]
