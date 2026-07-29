"""End-to-end processing pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from applehealth.association import AssociationFacade
from applehealth.constants import DEFAULT_BATCH_SIZE, SQLITE_FILENAME
from applehealth.db.collecting_repository import CollectingRepository
from applehealth.db.connection import open_database
from applehealth.db.repository import RecordRepository
from applehealth.export.csv_exporter import export_all_csv
from applehealth.parser.stream_parser import StreamParser
from applehealth.summary.generator import generate_summary


@dataclass
class PipelineResult:
    """Artifacts produced by a successful run."""

    output_dir: Path
    sqlite_path: Path
    parse_counts: dict[str, int]
    csv_counts: dict[str, int]
    summary_json: Path
    export_date: str | None


def run_pipeline(
    xml_path: Path,
    output_dir: Path,
    *,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> PipelineResult:
    """
    Process an Apple Health export.xml file:
    1. Stream-parse XML into SQLite
    2. Export CSV files
    3. Generate summary reports
    """
    xml_path = xml_path.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()

    if not xml_path.is_file():
        raise FileNotFoundError(f"XML file not found: {xml_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    sqlite_path = output_dir / SQLITE_FILENAME

    connection = open_database(sqlite_path)
    repository = RecordRepository(connection, batch_size=batch_size)
    collecting = CollectingRepository(repository)
    parser = StreamParser(xml_path, collecting)
    parse_counts = parser.parse()
    facade = AssociationFacade()
    associations = facade.associate(collecting.workouts, collecting.records)
    connection.close()

    connection = open_database(sqlite_path)
    csv_counts = export_all_csv(connection, output_dir)
    connection.close()

    summary_json = generate_summary(
        xml_path=xml_path,
        output_dir=output_dir,
        parse_counts=parse_counts,
        csv_counts=csv_counts,
        export_date=parser.export_date,
    )

    return PipelineResult(
        output_dir=output_dir,
        sqlite_path=sqlite_path,
        parse_counts=parse_counts,
        csv_counts=csv_counts,
        summary_json=summary_json,
        export_date=parser.export_date,
    )
