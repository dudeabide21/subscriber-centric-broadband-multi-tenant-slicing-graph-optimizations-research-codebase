"""Tests for the synthetic WireGuard parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from scb.telemetry.parse_wireguard_stats import parse_wireguard_stats
from scb.telemetry.schemas import EvidenceClass


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_wireguard_parser_tags_synthetic() -> None:
    path = _repo_root() / "data" / "samples" / "wireguard_stats_sample.txt"
    records = parse_wireguard_stats(path, _repo_root(), "0.1.0")
    assert len(records) == 1
    record = records[0]
    assert record.evidence_class is EvidenceClass.SYNTHETIC
    assert record.source_type == "wireguard_stats"


def test_wireguard_parser_extracts_fields() -> None:
    path = _repo_root() / "data" / "samples" / "wireguard_stats_sample.txt"
    records = parse_wireguard_stats(path, _repo_root(), "0.1.0")
    record = records[0]
    assert record.interface == "wg0"
    assert record.peer_id_hash == "peer-a"
    assert record.transfer_rx_bytes == 123456
    assert record.transfer_tx_bytes == 234567
    assert record.latest_handshake.startswith("2026-")


def test_wireguard_parser_rejects_unknown_key(tmp_path: Path) -> None:
    sample = tmp_path / "bad.txt"
    sample.write_text(
        "interface=wg0 peer_id_hash=p1 rx_bytes=1 tx_bytes=1 "
        "latest_handshake=x extra=z\n"
    )
    with pytest.raises(ValueError):
        parse_wireguard_stats(sample, tmp_path, "0.1.0")
