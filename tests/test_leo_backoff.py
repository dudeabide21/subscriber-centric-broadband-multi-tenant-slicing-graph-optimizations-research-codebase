from __future__ import annotations

import math
from dataclasses import FrozenInstanceError

import pytest

from scb.leo.backoff import (
    LeoBackoffReport,
    leo_backoff_delay,
    leo_backoff_report,
    leo_macro_epoch_backoff,
)


def test_realistic_leo_backoff_returns_expected_value() -> None:
    result = leo_macro_epoch_backoff(
        delta_t_macro=10.0,
        delta_t_max=60.0,
        sigma_rtt_sq=25.0,
        sigma_rtt_ref_sq=100.0,
        drop_leo=0.02,
        drop_ref=0.10,
        kappa_rtt=1.0,
        kappa_drop=0.5,
    )

    assert result == pytest.approx(
        10.0 * math.exp(0.35)
    )


def test_higher_rtt_variability_increases_interval() -> None:
    low = leo_macro_epoch_backoff(
        10.0,
        60.0,
        10.0,
        100.0,
        0.0,
        0.10,
        1.0,
        0.0,
    )
    high = leo_macro_epoch_backoff(
        10.0,
        60.0,
        50.0,
        100.0,
        0.0,
        0.10,
        1.0,
        0.0,
    )

    assert high > low


def test_higher_drop_ratio_increases_interval() -> None:
    low = leo_macro_epoch_backoff(
        10.0,
        60.0,
        0.0,
        100.0,
        0.01,
        0.10,
        0.0,
        1.0,
    )
    high = leo_macro_epoch_backoff(
        10.0,
        60.0,
        0.0,
        100.0,
        0.08,
        0.10,
        0.0,
        1.0,
    )

    assert high > low


def test_combined_terms_exceed_each_individual_term() -> None:
    rtt_only = leo_macro_epoch_backoff(
        10.0,
        60.0,
        25.0,
        100.0,
        0.0,
        0.10,
        1.0,
        1.0,
    )
    drop_only = leo_macro_epoch_backoff(
        10.0,
        60.0,
        0.0,
        100.0,
        0.02,
        0.10,
        1.0,
        1.0,
    )
    combined = leo_macro_epoch_backoff(
        10.0,
        60.0,
        25.0,
        100.0,
        0.02,
        0.10,
        1.0,
        1.0,
    )

    assert combined > rtt_only
    assert combined > drop_only


def test_large_exponent_clamps_to_maximum() -> None:
    result = leo_macro_epoch_backoff(
        10.0,
        30.0,
        1000.0,
        100.0,
        1.0,
        0.10,
        5.0,
        5.0,
    )

    assert result == 30.0


def test_output_is_never_below_macro_interval() -> None:
    result = leo_macro_epoch_backoff(
        10.0,
        60.0,
        0.0,
        100.0,
        0.0,
        0.10,
        0.0,
        0.0,
    )

    assert result >= 10.0


def test_output_is_float() -> None:
    result = leo_macro_epoch_backoff(
        10,
        60,
        0,
        100,
        0,
        1,
        0,
        0,
    )

    assert type(result) is float


def test_zero_macro_interval_fails() -> None:
    with pytest.raises(ValueError):
        leo_macro_epoch_backoff(
            0.0,
            60.0,
            0.0,
            100.0,
            0.0,
            0.10,
            1.0,
            1.0,
        )


def test_negative_macro_interval_fails() -> None:
    with pytest.raises(ValueError):
        leo_macro_epoch_backoff(
            -1.0,
            60.0,
            0.0,
            100.0,
            0.0,
            0.10,
            1.0,
            1.0,
        )


def test_maximum_below_macro_interval_fails() -> None:
    with pytest.raises(ValueError):
        leo_macro_epoch_backoff(
            10.0,
            9.0,
            0.0,
            100.0,
            0.0,
            0.10,
            1.0,
            1.0,
        )


def test_negative_sigma_rtt_sq_fails() -> None:
    with pytest.raises(ValueError):
        leo_macro_epoch_backoff(
            10.0,
            60.0,
            -1.0,
            100.0,
            0.0,
            0.10,
            1.0,
            1.0,
        )


def test_zero_sigma_reference_fails() -> None:
    with pytest.raises(ValueError):
        leo_macro_epoch_backoff(
            10.0,
            60.0,
            1.0,
            0.0,
            0.0,
            0.10,
            1.0,
            1.0,
        )


def test_negative_sigma_reference_fails() -> None:
    with pytest.raises(ValueError):
        leo_macro_epoch_backoff(
            10.0,
            60.0,
            1.0,
            -1.0,
            0.0,
            0.10,
            1.0,
            1.0,
        )


def test_negative_drop_leo_fails() -> None:
    with pytest.raises(ValueError):
        leo_macro_epoch_backoff(
            10.0,
            60.0,
            1.0,
            100.0,
            -0.10,
            0.10,
            1.0,
            1.0,
        )


def test_zero_drop_reference_fails() -> None:
    with pytest.raises(ValueError):
        leo_macro_epoch_backoff(
            10.0,
            60.0,
            1.0,
            100.0,
            0.10,
            0.0,
            1.0,
            1.0,
        )


