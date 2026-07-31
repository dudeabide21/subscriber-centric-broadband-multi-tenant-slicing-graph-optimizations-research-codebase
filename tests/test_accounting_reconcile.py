"""Tests for deterministic accounting counter reconciliation."""

import pytest

from scb.telemetry.accounting_reconcile import (
    AccountingReconciliation,
    reconcile_accounting_counters,
)


def test_exact_accounting_match_is_within_zero_tolerance() -> None:
    result = reconcile_accounting_counters(1200, 4500, 1200, 4500)

    assert result == AccountingReconciliation(
        radius_bytes_in=1200,
        radius_bytes_out=4500,
        gateway_bytes_in=1200,
        gateway_bytes_out=4500,
        input_mismatch=0,
        output_mismatch=0,
        byte_mismatch=0,
        tolerance_bytes=0,
        within_tolerance=True,
    )


def test_directional_mismatches_are_summed() -> None:
    result = reconcile_accounting_counters(
        1200,
        4500,
        1100,
        4700,
        tolerance_bytes=300,
    )

    assert result.input_mismatch == 100
    assert result.output_mismatch == 200
    assert result.byte_mismatch == 300
    assert result.within_tolerance is True


def test_mismatch_above_tolerance_fails() -> None:
    result = reconcile_accounting_counters(
        1200,
        4500,
        1100,
        4700,
        tolerance_bytes=299,
    )

    assert result.within_tolerance is False


def test_aggregate_fields_match_stage2_schema_names() -> None:
    result = reconcile_accounting_counters(1, 2, 1, 2)

    assert result.aggregate_fields() == {
        "radius_bytes_in": 1,
        "radius_bytes_out": 2,
        "gateway_bytes_in": 1,
        "gateway_bytes_out": 2,
        "byte_mismatch": 0,
        "within_tolerance": True,
    }


@pytest.mark.parametrize(
    "arguments",
    [
        (-1, 0, 0, 0),
        (0, -1, 0, 0),
        (0, 0, -1, 0),
        (0, 0, 0, -1),
    ],
)
def test_negative_counters_fail(arguments: tuple[int, int, int, int]) -> None:
    with pytest.raises(ValueError, match="non-negative"):
        reconcile_accounting_counters(*arguments)


@pytest.mark.parametrize("value", [True, 1.5, "1", None])
def test_non_integer_counter_types_fail(value: object) -> None:
    with pytest.raises(TypeError, match="must be an integer"):
        reconcile_accounting_counters(value, 0, 0, 0)  # type: ignore[arg-type]


def test_invalid_tolerance_fails() -> None:
    with pytest.raises(ValueError, match="tolerance_bytes"):
        reconcile_accounting_counters(0, 0, 0, 0, tolerance_bytes=-1)
