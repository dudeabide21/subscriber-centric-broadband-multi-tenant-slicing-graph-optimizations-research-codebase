"""Adversarial and reproducibility tests for the Stage 3 parser contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scb.telemetry.parse_openwrt_metrics import parse_openwrt_metrics
from scb.telemetry.parse_radius_logs import (
    parse_radius_acct_log,
    parse_radius_auth_log,
)
from scb.telemetry.parse_tc_stats import parse_tc_stats
from scb.telemetry.parse_wireguard_stats import parse_wireguard_stats
from scb.telemetry.sample_processing import parse_all_samples, parse_sample_file

PARSED_AT = "2026-07-30T12:00:00Z"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _source(tmp_path: Path, name: str, line: str) -> Path:
    path = tmp_path / name
    path.write_text(line + "\n", encoding="utf-8")
    return path


@pytest.mark.parametrize(
    "line",
    [
        "2026-07-30T12:00:00Z AUTH subscriber_id_hash=h ap_id=a "
        "result=ACCEPT broken",
        "2026-07-30T12:00:00Z AUTH subscriber_id_hash=h ap_id=a "
        "result=ACCEPT latency_ms=1 unknown=x",
        "2026-07-30T12:00:00Z AUTH subscriber_id_hash=h ap_id=a "
        "result=ACCEPT result=REJECT latency_ms=1",
        "2026-07-30T12:00:00Z AUTH subscriber_id_hash=h ap_id=a result=ACCEPT",
        "2026-07-30T12:00:00 AUTH subscriber_id_hash=h ap_id=a "
        "result=ACCEPT latency_ms=1",
        "2026-07-30T12:00:00Z ACCT subscriber_id_hash=h ap_id=a "
        "result=ACCEPT latency_ms=1",
        "2026-07-30T12:00:00Z AUTH subscriber_id_hash=h ap_id=a "
        "result=MAYBE latency_ms=1",
        "2026-07-30T12:00:00Z AUTH subscriber_id_hash=h ap_id=a "
        "result=ACCEPT latency_ms=-1",
    ],
)
def test_radius_auth_rejects_contract_violations(tmp_path: Path, line: str) -> None:
    path = _source(tmp_path, "auth.log", line)
    with pytest.raises(ValueError):
        parse_radius_auth_log(path, tmp_path, "test")


def test_radius_accounting_rejects_negative_counter(tmp_path: Path) -> None:
    path = _source(
        tmp_path,
        "acct.log",
        "2026-07-30T12:00:00Z ACCT subscriber_id_hash=h ap_id=a "
        "session_id=s input_octets=-1 output_octets=1",
    )
    with pytest.raises(ValueError, match="non-negative"):
        parse_radius_acct_log(path, tmp_path, "test")


@pytest.mark.parametrize(
    "line",
    [
        "2026-07-30T12:00:00Z ap_id=a cpu_percent=1 ram_used_mb=1 "
        "ram_total_mb=2 irq_rate=1 load_avg=1 extra=x",
        "2026-07-30T12:00:00Z ap_id=a cpu_percent=101 ram_used_mb=1 "
        "ram_total_mb=2 irq_rate=1 load_avg=1",
        "2026-07-30T12:00:00Z ap_id=a cpu_percent=1 ram_used_mb=3 "
        "ram_total_mb=2 irq_rate=1 load_avg=1",
        "2026-07-30T12:00:00Z ap_id=a cpu_percent=nan ram_used_mb=1 "
        "ram_total_mb=2 irq_rate=1 load_avg=1",
        "2026-07-30T12:00:00 ap_id=a cpu_percent=1 ram_used_mb=1 "
        "ram_total_mb=2 irq_rate=1 load_avg=1",
    ],
)
def test_openwrt_rejects_contract_violations(tmp_path: Path, line: str) -> None:
    path = _source(tmp_path, "openwrt.txt", line)
    with pytest.raises(ValueError):
        parse_openwrt_metrics(path, tmp_path, "test")


@pytest.mark.parametrize(
    "line",
    [
        "interface=wg0 peer_id_hash=p rx_bytes=-1 tx_bytes=1 "
        "latest_handshake=2026-07-30T12:00:00Z",
        "interface=wg0 peer_id_hash=p rx_bytes=1 tx_bytes=1 "
        "latest_handshake=2026-07-30T12:00:00",
        "interface=wg0 peer_id_hash=p rx_bytes=1 tx_bytes=1",
        "interface=wg0 interface=wg1 peer_id_hash=p rx_bytes=1 tx_bytes=1 "
        "latest_handshake=2026-07-30T12:00:00Z",
        "interface=wg0 peer_id_hash=p rx_bytes=1 tx_bytes=1 broken",
    ],
)
def test_wireguard_rejects_contract_violations(tmp_path: Path, line: str) -> None:
    path = _source(tmp_path, "wireguard.txt", line)
    with pytest.raises(ValueError):
        parse_wireguard_stats(path, tmp_path, "test")


def test_tc_rejects_duplicate_class_ids(tmp_path: Path) -> None:
    line = (
        "class htb 1:10 root rate 10Mbit ceil 20Mbit sent 1 bytes "
        "1 packets 0 drops backlog 0b 0p requeues 0"
    )
    path = _source(tmp_path, "tc.txt", f"{line}\n{line}")
    with pytest.raises(ValueError, match="duplicate class_id"):
        parse_tc_stats(path, tmp_path, "test")


def test_tc_rejects_rate_above_ceil(tmp_path: Path) -> None:
    path = _source(
        tmp_path,
        "tc.txt",
        "class htb 1:10 root rate 30Mbit ceil 20Mbit sent 1 bytes "
        "1 packets 0 drops backlog 0b 0p requeues 0",
    )
    with pytest.raises(ValueError, match="rate exceeds ceil"):
        parse_tc_stats(path, tmp_path, "test")


@pytest.mark.parametrize("parser_name", ["radius", "tc", "openwrt", "wireguard"])
def test_all_parsers_reject_empty_sources(tmp_path: Path, parser_name: str) -> None:
    path = _source(tmp_path, "empty.txt", "# comments only")
    parsers = {
        "radius": parse_radius_auth_log,
        "tc": parse_tc_stats,
        "openwrt": parse_openwrt_metrics,
        "wireguard": parse_wireguard_stats,
    }
    with pytest.raises(ValueError, match="no data records"):
        parsers[parser_name](path, tmp_path, "test")


def test_parse_sample_file_stamps_one_time_and_exact_digest() -> None:
    root = _repo_root()
    path = root / "data" / "samples" / "radius_auth_sample.log"
    table = parse_sample_file(root, path, parsed_at=PARSED_AT)

    assert {row["parsed_at"] for row in table.rows} == {PARSED_AT}
    assert table.source_sha256 == hashlib.sha256(path.read_bytes()).hexdigest()
    assert table.source_file == "data/samples/radius_auth_sample.log"


def test_parse_all_samples_is_byte_reproducible(tmp_path: Path) -> None:
    root = _repo_root()
    first = tmp_path / "first"
    second = tmp_path / "second"
    parse_all_samples(root / "data" / "samples", first, parsed_at=PARSED_AT)
    parse_all_samples(root / "data" / "samples", second, parsed_at=PARSED_AT)

    first_files = sorted(path.name for path in first.iterdir())
    assert first_files == sorted(path.name for path in second.iterdir())
    for name in first_files:
        assert (first / name).read_bytes() == (second / name).read_bytes()

    summary = json.loads((first / "summary.json").read_text(encoding="utf-8"))
    assert summary["generated_at"] == PARSED_AT
    assert len(summary["source_sha256"]) == summary["files"] == 5
    assert set(summary["evidence_classes"]) == {"Synthetic"}


def test_parse_all_samples_rejects_empty_directory(tmp_path: Path) -> None:
    samples = tmp_path / "samples"
    samples.mkdir()
    with pytest.raises(ValueError, match="contains no files"):
        parse_all_samples(samples, tmp_path / "output", repo_root=tmp_path)


def test_parse_sample_file_rejects_source_outside_root(
    tmp_path: Path,
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = _source(
        tmp_path,
        "radius_auth_sample.log",
        "2026-07-30T12:00:00Z AUTH subscriber_id_hash=h ap_id=a "
        "result=ACCEPT latency_ms=1",
    )
    with pytest.raises(ValueError, match="outside repository root"):
        parse_sample_file(root, outside, parsed_at=PARSED_AT)
