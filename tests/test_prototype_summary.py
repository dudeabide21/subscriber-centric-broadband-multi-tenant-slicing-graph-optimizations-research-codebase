"""Tests for deterministic Stage 2 prototype acceptance reporting."""

from __future__ import annotations

import copy
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scb.prototype import (
    PrototypeRun,
    load_prototype_run,
    render_prototype_summary,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_RUN_DIRECTORY = REPOSITORY_ROOT / "data" / "samples" / "prototype_run_001"
COMMITTED_REPORT = REPOSITORY_ROOT / "reports" / "prototype_run_001.md"
SUMMARY_SCRIPT = REPOSITORY_ROOT / "scripts" / "prototype" / "summarize_run.py"

REQUIRED_HEADINGS = (
    "# Prototype Acceptance Report — prototype_run_001",
    "## Acceptance statement",
    "## Run identity and provenance",
    "## Accepted subscriber path",
    "## Rejected subscriber path",
    "## Slice and shaping representation",
    "## Accounting consistency",
    "## Edge-resource snapshot",
    "## Limitations",
    "## Next live-lab steps",
)

REQUIRED_LIMITATIONS = (
    "This run is an emulated scaffold.",
    "It is not measured evidence.",
    "It does not validate FreeRADIUS execution.",
    "It does not validate OpenWrt behavior.",
    "It does not validate dynamic VLAN enforcement.",
    "It does not validate traffic-shaping enforcement.",
    "It does not validate cross-slice isolation.",
    "It does not validate Wi-Fi airtime.",
    "It does not prove AP CPU, RAM, or IRQ feasibility.",
    "It is not production-ready.",
)


@pytest.fixture
def sample_run() -> PrototypeRun:
    return load_prototype_run(SAMPLE_RUN_DIRECTORY)


def _copy_run(
    run: PrototypeRun,
    *,
    records: list[dict[str, object]] | None = None,
) -> PrototypeRun:
    copied_records = copy.deepcopy(list(run.records)) if records is None else records
    return PrototypeRun(
        run_id=run.run_id,
        records=tuple(copied_records),
        evidence_classes=run.evidence_classes,
    )


def _record_with(
    run: PrototypeRun,
    marker: str,
    **updates: object,
) -> list[dict[str, object]]:
    records = copy.deepcopy(list(run.records))
    for record in records:
        if marker in record:
            record.update(updates)
            return records
    raise AssertionError(f"fixture record marker not found: {marker}")


def test_fixture_run_renders_all_required_sections(
    sample_run: PrototypeRun,
) -> None:
    report = render_prototype_summary(sample_run)

    positions = [report.index(heading) for heading in REQUIRED_HEADINGS]

    assert positions == sorted(positions)
    assert report.endswith("\n")
    assert not report.endswith("\n\n")


def test_report_labels_fixture_evidence_as_emulated(
    sample_run: PrototypeRun,
) -> None:
    report = render_prototype_summary(sample_run)

    assert "| Evidence class | Emulated |" in report
    assert "not measured evidence" in report


def test_report_traces_accepted_subscriber_relationships(
    sample_run: PrototypeRun,
) -> None:
    report = render_prototype_summary(sample_run)

    for expected in (
        "subscriber-demo-001",
        "stage2-session-001",
        "acct-prototype-basic-001",
        "slice-basic",
        "110",
        "20 Mbps",
        "ap-lab-001",
    ):
        assert expected in report


def test_report_traces_rejected_subscriber_without_service(
    sample_run: PrototypeRun,
) -> None:
    report = render_prototype_summary(sample_run)

    assert "subscriber-demo-invalid" in report
    assert "invalid-subscriber" in report
    assert (
        "| subscriber-demo-invalid | reject | invalid-subscriber | "
        "not applicable | not applicable | no | no |"
    ) in report


def test_report_contains_all_mandatory_limitations(
    sample_run: PrototypeRun,
) -> None:
    report = render_prototype_summary(sample_run)

    for limitation in REQUIRED_LIMITATIONS:
        assert limitation in report


def test_record_order_does_not_change_output(
    sample_run: PrototypeRun,
) -> None:
    reversed_run = PrototypeRun(
        run_id=sample_run.run_id,
        records=tuple(reversed(sample_run.records)),
        evidence_classes=sample_run.evidence_classes,
    )

    assert render_prototype_summary(reversed_run) == (
        render_prototype_summary(sample_run)
    )


def test_render_does_not_mutate_records(
    sample_run: PrototypeRun,
) -> None:
    before = copy.deepcopy(sample_run.records)

    render_prototype_summary(sample_run)

    assert sample_run.records == before


def test_render_is_repeatable(sample_run: PrototypeRun) -> None:
    first = render_prototype_summary(sample_run)
    second = render_prototype_summary(sample_run)

    assert second == first


def test_unknown_record_signature_fails(
    sample_run: PrototypeRun,
) -> None:
    records = copy.deepcopy(list(sample_run.records))
    records[0] = {
        "run_id": sample_run.run_id,
        "scenario_id": "single-subscriber-policy-path",
        "evidence_class": "E",
        "timestamp": "2026-07-27T00:00:00Z",
        "source": "test",
    }

    with pytest.raises(
        ValueError,
        match="no recognized prototype record signature",
    ):
        render_prototype_summary(_copy_run(sample_run, records=records))


def test_ambiguous_record_signature_fails(
    sample_run: PrototypeRun,
) -> None:
    records = _record_with(
        sample_run,
        "auth_result",
        slice_id="ambiguous",
    )

    with pytest.raises(
        ValueError,
        match="ambiguous prototype record signatures",
    ):
        render_prototype_summary(_copy_run(sample_run, records=records))


def test_missing_report_field_fails(
    sample_run: PrototypeRun,
) -> None:
    records = copy.deepcopy(list(sample_run.records))
    for record in records:
        if "slice_id" in record:
            del record["rate_limit_mbps"]
            break

    with pytest.raises(
        ValueError,
        match="missing required fields: rate_limit_mbps",
    ):
        render_prototype_summary(_copy_run(sample_run, records=records))


def test_inconsistent_scenario_id_fails(
    sample_run: PrototypeRun,
) -> None:
    records = _record_with(
        sample_run,
        "cpu_ratio",
        scenario_id="different-scenario",
    )

    with pytest.raises(
        ValueError,
        match="one shared scenario_id",
    ):
        render_prototype_summary(_copy_run(sample_run, records=records))


@pytest.mark.parametrize(
    ("marker", "updates", "message"),
    [
        (
            "slice_id",
            {"subscriber_id": "unknown-subscriber"},
            "has no slice record",
        ),
        (
            "radius_bytes_in",
            {"session_id": "unknown-session"},
            "does not match an accepted subscriber session",
        ),
        (
            "cpu_ratio",
            {"ap_id": "unknown-ap"},
            "references unreported AP",
        ),
    ],
)
def test_broken_cross_record_relationship_fails(
    sample_run: PrototypeRun,
    marker: str,
    updates: dict[str, object],
    message: str,
) -> None:
    records = _record_with(sample_run, marker, **updates)

    with pytest.raises(ValueError, match=message):
        render_prototype_summary(_copy_run(sample_run, records=records))


def test_cli_output_equals_library_output(
    sample_run: PrototypeRun,
    tmp_path: Path,
) -> None:
    output = tmp_path / "report.md"
    environment = {
        **os.environ,
        "PYTHONPATH": str(REPOSITORY_ROOT / "src"),
        "TMPDIR": "/tmp",
    }

    completed = subprocess.run(
        [
            sys.executable,
            str(SUMMARY_SCRIPT),
            "--run-dir",
            str(SAMPLE_RUN_DIRECTORY),
            "--output",
            str(output),
        ],
        cwd=REPOSITORY_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout == ""
    assert completed.stderr == ""
    assert output.read_text(encoding="utf-8") == (render_prototype_summary(sample_run))


def test_cli_returns_nonzero_for_invalid_run(tmp_path: Path) -> None:
    output = tmp_path / "report.md"
    environment = {
        **os.environ,
        "PYTHONPATH": str(REPOSITORY_ROOT / "src"),
        "TMPDIR": "/tmp",
    }

    completed = subprocess.run(
        [
            sys.executable,
            str(SUMMARY_SCRIPT),
            "--run-dir",
            str(tmp_path / "missing"),
            "--output",
            str(output),
        ],
        cwd=REPOSITORY_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 1
    assert completed.stdout == ""
    assert "error: missing prototype run directory" in completed.stderr
    assert not output.exists()


def test_committed_report_matches_renderer(
    sample_run: PrototypeRun,
) -> None:
    assert COMMITTED_REPORT.read_text(encoding="utf-8") == (
        render_prototype_summary(sample_run)
    )


def test_report_has_no_machine_specific_path(
    sample_run: PrototypeRun,
) -> None:
    report = render_prototype_summary(sample_run)

    assert str(REPOSITORY_ROOT) not in report
    assert "/home/" not in report
    assert "/mnt/" not in report
    assert "Generated at" not in report
