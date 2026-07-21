"""LEO-specific macro-epoch backoff equation code mirror.

This module computes the Draft 10 LEO macro-epoch interval. It does not
collect metrics, select a backhaul path, or bypass safety filtering.

``kappa_rtt`` and ``kappa_drop`` are non-negative sensitivity coefficients,
not simplex weights.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real

from scb.common.weights import (
    validate_nonnegative_sensitivities,
)


@dataclass(frozen=True)
class LeoBackoffReport:
    """Validated LEO macro-epoch backoff calculation."""

    delta_t_eff: float
    raw_interval: float
    rtt_variability_term: float
    drop_term: float
    exponent: float
    clamped: bool


@dataclass(frozen=True)
class _LeoBackoffCalculation:
    """Internal result shared by public backoff helpers."""

    delta_t_eff: float
    raw_interval: float
    rtt_variability_term: float
    drop_term: float
    exponent: float
    clamped: bool


def _coerce_finite_real(
    value: Real,
    *,
    name: str,
) -> float:
    """Convert one real numeric input to a finite built-in float."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(
            f"{name} must be a real numeric value"
        )

    try:
        converted = float(value)
    except (OverflowError, TypeError, ValueError):
        raise ValueError(
            f"{name} must be finite"
        ) from None

    if not math.isfinite(converted):
        raise ValueError(
            f"{name} must be finite"
        )

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
        raise ValueError(
            f"{name} must be non-negative"
        )

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
        raise ValueError(
            f"{name} must be greater than zero"
        )

    return converted


def _validate_sensitivities(
    kappa_rtt: Real,
    kappa_drop: Real,
) -> tuple[float, float]:
    """Validate two non-negative, non-simplex sensitivities."""
    validated = tuple(
        validate_nonnegative_sensitivities(
            (
                kappa_rtt,
                kappa_drop,
            )
        )
    )

    if len(validated) != 2:
        raise ValueError(
            "exactly two LEO backoff sensitivities "
            "are required"
        )

    return validated[0], validated[1]


def _calculate_leo_backoff(
    delta_t_macro: Real,
    delta_t_max: Real,
    sigma_rtt_sq: Real,
    sigma_rtt_ref_sq: Real,
    drop_leo: Real,
    drop_ref: Real,
    kappa_rtt: Real,
    kappa_drop: Real,
    epsilon: Real,
) -> _LeoBackoffCalculation:
    """Validate inputs and calculate the LEO backoff equation."""
    base = _validate_positive(
        delta_t_macro,
        name="delta_t_macro",
    )
    maximum = _validate_positive(
        delta_t_max,
        name="delta_t_max",
    )

    if maximum < base:
        raise ValueError(
            "delta_t_max must be greater than or equal "
            "to delta_t_macro"
        )

    sigma = _validate_nonnegative(
        sigma_rtt_sq,
        name="sigma_rtt_sq",
    )
    sigma_reference = _validate_positive(
        sigma_rtt_ref_sq,
        name="sigma_rtt_ref_sq",
    )
    drop = _validate_nonnegative(
        drop_leo,
        name="drop_leo",
    )
    reference_drop = _validate_positive(
        drop_ref,
        name="drop_ref",
    )

    validated_kappa_rtt, validated_kappa_drop = (
        _validate_sensitivities(
            kappa_rtt,
            kappa_drop,
        )
    )

    validated_epsilon = _validate_positive(
        epsilon,
        name="epsilon",
    )

    rtt_variability_term = (
        sigma
        / (
            sigma_reference
            + validated_epsilon
        )
    )
    drop_term = (
        drop
        / (
            reference_drop
            + validated_epsilon
        )
    )

    rtt_contribution = (
        validated_kappa_rtt
        * rtt_variability_term
    )
    drop_contribution = (
        validated_kappa_drop
        * drop_term
    )

    # There are only two non-negative terms. Ordinary addition is
    # intentional because math.fsum may raise intermediate overflow
    # for very large finite sensitivities.
    exponent = (
        rtt_contribution
        + drop_contribution
    )

    try:
        raw_interval = (
            base
            * math.exp(exponent)
        )
    except OverflowError:
        raw_interval = math.inf

    delta_t_eff = min(
        maximum,
        max(
            base,
            raw_interval,
        ),
    )

    return _LeoBackoffCalculation(
        delta_t_eff=float(delta_t_eff),
        raw_interval=float(raw_interval),
        rtt_variability_term=float(
            rtt_variability_term
        ),
        drop_term=float(drop_term),
        exponent=float(exponent),
        clamped=(
            raw_interval < base
            or raw_interval > maximum
        ),
    )


def leo_macro_epoch_backoff(
    delta_t_macro: Real,
    delta_t_max: Real,
    sigma_rtt_sq: Real,
    sigma_rtt_ref_sq: Real,
    drop_leo: Real,
    drop_ref: Real,
    kappa_rtt: Real,
    kappa_drop: Real,
    *,
    epsilon: Real = 1e-9,
) -> float:
    """Return the clamped Draft 10 LEO macro-epoch interval.

    ``kappa_rtt`` and ``kappa_drop`` are non-negative sensitivity
    coefficients. They are not simplex weights and are not required
    to sum to one.
    """
    return _calculate_leo_backoff(
        delta_t_macro,
        delta_t_max,
        sigma_rtt_sq,
        sigma_rtt_ref_sq,
        drop_leo,
        drop_ref,
        kappa_rtt,
        kappa_drop,
        epsilon=epsilon,
    ).delta_t_eff


def leo_backoff_report(
    delta_t_macro: Real,
    delta_t_max: Real,
    sigma_rtt_sq: Real,
    sigma_rtt_ref_sq: Real,
    drop_leo: Real,
    drop_ref: Real,
    kappa_rtt: Real,
    kappa_drop: Real,
    *,
    epsilon: Real = 1e-9,
) -> LeoBackoffReport:
    """Return the interval and dimensionless backoff terms."""
    calculation = _calculate_leo_backoff(
        delta_t_macro,
        delta_t_max,
        sigma_rtt_sq,
        sigma_rtt_ref_sq,
        drop_leo,
        drop_ref,
        kappa_rtt,
        kappa_drop,
        epsilon=epsilon,
    )

    return LeoBackoffReport(
        delta_t_eff=calculation.delta_t_eff,
        raw_interval=calculation.raw_interval,
        rtt_variability_term=(
            calculation.rtt_variability_term
        ),
        drop_term=calculation.drop_term,
        exponent=calculation.exponent,
        clamped=calculation.clamped,
    )
    