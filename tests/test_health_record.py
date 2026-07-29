"""Tests for HealthRecord domain entity and quantity parser migration."""

from __future__ import annotations

from datetime import datetime

from applehealth.constants import HEART_RATE_TYPE
from applehealth.parser.stream_parser import _quantity_record


def test_quantity_record_returns_health_record() -> None:
    attributes = {
        "sourceName": "Apple Watch",
        "sourceVersion": "10.0",
        "device": "Watch",
        "creationDate": "2026-07-01 08:00:00 -0600",
        "startDate": "2026-07-01 08:00:00 -0600",
        "endDate": "2026-07-01 08:00:00 -0600",
        "value": "72",
        "unit": "count/min",
    }

    record = _quantity_record(attributes, HEART_RATE_TYPE)

    assert record.tipo_registro == HEART_RATE_TYPE
    assert record.fuente_origen == "Apple Watch"
    assert record.dispositivo == "Watch"
    assert record.unidad_medida == "count/min"
    assert record.valor == 72.0
    assert record.metadatos["source_version"] == "10.0"
    assert record.fecha_inicio == datetime.strptime(
        "2026-07-01 08:00:00 -0600",
        "%Y-%m-%d %H:%M:%S %z",
    )
    assert record.fecha_fin == record.fecha_inicio
    assert record.fecha_creacion == record.fecha_inicio
