"""Tests for the synthetic RADIUS log parsers."""

from __future__ import annotations

from pathlib import Path

import pytest

from scb.telemetry.parse_radius_logs import (
    parse_radius_acct_log,
    parse_radius_auth_log,
)
from scb.telemetry.schemas import EvidenceClass


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_radius_auth_parser_tags_synthetic() -> None:
    path = _repo_root() / "data" / "samples" / "radius_auth_sample.log"
    records = parse_radius_auth_log(path, _repo_root(), "0.1.0")
    assert records, "expected at least one auth record"
    for record in records:
        assert record.evidence_class is EvidenceClass.SYNTHETIC
        assert record.source_type == "radius_auth"
        assert record.parser_version == "0.1.0"
        assert record.source_file.endswith("radius_auth_sample.log")


def test_radius_auth_parser_extracts_fields() -> None:
    path = _repo_root() / "data" / "samples" / "radius_auth_sample.log"
    records = parse_radius_auth_log(path, _repo_root(), "0.1.0")
    accept = [r for r in records if r.auth_result == "ACCEPT"]
    reject = [r for r in records if r.auth_result == "REJECT"]
    assert accept and reject
    assert accept[0].subscriber_id_hash == "hash_a1"
    assert accept[0].ap_id == "ap-01"
    assert accept[0].auth_latency_ms == pytest.approx(12.4)


def test_radius_acct_parser_extracts_octets() -> None:
    path = _repo_root() / "data" / "samples" / "radius_acct_sample.log"
    records = parse_radius_acct_log(path, _repo_root(), "0.1.0")
    assert len(records) == 1
    assert records[0].input_octets == 1200
    assert records[0].output_octets == 4500
    assert records[0].accounting_session_id == "sess-1"


def test_radius_parser_evidence_class_propagation(tmp_path: Path) -> None:
    sample = tmp_path / "auth.log"
    sample.write_text(
        "2026-07-03T08:00:00Z AUTH subscriber_id_hash=h1 ap_id=ap-01 "
        "result=ACCEPT latency_ms=1.0\n"
    )
    records = parse_radius_auth_log(
        sample, tmp_path, "test", evidence_class=EvidenceClass.MEASURED
    )
    assert records[0].evidence_class is EvidenceClass.MEASURED
