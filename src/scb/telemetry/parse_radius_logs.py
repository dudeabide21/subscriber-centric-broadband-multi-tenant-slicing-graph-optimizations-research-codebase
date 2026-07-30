"""Parse strict RADIUS authentication and accounting telemetry."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from scb.telemetry.parser_common import (
    finite_float,
    iter_data_lines,
    nonnegative_int,
    parse_strict_key_values,
    read_utf8_text,
    repository_relative_source,
    require_records,
    validate_aware_timestamp,
)
from scb.telemetry.schemas import EvidenceClass, RadiusRecord

_COMMON_KEYS = {"subscriber_id_hash", "ap_id"}
_AUTH_KEYS = _COMMON_KEYS | {"auth_result", "auth_latency_ms"}
_ACCT_KEYS = _COMMON_KEYS | {
    "accounting_session_id",
    "input_octets",
    "output_octets",
}
_ALIASES = {
    "result": "auth_result",
    "latency_ms": "auth_latency_ms",
    "session_id": "accounting_session_id",
}
_AUTH_RESULTS = {"ACCEPT", "REJECT", "ERROR"}


def _parse_time(parsed_at: str | None) -> str:
    value = parsed_at or datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return validate_aware_timestamp(value, field="parsed_at")


def _base_line(line: str, *, line_number: int) -> tuple[str, str, list[str]]:
    tokens = line.split()
    if len(tokens) < 3:
        raise ValueError(
            f"RADIUS line {line_number}: expected timestamp, event, and fields"
        )
    timestamp, event_type, *fields = tokens
    validate_aware_timestamp(timestamp, field=f"RADIUS line {line_number} timestamp")
    return timestamp, event_type, fields


def parse_radius_auth_log(
    path: Path,
    repo_root: Path,
    parser_version: str,
    evidence_class: EvidenceClass = EvidenceClass.SYNTHETIC,
    *,
    parsed_at: str | None = None,
) -> list[RadiusRecord]:
    """Parse authentication events, rejecting incomplete or ambiguous lines."""

    source_file = repository_relative_source(path, repo_root)
    parse_time = _parse_time(parsed_at)
    records: list[RadiusRecord] = []
    for line_number, line in iter_data_lines(read_utf8_text(path)):
        timestamp, event_type, tokens = _base_line(line, line_number=line_number)
        if event_type != "AUTH":
            raise ValueError(f"RADIUS line {line_number}: expected AUTH event")
        context = f"RADIUS AUTH line {line_number}"
        values = parse_strict_key_values(
            tokens,
            allowed_keys=_AUTH_KEYS,
            required_keys=_AUTH_KEYS,
            aliases=_ALIASES,
            context=context,
        )
        auth_result = values["auth_result"].upper()
        if auth_result not in _AUTH_RESULTS:
            raise ValueError(f"{context}: unsupported auth result {auth_result!r}")
        records.append(
            RadiusRecord(
                evidence_class=evidence_class,
                source_file=source_file,
                source_type="radius_auth",
                parser_version=parser_version,
                parsed_at=parse_time,
                timestamp=timestamp,
                event_type=event_type,
                subscriber_id_hash=values["subscriber_id_hash"],
                ap_id=values["ap_id"],
                auth_result=auth_result,
                auth_latency_ms=finite_float(
                    values["auth_latency_ms"], field=f"{context} auth_latency_ms"
                ),
            )
        )
    return require_records(records, context="RADIUS authentication log")


def parse_radius_acct_log(
    path: Path,
    repo_root: Path,
    parser_version: str,
    evidence_class: EvidenceClass = EvidenceClass.SYNTHETIC,
    *,
    parsed_at: str | None = None,
) -> list[RadiusRecord]:
    """Parse accounting events without repairing missing counters."""

    source_file = repository_relative_source(path, repo_root)
    parse_time = _parse_time(parsed_at)
    records: list[RadiusRecord] = []
    for line_number, line in iter_data_lines(read_utf8_text(path)):
        timestamp, event_type, tokens = _base_line(line, line_number=line_number)
        if event_type != "ACCT":
            raise ValueError(f"RADIUS line {line_number}: expected ACCT event")
        context = f"RADIUS ACCT line {line_number}"
        values = parse_strict_key_values(
            tokens,
            allowed_keys=_ACCT_KEYS,
            required_keys=_ACCT_KEYS,
            aliases=_ALIASES,
            context=context,
        )
        records.append(
            RadiusRecord(
                evidence_class=evidence_class,
                source_file=source_file,
                source_type="radius_acct",
                parser_version=parser_version,
                parsed_at=parse_time,
                timestamp=timestamp,
                event_type=event_type,
                subscriber_id_hash=values["subscriber_id_hash"],
                ap_id=values["ap_id"],
                accounting_session_id=values["accounting_session_id"],
                input_octets=nonnegative_int(
                    values["input_octets"], field=f"{context} input_octets"
                ),
                output_octets=nonnegative_int(
                    values["output_octets"], field=f"{context} output_octets"
                ),
            )
        )
    return require_records(records, context="RADIUS accounting log")
