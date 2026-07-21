from __future__ import annotations

import math
from dataclasses import FrozenInstanceError

import pytest

from scb.leo.cost import (
    LeoCostReport,
    leo_energy_cost,
    leo_resilience_cost,
    leo_resilience_cost_report,
)


PSI = (
    0.30,
    0.20,
    0.20,
    0.15,
    0.15,
)


def test_valid_energy_cost_returns_expected_value() -> None:
    assert leo_energy_cost(
        75.0,
        100.0,
    ) == pytest.approx(0.25)


def test_higher_available_power_lowers_energy_cost() -> None:
    high_power = leo_energy_cost(
        80.0,
        100.0,
    )
    low_power = leo_energy_cost(
        20.0,
        100.0,
    )

    assert high_power < low_power


def test_full_available_power_gives_approximately_zero() -> None:
    assert leo_energy_cost(
        100.0,
        100.0,
    ) == pytest.approx(
        0.0,
        abs=1e-9,
    )


def test_negative_available_power_fails() -> None:
    with pytest.raises(ValueError):
        leo_energy_cost(
            -1.0,
            100.0,
        )


def test_zero_maximum_power_fails() -> None:
    with pytest.raises(ValueError):
        leo_energy_cost(
            0.0,
            0.0,
        )


def test_negative_maximum_power_fails() -> None:
    with pytest.raises(ValueError):
        leo_energy_cost(
            0.0,
            -1.0,
        )


def test_available_power_above_maximum_fails() -> None:
    with pytest.raises(ValueError):
        leo_energy_cost(
            101.0,
            100.0,
        )


def test_nonpositive_energy_epsilon_fails() -> None:
    with pytest.raises(ValueError):
        leo_energy_cost(
            50.0,
            100.0,
            epsilon=0.0,
        )


def test_realistic_leo_resilience_cost() -> None:
    cost = leo_resilience_cost(
        rtt=80.0,
        rtt_ref=100.0,
        jitter=20.0,
        jitter_ref=50.0,
        outage_probability=0.10,
        handover_risk=0.20,
        energy_cost=0.25,
        psi=PSI,
    )

    assert cost == pytest.approx(0.4075)


def test_negative_rtt_fails() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            -1.0,
            100.0,
            20.0,
            50.0,
            0.10,
            0.20,
            0.25,
            PSI,
        )


def test_zero_rtt_reference_fails() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            80.0,
            0.0,
            20.0,
            50.0,
            0.10,
            0.20,
            0.25,
            PSI,
        )


def test_negative_rtt_reference_fails() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            80.0,
            -1.0,
            20.0,
            50.0,
            0.10,
            0.20,
            0.25,
            PSI,
        )


def test_negative_jitter_fails() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            80.0,
            100.0,
            -1.0,
            50.0,
            0.10,
            0.20,
            0.25,
            PSI,
        )


def test_zero_jitter_reference_fails() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            80.0,
            100.0,
            20.0,
            0.0,
            0.10,
            0.20,
            0.25,
            PSI,
        )


def test_negative_jitter_reference_fails() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            80.0,
            100.0,
            20.0,
            -1.0,
            0.10,
            0.20,
            0.25,
            PSI,
        )


def test_outage_probability_below_zero_fails() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            80.0,
            100.0,
            20.0,
            50.0,
            -0.10,
            0.20,
            0.25,
            PSI,
        )


def test_outage_probability_above_one_fails() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            80.0,
            100.0,
            20.0,
            50.0,
            1.10,
            0.20,
            0.25,
            PSI,
        )


def test_handover_risk_below_zero_fails() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            80.0,
            100.0,
            20.0,
            50.0,
            0.10,
            -0.10,
            0.25,
            PSI,
        )


def test_handover_risk_above_one_fails() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            80.0,
            100.0,
            20.0,
            50.0,
            0.10,
            1.10,
            0.25,
            PSI,
        )


def test_energy_cost_below_zero_fails() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            80.0,
            100.0,
            20.0,
            50.0,
            0.10,
            0.20,
            -0.10,
            PSI,
        )


def test_energy_cost_above_one_fails() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            80.0,
            100.0,
            20.0,
            50.0,
            0.10,
            0.20,
            1.10,
            PSI,
        )


def test_negative_psi_weight_fails() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            80.0,
            100.0,
            20.0,
            50.0,
            0.10,
            0.20,
            0.25,
            (
                -0.10,
                0.30,
                0.30,
                0.30,
                0.20,
            ),
        )


