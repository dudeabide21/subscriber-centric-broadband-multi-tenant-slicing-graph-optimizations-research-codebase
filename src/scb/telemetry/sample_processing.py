"""Parse synthetic sample telemetry into typed research records.

The driver walks ``data/samples/``, dispatches each file to the appropriate
typed parser, and writes processed CSV/JSON outputs to ``data/processed/``.
All parsed records carry an evidence class and provenance metadata so the
caller can always tell synthetic samples apart from real measurements.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from scb.common.constants import PARSER_VERSION
from scb.telemetry.parse_openwrt_metrics import parse_openwrt_metrics
from scb.telemetry.parse_radius_logs import (
    parse_radius_acct_log,
    parse_radius_auth_log,
)
from scb.telemetry.parse_tc_stats import parse_tc_stats
from scb.telemetry.parse_wireguard_stats import parse_wireguard_stats
from scb.telemetry.schemas import BaseTelemetryRecord, ParsedDatasetSummary

EVIDENCE_CLASS = "Synthetic"


@dataclass(frozen=True)
class ParsedTable:
    """Parsed records for one sample source."""

    stem: str
    rows: list[dict[str, object]]


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _serialize_record(record: BaseModel) -> dict[str, object]:
    """Convert a Pydantic record to a JSON-friendly dictionary."""

    return json.loads(record.model_dump_json())


def _parse_file(root: Path, path: Path) -> list[BaseTelemetryRecord]:
    """Dispatch a sample file to the appropriate typed parser."""

    name = path.name
    if name == "radius_auth_sample.log":
        return list(parse_radius_auth_log(path, root, PARSER_VERSION))
    if name == "radius_acct_sample.log":
        return list(parse_radius_acct_log(path, root, PARSER_VERSION))
    if name == "openwrt_metrics_sample.txt":
        return list(parse_openwrt_metrics(path, root, PARSER_VERSION))
    if name == "tc_stats_sample.txt":
        return list(parse_tc_stats(path, root, PARSER_VERSION))
    if name == "wireguard_stats_sample.txt":
        return list(parse_wireguard_stats(path, root, PARSER_VERSION))
    raise ValueError(f"unsupported sample file: {name}")


def parse_sample_file(root: Path, path: Path) -> ParsedTable:
    """Parse one sample file into a stable table of records."""

    records = _parse_file(root, path)
    rows = [_serialize_record(record) for record in records]
    return ParsedTable(stem=path.stem, rows=rows)


def write_parsed_table(table: ParsedTable, output_dir: Path) -> None:
    """Write parsed output as CSV and JSON for downstream review."""

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"{table.stem}.csv"
    json_path = output_dir / f"{table.stem}.json"

    fieldnames = sorted({key for row in table.rows for key in row})
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(table.rows)

    json_path.write_text(
        json.dumps(table.rows, indent=2, sort_keys=True), encoding="utf-8"
    )


def write_summary(tables: list[ParsedTable], output_dir: Path) -> None:
    """Write a JSON summary of the parsed dataset."""

    output_dir.mkdir(parents=True, exist_ok=True)
    counter: Counter[str] = Counter()
    total = 0
    for table in tables:
        for row in table.rows:
            counter[str(row.get("evidence_class", "Unknown"))] += 1
            total += 1
    summary = ParsedDatasetSummary(
        sample_count=total,
        files=len(tables),
        evidence_classes=dict(counter),
        parser_version=PARSER_VERSION,
    )
    (output_dir / "summary.json").write_text(
        json.dumps(json.loads(summary.model_dump_json()), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def parse_all_samples(samples_dir: Path, output_dir: Path) -> list[ParsedTable]:
    """Parse every synthetic sample in ``samples_dir``.

    The parser intentionally fails loudly if a file is malformed so the audit
    surface does not quietly invent output. A ``summary.json`` file with the
    total record count and per-evidence-class counts is written to
    ``output_dir``.
    """

    root = samples_dir.parents[1]
    tables: list[ParsedTable] = []
    for path in sorted(samples_dir.iterdir()):
        if not path.is_file():
            continue
        table = parse_sample_file(root, path)
        write_parsed_table(table, output_dir)
        tables.append(table)
    write_summary(tables, output_dir)
    return tables


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--samples-dir",
        type=Path,
        default=_repo_root() / "data" / "samples",
        help="Directory containing synthetic sample telemetry.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=_repo_root() / "data" / "processed",
        help="Directory where parsed outputs will be written.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    if not args.samples_dir.exists():
        raise FileNotFoundError(f"missing samples directory: {args.samples_dir}")
    parse_all_samples(args.samples_dir, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
