"""Parse synthetic RADIUS authentication and accounting logs.

The synthetic RADIUS sample format is a deliberately simple key/value layout:

    <ISO-timestamp> <AUTH|ACCT> <key=value> <key=value> ...

The parser is intentionally strict: malformed lines raise an error so the
researcher can never silently invent records. The returned records are
Pydantic :class:`RadiusRecord` instances with the standard provenance
metadata (evidence class, source file, parser version, parse timestamp).
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from scb.telemetry.schemas import EvidenceClass, RadiusRecord

_AUTH_RESULT_KEYS = {"result", "auth_result"}
_LATENCY_KEYS = {"latency_ms", "auth_latency_ms"}
_SESSION_KEYS = {"session_id", "accounting_session_id"}
_OCTET_KEYS_IN = {"input_octets"}
_OCTET_KEYS_OUT = {"output_octets"}


def _coerce_int(value: str) -> int:
    return int(value)


def _coerce_float(value: str) -> float:
    return float(value)


def _parse_key_values(
    tokens: Iterable[str],
    record: RadiusRecord,
) -> None:
    """Populate a :class:`RadiusRecord` from ``key=value`` tokens."""

    for token in tokens:
        if "=" not in token:
            continue
        key, raw = token.split("=", 1)
        key = key.strip()
        raw = raw.strip()
        if key == "subscriber_id_hash":
            record.subscriber_id_hash = raw
        elif key == "ap_id":
            record.ap_id = raw
        elif key in _AUTH_RESULT_KEYS:
            record.auth_result = raw
        elif key in _LATENCY_KEYS:
            record.auth_latency_ms = _coerce_float(raw)
        elif key in _SESSION_KEYS:
            record.accounting_session_id = raw
        elif key in _OCTET_KEYS_IN:
            record.input_octets = _coerce_int(raw)
        elif key in _OCTET_KEYS_OUT:
            record.output_octets = _coerce_int(raw)


def _iter_lines(text: str) -> Iterable[str]:
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        yield line


def parse_radius_auth_log(
    path: Path,
    repo_root: Path,
    parser_version: str,
    evidence_class: EvidenceClass = EvidenceClass.SYNTHETIC,
) -> list[RadiusRecord]:
    """Parse a synthetic RADIUS authentication log.

    Args:
        path: Path to the log file.
        repo_root: Repository root used to compute the relative source file.
        parser_version: Parser version stamp added to every record.
        evidence_class: Defaults to :attr:`EvidenceClass.SYNTHETIC`. Real
            measurement data should be re-tagged upstream.

    Returns:
        A list of :class:`RadiusRecord` objects.

    Raises:
        ValueError: If a line is malformed.
    """

    records: list[RadiusRecord] = []
    text = path.read_text(encoding="utf-8")
    for line in _iter_lines(text):
        tokens = line.split()
        if len(tokens) < 2:
            raise ValueError(f"invalid radius line: {line}")
        timestamp, event_type, *rest = tokens
        record = RadiusRecord(
            evidence_class=evidence_class,
            source_file=path.relative_to(repo_root).as_posix(),
            source_type="radius_auth",
            parser_version=parser_version,
            timestamp=timestamp,
            event_type=event_type,
        )
        _parse_key_values(rest, record)
        records.append(record)
    return records


def parse_radius_acct_log(
    path: Path,
    repo_root: Path,
    parser_version: str,
    evidence_class: EvidenceClass = EvidenceClass.SYNTHETIC,
) -> list[RadiusRecord]:
    """Parse a synthetic RADIUS accounting log."""

    records: list[RadiusRecord] = []
    text = path.read_text(encoding="utf-8")
    for line in _iter_lines(text):
        tokens = line.split()
        if len(tokens) < 2:
            raise ValueError(f"invalid radius line: {line}")
        timestamp, event_type, *rest = tokens
        record = RadiusRecord(
            evidence_class=evidence_class,
            source_file=path.relative_to(repo_root).as_posix(),
            source_type="radius_acct",
            parser_version=parser_version,
            timestamp=timestamp,
            event_type=event_type,
        )
        _parse_key_values(rest, record)
        records.append(record)
    return records
