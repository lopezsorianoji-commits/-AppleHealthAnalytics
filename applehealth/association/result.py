"""Contrato de salida del módulo de asociación."""

from __future__ import annotations

from dataclasses import dataclass

from applehealth.models import HealthRecord
from applehealth.workout import WorkoutRecord


@dataclass
class AssociationResult:
    """Representa el resultado de una asociación entre un entrenamiento y los registros de salud candidatos."""

    workout: WorkoutRecord
    records: list[HealthRecord]
