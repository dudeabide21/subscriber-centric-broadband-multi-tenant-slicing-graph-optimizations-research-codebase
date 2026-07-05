"""Tests for the synthetic OpenWrt metrics parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from scb.telemetry.parse_openwrt_metrics import parse_openwrt_metrics
from scb.telemetry.schemas import EvidenceClass


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_openwrt_parser_tags_synthetic() -> None:
    path = _repo_root() / "data" / "samples" / "openwrt_metrics_sample.txt"
    records = parse_openwrt_metrics(path, _repo_root(), "0.1.0")
    assert len(records) == 1
    record = records[0]
    assert record.evidence_class is EvidenceClass.SYNTHETIC
    assert record.source_type == "openwrt_metrics"
    assert record.parser_version == "0.1.0"


def test_openwrt_parser_extracts_metrics() -> None:
    path = _repo_root() / "data" / "samples" / "openwrt_metrics_sample.txt"
    records = parse_openwrt_metrics(path, _repo_root(), "0.1.0")
    record = records[0]
    assert record.ap_id == "ap-01"
    assert record.cpu_percent == pytest.approx(37.5)
    assert record.ram_used_mb == pytest.approx(112.0)
    assert record.ram_total_mb == pytest.approx(256.0)
    assert record.irq_rate == pytest.approx(88.2)
    assert record.load_avg == pytest.approx(0.41)


def test_openwrt_parser_rejects_missing_keys(tmp_path: Path) -> None:
    sample = tmp_path / "missing.txt"
    sample.write_text("2026-07-03T08:01:00Z ap_id=ap-01 cpu_percent=1.0\n")
    with pytest.raises(ValueError):
        parse_openwrt_metrics(sample, tmp_path, "0.1.0")
