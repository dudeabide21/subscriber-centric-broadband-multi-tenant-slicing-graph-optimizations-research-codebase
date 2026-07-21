from __future__ import annotations

import math
from dataclasses import FrozenInstanceError

import pytest

from scb.control.cost import (
    CmdpCostReport,
    cmdp_cost,
    cmdp_cost_report,
    cmdp_reward,
)


REALISTIC_OMEGA = (
    0.15,
    0.20,
    0.10,
    0.15,
    0.05,
    0.20,
    0.15,
)


def test_valid_cmdp_cost_returns_expected_value() -> None:
    cost = cmdp_cost(
        interference=0.20,
        sla_violation=0.10,
        tunnel_overhead=0.05,
        edge_overhead=0.25,
        leo_overhead=0.00,
        throughput_norm=0.80,
        fairness=0.90,
        omega=REALISTIC_OMEGA,
    )

    assert cost == pytest.approx(-0.2025)


def test_cmdp_cost_returns_float() -> None:
    cost = cmdp_cost(
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        (1, 0, 0, 0, 0, 0, 0),
    )

    assert type(cost) is float


def test_reward_equals_negative_cost() -> None:
    cost = cmdp_cost(
        0.20,
        0.10,
        0.05,
        0.25,
        0.00,
        0.80,
        0.90,
        REALISTIC_OMEGA,
    )
    reward = cmdp_reward(
        0.20,
        0.10,
        0.05,
        0.25,
        0.00,
        0.80,
        0.90,
        REALISTIC_OMEGA,
    )

    assert reward == -cost


