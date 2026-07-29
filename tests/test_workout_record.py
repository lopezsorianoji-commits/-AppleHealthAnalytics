"""Tests for WorkoutRecord domain entity and workout parser migration."""

from __future__ import annotations

from datetime import datetime

from applehealth.parser.stream_parser import _workout_record


def test_workout_record_returns_workout_record() -> None:
    attributes = {
        "workoutActivityType": "HKWorkoutActivityTypeRunning",
        "duration": "30",
        "durationUnit": "min",
        "sourceName": "Apple Watch",
        "sourceVersion": "10.0",
        "device": "Watch",
        "creationDate": "2026-07-01 08:30:00 -0600",
        "startDate": "2026-07-01 08:00:00 -0600",
        "endDate": "2026-07-01 08:30:00 -0600",
        "totalDistance": "5.2",
        "totalDistanceUnit": "km",
        "totalEnergyBurned": "320",
        "totalEnergyBurnedUnit": "kcal",
    }

    record = _workout_record(attributes)

    assert record.tipo_actividad == "HKWorkoutActivityTypeRunning"
    assert record.duracion == 30.0
    assert record.unidad_duracion == "min"
    assert record.fuente_origen == "Apple Watch"
    assert record.dispositivo == "Watch"
    assert record.distancia_total == 5.2
    assert record.unidad_distancia == "km"
    assert record.energia_total == 320.0
    assert record.unidad_energia == "kcal"
    assert record.metadatos == {"sourceVersion": "10.0"}
    assert record.fecha_inicio == datetime.strptime(
        "2026-07-01 08:00:00 -0600",
        "%Y-%m-%d %H:%M:%S %z",
    )
    assert record.fecha_fin == datetime.strptime(
        "2026-07-01 08:30:00 -0600",
        "%Y-%m-%d %H:%M:%S %z",
    )
    assert record.fecha_creacion == datetime.strptime(
        "2026-07-01 08:30:00 -0600",
        "%Y-%m-%d %H:%M:%S %z",
    )
