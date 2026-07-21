"""LEO/backhaul resilience-cost equation code mirror.

This module computes the Draft 10 LEO resilience cost. It does not select a
backhaul path, collect live measurements, or bypass safety filtering. ``psi``
contains five convex cost weights.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from numbers import Real
from types import MappingProxyType

from scb.common.weights import validate_psi_weights

_PSI_ORDER = (
    "rtt",
    "jitter",
    "outage",
    "handover",
    "energy",
)

@dataclass(frozen=True)
class LeoCostReport:
    """Validated LEO resilience-cost terms and weighted contributions."""

    cost: float
    rtt_term: float
    jitter_term: float
    outage_term: float
    handover_term: float
    energy_term: float
    weighted_terms: Mapping[str, float]
    psi: tuple[float, ...]


@dataclass(frozen=True)
class _LeoCostCalculation:
    """Internal result shared by the public cost helpers."""

    cost: float
    rtt_term: float
    jitter_term: float
    outage_term: float
    handover_term: float
    energy_term: float
    weighted_terms: tuple[tuple[str, float], ...]
    psi: tuple[float, ...]


def _coerce_finite_real(
    value: Real,
    *,
    name: str,
) -> float:
    """Convert one real numeric input to a finite built-in float."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a real numeric value")

    try:
        converted = float(value)
    except (OverflowError, TypeError, ValueError):
        raise ValueError(f"{name} must be finite") from None

    if not math.isfinite(converted):
        raise ValueError(f"{name} must be finite")

    return converted


def _validate_nonnegative(
    value: Real,
    *,
    name: str,
) -> float:
    """Validate a finite value greater than or equal to zero."""
    converted = _coerce_finite_real(
        value,
        name=name,
    )

    if converted < 0.0:
        raise ValueError(f"{name} must be non-negative")

    return converted


def _validate_positive(
    value: Real,
    *,
    name: str,
) -> float:
    """Validate a finite value strictly greater than zero."""
    converted = _coerce_finite_real(
        value,
        name=name,
    )

    if converted <= 0.0:
        raise ValueError(f"{name} must be greater than zero")

    return converted


def _validate_unit_interval(
    value: Real,
    *,
    name: str,
) -> float:
    """Validate a finite value in the closed interval [0, 1]."""
    converted = _coerce_finite_real(
        value,
        name=name,
    )

    if not 0.0 <= converted <= 1.0:
        raise ValueError(f"{name} must be in [0, 1]")

    return converted

def _validate_psi(
    psi: Sequence[Real] | Mapping[object, Real],
) -> tuple[float, ...]:
    """Validate exactly five convex LEO cost weights."""
    if isinstance(psi, Mapping):
        if (
            set(psi.keys()) != set(_PSI_ORDER)
            or len(psi) != len(_PSI_ORDER)
        ):
            raise ValueError(
                "psi mapping must contain exactly "
                "the canonical five keys"
            )

        ordered = tuple(
            psi[name]
            for name in _PSI_ORDER
        )
    else:
        ordered = tuple(psi)

    if len(ordered) != 5:
        raise ValueError(
            "psi must contain exactly five weights"
        )

    return tuple(
        validate_psi_weights(ordered)
    )
    
def leo_energy_cost(
    pwr_avail: Real,
    pwr_max: Real,
    *,
    epsilon: Real = 1e-9,
) -> float:
    """Return the Draft 10 LEO energy-cost term.

    The implemented expression is:

        EnergyCost = 1 - PwrAvail / (PwrMax + epsilon)

    The result is not clamped.
    """
    available = _validate_nonnegative(
        pwr_avail,
        name="pwr_avail",
    )
    maximum = _validate_positive(
        pwr_max,
        name="pwr_max",
    )
    validated_epsilon = _validate_positive(
        epsilon,
        name="epsilon",
    )

    if available > maximum:
        raise ValueError(
            "pwr_avail must not exceed pwr_max"
        )

    return float(
        1.0
        - available
        / (maximum + validated_epsilon)
    )


