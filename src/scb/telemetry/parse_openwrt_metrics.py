"""Parse strict OpenWrt CPU, memory, interrupt, and load telemetry."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from scb.telemetry.parser_common import (
    finite_float,
    iter_data_lines,
    parse_strict_key_values,
    read_utf8_text,
    repository_relative_source,
    require_records,
    validate_aware_timestamp,
)
from scb.telemetry.schemas import EvidenceClass, OpenWrtMetricRecord

_REQUIRED_KEYS = {
    "ap_id",
    "cpu_percent",
    "ram_used_mb",
    "ram_total_mb",
    "irq_rate",
    "load_avg",
}


def parse_openwrt_metrics(
    path: Path,
    repo_root: Path,
    parser_version: str,
    evidence_class: EvidenceClass = EvidenceClass.SYNTHETIC,
    *,
    parsed_at: str | None = None,
) -> list[OpenWrtMetricRecord]:
    """Parse complete metric snapshots and reject impossible values."""

    source_file = repository_relative_source(path, repo_root)
    parse_time = parsed_at or datetime.now(UTC).isoformat().replace("+00:00", "Z")
    validate_aware_timestamp(parse_time, field="parsed_at")
    records: list[OpenWrtMetricRecord] = []
    for line_number, line in iter_data_lines(read_utf8_text(path)):
        tokens = line.split()
        if len(tokens) < 2:
            raise ValueError(f"OpenWrt line {line_number}: missing metric fields")
        timestamp, *fields = tokens
        validate_aware_timestamp(
            timestamp, field=f"OpenWrt line {line_number} timestamp"
        )
        context = f"OpenWrt line {line_number}"
        values = parse_strict_key_values(
            fields,
            allowed_keys=_REQUIRED_KEYS,
            required_keys=_REQUIRED_KEYS,
            context=context,
        )
        cpu_percent = finite_float(
            values["cpu_percent"], field=f"{context} cpu_percent", maximum=100.0
        )
        ram_used_mb = finite_float(
            values["ram_used_mb"], field=f"{context} ram_used_mb"
        )
        ram_total_mb = finite_float(
            values["ram_total_mb"],
            field=f"{context} ram_total_mb",
            exclusive_minimum=True,
        )
        if ram_used_mb > ram_total_mb:
            raise ValueError(f"{context}: ram_used_mb exceeds ram_total_mb")
        records.append(
            OpenWrtMetricRecord(
                evidence_class=evidence_class,
                source_file=source_file,
                source_type="openwrt_metrics",
                parser_version=parser_version,
                parsed_at=parse_time,
                timestamp=timestamp,
                ap_id=values["ap_id"],
                cpu_percent=cpu_percent,
                ram_used_mb=ram_used_mb,
                ram_total_mb=ram_total_mb,
                irq_rate=finite_float(values["irq_rate"], field=f"{context} irq_rate"),
                load_avg=finite_float(values["load_avg"], field=f"{context} load_avg"),
            )
        )
    return require_records(records, context="OpenWrt metrics")
