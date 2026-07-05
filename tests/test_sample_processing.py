"""Integration tests for the sample processing driver."""

from __future__ import annotations

import json
from pathlib import Path

from scb.telemetry.sample_processing import main, parse_all_samples, parse_sample_file


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_parse_sample_file_tags_records_synthetic() -> None:
    root = _repo_root()
    table = parse_sample_file(
        root, root / "data" / "samples" / "radius_auth_sample.log"
    )
    assert table.stem == "radius_auth_sample"
    assert len(table.rows) == 2
    assert table.rows[0]["evidence_class"] == "Synthetic"
    assert table.rows[0]["event_type"] == "AUTH"


def test_parse_all_samples_writes_outputs(tmp_path: Path) -> None:
    root = _repo_root()
    tables = parse_all_samples(root / "data" / "samples", tmp_path)
    assert len(tables) == 5
    assert (tmp_path / "tc_stats_sample.csv").exists()
    assert (tmp_path / "wireguard_stats_sample.json").exists()
    summary = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert summary["files"] == 5
    assert summary["sample_count"] >= 5
    assert summary["evidence_classes"].get("Synthetic", 0) == summary["sample_count"]


def test_main_runs_successfully(tmp_path: Path) -> None:
    root = _repo_root()
    rc = main(
        [
            "--samples-dir",
            str(root / "data" / "samples"),
            "--output-dir",
            str(tmp_path),
        ]
    )
    assert rc == 0
    assert (tmp_path / "summary.json").exists()
