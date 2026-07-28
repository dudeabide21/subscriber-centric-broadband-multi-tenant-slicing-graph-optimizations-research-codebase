"""Tests for strict Stage 2 prototype evidence loading."""

from __future__ import annotations

import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from scb.prototype.evidence import (
    COMMON_REQUIRED_FIELDS,
    PrototypeRun,
    classify_evidence_record,
    load_json_record,
    load_prototype_run,
    validate_required_fields,
)
from scb.telemetry.schemas import EvidenceClass


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_RUN_DIRECTORY = (
    REPOSITORY_ROOT
    / "data"
    / "samples"
    / "prototype_run_001"
)


def _record(
    *,
    run_id: object = "prototype_run_test",
    evidence_class: object = "E",
) -> dict[str, object]:
    return {
        "run_id": run_id,
        "scenario_id": "test-scenario",
        "evidence_class": evidence_class,
        "timestamp": "2026-07-27T00:00:00Z",
        "source": "test-fixture",
    }


def _write_json(
    directory: Path,
    name: str,
    value: object,
) -> Path:
    path = directory / name
    path.write_text(
        json.dumps(value, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def test_load_json_record_returns_object(
    tmp_path: Path,
) -> None:
    path = _write_json(
        tmp_path,
        "record.json",
        _record(),
    )

    assert load_json_record(path) == _record()


def test_load_json_record_rejects_missing_path(
    tmp_path: Path,
) -> None:
    path = tmp_path / "missing.json"

    with pytest.raises(
        FileNotFoundError,
        match="missing evidence record",
    ):
        load_json_record(path)


def test_load_json_record_rejects_directory(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        IsADirectoryError,
        match="not a file",
    ):
        load_json_record(tmp_path)


def test_load_json_record_rejects_invalid_utf8(
    tmp_path: Path,
) -> None:
    path = tmp_path / "invalid-utf8.json"
    path.write_bytes(b"\xff\xfe\x00")

    with pytest.raises(
        ValueError,
        match="not valid UTF-8",
    ):
        load_json_record(path)


def test_load_json_record_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    path = tmp_path / "invalid.json"
    path.write_text(
        '{"run_id":',
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="invalid JSON evidence record",
    ):
        load_json_record(path)


def test_load_json_record_rejects_non_object_json(
    tmp_path: Path,
) -> None:
    path = _write_json(
        tmp_path,
        "records.json",
        [_record()],
    )

    with pytest.raises(
        ValueError,
        match="must contain a JSON object",
    ):
        load_json_record(path)


def test_validate_required_fields_accepts_complete_record() -> None:
    validate_required_fields(
        _record(),
        COMMON_REQUIRED_FIELDS,
    )


def test_validate_required_fields_sorts_missing_names() -> None:
    record = {
        "source": "test-fixture",
    }

    with pytest.raises(ValueError) as exc_info:
        validate_required_fields(
            record,
            (
                "timestamp",
                "run_id",
                "source",
                "evidence_class",
            ),
        )

    assert str(exc_info.value) == (
        "missing required fields: "
        "evidence_class, run_id, timestamp"
    )


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("M", EvidenceClass.MEASURED),
        ("E", EvidenceClass.EMULATED),
        ("S", EvidenceClass.SIMULATED),
        ("C", EvidenceClass.CONTEXTUAL),
    ],
)
def test_classify_evidence_record_maps_aggregate_codes(
    code: str,
    expected: EvidenceClass,
) -> None:
    assert classify_evidence_record(
        {"evidence_class": code}
    ) is expected


def test_classify_evidence_record_rejects_missing_code() -> None:
    with pytest.raises(
        ValueError,
        match="missing required fields",
    ):
        classify_evidence_record({})


def test_classify_evidence_record_rejects_non_string_code() -> None:
    with pytest.raises(
        ValueError,
        match="must be a string code",
    ):
        classify_evidence_record(
            {"evidence_class": 1}
        )


def test_classify_evidence_record_rejects_unknown_code() -> None:
    with pytest.raises(
        ValueError,
        match="unsupported evidence_class code",
    ):
        classify_evidence_record(
            {"evidence_class": "Synthetic"}
        )