def _calculate_leo_resilience_cost(
    rtt: Real,
    rtt_ref: Real,
    jitter: Real,
    jitter_ref: Real,
    outage_probability: Real,
    handover_risk: Real,
    energy_cost: Real,
    psi: Sequence[Real] | Mapping[object, Real],
) -> _LeoCostCalculation:
    """Validate inputs and calculate the five weighted LEO terms."""
    validated_rtt = _validate_nonnegative(
        rtt,
        name="rtt",
    )
    validated_rtt_ref = _validate_positive(
        rtt_ref,
        name="rtt_ref",
    )
    validated_jitter = _validate_nonnegative(
        jitter,
        name="jitter",
    )
    validated_jitter_ref = _validate_positive(
        jitter_ref,
        name="jitter_ref",
    )
    validated_outage = _validate_unit_interval(
        outage_probability,
        name="outage_probability",
    )
    validated_handover = _validate_unit_interval(
        handover_risk,
        name="handover_risk",
    )
    validated_energy = _validate_unit_interval(
        energy_cost,
        name="energy_cost",
    )
    validated_psi = _validate_psi(psi)

    rtt_term = (
        validated_rtt
        / validated_rtt_ref
    )
    jitter_term = (
        validated_jitter
        / validated_jitter_ref
    )

    weighted_terms = (
        (
            "rtt",
            validated_psi[0] * rtt_term,
        ),
        (
            "jitter",
            validated_psi[1] * jitter_term,
        ),
        (
            "outage",
            validated_psi[2] * validated_outage,
        ),
        (
            "handover",
            validated_psi[3] * validated_handover,
        ),
        (
            "energy",
            validated_psi[4] * validated_energy,
        ),
    )

    # Ordinary summation avoids math.fsum's intermediate-overflow
    # exception for extremely large non-negative terms.
    cost = sum(
        value for _, value in weighted_terms
    )

    if not math.isfinite(cost):
        raise ValueError(
            "calculated LEO resilience cost must be finite"
        )

    return _LeoCostCalculation(
        cost=float(cost),
        rtt_term=float(rtt_term),
        jitter_term=float(jitter_term),
        outage_term=validated_outage,
        handover_term=validated_handover,
        energy_term=validated_energy,
        weighted_terms=weighted_terms,
        psi=validated_psi,
    )


def leo_resilience_cost(
    rtt: Real,
    rtt_ref: Real,
    jitter: Real,
    jitter_ref: Real,
    outage_probability: Real,
    handover_risk: Real,
    energy_cost: Real,
    psi: Sequence[Real] | Mapping[object, Real],
) -> float:
    """Return the Draft 10 LEO/backhaul resilience cost.

    ``psi`` contains five convex cost weights. The returned value is the raw
    dimensionless Eq. 4.43 ``C_LEO`` cost. RTT and jitter ratios may exceed
    one, so the result may exceed one and is not clamped. It is not
    automatically the normalized CMDP ``O_LEO`` term.
    """
    return _calculate_leo_resilience_cost(
        rtt,
        rtt_ref,
        jitter,
        jitter_ref,
        outage_probability,
        handover_risk,
        energy_cost,
        psi,
    ).cost


def leo_resilience_cost_report(
    rtt: Real,
    rtt_ref: Real,
    jitter: Real,
    jitter_ref: Real,
    outage_probability: Real,
    handover_risk: Real,
    energy_cost: Real,
    psi: Sequence[Real] | Mapping[object, Real],
) -> LeoCostReport:
    """Return the cost and validated weighted LEO terms."""
    calculation = _calculate_leo_resilience_cost(
        rtt,
        rtt_ref,
        jitter,
        jitter_ref,
        outage_probability,
        handover_risk,
        energy_cost,
        psi,
    )

    return LeoCostReport(
        cost=calculation.cost,
        rtt_term=calculation.rtt_term,
        jitter_term=calculation.jitter_term,
        outage_term=calculation.outage_term,
        handover_term=calculation.handover_term,
        energy_term=calculation.energy_term,
        weighted_terms=MappingProxyType(
            dict(calculation.weighted_terms)
        ),
        psi=calculation.psi,
    )