"""Parse strict synthetic Linux ``tc`` class statistics."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

from scb.telemetry.parser_common import (
    iter_data_lines,
    read_utf8_text,
    repository_relative_source,
    require_records,
    validate_aware_timestamp,
)
from scb.telemetry.schemas import EvidenceClass, TcStatsRecord

_TC_LINE_RE = re.compile(
    r"^class\s+htb\s+(?P<class_id>\S+)\s+root\s+rate\s+"
    r"(?P<rate_mbit>\d+(?:\.\d+)?)Mbit\s+ceil\s+"
    r"(?P<ceil_mbit>\d+(?:\.\d+)?)Mbit\s+sent\s+"
    r"(?P<sent_bytes>\d+)\s+bytes\s+(?P<packets>\d+)\s+packets\s+"
    r"(?P<drops>\d+)\s+drops\s+backlog\s+"
    r"(?P<backlog_bytes>\d+)b\s+(?P<backlog_packets>\d+)p\s+requeues\s+"
    r"(?P<requeues>\d+)$"
)


def parse_tc_stats(
    path: Path,
    repo_root: Path,
    parser_version: str,
    interface: str = "ifb0",
    evidence_class: EvidenceClass = EvidenceClass.SYNTHETIC,
    *,
    parsed_at: str | None = None,
) -> list[TcStatsRecord]:
    """Parse class counters with unique IDs and coherent configured rates."""

    interface = interface.strip()
    if not interface:
        raise ValueError("tc interface must be non-empty")
    source_file = repository_relative_source(path, repo_root)
    parse_time = parsed_at or datetime.now(UTC).isoformat().replace("+00:00", "Z")
    validate_aware_timestamp(parse_time, field="parsed_at")
    records: list[TcStatsRecord] = []
    class_ids: set[str] = set()
    for line_number, line in iter_data_lines(read_utf8_text(path)):
        match = _TC_LINE_RE.fullmatch(line)
        if match is None:
            raise ValueError(f"tc line {line_number}: invalid class statistics")
        class_id = match.group("class_id")
        if class_id in class_ids:
            raise ValueError(f"tc line {line_number}: duplicate class_id {class_id!r}")
        class_ids.add(class_id)
        rate_mbit = float(match.group("rate_mbit"))
        ceil_mbit = float(match.group("ceil_mbit"))
        if rate_mbit <= 0 or ceil_mbit <= 0:
            raise ValueError(f"tc line {line_number}: rates must be positive")
        if rate_mbit > ceil_mbit:
            raise ValueError(f"tc line {line_number}: rate exceeds ceil")
        records.append(
            TcStatsRecord(
                evidence_class=evidence_class,
                source_file=source_file,
                source_type="tc_stats",
                parser_version=parser_version,
                parsed_at=parse_time,
                interface=interface,
                class_id=class_id,
                rate_mbit=rate_mbit,
                ceil_mbit=ceil_mbit,
                sent_bytes=int(match.group("sent_bytes")),
                packets=int(match.group("packets")),
                drops=int(match.group("drops")),
                backlog_bytes=int(match.group("backlog_bytes")),
                backlog_packets=int(match.group("backlog_packets")),
                requeues=int(match.group("requeues")),
            )
        )
    return require_records(records, context="tc statistics")
