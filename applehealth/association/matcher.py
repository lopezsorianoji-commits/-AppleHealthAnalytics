"""Evaluación de contención temporal entre entidades de dominio."""

from __future__ import annotations

from applehealth.models import HealthRecord
from applehealth.workout import WorkoutRecord


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