def test_psi_not_summing_to_one_fails() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            80.0,
            100.0,
            20.0,
            50.0,
            0.10,
            0.20,
            0.25,
            (0.10,) * 5,
        )


def test_psi_with_fewer_than_five_weights_fails() -> None:
    with pytest.raises(
        ValueError,
        match="exactly five",
    ):
        leo_resilience_cost(
            80.0,
            100.0,
            20.0,
            50.0,
            0.10,
            0.20,
            0.25,
            (0.25,) * 4,
        )


def test_psi_with_more_than_five_weights_fails() -> None:
    with pytest.raises(
        ValueError,
        match="exactly five",
    ):
        leo_resilience_cost(
            80.0,
            100.0,
            20.0,
            50.0,
            0.10,
            0.20,
            0.25,
            (1 / 6,) * 6,
        )


def test_nan_input_fails() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            math.nan,
            100.0,
            20.0,
            50.0,
            0.10,
            0.20,
            0.25,
            PSI,
        )


def test_infinite_input_fails() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            80.0,
            math.inf,
            20.0,
            50.0,
            0.10,
            0.20,
            0.25,
            PSI,
        )


def test_non_numeric_input_fails() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            "80",  # type: ignore[arg-type]
            100.0,
            20.0,
            50.0,
            0.10,
            0.20,
            0.25,
            PSI,
        )


def test_boolean_input_fails() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            True,
            100.0,
            20.0,
            50.0,
            0.10,
            0.20,
            0.25,
            PSI,
        )


def test_psi_is_not_silently_normalized() -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            80.0,
            100.0,
            20.0,
            50.0,
            0.10,
            0.20,
            0.25,
            (1.0,) * 5,
        )


def test_cost_report_contains_expected_terms() -> None:
    report = leo_resilience_cost_report(
        80.0,
        100.0,
        20.0,
        50.0,
        0.10,
        0.20,
        0.25,
        PSI,
    )

    assert isinstance(
        report,
        LeoCostReport,
    )
    assert report.cost == pytest.approx(0.4075)
    assert report.rtt_term == pytest.approx(0.8)
    assert report.jitter_term == pytest.approx(0.4)

    assert dict(
        report.weighted_terms
    ) == pytest.approx(
        {
            "rtt": 0.24,
            "jitter": 0.08,
            "outage": 0.02,
            "handover": 0.03,
            "energy": 0.0375,
        }
    )


def test_cost_report_is_frozen_and_read_only() -> None:
    report = leo_resilience_cost_report(
        80.0,
        100.0,
        20.0,
        50.0,
        0.10,
        0.20,
        0.25,
        PSI,
    )

    with pytest.raises(FrozenInstanceError):
        report.cost = 0.0  # type: ignore[misc]

    with pytest.raises(TypeError):
        report.weighted_terms["rtt"] = 1.0  # type: ignore[index]
        
def test_shuffled_psi_mapping_matches_canonical_tuple() -> None:
    mapping = {
        "energy": PSI[4],
        "rtt": PSI[0],
        "handover": PSI[3],
        "jitter": PSI[1],
        "outage": PSI[2],
    }
    terms = (
        80.0,
        100.0,
        20.0,
        50.0,
        0.10,
        0.20,
        0.25,
    )

    assert leo_resilience_cost(
        *terms,
        mapping,
    ) == pytest.approx(
        leo_resilience_cost(
            *terms,
            PSI,
        )
    )


@pytest.mark.parametrize(
    "mapping",
    [
        {
            "rtt": 1.0,
        },
        {
            "rtt": 1.0,
            "jitter": 0.0,
            "outage": 0.0,
            "handover": 0.0,
            "energy": 0.0,
            "unknown": 0.0,
        },
    ],
)
def test_invalid_psi_mapping_keys_fail(
    mapping: dict[str, float],
) -> None:
    with pytest.raises(ValueError):
        leo_resilience_cost(
            80.0,
            100.0,
            20.0,
            50.0,
            0.10,
            0.20,
            0.25,
            mapping,
        )


def test_raw_leo_cost_can_exceed_one_without_clamping() -> None:
    cost = leo_resilience_cost(
        300.0,
        100.0,
        150.0,
        50.0,
        0.5,
        0.5,
        0.5,
        PSI,
    )

    assert cost > 1.0
    assert cost == pytest.approx(1.75)