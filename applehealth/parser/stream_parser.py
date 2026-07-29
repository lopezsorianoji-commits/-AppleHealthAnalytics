"""Streaming parser for Apple Health export.xml files."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from applehealth.constants import QUANTITY_TYPES
from applehealth.db.repository import RecordRepository
from applehealth.models import HealthRecord
from applehealth.workout import WorkoutRecord


def _local_tag(tag: str) -> str:
    """Strip XML namespace from an element tag."""
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def _parse_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z")
    except ValueError:
        return None


def _quantity_record(
    attributes: dict[str, str],
    record_type: str | None,
) -> HealthRecord:
    return HealthRecord(
        tipo_registro=record_type,
        fecha_inicio=_parse_datetime(attributes.get("startDate")),
        fecha_fin=_parse_datetime(attributes.get("endDate")),
        fecha_creacion=_parse_datetime(attributes.get("creationDate")),
        fuente_origen=attributes.get("sourceName"),
        dispositivo=attributes.get("device"),
        unidad_medida=attributes.get("unit"),
        valor=_parse_float(attributes.get("value")),
        metadatos={"source_version": attributes.get("sourceVersion")},
    )


def _workout_record(attributes: dict[str, str]) -> WorkoutRecord:
    mapped = {
        "id",
        "workoutActivityType",
        "startDate",
        "endDate",
        "creationDate",
        "modificationDate",
        "duration",
        "durationUnit",
        "totalDistance",
        "totalDistanceUnit",
        "totalEnergyBurned",
        "totalEnergyBurnedUnit",
        "sourceName",
        "device",
    }
    return WorkoutRecord(
        identificador=attributes.get("id"),
        tipo_actividad=attributes.get("workoutActivityType"),
        fecha_inicio=_parse_datetime(attributes.get("startDate")),
        fecha_fin=_parse_datetime(attributes.get("endDate")),
        fecha_creacion=_parse_datetime(attributes.get("creationDate")),
        fecha_modificacion=_parse_datetime(attributes.get("modificationDate")),
        duracion=_parse_float(attributes.get("duration")),
        unidad_duracion=attributes.get("durationUnit"),
        distancia_total=_parse_float(attributes.get("totalDistance")),
        unidad_distancia=attributes.get("totalDistanceUnit"),
        energia_total=_parse_float(attributes.get("totalEnergyBurned")),
        unidad_energia=attributes.get("totalEnergyBurnedUnit"),
        fuente_origen=attributes.get("sourceName"),
        dispositivo=attributes.get("device"),
        metadatos={
            key: value for key, value in attributes.items() if key not in mapped
        },
    )


class StreamParser:
    """Parse export.xml in a single pass without loading the full document."""

    def __init__(self, xml_path: Path, repository: RecordRepository) -> None:
        self._xml_path = xml_path
        self._repository = repository
        self.export_date: str | None = None

    def parse(self) -> dict[str, int]:
        """Stream the XML file and persist matching records."""
        context = ET.iterparse(self._xml_path, events=("start", "end"))
        _, root = next(context)

        for event, element in context:
            tag = _local_tag(element.tag)

            if event == "start" and tag == "ExportDate":
                self.export_date = element.get("value")
                continue

            if event != "end":
                continue

            if tag == "Record":
                record_type = element.get("type")
                table = QUANTITY_TYPES.get(record_type or "")
                if table:
                    self._repository.add_quantity(
                        table,
                        _quantity_record(element.attrib, record_type),
                    )
            elif tag == "Workout":
                self._repository.add_workout(_workout_record(element.attrib))

            element.clear()
            if root is not None:
                for child in list(root):
                    if len(child) == 0 and child.text is None and len(child.attrib) == 0:
                        root.remove(child)

        self._repository.flush_all()
        return dict(self._repository.counts)