def test_cost_increases_when_interference_increases() -> None:
    omega = (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    low = cmdp_cost(
        0.20,
        0,
        0,
        0,
        0,
        0,
        0,
        omega,
    )
    high = cmdp_cost(
        0.80,
        0,
        0,
        0,
        0,
        0,
        0,
        omega,
    )

    assert high > low


def test_cost_increases_when_sla_violation_increases() -> None:
    omega = (0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    low = cmdp_cost(
        0,
        0.20,
        0,
        0,
        0,
        0,
        0,
        omega,
    )
    high = cmdp_cost(
        0,
        0.80,
        0,
        0,
        0,
        0,
        0,
        omega,
    )

    assert high > low


def test_cost_increases_when_tunnel_overhead_increases() -> None:
    omega = (0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0)

    low = cmdp_cost(
        0,
        0,
        0.20,
        0,
        0,
        0,
        0,
        omega,
    )
    high = cmdp_cost(
        0,
        0,
        0.80,
        0,
        0,
        0,
        0,
        omega,
    )

    assert high > low


def test_cost_increases_when_edge_overhead_increases() -> None:
    omega = (0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0)

    low = cmdp_cost(
        0,
        0,
        0,
        0.20,
        0,
        0,
        0,
        omega,
    )
    high = cmdp_cost(
        0,
        0,
        0,
        0.80,
        0,
        0,
        0,
        omega,
    )

    assert high > low


def test_cost_increases_when_leo_overhead_increases() -> None:
    omega = (0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0)

    low = cmdp_cost(
        0,
        0,
        0,
        0,
        0.20,
        0,
        0,
        omega,
    )
    high = cmdp_cost(
        0,
        0,
        0,
        0,
        0.80,
        0,
        0,
        omega,
    )

    assert high > low


def test_cost_decreases_when_throughput_norm_increases() -> None:
    omega = (0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    low = cmdp_cost(
        0,
        0,
        0,
        0,
        0,
        0.20,
        0,
        omega,
    )
    high = cmdp_cost(
        0,
        0,
        0,
        0,
        0,
        0.80,
        0,
        omega,
    )

    assert high < low


def test_cost_decreases_when_fairness_increases() -> None:
    omega = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0)

    low = cmdp_cost(
        0,
        0,
        0,
        0,
        0,
        0,
        0.20,
        omega,
    )
    high = cmdp_cost(
        0,
        0,
        0,
        0,
        0,
        0,
        0.80,
        omega,
    )

    assert high < low


def test_zero_and_one_input_boundaries_are_valid() -> None:
    cost = cmdp_cost(
        0,
        1,
        0,
        1,
        0,
        1,
        0,
        REALISTIC_OMEGA,
    )

    assert type(cost) is float


def test_input_below_zero_fails() -> None:
    with pytest.raises(ValueError):
        cmdp_cost(
            -0.01,
            0,
            0,
            0,
            0,
            0,
            0,
            REALISTIC_OMEGA,
        )


def test_input_above_one_fails() -> None:
    with pytest.raises(ValueError):
        cmdp_cost(
            0,
            1.01,
            0,
            0,
            0,
            0,
            0,
            REALISTIC_OMEGA,
        )


def test_nan_input_fails() -> None:
    with pytest.raises(ValueError):
        cmdp_cost(
            0,
            0,
            math.nan,
            0,
            0,
            0,
            0,
            REALISTIC_OMEGA,
        )


def test_positive_infinity_input_fails() -> None:
    with pytest.raises(ValueError):
        cmdp_cost(
            0,
            0,
            0,
            math.inf,
            0,
            0,
            0,
            REALISTIC_OMEGA,
        )


def test_negative_infinity_input_fails() -> None:
    with pytest.raises(ValueError):
        cmdp_cost(
            0,
            0,
            0,
            -math.inf,
            0,
            0,
            0,
            REALISTIC_OMEGA,
        )


def test_non_numeric_input_fails() -> None:
    with pytest.raises(ValueError):
        cmdp_cost(
            0,
            0,
            0,
            0,
            "invalid",  # type: ignore[arg-type]
            0,
            0,
            REALISTIC_OMEGA,
        )


def test_none_input_fails() -> None:
    with pytest.raises(ValueError):
        cmdp_cost(
            0,
            0,
            0,
            0,
            None,  # type: ignore[arg-type]
            0,
            0,
            REALISTIC_OMEGA,
        )


def test_complex_input_fails() -> None:
    with pytest.raises(ValueError):
        cmdp_cost(
            0,
            0,
            0,
            0,
            0,
            0.5 + 0j,  # type: ignore[arg-type]
            0,
            REALISTIC_OMEGA,
        )


def test_boolean_input_fails() -> None:
    with pytest.raises(ValueError):
        cmdp_cost(
            0,
            0,
            0,
            0,
            0,
            0,
            True,
            REALISTIC_OMEGA,
        )


def test_error_identifies_invalid_input() -> None:
    with pytest.raises(ValueError) as exc_info:
        cmdp_cost(
            0,
            0,
            0,
            0,
            0,
            1.1,
            0,
            REALISTIC_OMEGA,
        )

    assert "throughput_norm" in str(exc_info.value)


def test_negative_omega_weight_fails() -> None:
    omega = (
        -0.10,
        0.20,
        0.20,
        0.20,
        0.20,
        0.20,
        0.10,
    )

    with pytest.raises(ValueError):
        cmdp_cost(
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            omega,
        )


def test_omega_weights_that_do_not_sum_to_one_fail() -> None:
    with pytest.raises(ValueError):
        cmdp_cost(
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            (0.10,) * 7,
        )


def test_omega_with_fewer_than_seven_weights_fails() -> None:
    omega = (
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    )

    with pytest.raises(ValueError, match="exactly seven"):
        cmdp_cost(
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            omega,
        )


def test_omega_with_more_than_seven_weights_fails() -> None:
    omega = (
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    )

    with pytest.raises(ValueError, match="exactly seven"):
        cmdp_cost(
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            omega,
        )


def test_function_does_not_silently_normalize_weights() -> None:
    with pytest.raises(ValueError):
        cmdp_cost(
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            (1.0,) * 7,
        )


def test_omega_mapping_uses_insertion_order() -> None:
    omega = {
        "interference": 0.0,
        "sla_violation": 0.0,
        "tunnel_overhead": 0.0,
        "edge_overhead": 0.0,
        "leo_overhead": 0.0,
        "throughput_norm": 0.0,
        "fairness": 1.0,
    }

    cost = cmdp_cost(
        0,
        0,
        0,
        0,
        0,
        0,
        0.90,
        omega,
    )

    assert cost == pytest.approx(-0.90)


def test_utility_only_terms_can_produce_negative_cost() -> None:
    omega = (
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.5,
        0.5,
    )

    cost = cmdp_cost(
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        omega,
    )

    assert cost == pytest.approx(-1.0)


def test_positive_terms_can_produce_positive_cost() -> None:
    omega = (
        0.2,
        0.2,
        0.2,
        0.2,
        0.2,
        0.0,
        0.0,
    )

    cost = cmdp_cost(
        1,
        1,
        1,
        1,
        1,
        0,
        0,
        omega,
    )

    assert cost == pytest.approx(1.0)


def test_cmdp_reward_reuses_cost_validation() -> None:
    with pytest.raises(ValueError):
        cmdp_reward(
            0,
            0,
            0,
            0,
            0,
            0,
            1.1,
            REALISTIC_OMEGA,
        )


def test_cost_report_matches_realistic_example() -> None:
    report = cmdp_cost_report(
        0.20,
        0.10,
        0.05,
        0.25,
        0.00,
        0.80,
        0.90,
        REALISTIC_OMEGA,
    )

    assert isinstance(report, CmdpCostReport)
    assert report.positive_cost == pytest.approx(0.0925)
    assert report.negative_utility == pytest.approx(0.295)
    assert report.cost == pytest.approx(-0.2025)
    assert report.reward == pytest.approx(0.2025)


def test_cost_report_contains_signed_contributions() -> None:
    report = cmdp_cost_report(
        0.20,
        0.10,
        0.05,
        0.25,
        0.00,
        0.80,
        0.90,
        REALISTIC_OMEGA,
    )

    assert dict(report.contributions) == pytest.approx(
        {
            "interference": 0.0300,
            "sla_violation": 0.0200,
            "tunnel_overhead": 0.0050,
            "edge_overhead": 0.0375,
            "leo_overhead": 0.0000,
            "throughput_norm": -0.1600,
            "fairness": -0.1350,
        }
    )


def test_cost_report_contribution_order_is_deterministic() -> None:
    report = cmdp_cost_report(
        0.20,
        0.10,
        0.05,
        0.25,
        0.00,
        0.80,
        0.90,
        REALISTIC_OMEGA,
    )

    assert list(report.contributions) == [
        "interference",
        "sla_violation",
        "tunnel_overhead",
        "edge_overhead",
        "leo_overhead",
        "throughput_norm",
        "fairness",
    ]


def test_cost_report_is_frozen() -> None:
    report = cmdp_cost_report(
        0.20,
        0.10,
        0.05,
        0.25,
        0.00,
        0.80,
        0.90,
        REALISTIC_OMEGA,
    )

    with pytest.raises(FrozenInstanceError):
        report.cost = 0.0  # type: ignore[misc]


def test_cost_report_contributions_are_read_only() -> None:
    report = cmdp_cost_report(
        0.20,
        0.10,
        0.05,
        0.25,
        0.00,
        0.80,
        0.90,
        REALISTIC_OMEGA,
    )

    with pytest.raises(TypeError):
        report.contributions["interference"] = 1.0  # type: ignore[index]
        
def test_shuffled_omega_mapping_matches_canonical_tuple() -> None:
    mapping = {
        "fairness": REALISTIC_OMEGA[6],
        "interference": REALISTIC_OMEGA[0],
        "leo_overhead": REALISTIC_OMEGA[4],
        "sla_violation": REALISTIC_OMEGA[1],
        "throughput_norm": REALISTIC_OMEGA[5],
        "edge_overhead": REALISTIC_OMEGA[3],
        "tunnel_overhead": REALISTIC_OMEGA[2],
    }
    terms = (
        0.2,
        0.1,
        0.05,
        0.3,
        0.4,
        0.8,
        0.9,
    )

    assert cmdp_cost(
        *terms,
        mapping,
    ) == pytest.approx(
        cmdp_cost(
            *terms,
            REALISTIC_OMEGA,
        )
    )


@pytest.mark.parametrize(
    "mapping",
    [
        {
            "interference": 1.0,
        },
        {
            "interference": 1.0,
            "unknown": 0.0,
        },
        {
            "interference": 1.0,
            "sla_violation": 0.0,
            "tunnel_overhead": 0.0,
            "edge_overhead": 0.0,
            "leo_overhead": 0.0,
            "throughput_norm": 0.0,
            "fairness": 0.0,
            "unknown": 0.0,
        },
    ],
)

def test_invalid_omega_mapping_keys_fail(
    mapping: dict[str, float],
) -> None:
    with pytest.raises(ValueError):
        cmdp_cost(
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            mapping,
        )


def test_raw_leo_cost_above_one_is_rejected_as_cmdp_overhead() -> None:
    with pytest.raises(
        ValueError,
        match="leo_overhead",
    ):
        cmdp_cost(
            0,
            0,
            0,
            0,
            1.2,
            0,
            0,
            REALISTIC_OMEGA,
        )