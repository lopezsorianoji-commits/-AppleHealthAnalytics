"""Command-line interface."""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from applehealth import __version__
from applehealth.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="applehealth",
        description=(
            "Process Apple Health export.xml locally using streaming XML parsing "
            "and produce SQLite, CSV, and summary outputs."
        ),
    )
    parser.add_argument(
        "xml_file",
        type=Path,
        help="Path to Apple Health export.xml",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory for health.sqlite, CSV files, and summaries (default: output)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5_000,
        help="Number of records to buffer before writing to SQLite (default: 5000)",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = run_pipeline(
            args.xml_file,
            args.output_dir,
            batch_size=args.batch_size,
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except ET.ParseError as exc:
        print(f"Error: invalid XML — {exc}", file=sys.stderr)
        return 1

    print(f"Processed: {args.xml_file}")
    if result.export_date:
        print(f"Export date: {result.export_date}")
    print(f"Output directory: {result.output_dir}")
    print("Records parsed:")
    for table, count in result.parse_counts.items():
        print(f"  {table}: {count:,}")
    print("CSV rows written:")
    for filename, count in result.csv_counts.items():
        print(f"  {filename}: {count:,}")
    print(f"Summary: {result.summary_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
