"""Tests for the synthetic Linux ``tc`` parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from scb.telemetry.parse_tc_stats import parse_tc_stats
from scb.telemetry.schemas import EvidenceClass


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_tc_parser_tags_synthetic() -> None:
    path = _repo_root() / "data" / "samples" / "tc_stats_sample.txt"
    records = parse_tc_stats(path, _repo_root(), "0.1.0")
    assert records, "expected at least one tc record"
    for record in records:
        assert record.evidence_class is EvidenceClass.SYNTHETIC
        assert record.source_type == "tc_stats"
        assert record.parser_version == "0.1.0"


def test_tc_parser_extracts_numerics() -> None:
    path = _repo_root() / "data" / "samples" / "tc_stats_sample.txt"
    records = parse_tc_stats(path, _repo_root(), "0.1.0", interface="eth0")
    first = records[0]
    assert first.class_id == "1:10"
    assert first.rate_mbit == pytest.approx(50.0)
    assert first.ceil_mbit == pytest.approx(100.0)
    assert first.sent_bytes == 123456
    assert first.drops == 12
    assert first.interface == "eth0"


def test_tc_parser_rejects_malformed_line(tmp_path: Path) -> None:
    sample = tmp_path / "bad.txt"
    sample.write_text("not a tc line\n")
    with pytest.raises(ValueError):
        parse_tc_stats(sample, tmp_path, "0.1.0")
