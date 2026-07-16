from __future__ import annotations

import math
from dataclasses import FrozenInstanceError

import pytest

from scb.common.parameters import (
    BackhaulCapacity,
    DEFAULT_DELTA_MIN,
    DELTA_MIN_SENSITIVITY_SET,
    TokenTiming,
    validate_backhaul_capacity,
    validate_delta_min,
    validate_token_timing,
)


def test_default_delta_min_is_point_zero_five() -> None:
    assert DEFAULT_DELTA_MIN == 0.05


def test_delta_min_sensitivity_set_matches_manuscript() -> None:
    assert DELTA_MIN_SENSITIVITY_SET == (0.02, 0.05, 0.10)


def test_delta_min_sensitivity_set_is_tuple() -> None:
    assert isinstance(DELTA_MIN_SENSITIVITY_SET, tuple)


def test_valid_delta_min_passes() -> None:
    result = validate_delta_min(0.05)

    assert result == 0.05
    assert type(result) is float


def test_integer_delta_min_is_converted_to_float_before_bounds_check() -> None:
    with pytest.raises(ValueError):
        validate_delta_min(1)


def test_delta_min_zero_fails() -> None:
    with pytest.raises(ValueError):
        validate_delta_min(0.0)


def test_negative_delta_min_fails() -> None:
    with pytest.raises(ValueError):
        validate_delta_min(-0.01)


def test_delta_min_one_fails() -> None:
    with pytest.raises(ValueError):
        validate_delta_min(1.0)


def test_delta_min_above_one_fails() -> None:
    with pytest.raises(ValueError):
        validate_delta_min(1.01)


def test_delta_min_nan_fails() -> None:
    with pytest.raises(ValueError):
        validate_delta_min(math.nan)


def test_delta_min_positive_infinity_fails() -> None:
    with pytest.raises(ValueError):
        validate_delta_min(math.inf)


def test_delta_min_negative_infinity_fails() -> None:
    with pytest.raises(ValueError):
        validate_delta_min(-math.inf)


def test_delta_min_non_numeric_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_delta_min("0.05")  # type: ignore[arg-type]


def test_delta_min_none_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_delta_min(None)  # type: ignore[arg-type]


def test_delta_min_complex_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_delta_min(0.05 + 0.0j)  # type: ignore[arg-type]


def test_delta_min_boolean_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_delta_min(True)


def test_delta_min_error_identifies_parameter() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_delta_min(0.0)

    assert "delta_min" in str(exc_info.value)


def test_valid_token_timing_returns_frozen_dataclass_values() -> None:
    result = validate_token_timing(30.0, 60.0)

    assert isinstance(result, TokenTiming)
    assert result.t_token == 30.0
    assert result.t_rot == 60.0
    assert type(result.t_token) is float
    assert type(result.t_rot) is float


def test_integer_token_timing_values_are_converted_to_floats() -> None:
    result = validate_token_timing(30, 60)

    assert result == TokenTiming(t_token=30.0, t_rot=60.0)
    assert type(result.t_token) is float
    assert type(result.t_rot) is float


def test_token_timing_dataclass_is_frozen() -> None:
    result = validate_token_timing(30.0, 60.0)

    with pytest.raises(FrozenInstanceError):
        result.t_token = 40.0  # type: ignore[misc]


def test_token_timing_equal_values_fail() -> None:
    with pytest.raises(ValueError):
        validate_token_timing(60.0, 60.0)


def test_token_timing_token_greater_than_rotation_fails() -> None:
    with pytest.raises(ValueError):
        validate_token_timing(61.0, 60.0)


def test_zero_token_window_fails() -> None:
    with pytest.raises(ValueError):
        validate_token_timing(0.0, 60.0)


def test_negative_token_window_fails() -> None:
    with pytest.raises(ValueError):
        validate_token_timing(-1.0, 60.0)


def test_zero_rotation_period_fails() -> None:
    with pytest.raises(ValueError):
        validate_token_timing(30.0, 0.0)


def test_negative_rotation_period_fails() -> None:
    with pytest.raises(ValueError):
        validate_token_timing(30.0, -60.0)


def test_token_window_nan_fails() -> None:
    with pytest.raises(ValueError):
        validate_token_timing(math.nan, 60.0)


def test_rotation_period_nan_fails() -> None:
    with pytest.raises(ValueError):
        validate_token_timing(30.0, math.nan)


def test_token_window_infinity_fails() -> None:
    with pytest.raises(ValueError):
        validate_token_timing(math.inf, 60.0)


def test_rotation_period_infinity_fails() -> None:
    with pytest.raises(ValueError):
        validate_token_timing(30.0, math.inf)


