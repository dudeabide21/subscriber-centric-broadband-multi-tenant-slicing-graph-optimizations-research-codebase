from __future__ import annotations

import math
from dataclasses import FrozenInstanceError

import pytest

from scb.queueing.effective_service import (
    EffectiveServiceReport,
    effective_service_capacity,
    effective_service_capacity_from_sequence,
    effective_service_report,
)


def test_effective_service_capacity_returns_minimum() -> None:
    result = effective_service_capacity(
        50.0,
        25.0,
        40.0,
        30.0,
        10.0,
    )

    assert result == 10.0


def test_realistic_effective_service_capacity_example() -> None:
    result = effective_service_capacity(
        50.0,
        35.0,
        40.0,
        30.0,
        25.0,
    )

    assert result == 25.0


def test_effective_service_capacity_returns_float_for_integer_inputs() -> None:
    result = effective_service_capacity(
        50,
        35,
        40,
        30,
        25,
    )

    assert result == 25.0
    assert type(result) is float


def test_effective_service_capacity_preserves_zero() -> None:
    result = effective_service_capacity(
        50.0,
        35.0,
        0.0,
        30.0,
        25.0,
    )

    assert result == 0.0


def test_effective_service_capacity_does_not_normalize_or_weight_inputs() -> None:
    result = effective_service_capacity(
        500.0,
        350.0,
        400.0,
        300.0,
        250.0,
    )

    assert result == 250.0


def test_effective_service_capacity_rejects_negative_capacity() -> None:
    with pytest.raises(ValueError):
        effective_service_capacity(
            50.0,
            35.0,
            -1.0,
            30.0,
            25.0,
        )


def test_effective_service_capacity_rejects_nan() -> None:
    with pytest.raises(ValueError):
        effective_service_capacity(
            50.0,
            35.0,
            math.nan,
            30.0,
            25.0,
        )


def test_effective_service_capacity_rejects_positive_infinity() -> None:
    with pytest.raises(ValueError):
        effective_service_capacity(
            50.0,
            35.0,
            math.inf,
            30.0,
            25.0,
        )


def test_effective_service_capacity_rejects_negative_infinity() -> None:
    with pytest.raises(ValueError):
        effective_service_capacity(
            50.0,
            35.0,
            -math.inf,
            30.0,
            25.0,
        )


def test_effective_service_capacity_rejects_non_numeric_value() -> None:
    with pytest.raises(ValueError):
        effective_service_capacity(
            50.0,
            "35.0",  # type: ignore[arg-type]
            40.0,
            30.0,
            25.0,
        )


def test_effective_service_capacity_rejects_none() -> None:
    with pytest.raises(ValueError):
        effective_service_capacity(
            50.0,
            None,  # type: ignore[arg-type]
            40.0,
            30.0,
            25.0,
        )


def test_effective_service_capacity_rejects_complex_value() -> None:
    with pytest.raises(ValueError):
        effective_service_capacity(
            50.0,
            35.0 + 0.0j,  # type: ignore[arg-type]
            40.0,
            30.0,
            25.0,
        )


def test_effective_service_capacity_rejects_boolean_value() -> None:
    with pytest.raises(ValueError):
        effective_service_capacity(
            50.0,
            True,
            40.0,
            30.0,
            25.0,
        )


def test_sequence_wrapper_returns_minimum() -> None:
    result = effective_service_capacity_from_sequence(
        [50.0, 25.0, 10.0]
    )

    assert result == 10.0


def test_sequence_wrapper_returns_float_for_integer_values() -> None:
    result = effective_service_capacity_from_sequence([50, 25, 10])

    assert result == 10.0
    assert type(result) is float


def test_sequence_wrapper_rejects_empty_sequence() -> None:
    with pytest.raises(ValueError):
        effective_service_capacity_from_sequence([])


def test_sequence_wrapper_rejects_negative_capacity() -> None:
    with pytest.raises(ValueError):
        effective_service_capacity_from_sequence(
            [50.0, -1.0, 10.0]
        )


