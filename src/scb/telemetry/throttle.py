"""System-level telemetry-throttle equation code mirror.

This module computes the effective telemetry sampling interval:

    Delta_t_eff = clip_[Delta_t_base, Delta_t_sys_max](
        Delta_t_base * exp(
            kappa_B * [1 - B_curr / (B_nominal + epsilon)]_+
            + kappa_CPU * CPU_ratio
        )
    )

It does not collect telemetry or interact with devices. ``kappa_b`` and
``kappa_cpu`` are non-negative sensitivity coefficients, not simplex weights.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from numbers import Real
from types import MappingProxyType

from scb.common.parameters import validate_backhaul_capacity
from scb.common.weights import validate_nonnegative_sensitivities


@dataclass(frozen=True)
class TelemetryThrottleReport:
    """Validated telemetry-throttle calculation details."""

    delta_t_eff: float
    raw_interval: float
    backhaul_degradation: float
    cpu_ratio: float
    exponent: float
    clamped: bool
    inputs: Mapping[str, float]


@dataclass(frozen=True)
class _TelemetryCalculation:
    """Internal calculation shared by the public telemetry helpers."""

    delta_t_eff: float
    raw_interval: float
    backhaul_degradation: float
    cpu_ratio: float
    exponent: float
    clamped: bool
    inputs: tuple[tuple[str, float], ...]


def _coerce_finite_real(value: Real, *, name: str) -> float:
    """Convert one real numeric value to a finite built-in float."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a real numeric value")

    try:
        converted = float(value)
    except (OverflowError, TypeError, ValueError):
        raise ValueError(f"{name} must be finite") from None

    if not math.isfinite(converted):
        raise ValueError(f"{name} must be finite")

    return converted


def _validate_positive(value: Real, *, name: str) -> float:
    """Validate a finite value strictly greater than zero."""
    converted = _coerce_finite_real(value, name=name)

    if converted <= 0.0:
        raise ValueError(f"{name} must be greater than zero")

    return converted


def _validate_cpu_ratio(value: Real) -> float:
    """Validate normalized CPU pressure in the closed interval [0, 1]."""
    converted = _coerce_finite_real(
        value,
        name="cpu_ratio",
    )

    if not 0.0 <= converted <= 1.0:
        raise ValueError("cpu_ratio must be in [0, 1]")

    return converted


def _validate_sensitivities(
    kappa_b: Real,
    kappa_cpu: Real,
) -> tuple[float, float]:
    """Validate non-negative, non-simplex sensitivity coefficients."""
    validated = tuple(
        validate_nonnegative_sensitivities(
            (kappa_b, kappa_cpu)
        )
    )

    if len(validated) != 2:
        raise ValueError(
            "exactly two telemetry sensitivities are required"
        )

    return validated[0], validated[1]


def _calculate_telemetry_interval(
    delta_t_base: Real,
    delta_t_sys_max: Real,
    b_curr: Real,
    b_nominal: Real,
    cpu_ratio: Real,
    kappa_b: Real,
    kappa_cpu: Real,
    *,
    epsilon: Real,
) -> _TelemetryCalculation:
    """Validate inputs and compute the telemetry-throttle equation."""
    base = _validate_positive(
        delta_t_base,
        name="delta_t_base",
    )
    system_max = _validate_positive(
        delta_t_sys_max,
        name="delta_t_sys_max",
    )

    if system_max < base:
        raise ValueError(
            "delta_t_sys_max must be greater than or equal "
            "to delta_t_base"
        )

    backhaul = validate_backhaul_capacity(
        b_curr,
        b_nominal,
    )
    validated_cpu_ratio = _validate_cpu_ratio(cpu_ratio)
    validated_kappa_b, validated_kappa_cpu = (
        _validate_sensitivities(
            kappa_b,
            kappa_cpu,
        )
    )
    validated_epsilon = _validate_positive(
        epsilon,
        name="epsilon",
    )

    backhaul_degradation = max(
        0.0,
        1.0
        - backhaul.b_curr
        / (backhaul.b_nominal + validated_epsilon),
    )

    backhaul_term = (
     validated_kappa_b * backhaul_degradation
    )
    cpu_term = (
    validated_kappa_cpu * validated_cpu_ratio
   )

    exponent = backhaul_term + cpu_term

    try:
        raw_interval = base * math.exp(exponent)
    except OverflowError:
        raw_interval = math.inf

    delta_t_eff = min(
        system_max,
        max(base, raw_interval),
    )
    clamped = (
        raw_interval < base
        or raw_interval > system_max
    )

    inputs = (
        ("delta_t_base", base),
        ("delta_t_sys_max", system_max),
        ("b_curr", backhaul.b_curr),
        ("b_nominal", backhaul.b_nominal),
        ("cpu_ratio", validated_cpu_ratio),
        ("kappa_b", validated_kappa_b),
        ("kappa_cpu", validated_kappa_cpu),
        ("epsilon", validated_epsilon),
    )

    return _TelemetryCalculation(
        delta_t_eff=float(delta_t_eff),
        raw_interval=float(raw_interval),
        backhaul_degradation=float(
            backhaul_degradation
        ),
        cpu_ratio=validated_cpu_ratio,
        exponent=float(exponent),
        clamped=clamped,
        inputs=inputs,
    )


def system_telemetry_interval(
    delta_t_base: Real,
    delta_t_sys_max: Real,
    b_curr: Real,
    b_nominal: Real,
    cpu_ratio: Real,
    kappa_b: Real,
    kappa_cpu: Real,
    *,
    epsilon: Real = 1e-9,
) -> float:
    """Return the effective system telemetry sampling interval.

    Invalid inputs are rejected rather than normalized, clipped, or repaired.
    Only the final calculated interval is clamped between
    ``delta_t_base`` and ``delta_t_sys_max``.
    """
    return _calculate_telemetry_interval(
        delta_t_base,
        delta_t_sys_max,
        b_curr,
        b_nominal,
        cpu_ratio,
        kappa_b,
        kappa_cpu,
        epsilon=epsilon,
    ).delta_t_eff


def system_telemetry_report(
    delta_t_base: Real,
    delta_t_sys_max: Real,
    b_curr: Real,
    b_nominal: Real,
    cpu_ratio: Real,
    kappa_b: Real,
    kappa_cpu: Real,
    *,
    epsilon: Real = 1e-9,
) -> TelemetryThrottleReport:
    """Return telemetry interval and intermediate equation values."""
    calculation = _calculate_telemetry_interval(
        delta_t_base,
        delta_t_sys_max,
        b_curr,
        b_nominal,
        cpu_ratio,
        kappa_b,
        kappa_cpu,
        epsilon=epsilon,
    )

    return TelemetryThrottleReport(
        delta_t_eff=calculation.delta_t_eff,
        raw_interval=calculation.raw_interval,
        backhaul_degradation=(
            calculation.backhaul_degradation
        ),
        cpu_ratio=calculation.cpu_ratio,
        exponent=calculation.exponent,
        clamped=calculation.clamped,
        inputs=MappingProxyType(
            dict(calculation.inputs)
        ),
    )