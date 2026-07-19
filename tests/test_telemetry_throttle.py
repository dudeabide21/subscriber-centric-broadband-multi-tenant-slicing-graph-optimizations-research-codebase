from __future__ import annotations

import math
from dataclasses import FrozenInstanceError

import pytest

from scb.telemetry.throttle import (
    TelemetryThrottleReport,
    system_telemetry_interval,
    system_telemetry_report,
)


def test_normal_backhaul_and_zero_cpu_returns_base_interval() -> None:
    result = system_telemetry_interval(
        delta_t_base=10.0,
        delta_t_sys_max=60.0,
        b_curr=100.0,
        b_nominal=100.0,
        cpu_ratio=0.0,
        kappa_b=1.0,
        kappa_cpu=0.5,
    )

    assert result == pytest.approx(10.0)


def test_backhaul_degradation_increases_interval() -> None:
    normal = system_telemetry_interval(
        10.0,
        60.0,
        100.0,
        100.0,
        0.0,
        1.0,
        0.0,
    )
    degraded = system_telemetry_interval(
        10.0,
        60.0,
        50.0,
        100.0,
        0.0,
        1.0,
        0.0,
    )

    assert degraded > normal


def test_higher_cpu_pressure_increases_interval() -> None:
    low = system_telemetry_interval(
        10.0,
        60.0,
        100.0,
        100.0,
        0.2,
        0.0,
        1.0,
    )
    high = system_telemetry_interval(
        10.0,
        60.0,
        100.0,
        100.0,
        0.8,
        0.0,
        1.0,
    )

    assert high > low


def test_combined_pressure_exceeds_each_individual_pressure() -> None:
    backhaul_only = system_telemetry_interval(
        10.0,
        60.0,
        50.0,
        100.0,
        0.0,
        1.0,
        1.0,
    )
    cpu_only = system_telemetry_interval(
        10.0,
        60.0,
        100.0,
        100.0,
        0.5,
        1.0,
        1.0,
    )
    combined = system_telemetry_interval(
        10.0,
        60.0,
        50.0,
        100.0,
        0.5,
        1.0,
        1.0,
    )

    assert combined > backhaul_only
    assert combined > cpu_only


def test_backhaul_above_nominal_does_not_add_penalty() -> None:
    nominal = system_telemetry_interval(
        10.0,
        60.0,
        100.0,
        100.0,
        0.4,
        1.0,
        0.5,
    )
    above_nominal = system_telemetry_interval(
        10.0,
        60.0,
        150.0,
        100.0,
        0.4,
        1.0,
        0.5,
    )

    assert above_nominal == pytest.approx(nominal)


def test_large_exponent_clamps_to_system_maximum() -> None:
    result = system_telemetry_interval(
        delta_t_base=10.0,
        delta_t_sys_max=30.0,
        b_curr=0.0,
        b_nominal=100.0,
        cpu_ratio=1.0,
        kappa_b=5.0,
        kappa_cpu=5.0,
    )

    assert result == 30.0


def test_result_is_never_below_base_interval() -> None:
    result = system_telemetry_interval(
        10.0,
        60.0,
        200.0,
        100.0,
        0.0,
        0.0,
        0.0,
    )

    assert result >= 10.0


def test_result_is_a_float() -> None:
    result = system_telemetry_interval(
        10,
        60,
        100,
        100,
        0,
        0,
        0,
    )

    assert type(result) is float


def test_zero_base_interval_fails() -> None:
    with pytest.raises(ValueError):
        system_telemetry_interval(
            0.0,
            60.0,
            100.0,
            100.0,
            0.0,
            1.0,
            1.0,
        )


def test_negative_base_interval_fails() -> None:
    with pytest.raises(ValueError):
        system_telemetry_interval(
            -1.0,
            60.0,
            100.0,
            100.0,
            0.0,
            1.0,
            1.0,
        )


def test_system_maximum_below_base_fails() -> None:
    with pytest.raises(ValueError):
        system_telemetry_interval(
            10.0,
            9.0,
            100.0,
            100.0,
            0.0,
            1.0,
            1.0,
        )


def test_negative_current_backhaul_fails() -> None:
    with pytest.raises(ValueError):
        system_telemetry_interval(
            10.0,
            60.0,
            -1.0,
            100.0,
            0.0,
            1.0,
            1.0,
        )


def test_zero_nominal_backhaul_fails() -> None:
    with pytest.raises(ValueError):
        system_telemetry_interval(
            10.0,
            60.0,
            50.0,
            0.0,
            0.0,
            1.0,
            1.0,
        )


def test_negative_nominal_backhaul_fails() -> None:
    with pytest.raises(ValueError):
        system_telemetry_interval(
            10.0,
            60.0,
            50.0,
            -100.0,
            0.0,
            1.0,
            1.0,
        )


def test_cpu_ratio_below_zero_fails() -> None:
    with pytest.raises(ValueError):
        system_telemetry_interval(
            10.0,
            60.0,
            100.0,
            100.0,
            -0.01,
            1.0,
            1.0,
        )


def test_cpu_ratio_above_one_fails() -> None:
    with pytest.raises(ValueError):
        system_telemetry_interval(
            10.0,
            60.0,
            100.0,
            100.0,
            1.01,
            1.0,
            1.0,
        )


def test_negative_kappa_b_fails() -> None:
    with pytest.raises(ValueError):
        system_telemetry_interval(
            10.0,
            60.0,
            100.0,
            100.0,
            0.5,
            -0.1,
            1.0,
        )


