"""Effective bottleneck service-capacity code mirror.

The formal service capacity is:

    C_eff = min(C_tc, C_air, C_cpu, C_tun, C_bh)

The five components represent the configured traffic-control rate,
airtime-limited wireless capacity, CPU-limited forwarding capacity,
tunnel-limited capacity, and available backhaul capacity.

All capacities must use a consistent unit, such as Mbps. This module only
validates capacities and selects the bottleneck. It does not estimate,
normalize, weight, clamp, or impute capacity values.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from numbers import Real
from types import MappingProxyType


@dataclass(frozen=True)
class EffectiveServiceReport:
    """Validated effective-service result and bottleneck information.

    Attributes:
        c_eff: Minimum effective service capacity.
        bottleneck: Name of the first minimum-capacity component.
        capacities: Read-only mapping of normalized component names to values.
    """

    c_eff: float
    bottleneck: str
    capacities: Mapping[str, float]


def _coerce_capacity(value: Real, *, name: str) -> float:
    """Convert one capacity to a finite, non-negative built-in float."""
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a real numeric value")
    if not isinstance(value, Real):
        raise ValueError(f"{name} must be a real numeric value")

    try:
        converted = float(value)
    except (OverflowError, TypeError, ValueError):
        raise ValueError(f"{name} must be finite") from None

    if not math.isfinite(converted):
        raise ValueError(f"{name} must be finite")
    if converted < 0:
        raise ValueError(f"{name} must be non-negative")

    return converted


def _validate_capacity_pairs(
    capacity_pairs: Sequence[tuple[str, Real]],
) -> tuple[tuple[str, float], ...]:
    """Validate ordered capacity names and values."""
    if not capacity_pairs:
        raise ValueError("at least one capacity must be provided")

    return tuple(
        (name, _coerce_capacity(value, name=name))
        for name, value in capacity_pairs
    )


def _validate_formal_capacities(
    c_tc: Real,
    c_air: Real,
    c_cpu: Real,
    c_tun: Real,
    c_bh: Real,
) -> tuple[tuple[str, float], ...]:
    """Validate the five formal-model capacities in bottleneck order."""
    return _validate_capacity_pairs(
        (
            ("tc", c_tc),
            ("air", c_air),
            ("cpu", c_cpu),
            ("tun", c_tun),
            ("bh", c_bh),
        )
    )


def effective_service_capacity(
    c_tc: Real,
    c_air: Real,
    c_cpu: Real,
    c_tun: Real,
    c_bh: Real,
) -> float:
    """Return the formal effective bottleneck service capacity.

    The result code-mirrors:

        C_eff = min(C_tc, C_air, C_cpu, C_tun, C_bh)

    Args:
        c_tc: Configured traffic-control service rate.
        c_air: Airtime-limited wireless service capacity.
        c_cpu: CPU-limited forwarding capacity.
        c_tun: Tunnel-limited capacity after encapsulation or encryption.
        c_bh: Available backhaul capacity.

    Returns:
        The minimum validated capacity as a built-in float.

    Raises:
        ValueError: If any capacity is non-numeric, non-finite, or negative.
    """
    validated = _validate_formal_capacities(
        c_tc,
        c_air,
        c_cpu,
        c_tun,
        c_bh,
    )

    return min(value for _, value in validated)


def effective_service_capacity_from_sequence(
    capacities_mbps: Sequence[Real],
) -> float:
    """Return the minimum of a non-empty capacity sequence.

    This compatibility helper preserves the repository's existing
    sequence-based API. The formal five-component model should use
    :func:`effective_service_capacity` or :func:`effective_service_report`.
    """
    capacity_pairs = tuple(
        (f"capacity_{index}", value)
        for index, value in enumerate(capacities_mbps, start=1)
    )
    validated = _validate_capacity_pairs(capacity_pairs)

    return min(value for _, value in validated)


def effective_service_report(
    c_tc: Real,
    c_air: Real,
    c_cpu: Real,
    c_tun: Real,
    c_bh: Real,
) -> EffectiveServiceReport:
    """Return effective capacity, bottleneck name, and validated inputs.

    Bottleneck ties are resolved deterministically in this order:

        tc -> air -> cpu -> tun -> bh
    """
    validated = _validate_formal_capacities(
        c_tc,
        c_air,
        c_cpu,
        c_tun,
        c_bh,
    )

    bottleneck, c_eff = min(
        validated,
        key=lambda item: item[1],
    )

    capacities = MappingProxyType(dict(validated))

    return EffectiveServiceReport(
        c_eff=c_eff,
        bottleneck=bottleneck,
        capacities=capacities,
    )