def test_sequence_wrapper_rejects_nan() -> None:
    with pytest.raises(ValueError):
        effective_service_capacity_from_sequence(
            [50.0, math.nan, 10.0]
        )


def test_sequence_wrapper_rejects_infinity() -> None:
    with pytest.raises(ValueError):
        effective_service_capacity_from_sequence(
            [50.0, math.inf, 10.0]
        )


def test_sequence_wrapper_rejects_non_numeric_capacity() -> None:
    with pytest.raises(ValueError):
        effective_service_capacity_from_sequence(
            [50.0, "invalid", 10.0]  # type: ignore[list-item]
        )


def test_realistic_effective_service_report() -> None:
    report = effective_service_report(
        c_tc=50.0,
        c_air=35.0,
        c_cpu=40.0,
        c_tun=30.0,
        c_bh=25.0,
    )

    assert isinstance(report, EffectiveServiceReport)
    assert report.c_eff == 25.0
    assert report.bottleneck == "bh"
    assert dict(report.capacities) == {
        "tc": 50.0,
        "air": 35.0,
        "cpu": 40.0,
        "tun": 30.0,
        "bh": 25.0,
    }


def test_report_uses_normalized_capacity_names_in_fixed_order() -> None:
    report = effective_service_report(
        50.0,
        35.0,
        40.0,
        30.0,
        25.0,
    )

    assert list(report.capacities) == [
        "tc",
        "air",
        "cpu",
        "tun",
        "bh",
    ]


def test_report_capacity_values_are_floats() -> None:
    report = effective_service_report(
        50,
        35,
        40,
        30,
        25,
    )

    assert report.c_eff == 25.0
    assert type(report.c_eff) is float
    assert all(
        type(value) is float
        for value in report.capacities.values()
    )


def test_report_identifies_tc_bottleneck() -> None:
    report = effective_service_report(
        10.0,
        20.0,
        30.0,
        40.0,
        50.0,
    )

    assert report.bottleneck == "tc"
    assert report.c_eff == 10.0


def test_report_identifies_air_bottleneck() -> None:
    report = effective_service_report(
        20.0,
        10.0,
        30.0,
        40.0,
        50.0,
    )

    assert report.bottleneck == "air"
    assert report.c_eff == 10.0


def test_report_identifies_cpu_bottleneck() -> None:
    report = effective_service_report(
        20.0,
        30.0,
        10.0,
        40.0,
        50.0,
    )

    assert report.bottleneck == "cpu"
    assert report.c_eff == 10.0


def test_report_identifies_tun_bottleneck() -> None:
    report = effective_service_report(
        20.0,
        30.0,
        40.0,
        10.0,
        50.0,
    )

    assert report.bottleneck == "tun"
    assert report.c_eff == 10.0


def test_report_identifies_bh_bottleneck() -> None:
    report = effective_service_report(
        20.0,
        30.0,
        40.0,
        50.0,
        10.0,
    )

    assert report.bottleneck == "bh"
    assert report.c_eff == 10.0


def test_tie_between_tc_and_air_selects_tc() -> None:
    report = effective_service_report(
        10.0,
        10.0,
        20.0,
        30.0,
        40.0,
    )

    assert report.bottleneck == "tc"


def test_tie_between_air_and_cpu_selects_air() -> None:
    report = effective_service_report(
        20.0,
        10.0,
        10.0,
        30.0,
        40.0,
    )

    assert report.bottleneck == "air"


def test_tie_between_cpu_and_tun_selects_cpu() -> None:
    report = effective_service_report(
        20.0,
        30.0,
        10.0,
        10.0,
        40.0,
    )

    assert report.bottleneck == "cpu"


def test_tie_between_tun_and_bh_selects_tun() -> None:
    report = effective_service_report(
        20.0,
        30.0,
        40.0,
        10.0,
        10.0,
    )

    assert report.bottleneck == "tun"


def test_all_equal_capacities_select_tc() -> None:
    report = effective_service_report(
        10.0,
        10.0,
        10.0,
        10.0,
        10.0,
    )

    assert report.bottleneck == "tc"
    assert report.c_eff == 10.0