def test_negative_kappa_cpu_fails() -> None:
    with pytest.raises(ValueError):
        system_telemetry_interval(
            10.0,
            60.0,
            100.0,
            100.0,
            0.5,
            1.0,
            -0.1,
        )


def test_nan_input_fails() -> None:
    with pytest.raises(ValueError):
        system_telemetry_interval(
            10.0,
            60.0,
            100.0,
            100.0,
            math.nan,
            1.0,
            1.0,
        )


def test_positive_infinity_input_fails() -> None:
    with pytest.raises(ValueError):
        system_telemetry_interval(
            10.0,
            60.0,
            math.inf,
            100.0,
            0.5,
            1.0,
            1.0,
        )


def test_negative_infinity_input_fails() -> None:
    with pytest.raises(ValueError):
        system_telemetry_interval(
            10.0,
            60.0,
            100.0,
            100.0,
            0.5,
            -math.inf,
            1.0,
        )


def test_non_numeric_input_fails() -> None:
    with pytest.raises(ValueError):
        system_telemetry_interval(
            10.0,
            60.0,
            100.0,
            100.0,
            "0.5",  # type: ignore[arg-type]
            1.0,
            1.0,
        )


def test_boolean_input_fails() -> None:
    with pytest.raises(ValueError):
        system_telemetry_interval(
            10.0,
            60.0,
            100.0,
            100.0,
            True,
            1.0,
            1.0,
        )


def test_zero_epsilon_fails() -> None:
    with pytest.raises(ValueError):
        system_telemetry_interval(
            10.0,
            60.0,
            100.0,
            100.0,
            0.5,
            1.0,
            1.0,
            epsilon=0.0,
        )


def test_negative_epsilon_fails() -> None:
    with pytest.raises(ValueError):
        system_telemetry_interval(
            10.0,
            60.0,
            100.0,
            100.0,
            0.5,
            1.0,
            1.0,
            epsilon=-1e-9,
        )


def test_sensitivities_are_not_required_to_sum_to_one() -> None:
    result = system_telemetry_interval(
        10.0,
        60.0,
        100.0,
        100.0,
        0.25,
        2.0,
        3.0,
    )

    assert result > 10.0


def test_zero_sensitivities_are_valid() -> None:
    result = system_telemetry_interval(
        10.0,
        60.0,
        0.0,
        100.0,
        1.0,
        0.0,
        0.0,
    )

    assert result == pytest.approx(10.0)


def test_realistic_telemetry_example() -> None:
    result = system_telemetry_interval(
        delta_t_base=10.0,
        delta_t_sys_max=60.0,
        b_curr=50.0,
        b_nominal=100.0,
        cpu_ratio=0.50,
        kappa_b=1.0,
        kappa_cpu=0.5,
        epsilon=1e-9,
    )

    expected = 10.0 * math.exp(0.75)

    assert result == pytest.approx(expected)


def test_realistic_report_contains_expected_values() -> None:
    report = system_telemetry_report(
        delta_t_base=10.0,
        delta_t_sys_max=60.0,
        b_curr=50.0,
        b_nominal=100.0,
        cpu_ratio=0.50,
        kappa_b=1.0,
        kappa_cpu=0.5,
        epsilon=1e-9,
    )

    assert isinstance(report, TelemetryThrottleReport)
    assert report.backhaul_degradation == pytest.approx(0.5)
    assert report.exponent == pytest.approx(0.75)
    assert report.raw_interval == pytest.approx(
        10.0 * math.exp(0.75)
    )
    assert report.delta_t_eff == pytest.approx(
        10.0 * math.exp(0.75)
    )
    assert report.clamped is False


def test_clamped_report_identifies_clamping() -> None:
    report = system_telemetry_report(
        10.0,
        30.0,
        0.0,
        100.0,
        1.0,
        5.0,
        5.0,
    )

    assert report.raw_interval > 30.0
    assert report.delta_t_eff == 30.0
    assert report.clamped is True


def test_report_uses_same_validation_path() -> None:
    with pytest.raises(ValueError):
        system_telemetry_report(
            10.0,
            60.0,
            -1.0,
            100.0,
            0.5,
            1.0,
            1.0,
        )


def test_report_inputs_are_read_only() -> None:
    report = system_telemetry_report(
        10.0,
        60.0,
        50.0,
        100.0,
        0.5,
        1.0,
        0.5,
    )

    with pytest.raises(TypeError):
        report.inputs["b_curr"] = 75.0  # type: ignore[index]


def test_telemetry_report_is_frozen() -> None:
    report = system_telemetry_report(
        10.0,
        60.0,
        50.0,
        100.0,
        0.5,
        1.0,
        0.5,
    )

    with pytest.raises(FrozenInstanceError):
        report.delta_t_eff = 20.0  # type: ignore[misc]


def test_function_does_not_mutate_argument_container() -> None:
    arguments = {
        "delta_t_base": 10.0,
        "delta_t_sys_max": 60.0,
        "b_curr": 50.0,
        "b_nominal": 100.0,
        "cpu_ratio": 0.5,
        "kappa_b": 1.0,
        "kappa_cpu": 0.5,
    }
    original = dict(arguments)

    system_telemetry_interval(**arguments)

    assert arguments == original


def test_extreme_finite_sensitivities_clamp_without_overflow_error() -> None:
    result = system_telemetry_interval(
        10.0,
        60.0,
        0.0,
        100.0,
        1.0,
        1e308,
        1e308,
    )

    assert result == 60.0