def test_token_window_non_numeric_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_token_timing("30", 60.0)  # type: ignore[arg-type]


def test_rotation_period_non_numeric_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_token_timing(30.0, "60")  # type: ignore[arg-type]


def test_token_window_boolean_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_token_timing(True, 60.0)


def test_rotation_period_boolean_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_token_timing(30.0, False)


def test_token_timing_error_identifies_t_token() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_token_timing(0.0, 60.0)

    assert "t_token" in str(exc_info.value)


def test_token_timing_error_identifies_t_rot() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_token_timing(30.0, 0.0)

    assert "t_rot" in str(exc_info.value)


def test_token_ordering_error_identifies_both_parameters() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_token_timing(60.0, 60.0)

    message = str(exc_info.value)
    assert "t_token" in message
    assert "t_rot" in message


def test_valid_backhaul_capacity_returns_frozen_dataclass_values() -> None:
    result = validate_backhaul_capacity(50.0, 100.0)

    assert isinstance(result, BackhaulCapacity)
    assert result.b_curr == 50.0
    assert result.b_nominal == 100.0
    assert type(result.b_curr) is float
    assert type(result.b_nominal) is float


def test_integer_backhaul_values_are_converted_to_floats() -> None:
    result = validate_backhaul_capacity(50, 100)

    assert result == BackhaulCapacity(
        b_curr=50.0,
        b_nominal=100.0,
    )
    assert type(result.b_curr) is float
    assert type(result.b_nominal) is float


def test_backhaul_capacity_dataclass_is_frozen() -> None:
    result = validate_backhaul_capacity(50.0, 100.0)

    with pytest.raises(FrozenInstanceError):
        result.b_curr = 75.0  # type: ignore[misc]


def test_zero_current_backhaul_capacity_passes() -> None:
    result = validate_backhaul_capacity(0.0, 100.0)

    assert result == BackhaulCapacity(
        b_curr=0.0,
        b_nominal=100.0,
    )


def test_current_capacity_may_exceed_nominal_capacity() -> None:
    '''This test is intentional: the current backhaul capacity may exceed the nominal capacity.'''
    result = validate_backhaul_capacity(150.0, 100.0)

    assert result == BackhaulCapacity(
        b_curr=150.0,
        b_nominal=100.0,
    )


def test_negative_current_backhaul_capacity_fails() -> None:
    with pytest.raises(ValueError):
        validate_backhaul_capacity(-0.1, 100.0)


def test_zero_nominal_backhaul_capacity_fails() -> None:
    with pytest.raises(ValueError):
        validate_backhaul_capacity(0.0, 0.0)


def test_negative_nominal_backhaul_capacity_fails() -> None:
    with pytest.raises(ValueError):
        validate_backhaul_capacity(50.0, -100.0)


def test_current_backhaul_nan_fails() -> None:
    with pytest.raises(ValueError):
        validate_backhaul_capacity(math.nan, 100.0)


def test_nominal_backhaul_nan_fails() -> None:
    with pytest.raises(ValueError):
        validate_backhaul_capacity(50.0, math.nan)


def test_current_backhaul_positive_infinity_fails() -> None:
    with pytest.raises(ValueError):
        validate_backhaul_capacity(math.inf, 100.0)


def test_nominal_backhaul_positive_infinity_fails() -> None:
    with pytest.raises(ValueError):
        validate_backhaul_capacity(50.0, math.inf)


def test_current_backhaul_negative_infinity_fails() -> None:
    with pytest.raises(ValueError):
        validate_backhaul_capacity(-math.inf, 100.0)


def test_nominal_backhaul_negative_infinity_fails() -> None:
    with pytest.raises(ValueError):
        validate_backhaul_capacity(50.0, -math.inf)


def test_current_backhaul_non_numeric_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_backhaul_capacity("50", 100.0)  # type: ignore[arg-type]


def test_nominal_backhaul_non_numeric_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_backhaul_capacity(50.0, "100")  # type: ignore[arg-type]


def test_current_backhaul_none_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_backhaul_capacity(None, 100.0)  # type: ignore[arg-type]


def test_nominal_backhaul_none_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_backhaul_capacity(50.0, None)  # type: ignore[arg-type]


def test_current_backhaul_boolean_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_backhaul_capacity(True, 100.0)


def test_nominal_backhaul_boolean_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_backhaul_capacity(50.0, False)


def test_backhaul_error_identifies_b_curr() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_backhaul_capacity(-1.0, 100.0)

    assert "b_curr" in str(exc_info.value)


def test_backhaul_error_identifies_b_nominal() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_backhaul_capacity(50.0, 0.0)

    assert "b_nominal" in str(exc_info.value)