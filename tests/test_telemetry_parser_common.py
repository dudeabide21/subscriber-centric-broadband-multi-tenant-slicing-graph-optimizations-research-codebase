"""Tests for shared strict telemetry parser utilities."""

from pathlib import Path

import pytest

from scb.telemetry.parser_common import (
    finite_float,
    nonnegative_int,
    parse_strict_key_values,
    read_utf8_text,
    repository_relative_source,
    require_records,
    source_sha256,
    validate_aware_timestamp,
)


def test_read_utf8_text_rejects_invalid_utf8(tmp_path: Path) -> None:
    path = tmp_path / "bad.log"
    path.write_bytes(b"\xff\xfe")

    with pytest.raises(ValueError, match="not valid UTF-8"):
        read_utf8_text(path)


def test_repository_relative_source_rejects_outside_path(
    tmp_path: Path,
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.log"
    outside.write_text("data\n", encoding="utf-8")

    with pytest.raises(ValueError, match="outside repository root"):
        repository_relative_source(outside, root)


@pytest.mark.parametrize(
    "timestamp",
    ["2026-07-30T12:00:00Z", "2026-07-30T17:45:00+05:45"],
)
def test_validate_aware_timestamp_accepts_offsets(timestamp: str) -> None:
    assert validate_aware_timestamp(timestamp) == timestamp


@pytest.mark.parametrize(
    "timestamp",
    ["", "not-a-time", "2026-07-30T12:00:00"],
)
def test_validate_aware_timestamp_rejects_invalid_values(
    timestamp: str,
) -> None:
    with pytest.raises(ValueError):
        validate_aware_timestamp(timestamp)


def test_parse_strict_key_values_applies_aliases() -> None:
    values = parse_strict_key_values(
        ["result=ACCEPT", "latency_ms=1.5"],
        allowed_keys={"auth_result", "auth_latency_ms"},
        required_keys={"auth_result", "auth_latency_ms"},
        aliases={
            "result": "auth_result",
            "latency_ms": "auth_latency_ms",
        },
        context="radius",
    )

    assert values == {
        "auth_result": "ACCEPT",
        "auth_latency_ms": "1.5",
    }


@pytest.mark.parametrize(
    ("tokens", "message"),
    [
        (["broken"], "malformed token"),
        (["unknown=x"], "unknown key"),
        (["a=1", "a=2"], "duplicate key"),
        (["a="], "empty key or value"),
        ([], "missing keys"),
    ],
)
def test_parse_strict_key_values_rejects_bad_tokens(
    tokens: list[str],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        parse_strict_key_values(
            tokens,
            allowed_keys={"a"},
            required_keys={"a"},
            context="test",
        )


@pytest.mark.parametrize("value", ["0", "42"])
def test_nonnegative_int_accepts_valid_values(value: str) -> None:
    assert nonnegative_int(value, field="counter") == int(value)


@pytest.mark.parametrize("value", ["-1", "1.5", "nan"])
def test_nonnegative_int_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        nonnegative_int(value, field="counter")


@pytest.mark.parametrize("value", ["0", "1.5", "2e2"])
def test_finite_float_accepts_valid_values(value: str) -> None:
    assert finite_float(value, field="metric") == pytest.approx(float(value))


@pytest.mark.parametrize("value", ["-1", "nan", "inf", "x"])
def test_finite_float_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        finite_float(value, field="metric")


def test_require_records_rejects_empty_source() -> None:
    with pytest.raises(ValueError, match="no data records"):
        require_records([], context="source")


def test_source_sha256_hashes_exact_bytes(tmp_path: Path) -> None:
    path = tmp_path / "source.log"
    path.write_bytes(b"abc")

    assert source_sha256(path) == (
        "ba7816bf8f01cfea414140de5dae2223" "b00361a396177a9cb410ff61f20015ad"
    )
