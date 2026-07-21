from __future__ import annotations

import math

import pytest

from scb.queueing import (
    diffusion_coefficient,
    effective_bandwidth,
    effective_service_capacity,
    effective_service_capacity_from_sequence,
    mean_arrival_rate,
    overflow_risk_indicator,
)


def test_effective_service_capacity_returns_minimum() -> None:
    assert effective_service_capacity(50.0, 25.0, 40.0, 30.0, 10.0) == 10.0


def test_effective_service_capacity_from_sequence_returns_minimum() -> None:
    assert effective_service_capacity_from_sequence([50.0, 25.0, 10.0]) == 10.0


def test_effective_bandwidth_matches_empirical_formula() -> None:
    value = effective_bandwidth([100.0, 200.0], theta=0.01, t_seconds=10.0)
    expected = math.log((math.exp(1.0) + math.exp(2.0)) / 2.0) / (0.01 * 10.0)
    assert value == pytest.approx(expected)


def test_overflow_risk_indicator_decays_with_buffer() -> None:
    assert overflow_risk_indicator(0.5, 2.0) == pytest.approx(math.exp(-1.0))


def test_mean_arrival_rate_uses_sample_mean_over_window() -> None:
    assert mean_arrival_rate([100.0, 200.0], delta_seconds=10.0) == pytest.approx(15.0)


def test_diffusion_coefficient_matches_centered_variance() -> None:
    increments = [100.0, 120.0, 140.0]
    lambda_hat = mean_arrival_rate(increments, delta_seconds=10.0)
    assert diffusion_coefficient(
        increments,
        delta_seconds=10.0,
        lambda_hat=lambda_hat,
    ) == pytest.approx(40.0)
    
