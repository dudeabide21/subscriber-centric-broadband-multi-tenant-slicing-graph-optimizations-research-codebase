from __future__ import annotations

import math

import pytest

from scb.common.weights import (
    is_simplex_weights,
    validate_beta_weights,
    validate_nonnegative_sensitivities,
    validate_omega_weights,
    validate_psi_weights,
    validate_simplex_weights,
    validate_zeta_weights,
)


def test_valid_simplex_list_passes() -> None:
    result = validate_simplex_weights([0.2, 0.3, 0.5])

    assert result == (0.2, 0.3, 0.5)
    assert isinstance(result, tuple)
    assert all(isinstance(value, float) for value in result)


def test_valid_simplex_integer_values_are_converted_to_floats() -> None:
    result = validate_simplex_weights([1, 0])

    assert result == (1.0, 0.0)
    assert all(type(value) is float for value in result)


def test_valid_simplex_mapping_preserves_insertion_order() -> None:
    weights = {
        "third": 0.2,
        "first": 0.5,
        "second": 0.3,
    }

    result = validate_simplex_weights(weights)

    assert result == (0.2, 0.5, 0.3)


def test_zero_simplex_weights_are_allowed() -> None:
    result = validate_simplex_weights([0.0, 1.0, 0.0])

    assert result == (0.0, 1.0, 0.0)


def test_negative_simplex_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights([0.6, -0.1, 0.5])


def test_tiny_negative_simplex_value_fails_even_within_atol() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights(
            [-1e-12, 1.000000000001],
            atol=1e-9,
        )


def test_simplex_sum_below_one_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights([0.2, 0.3, 0.4])


def test_simplex_sum_above_one_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights([0.4, 0.4, 0.4])


def test_empty_simplex_sequence_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights([])


def test_empty_simplex_mapping_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights({})


def test_simplex_nan_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights([math.nan, 1.0])


def test_simplex_positive_infinity_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights([math.inf, 0.0])


def test_simplex_negative_infinity_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights([-math.inf, math.inf])


def test_simplex_non_numeric_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights([0.5, "0.5"])


def test_simplex_none_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights([0.5, None])


def test_simplex_complex_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights([0.5, 0.5 + 0.0j])


def test_simplex_boolean_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights([True, False])


def test_string_container_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights("0.5,0.5")


def test_bytes_container_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights(b"\x00\x01")


def test_bytearray_container_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights(bytearray([0, 1]))


def test_generator_input_fails() -> None:
    weights = (value for value in [0.5, 0.5])

    with pytest.raises(ValueError):
        validate_simplex_weights(weights)  # type: ignore[arg-type]


def test_simplex_sum_within_absolute_tolerance_passes() -> None:
    result = validate_simplex_weights(
        [0.5, 0.5000000005],
        atol=1e-9,
    )

    assert result == (0.5, 0.5000000005)


def test_simplex_sum_outside_absolute_tolerance_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights(
            [0.5, 0.50000001],
            atol=1e-9,
        )


def test_zero_atol_accepts_exact_simplex_sum() -> None:
    result = validate_simplex_weights(
        [0.25, 0.75],
        atol=0.0,
    )

    assert result == (0.25, 0.75)


def test_zero_atol_rejects_inexact_simplex_sum() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights(
            [0.5, 0.5000000005],
            atol=0.0,
        )


def test_negative_atol_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights([0.5, 0.5], atol=-1e-9)


def test_nan_atol_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights([0.5, 0.5], atol=math.nan)


def test_infinite_atol_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights([0.5, 0.5], atol=math.inf)


def test_non_numeric_atol_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights([0.5, 0.5], atol="1e-9")  # type: ignore[arg-type]


def test_boolean_atol_fails() -> None:
    with pytest.raises(ValueError):
        validate_simplex_weights([0.5, 0.5], atol=True)


def test_nonnegative_sensitivities_pass_when_sum_is_not_one() -> None:
    result = validate_nonnegative_sensitivities([2.0, 3.0, 4.0])

    assert result == (2.0, 3.0, 4.0)


def test_nonnegative_sensitivity_mapping_preserves_insertion_order() -> None:
    sensitivities = {
        "kappa_drop": 4.0,
        "kappa_rtt": 2.0,
        "kappa_cpu": 3.0,
    }

    result = validate_nonnegative_sensitivities(sensitivities)

    assert result == (4.0, 2.0, 3.0)


def test_zero_sensitivities_pass() -> None:
    result = validate_nonnegative_sensitivities([0.0, 0.0])

    assert result == (0.0, 0.0)


def test_integer_sensitivities_are_converted_to_floats() -> None:
    result = validate_nonnegative_sensitivities([1, 2, 3])

    assert result == (1.0, 2.0, 3.0)
    assert all(type(value) is float for value in result)


def test_empty_sensitivities_fail() -> None:
    with pytest.raises(ValueError):
        validate_nonnegative_sensitivities([])


def test_negative_sensitivity_fails() -> None:
    with pytest.raises(ValueError):
        validate_nonnegative_sensitivities([1.0, -0.1])