def test_zero_capacity_becomes_bottleneck() -> None:
    report = effective_service_report(
        50.0,
        35.0,
        0.0,
        30.0,
        25.0,
    )

    assert report.bottleneck == "cpu"
    assert report.c_eff == 0.0


def test_zero_capacity_tie_uses_fixed_order() -> None:
    report = effective_service_report(
        50.0,
        0.0,
        0.0,
        30.0,
        25.0,
    )

    assert report.bottleneck == "air"
    assert report.c_eff == 0.0


def test_report_rejects_negative_tc_capacity() -> None:
    with pytest.raises(ValueError):
        effective_service_report(
            -1.0,
            20.0,
            30.0,
            40.0,
            50.0,
        )


def test_report_rejects_negative_air_capacity() -> None:
    with pytest.raises(ValueError):
        effective_service_report(
            20.0,
            -1.0,
            30.0,
            40.0,
            50.0,
        )


def test_report_rejects_negative_cpu_capacity() -> None:
    with pytest.raises(ValueError):
        effective_service_report(
            20.0,
            30.0,
            -1.0,
            40.0,
            50.0,
        )


def test_report_rejects_negative_tun_capacity() -> None:
    with pytest.raises(ValueError):
        effective_service_report(
            20.0,
            30.0,
            40.0,
            -1.0,
            50.0,
        )


def test_report_rejects_negative_bh_capacity() -> None:
    with pytest.raises(ValueError):
        effective_service_report(
            20.0,
            30.0,
            40.0,
            50.0,
            -1.0,
        )


def test_report_rejects_nan() -> None:
    with pytest.raises(ValueError):
        effective_service_report(
            20.0,
            math.nan,
            40.0,
            50.0,
            60.0,
        )


def test_report_rejects_positive_infinity() -> None:
    with pytest.raises(ValueError):
        effective_service_report(
            20.0,
            math.inf,
            40.0,
            50.0,
            60.0,
        )


def test_report_rejects_negative_infinity() -> None:
    with pytest.raises(ValueError):
        effective_service_report(
            20.0,
            -math.inf,
            40.0,
            50.0,
            60.0,
        )


def test_report_rejects_non_numeric_value() -> None:
    with pytest.raises(ValueError):
        effective_service_report(
            20.0,
            "30.0",  # type: ignore[arg-type]
            40.0,
            50.0,
            60.0,
        )


def test_report_rejects_none() -> None:
    with pytest.raises(ValueError):
        effective_service_report(
            20.0,
            None,  # type: ignore[arg-type]
            40.0,
            50.0,
            60.0,
        )


def test_report_rejects_complex_value() -> None:
    with pytest.raises(ValueError):
        effective_service_report(
            20.0,
            30.0 + 0.0j,  # type: ignore[arg-type]
            40.0,
            50.0,
            60.0,
        )


def test_report_rejects_boolean_value() -> None:
    with pytest.raises(ValueError):
        effective_service_report(
            20.0,
            False,
            40.0,
            50.0,
            60.0,
        )


def test_report_error_identifies_invalid_capacity() -> None:
    with pytest.raises(ValueError) as exc_info:
        effective_service_report(
            20.0,
            -1.0,
            40.0,
            50.0,
            60.0,
        )

    assert "air" in str(exc_info.value)


def test_effective_service_report_is_frozen() -> None:
    report = effective_service_report(
        50.0,
        35.0,
        40.0,
        30.0,
        25.0,
    )

    with pytest.raises(FrozenInstanceError):
        report.c_eff = 30.0  # type: ignore[misc]


def test_report_capacities_mapping_is_read_only() -> None:
    report = effective_service_report(
        50.0,
        35.0,
        40.0,
        30.0,
        25.0,
    )

    with pytest.raises(TypeError):
        report.capacities["tc"] = 100.0  # type: ignore[index]


def test_capacity_and_report_use_the_same_effective_minimum() -> None:
    capacity = effective_service_capacity(
        50.0,
        35.0,
        40.0,
        30.0,
        25.0,
    )
    report = effective_service_report(
        50.0,
        35.0,
        40.0,
        30.0,
        25.0,
    )

    assert capacity == report.c_eff