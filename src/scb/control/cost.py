"""CMDP instantaneous cost-function code mirror.

The cost-minimising objective is:

    C = omega_1 I(G) + omega_2 V_SLA + omega_3 O_tun
        + omega_4 O_edge + omega_5 O_LEO
        - omega_6 T_norm - omega_7 J

All seven terms must already be normalized to [0, 1]. This module validates
but does not normalize, clamp, impute, or otherwise repair inputs. Safety
filtering and learning algorithms are outside this module.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from numbers import Real
from types import MappingProxyType

from scb.common.weights import validate_omega_weights


@dataclass(frozen=True)
class CmdpCostReport:
    """Validated CMDP cost totals and signed weighted contributions."""

    cost: float
    reward: float
    positive_cost: float
    negative_utility: float
    contributions: Mapping[str, float]


@dataclass(frozen=True)
class _CmdpCalculation:
    """Internal validated calculation shared by public helpers."""

    cost: float
    positive_cost: float
    negative_utility: float
    contributions: tuple[tuple[str, float], ...]


def _coerce_unit_interval(value: Real, *, name: str) -> float:
    """Convert one normalized term to a finite float in [0, 1]."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a real numeric value")

    try:
        converted = float(value)
    except (OverflowError, TypeError, ValueError):
        raise ValueError(f"{name} must be finite") from None

    if not math.isfinite(converted):
        raise ValueError(f"{name} must be finite")
    if not 0.0 <= converted <= 1.0:
        raise ValueError(f"{name} must be in [0, 1]")

    return converted


def _validate_inputs(
    interference: Real,
    sla_violation: Real,
    tunnel_overhead: Real,
    edge_overhead: Real,
    leo_overhead: Real,
    throughput_norm: Real,
    fairness: Real,
) -> tuple[float, float, float, float, float, float, float]:
    """Validate the seven normalized CMDP terms in equation order."""
    return (
        _coerce_unit_interval(
            interference,
            name="interference",
        ),
        _coerce_unit_interval(
            sla_violation,
            name="sla_violation",
        ),
        _coerce_unit_interval(
            tunnel_overhead,
            name="tunnel_overhead",
        ),
        _coerce_unit_interval(
            edge_overhead,
            name="edge_overhead",
        ),
        _coerce_unit_interval(
            leo_overhead,
            name="leo_overhead",
        ),
        _coerce_unit_interval(
            throughput_norm,
            name="throughput_norm",
        ),
        _coerce_unit_interval(
            fairness,
            name="fairness",
        ),
    )


def _validate_omega(
    omega: Sequence[Real] | Mapping[object, Real],
) -> tuple[float, ...]:
    """Validate exactly seven convex CMDP weights without normalization."""
    validated = tuple(validate_omega_weights(omega))

    if len(validated) != 7:
        raise ValueError("omega must contain exactly seven weights")

    return validated


def _calculate_cmdp_cost(
    interference: Real,
    sla_violation: Real,
    tunnel_overhead: Real,
    edge_overhead: Real,
    leo_overhead: Real,
    throughput_norm: Real,
    fairness: Real,
    omega: Sequence[Real] | Mapping[object, Real],
) -> _CmdpCalculation:
    """Validate inputs and compute the signed weighted CMDP terms once."""
    terms = _validate_inputs(
        interference,
        sla_violation,
        tunnel_overhead,
        edge_overhead,
        leo_overhead,
        throughput_norm,
        fairness,
    )
    weights = _validate_omega(omega)

    contributions = (
        ("interference", weights[0] * terms[0]),
        ("sla_violation", weights[1] * terms[1]),
        ("tunnel_overhead", weights[2] * terms[2]),
        ("edge_overhead", weights[3] * terms[3]),
        ("leo_overhead", weights[4] * terms[4]),
        ("throughput_norm", -weights[5] * terms[5]),
        ("fairness", -weights[6] * terms[6]),
    )

    positive_cost = math.fsum(
        value for _, value in contributions[:5]
    )
    negative_utility = math.fsum(
        -value for _, value in contributions[5:]
    )
    cost = math.fsum(
        value for _, value in contributions
    )

    return _CmdpCalculation(
        cost=float(cost),
        positive_cost=float(positive_cost),
        negative_utility=float(negative_utility),
        contributions=contributions,
    )


def cmdp_cost(
    interference: Real,
    sla_violation: Real,
    tunnel_overhead: Real,
    edge_overhead: Real,
    leo_overhead: Real,
    throughput_norm: Real,
    fairness: Real,
    omega: Sequence[Real] | Mapping[object, Real],
) -> float:
    """Return the Draft 10 CMDP instantaneous cost as a float.

    This function code-mirrors the cost-minimising seven-term equation.
    Throughput and fairness enter with negative signs, so a negative total
    cost is valid.
    """
    return _calculate_cmdp_cost(
        interference,
        sla_violation,
        tunnel_overhead,
        edge_overhead,
        leo_overhead,
        throughput_norm,
        fairness,
        omega,
    ).cost


def cmdp_reward(
    interference: Real,
    sla_violation: Real,
    tunnel_overhead: Real,
    edge_overhead: Real,
    leo_overhead: Real,
    throughput_norm: Real,
    fairness: Real,
    omega: Sequence[Real] | Mapping[object, Real],
) -> float:
    """Return the derived reward, defined only as ``-cmdp_cost(...)``."""
    return -cmdp_cost(
        interference,
        sla_violation,
        tunnel_overhead,
        edge_overhead,
        leo_overhead,
        throughput_norm,
        fairness,
        omega,
    )


def cmdp_cost_report(
    interference: Real,
    sla_violation: Real,
    tunnel_overhead: Real,
    edge_overhead: Real,
    leo_overhead: Real,
    throughput_norm: Real,
    fairness: Real,
    omega: Sequence[Real] | Mapping[object, Real],
) -> CmdpCostReport:
    """Return cost totals and deterministic per-term contributions."""
    calculation = _calculate_cmdp_cost(
        interference,
        sla_violation,
        tunnel_overhead,
        edge_overhead,
        leo_overhead,
        throughput_norm,
        fairness,
        omega,
    )

    return CmdpCostReport(
        cost=calculation.cost,
        reward=-calculation.cost,
        positive_cost=calculation.positive_cost,
        negative_utility=calculation.negative_utility,
        contributions=MappingProxyType(
            dict(calculation.contributions)
        ),
    )