def test_negative_drop_reference_fails() -> None:
    with pytest.raises(ValueError):
        leo_macro_epoch_backoff(
            10.0,
            60.0,
            1.0,
            100.0,
            0.10,
            -1.0,
            1.0,
            1.0,
        )


def test_negative_kappa_rtt_fails() -> None:
    with pytest.raises(ValueError):
        leo_macro_epoch_backoff(
            10.0,
            60.0,
            1.0,
            100.0,
            0.10,
            0.10,
            -1.0,
            1.0,
        )


def test_negative_kappa_drop_fails() -> None:
    with pytest.raises(ValueError):
        leo_macro_epoch_backoff(
            10.0,
            60.0,
            1.0,
            100.0,
            0.10,
            0.10,
            1.0,
            -1.0,
        )


def test_nan_input_fails() -> None:
    with pytest.raises(ValueError):
        leo_macro_epoch_backoff(
            10.0,
            60.0,
            math.nan,
            100.0,
            0.10,
            0.10,
            1.0,
            1.0,
        )


def test_infinite_input_fails() -> None:
    with pytest.raises(ValueError):
        leo_macro_epoch_backoff(
            10.0,
            60.0,
            1.0,
            math.inf,
            0.10,
            0.10,
            1.0,
            1.0,
        )


def test_non_numeric_input_fails() -> None:
    with pytest.raises(ValueError):
        leo_macro_epoch_backoff(
            10.0,
            60.0,
            "1",  # type: ignore[arg-type]
            100.0,
            0.10,
            0.10,
            1.0,
            1.0,
        )


def test_boolean_input_fails() -> None:
    with pytest.raises(ValueError):
        leo_macro_epoch_backoff(
            10.0,
            60.0,
            True,
            100.0,
            0.10,
            0.10,
            1.0,
            1.0,
        )


def test_zero_epsilon_fails() -> None:
    with pytest.raises(ValueError):
        leo_macro_epoch_backoff(
            10.0,
            60.0,
            1.0,
            100.0,
            0.10,
            0.10,
            1.0,
            1.0,
            epsilon=0.0,
        )


def test_negative_epsilon_fails() -> None:
    with pytest.raises(ValueError):
        leo_macro_epoch_backoff(
            10.0,
            60.0,
            1.0,
            100.0,
            0.10,
            0.10,
            1.0,
            1.0,
            epsilon=-1e-9,
        )


def test_sensitivities_need_not_sum_to_one() -> None:
    result = leo_macro_epoch_backoff(
        10.0,
        60.0,
        10.0,
        100.0,
        0.01,
        0.10,
        2.0,
        3.0,
    )

    assert result > 10.0


def test_zero_sensitivities_are_valid() -> None:
    result = leo_macro_epoch_backoff(
        10.0,
        60.0,
        1000.0,
        100.0,
        1.0,
        0.10,
        0.0,
        0.0,
    )

    assert result == pytest.approx(10.0)


def test_backoff_report_matches_realistic_example() -> None:
    report = leo_backoff_report(
        10.0,
        60.0,
        25.0,
        100.0,
        0.02,
        0.10,
        1.0,
        0.5,
    )

    assert isinstance(
        report,
        LeoBackoffReport,
    )
    assert report.rtt_variability_term == pytest.approx(
        0.25
    )
    assert report.drop_term == pytest.approx(
        0.20
    )
    assert report.exponent == pytest.approx(
        0.35
    )
    assert report.raw_interval == pytest.approx(
        10.0 * math.exp(0.35)
    )
    assert report.delta_t_eff == pytest.approx(
        10.0 * math.exp(0.35)
    )
    assert report.clamped is False


def test_clamped_report_marks_clamping() -> None:
    report = leo_backoff_report(
        10.0,
        30.0,
        1000.0,
        100.0,
        1.0,
        0.10,
        5.0,
        5.0,
    )

    assert report.raw_interval > 30.0
    assert report.delta_t_eff == 30.0
    assert report.clamped is True


def test_backoff_report_is_frozen() -> None:
    report = leo_backoff_report(
        10.0,
        60.0,
        25.0,
        100.0,
        0.02,
        0.10,
        1.0,
        0.5,
    )

    with pytest.raises(FrozenInstanceError):
        report.delta_t_eff = 20.0  # type: ignore[misc]


def test_extreme_sensitivities_clamp_without_fsum_overflow() -> None:
    result = leo_macro_epoch_backoff(
        10.0,
        60.0,
        100.0,
        100.0,
        1.0,
        1.0,
        1e308,
        1e308,
    )

    assert result == 60.0


def test_legacy_backoff_wrapper_remains_compatible() -> None:
    legacy = leo_backoff_delay(
        delta_t_macro=10.0,
        sigma2_rtt=25.0,
        sigma2_rtt_ref=100.0,
        drop_leo=0.02,
        drop_ref=0.10,
        psi1=1.0,
        psi2=0.5,
        delta_t_max=60.0,
    )

    canonical = leo_macro_epoch_backoff(
        10.0,
        60.0,
        25.0,
        100.0,
        0.02,
        0.10,
        1.0,
        0.5,
    )

    assert legacy == pytest.approx(canonical)