def test_load_prototype_run_orders_records_and_ignores_readme(
    tmp_path: Path,
) -> None:
    _write_json(
        tmp_path,
        "z-record.json",
        _record(),
    )

    first = _record()
    first["source"] = "alphabetically-first"

    _write_json(
        tmp_path,
        "a-record.json",
        first,
    )

    (tmp_path / "README.md").write_text(
        "ignored\n",
        encoding="utf-8",
    )

    run = load_prototype_run(tmp_path)

    assert run.run_id == "prototype_run_test"
    assert [
        record["source"]
        for record in run.records
    ] == [
        "alphabetically-first",
        "test-fixture",
    ]
    assert run.evidence_classes == (
        EvidenceClass.EMULATED,
    )


def test_load_prototype_run_collects_unique_evidence_classes(
    tmp_path: Path,
) -> None:
    _write_json(
        tmp_path,
        "a-measured.json",
        _record(evidence_class="M"),
    )
    _write_json(
        tmp_path,
        "b-emulated.json",
        _record(evidence_class="E"),
    )
    _write_json(
        tmp_path,
        "c-measured.json",
        _record(evidence_class="M"),
    )

    run = load_prototype_run(tmp_path)

    assert run.evidence_classes == (
        EvidenceClass.MEASURED,
        EvidenceClass.EMULATED,
    )


def test_load_prototype_run_rejects_missing_directory(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        FileNotFoundError,
        match="missing prototype run",
    ):
        load_prototype_run(
            tmp_path / "missing"
        )


def test_load_prototype_run_rejects_file_path(
    tmp_path: Path,
) -> None:
    path = _write_json(
        tmp_path,
        "record.json",
        _record(),
    )

    with pytest.raises(
        NotADirectoryError,
        match="not a directory",
    ):
        load_prototype_run(path)


def test_load_prototype_run_rejects_empty_directory(
    tmp_path: Path,
) -> None:
    (tmp_path / "README.md").write_text(
        "no records\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="contains no JSON records",
    ):
        load_prototype_run(tmp_path)


def test_load_prototype_run_reports_missing_common_field(
    tmp_path: Path,
) -> None:
    record = _record()
    del record["source"]

    _write_json(
        tmp_path,
        "broken.json",
        record,
    )

    with pytest.raises(ValueError) as exc_info:
        load_prototype_run(tmp_path)

    assert str(exc_info.value) == (
        "invalid prototype record broken.json: "
        "missing required fields: source"
    )


def test_load_prototype_run_rejects_empty_run_id(
    tmp_path: Path,
) -> None:
    _write_json(
        tmp_path,
        "record.json",
        _record(run_id="  "),
    )

    with pytest.raises(
        ValueError,
        match="run_id must be a non-empty string",
    ):
        load_prototype_run(tmp_path)


def test_load_prototype_run_rejects_inconsistent_run_ids(
    tmp_path: Path,
) -> None:
    _write_json(
        tmp_path,
        "a-record.json",
        _record(run_id="run-one"),
    )
    _write_json(
        tmp_path,
        "b-record.json",
        _record(run_id="run-two"),
    )

    with pytest.raises(ValueError) as exc_info:
        load_prototype_run(tmp_path)

    assert str(exc_info.value) == (
        "inconsistent run_id in b-record.json: "
        "expected 'run-one', got 'run-two'"
    )


def test_prototype_run_is_frozen() -> None:
    run = PrototypeRun(
        run_id="prototype_run_test",
        records=(_record(),),
        evidence_classes=(
            EvidenceClass.EMULATED,
        ),
    )

    with pytest.raises(FrozenInstanceError):
        run.run_id = "changed"  # type: ignore[misc]


def test_load_repository_stage2_sample_run() -> None:
    run = load_prototype_run(
        SAMPLE_RUN_DIRECTORY
    )

    assert run.run_id == "prototype_run_001"
    assert len(run.records) == 5
    assert run.evidence_classes == (
        EvidenceClass.EMULATED,
    )
