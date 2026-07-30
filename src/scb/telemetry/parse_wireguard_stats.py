"""Parse strict WireGuard transfer statistics."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from scb.telemetry.parser_common import (
    iter_data_lines,
    nonnegative_int,
    parse_strict_key_values,
    read_utf8_text,
    repository_relative_source,
    require_records,
    validate_aware_timestamp,
)
from scb.telemetry.schemas import EvidenceClass, WireGuardStatsRecord

_REQUIRED_KEYS = {
    "interface",
    "peer_id_hash",
    "rx_bytes",
    "tx_bytes",
    "latest_handshake",
}


def parse_wireguard_stats(
    path: Path,
    repo_root: Path,
    parser_version: str,
    evidence_class: EvidenceClass = EvidenceClass.SYNTHETIC,
    *,
    parsed_at: str | None = None,
) -> list[WireGuardStatsRecord]:
    """Parse complete peer snapshots without counter defaults or repairs."""

    source_file = repository_relative_source(path, repo_root)
    parse_time = parsed_at or datetime.now(UTC).isoformat().replace("+00:00", "Z")
    validate_aware_timestamp(parse_time, field="parsed_at")
    records: list[WireGuardStatsRecord] = []
    for line_number, line in iter_data_lines(read_utf8_text(path)):
        context = f"WireGuard line {line_number}"
        values = parse_strict_key_values(
            line.split(),
            allowed_keys=_REQUIRED_KEYS,
            required_keys=_REQUIRED_KEYS,
            context=context,
        )
        validate_aware_timestamp(
            values["latest_handshake"], field=f"{context} latest_handshake"
        )
        records.append(
            WireGuardStatsRecord(
                evidence_class=evidence_class,
                source_file=source_file,
                source_type="wireguard_stats",
                parser_version=parser_version,
                parsed_at=parse_time,
                interface=values["interface"],
                peer_id_hash=values["peer_id_hash"],
                transfer_rx_bytes=nonnegative_int(
                    values["rx_bytes"], field=f"{context} rx_bytes"
                ),
                transfer_tx_bytes=nonnegative_int(
                    values["tx_bytes"], field=f"{context} tx_bytes"
                ),
                latest_handshake=values["latest_handshake"],
            )
        )
    return require_records(records, context="WireGuard statistics")
