"""Integration tests for AppleHealthAnalytics v0.1."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from applehealth.constants import (
    ACTIVE_ENERGY_CSV,
    HEART_RATE_CSV,
    HRV_CSV,
    SQLITE_FILENAME,
    STEPS_CSV,
    SUMMARY_JSON,
    SUMMARY_MD,
    WORKOUTS_CSV,
)
from applehealth.db.connection import open_database
from applehealth.db.repository import HealthRecordReference, RecordRepository
from applehealth.pipeline import run_pipeline

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_XML = FIXTURES / "sample_export.xml"


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    return tmp_path / "out"


def test_pipeline_produces_all_outputs(output_dir: Path) -> None:
    result = run_pipeline(SAMPLE_XML, output_dir)

    assert result.sqlite_path.is_file()
    assert (output_dir / HEART_RATE_CSV).is_file()
    assert (output_dir / HRV_CSV).is_file()
    assert (output_dir / WORKOUTS_CSV).is_file()
    assert (output_dir / STEPS_CSV).is_file()
    assert (output_dir / ACTIVE_ENERGY_CSV).is_file()
    assert (output_dir / SUMMARY_JSON).is_file()
    assert (output_dir / SUMMARY_MD).is_file()


def test_parse_counts(output_dir: Path) -> None:
    result = run_pipeline(SAMPLE_XML, output_dir)

    assert result.parse_counts["heart_rate"] == 2
    assert result.parse_counts["hrv"] == 1
    assert result.parse_counts["step_count"] == 1
    assert result.parse_counts["active_energy"] == 1
    assert result.parse_counts["workouts"] == 2
    assert result.export_date == "2026-07-27 12:00:00 -0600"


def test_sqlite_contents(output_dir: Path) -> None:
    run_pipeline(SAMPLE_XML, output_dir)
    connection = sqlite3.connect(output_dir / SQLITE_FILENAME)
    heart_rate_count = connection.execute("SELECT COUNT(*) FROM heart_rate").fetchone()[0]
    workout_count = connection.execute("SELECT COUNT(*) FROM workouts").fetchone()[0]
    connection.close()

    assert heart_rate_count == 2
    assert workout_count == 2


def test_workout_health_record_associations(output_dir: Path) -> None:
    run_pipeline(SAMPLE_XML, output_dir)
    connection = sqlite3.connect(output_dir / SQLITE_FILENAME)
    rows = connection.execute(
        "SELECT workout_id, health_record_table, health_record_id "
        "FROM workout_health_record "
        "ORDER BY workout_id, health_record_table, health_record_id"
    ).fetchall()
    connection.close()

    assert rows == [
        (1, "active_energy", 1),
        (1, "heart_rate", 1),
        (1, "step_count", 1),
        (2, "active_energy", 1),
        (2, "step_count", 1),
    ]


def test_get_associated_health_records(output_dir: Path) -> None:
    run_pipeline(SAMPLE_XML, output_dir)
    connection = open_database(output_dir / SQLITE_FILENAME)
    repository = RecordRepository(connection)
    references = repository.get_associated_health_records(1)
    connection.close()

    assert references == [
        HealthRecordReference("active_energy", 1),
        HealthRecordReference("heart_rate", 1),
        HealthRecordReference("step_count", 1),
    ]


def test_get_health_record(output_dir: Path) -> None:
    run_pipeline(SAMPLE_XML, output_dir)
    connection = open_database(output_dir / SQLITE_FILENAME)
    repository = RecordRepository(connection)
    reference = repository.get_associated_health_records(1)[0]
    row = repository.get_health_record(reference)
    connection.close()

    assert row is not None
    assert row["id"] == reference.health_record_id


def test_summary_json_structure(output_dir: Path) -> None:
    run_pipeline(SAMPLE_XML, output_dir)
    summary = json.loads((output_dir / SUMMARY_JSON).read_text(encoding="utf-8"))

    assert summary["version"] == "0.1.0"
    assert summary["source"]["export_date"] == "2026-07-27 12:00:00 -0600"
    assert summary["metrics"]["Heart Rate"]["record_count"] == 2
    assert summary["metrics"]["Workouts"]["record_count"] == 2


def test_missing_xml_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        run_pipeline(tmp_path / "missing.xml", tmp_path / "out")
