"""Generate summary.json and summary.md from processed data."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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

METRIC_LABELS: dict[str, str] = {
    "heart_rate": "Heart Rate",
    "hrv": "Heart Rate Variability (SDNN)",
    "workouts": "Workouts",
    "step_count": "Step Count",
    "active_energy": "Active Energy Burned",
}


def _table_stats(connection: sqlite3.Connection, table: str) -> dict[str, Any]:
    cursor = connection.execute(
        f"""
        SELECT
            COUNT(*) AS record_count,
            MIN(start_date) AS earliest,
            MAX(start_date) AS latest,
            MIN(value) AS min_value,
            MAX(value) AS max_value,
            AVG(value) AS avg_value
        FROM {table}
        """
    )
    row = cursor.fetchone()
    return {
        "record_count": row["record_count"] or 0,
        "date_range": {
            "earliest": row["earliest"],
            "latest": row["latest"],
        },
        "value_stats": {
            "min": row["min_value"],
            "max": row["max_value"],
            "avg": round(row["avg_value"], 4) if row["avg_value"] is not None else None,
        },
    }


def _workout_stats(connection: sqlite3.Connection) -> dict[str, Any]:
    cursor = connection.execute(
        """
        SELECT
            COUNT(*) AS record_count,
            MIN(start_date) AS earliest,
            MAX(start_date) AS latest,
            SUM(duration) AS total_duration,
            SUM(total_distance) AS total_distance,
            SUM(total_energy_burned) AS total_energy_burned
        FROM workouts
        """
    )
    row = cursor.fetchone()
    activity_cursor = connection.execute(
        """
        SELECT workout_activity_type, COUNT(*) AS count
        FROM workouts
        GROUP BY workout_activity_type
        ORDER BY count DESC
        LIMIT 10
        """
    )
    top_activities = [
        {"type": activity_row["workout_activity_type"], "count": activity_row["count"]}
        for activity_row in activity_cursor.fetchall()
    ]
    return {
        "record_count": row["record_count"] or 0,
        "date_range": {
            "earliest": row["earliest"],
            "latest": row["latest"],
        },
        "totals": {
            "duration": row["total_duration"],
            "distance": row["total_distance"],
            "energy_burned": row["total_energy_burned"],
        },
        "top_activities": top_activities,
    }


def build_summary_payload(
    *,
    xml_path: Path,
    output_dir: Path,
    parse_counts: dict[str, int],
    csv_counts: dict[str, int],
    export_date: str | None,
) -> dict[str, Any]:
    """Assemble the summary data structure."""
    db_path = output_dir / SQLITE_FILENAME
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row

    metrics: dict[str, Any] = {}
    for table, label in METRIC_LABELS.items():
        if table == "workouts":
            metrics[label] = _workout_stats(connection)
        else:
            metrics[label] = _table_stats(connection, table)

    connection.close()

    return {
        "version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "xml_file": str(xml_path.resolve()),
            "export_date": export_date,
        },
        "outputs": {
            "directory": str(output_dir.resolve()),
            "sqlite": SQLITE_FILENAME,
            "csv_files": {
                "heart_rate": HEART_RATE_CSV,
                "hrv": HRV_CSV,
                "workouts": WORKOUTS_CSV,
                "steps": STEPS_CSV,
                "active_energy": ACTIVE_ENERGY_CSV,
            },
            "summary_json": SUMMARY_JSON,
            "summary_md": SUMMARY_MD,
        },
        "parsed_counts": parse_counts,
        "exported_csv_rows": csv_counts,
        "metrics": metrics,
    }


def _render_markdown(summary: dict[str, Any]) -> str:
    lines: list[str] = [
        "# Apple Health Analytics — Summary",
        "",
        f"- **Version:** {summary['version']}",
        f"- **Generated:** {summary['generated_at']}",
        f"- **Source XML:** `{summary['source']['xml_file']}`",
    ]
    if summary["source"]["export_date"]:
        lines.append(f"- **Export date:** {summary['source']['export_date']}")
    lines.extend(["", "## Parsed record counts", ""])

    for table, count in summary["parsed_counts"].items():
        lines.append(f"- **{table}:** {count:,}")

    lines.extend(["", "## Metrics", ""])

    for label, data in summary["metrics"].items():
        lines.append(f"### {label}")
        lines.append("")
        lines.append(f"- Records: **{data['record_count']:,}**")
        date_range = data.get("date_range", {})
        if date_range.get("earliest") or date_range.get("latest"):
            lines.append(
                f"- Date range: {date_range.get('earliest') or '—'} → "
                f"{date_range.get('latest') or '—'}"
            )
        if "value_stats" in data and data["record_count"]:
            stats = data["value_stats"]
            lines.append(
                f"- Value: min {stats['min']}, max {stats['max']}, avg {stats['avg']}"
            )
        if "totals" in data and data["record_count"]:
            totals = data["totals"]
            lines.append(
                f"- Totals: duration {totals.get('duration')}, "
                f"distance {totals.get('distance')}, "
                f"energy {totals.get('energy_burned')}"
            )
        if data.get("top_activities"):
            lines.append("- Top activities:")
            for activity in data["top_activities"]:
                lines.append(f"  - {activity['type']}: {activity['count']:,}")
        lines.append("")

    lines.extend(["## Output files", ""])
    outputs = summary["outputs"]
    lines.append(f"- Directory: `{outputs['directory']}`")
    lines.append(f"- SQLite: `{outputs['sqlite']}`")
    for name, filename in outputs["csv_files"].items():
        rows = summary["exported_csv_rows"].get(filename, 0)
        lines.append(f"- `{filename}` ({name}): {rows:,} rows")
    lines.append(f"- `{outputs['summary_json']}`")
    lines.append(f"- `{outputs['summary_md']}`")
    lines.append("")

    return "\n".join(lines)


def generate_summary(
    *,
    xml_path: Path,
    output_dir: Path,
    parse_counts: dict[str, int],
    csv_counts: dict[str, int],
    export_date: str | None,
) -> Path:
    """Write summary.json and summary.md; return path to summary.json."""
    summary = build_summary_payload(
        xml_path=xml_path,
        output_dir=output_dir,
        parse_counts=parse_counts,
        csv_counts=csv_counts,
        export_date=export_date,
    )

    json_path = output_dir / SUMMARY_JSON
    md_path = output_dir / SUMMARY_MD

    json_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(_render_markdown(summary), encoding="utf-8")
    return json_path