def test_sensitivity_nan_fails() -> None:
    with pytest.raises(ValueError):
        validate_nonnegative_sensitivities([1.0, math.nan])


def test_sensitivity_infinity_fails() -> None:
    with pytest.raises(ValueError):
        validate_nonnegative_sensitivities([1.0, math.inf])


def test_sensitivity_non_numeric_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_nonnegative_sensitivities([1.0, "invalid"])


def test_sensitivity_boolean_value_fails() -> None:
    with pytest.raises(ValueError):
        validate_nonnegative_sensitivities([True, 1.0])


def test_sensitivities_are_not_implicitly_normalized() -> None:
    result = validate_nonnegative_sensitivities([2.0, 3.0])

    assert result == (2.0, 3.0)
    assert math.fsum(result) == 5.0


def test_non_simplex_sensitivities_fail_simplex_validation() -> None:
    values = [2.0, 3.0, 4.0]

    assert validate_nonnegative_sensitivities(values) == (2.0, 3.0, 4.0)

    with pytest.raises(ValueError):
        validate_simplex_weights(values)


def test_is_simplex_weights_returns_true_for_valid_weights() -> None:
    assert is_simplex_weights([0.25, 0.75]) is True


def test_is_simplex_weights_returns_true_for_valid_mapping() -> None:
    assert is_simplex_weights({"first": 0.4, "second": 0.6}) is True


def test_is_simplex_weights_returns_false_for_negative_weight() -> None:
    assert is_simplex_weights([1.1, -0.1]) is False


def test_is_simplex_weights_returns_false_for_invalid_sum() -> None:
    assert is_simplex_weights([0.2, 0.2]) is False


def test_is_simplex_weights_returns_false_for_empty_input() -> None:
    assert is_simplex_weights([]) is False


def test_is_simplex_weights_returns_false_for_nan() -> None:
    assert is_simplex_weights([math.nan, 1.0]) is False


def test_is_simplex_weights_returns_false_for_non_numeric_value() -> None:
    assert is_simplex_weights([0.5, "invalid"]) is False


def test_is_simplex_weights_returns_false_for_invalid_atol() -> None:
    assert is_simplex_weights([0.5, 0.5], atol=-1e-9) is False


def test_simplex_error_message_contains_custom_name() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_simplex_weights([], name="beta")

    assert "beta" in str(exc_info.value)


def test_simplex_negative_value_error_contains_custom_name() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_simplex_weights(
            [1.1, -0.1],
            name="omega coefficients",
        )

    assert "omega coefficients" in str(exc_info.value)


def test_simplex_sum_error_contains_custom_name() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_simplex_weights(
            [0.2, 0.2],
            name="zeta coefficients",
        )

    assert "zeta coefficients" in str(exc_info.value)


def test_simplex_atol_error_contains_custom_name() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_simplex_weights(
            [0.5, 0.5],
            name="psi coefficients",
            atol=-1.0,
        )

    assert "psi coefficients" in str(exc_info.value)


def test_sensitivity_error_message_contains_custom_name() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_nonnegative_sensitivities(
            [1.0, -1.0],
            name="kappa coefficients",
        )

    assert "kappa coefficients" in str(exc_info.value)


def test_validate_beta_weights_passes() -> None:
    result = validate_beta_weights([0.25, 0.25, 0.25, 0.25])

    assert result == (0.25, 0.25, 0.25, 0.25)


def test_validate_omega_weights_passes() -> None:
    result = validate_omega_weights([0.4, 0.6])

    assert result == (0.4, 0.6)


def test_validate_psi_weights_passes() -> None:
    result = validate_psi_weights([0.2, 0.2, 0.2, 0.2, 0.2])

    assert result == (0.2, 0.2, 0.2, 0.2, 0.2)


def test_validate_zeta_weights_passes() -> None:
    result = validate_zeta_weights([0.1, 0.2, 0.3, 0.4])

    assert result == (0.1, 0.2, 0.3, 0.4)


def test_beta_wrapper_rejects_invalid_sum() -> None:
    with pytest.raises(ValueError):
        validate_beta_weights([0.2, 0.2])


def test_omega_wrapper_rejects_negative_value() -> None:
    with pytest.raises(ValueError):
        validate_omega_weights([1.1, -0.1])


def test_psi_wrapper_rejects_invalid_sum() -> None:
    with pytest.raises(ValueError):
        validate_psi_weights([0.1, 0.1, 0.1, 0.1, 0.1])


def test_zeta_wrapper_rejects_non_finite_value() -> None:
    with pytest.raises(ValueError):
        validate_zeta_weights([0.2, 0.2, 0.2, 0.2, math.inf])


def test_beta_wrapper_error_identifies_beta_weights() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_beta_weights([0.2, 0.2])

    assert "beta weights" in str(exc_info.value)


def test_omega_wrapper_error_identifies_omega_weights() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_omega_weights([0.2, 0.2])

    assert "omega weights" in str(exc_info.value)


def test_psi_wrapper_error_identifies_psi_weights() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_psi_weights([0.2, 0.2])

    assert "psi weights" in str(exc_info.value)


def test_zeta_wrapper_error_identifies_zeta_weights() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_zeta_weights([0.2, 0.2])

    assert "zeta weights" in str(exc_info.value)