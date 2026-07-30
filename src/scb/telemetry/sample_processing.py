"""Parse synthetic sample telemetry into deterministic research records."""

from __future__ import annotations

import argparse
import csv
import io
import json
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from scb.common.constants import PARSER_VERSION
from scb.telemetry.parse_openwrt_metrics import parse_openwrt_metrics
from scb.telemetry.parse_radius_logs import parse_radius_acct_log, parse_radius_auth_log
from scb.telemetry.parse_tc_stats import parse_tc_stats
from scb.telemetry.parse_wireguard_stats import parse_wireguard_stats
from scb.telemetry.parser_common import (
    repository_relative_source,
    source_sha256,
    validate_aware_timestamp,
)
from scb.telemetry.schemas import BaseTelemetryRecord, ParsedDatasetSummary


@dataclass(frozen=True)
class ParsedTable:
    """Parsed records and immutable source provenance for one input file."""

    stem: str
    source_file: str
    source_sha256: str
    rows: list[dict[str, object]]


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _run_timestamp(value: str | None) -> str:
    timestamp = value or _utc_now()
    return validate_aware_timestamp(timestamp, field="parsed_at")


def _serialize_record(record: BaseModel) -> dict[str, object]:
    return json.loads(record.model_dump_json())


def _parse_file(root: Path, path: Path, parsed_at: str) -> list[BaseTelemetryRecord]:
    name = path.name
    if name == "radius_auth_sample.log":
        return list(
            parse_radius_auth_log(path, root, PARSER_VERSION, parsed_at=parsed_at)
        )
    if name == "radius_acct_sample.log":
        return list(
            parse_radius_acct_log(path, root, PARSER_VERSION, parsed_at=parsed_at)
        )
    if name == "openwrt_metrics_sample.txt":
        return list(
            parse_openwrt_metrics(path, root, PARSER_VERSION, parsed_at=parsed_at)
        )
    if name == "tc_stats_sample.txt":
        return list(parse_tc_stats(path, root, PARSER_VERSION, parsed_at=parsed_at))
    if name == "wireguard_stats_sample.txt":
        return list(
            parse_wireguard_stats(path, root, PARSER_VERSION, parsed_at=parsed_at)
        )
    raise ValueError(f"unsupported sample file: {name}")


def parse_sample_file(
    root: Path,
    path: Path,
    *,
    parsed_at: str | None = None,
) -> ParsedTable:
    """Parse one file using one timestamp and an exact-byte source digest."""

    parse_time = _run_timestamp(parsed_at)
    source_file = repository_relative_source(path, root)
    records = _parse_file(root, path, parse_time)
    return ParsedTable(
        stem=path.stem,
        source_file=source_file,
        source_sha256=source_sha256(path),
        rows=[_serialize_record(record) for record in records],
    )


def _atomic_write_text(path: Path, text: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def write_parsed_table(table: ParsedTable, output_dir: Path) -> None:
    """Atomically write stable CSV and JSON representations."""

    output_dir.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in table.rows for key in row})
    csv_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(table.rows)
    _atomic_write_text(output_dir / f"{table.stem}.csv", csv_buffer.getvalue())
    _atomic_write_text(
        output_dir / f"{table.stem}.json",
        json.dumps(table.rows, indent=2, sort_keys=True) + "\n",
    )


def write_summary(
    tables: list[ParsedTable], output_dir: Path, *, generated_at: str
) -> None:
    """Atomically write the run manifest, including every source digest."""

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
        source_sha256={table.source_file: table.source_sha256 for table in tables},
        generated_at=generated_at,
    )
    payload = json.dumps(
        json.loads(summary.model_dump_json()), indent=2, sort_keys=True
    )
    _atomic_write_text(output_dir / "summary.json", payload + "\n")


def parse_all_samples(
    samples_dir: Path,
    output_dir: Path,
    *,
    parsed_at: str | None = None,
    repo_root: Path | None = None,
) -> list[ParsedTable]:
    """Parse all supported files, failing on empty or malformed input."""

    root = (repo_root or _repo_root()).resolve(strict=True)
    samples_dir = samples_dir.resolve(strict=True)
    parse_time = _run_timestamp(parsed_at)
    paths = sorted(path for path in samples_dir.iterdir() if path.is_file())
    if not paths:
        raise ValueError(f"sample directory contains no files: {samples_dir}")
    tables = [parse_sample_file(root, path, parsed_at=parse_time) for path in paths]
    for table in tables:
        write_parsed_table(table, output_dir)
    write_summary(tables, output_dir, generated_at=parse_time)
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
    parser.add_argument(
        "--parsed-at",
        help="Aware ISO-8601 run timestamp for byte-reproducible output.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    if not args.samples_dir.exists():
        raise FileNotFoundError(f"missing samples directory: {args.samples_dir}")
    parse_all_samples(
        args.samples_dir,
        args.output_dir,
        parsed_at=args.parsed_at,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
