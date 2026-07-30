"""Load and classify aggregate Stage 2 prototype evidence records.

The loader is intentionally small and strict. It reads local UTF-8 JSON
objects, checks common provenance fields, maps compact aggregate evidence
codes onto the repository's public :class:`EvidenceClass` enum, and rejects
mixed run identifiers. It does not repair malformed records or perform
record-specific JSON Schema validation.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

from scb.telemetry.schemas import EvidenceClass


COMMON_REQUIRED_FIELDS = (
    "run_id",
    "scenario_id",
    "evidence_class",
    "timestamp",
    "source",
)

_EVIDENCE_CLASS_BY_CODE = {
    "M": EvidenceClass.MEASURED,
    "E": EvidenceClass.EMULATED,
    "S": EvidenceClass.SIMULATED,
    "C": EvidenceClass.CONTEXTUAL,
}


@dataclass(frozen=True)
class PrototypeRun:
    """A deterministically loaded aggregate prototype evidence run.

    Attributes:
        run_id: Shared non-empty run identifier from every JSON record.
        records: Records ordered by their source filename.
        evidence_classes: Unique evidence classes in first-seen record order.
    """

    run_id: str
    records: tuple[dict[str, object], ...]
    evidence_classes: tuple[EvidenceClass, ...]


def load_json_record(path: Path) -> dict[str, object]:
    """Load one local UTF-8 JSON object without repairing its contents.

    Args:
        path: Path to one JSON record.

    Returns:
        The decoded JSON object.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
        IsADirectoryError: If ``path`` is not a regular file.
        ValueError: If the file is not UTF-8, contains invalid JSON, or has a
            non-object top-level value.
    """

    if not path.exists():
        raise FileNotFoundError(f"missing evidence record: {path}")
    if not path.is_file():
        raise IsADirectoryError(f"evidence record is not a file: {path}")

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"evidence record is not valid UTF-8: {path}"
        ) from exc

    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"invalid JSON evidence record: {path}: {exc.msg}"
        ) from exc

    if not isinstance(value, dict):
        raise ValueError(
            f"evidence record must contain a JSON object: {path}"
        )

    return value


def validate_required_fields(
    record: Mapping[str, object],
    required_fields: Iterable[str],
) -> None:
    """Reject a record that omits any required field.

    Missing names are sorted so failures are deterministic across callers.
    The function checks presence only; it does not synthesize defaults or
    validate record-specific field values.
    """

    missing = sorted(set(required_fields) - set(record))
    if missing:
        raise ValueError(
            f"missing required fields: {', '.join(missing)}"
        )


def classify_evidence_record(
    record: Mapping[str, object],
) -> EvidenceClass:
    """Map an aggregate ``M/E/S/C`` code to :class:`EvidenceClass`.

    ``Synthetic`` is intentionally not accepted here. It belongs to the raw
    telemetry sample layer, while aggregate Stage 2 schemas use only the four
    explicit evidence codes.
    """

    validate_required_fields(record, ("evidence_class",))
    code = record["evidence_class"]

    if not isinstance(code, str):
        raise ValueError("evidence_class must be a string code")

    try:
        return _EVIDENCE_CLASS_BY_CODE[code]
    except KeyError as exc:
        allowed = ", ".join(_EVIDENCE_CLASS_BY_CODE)
        raise ValueError(
            f"unsupported evidence_class code {code!r}; "
            f"expected one of: {allowed}"
        ) from exc


def load_prototype_run(run_dir: Path) -> PrototypeRun:
    """Load every direct ``*.json`` record in one prototype run directory.

    Files are ordered lexicographically by filename. Non-JSON files such as a
    run README are ignored. Every JSON object must contain the common Stage 2
    provenance fields and share one non-empty string ``run_id``.
    """

    if not run_dir.exists():
        raise FileNotFoundError(
            f"missing prototype run directory: {run_dir}"
        )
    if not run_dir.is_dir():
        raise NotADirectoryError(
            f"prototype run path is not a directory: {run_dir}"
        )

    record_paths = sorted(
        path
        for path in run_dir.glob("*.json")
        if path.is_file()
    )

    if not record_paths:
        raise ValueError(
            f"prototype run contains no JSON records: {run_dir}"
        )

    records: list[dict[str, object]] = []
    classifications: list[EvidenceClass] = []
    expected_run_id: str | None = None

    for path in record_paths:
        record = load_json_record(path)

        try:
            validate_required_fields(
                record,
                COMMON_REQUIRED_FIELDS,
            )
            evidence_class = classify_evidence_record(record)
        except ValueError as exc:
            raise ValueError(
                f"invalid prototype record {path.name}: {exc}"
            ) from exc

        run_id = record["run_id"]

        if not isinstance(run_id, str) or not run_id.strip():
            raise ValueError(
                f"invalid prototype record {path.name}: "
                "run_id must be a non-empty string"
            )

        if expected_run_id is None:
            expected_run_id = run_id
        elif run_id != expected_run_id:
            raise ValueError(
                f"inconsistent run_id in {path.name}: "
                f"expected {expected_run_id!r}, got {run_id!r}"
            )

        records.append(record)
        classifications.append(evidence_class)

    assert expected_run_id is not None

    return PrototypeRun(
        run_id=expected_run_id,
        records=tuple(records),
        evidence_classes=tuple(
            dict.fromkeys(classifications)
        ),
    )
