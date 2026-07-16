"""Validation helpers for fixed evaluation and operational parametes"""

from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real

DEFAULT_DELTA_MIN = 0.05
DELTA_MIN_SENSITIVITY_SET = (0.02,0.05,0.10)


@dataclass(frozen=True)
class TokenTiming:
    """Validated cached-token timing parameters.

    Attributes:
        t_token: Maximum cached-token validity window.
        t_rot: Operational token-signing key rotation period.
    """

    t_token: float
    t_rot: float


@dataclass(frozen=True)
class BackhaulCapacity:
    """Validated current and nominal backhaul capacities.

    Attributes:
        b_curr: Current measured available backhaul capacity.
        b_nominal: Nominal expected backhaul capacity.
    """

    b_curr: float
    b_nominal: float


def _coerce_finite_real(value: Real, *, name: str) -> float:
    """Coerce a scalar into a finite, non-boolean real-valued float."""
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a real numeric value")
    if not isinstance(value, Real):
        raise ValueError(f"{name} must be a real numeric value")

    converted = float(value)

    if not math.isfinite(converted):
        raise ValueError(f"{name} must be finite")

    return converted


def validate_delta_min(delta_min: Real) -> float:
    """Validate the pre-registered practical-improvement threshold.

    The threshold must be strictly between zero and one. The upper bound is
    an engineering assumption consistent with the manuscript's normalized
    composite-score framing; it is not derived from a separately proven
    universal bound on every possible score realization.
    """
    validated = _coerce_finite_real(delta_min, name="delta_min")

    if validated <= 0:
        raise ValueError("delta_min must be greater than zero")
    if validated >= 1:
        raise ValueError("delta_min must be less than one")

    return validated


def validate_token_timing(t_token: Real, t_rot: Real) -> TokenTiming:
    """Validate cached-token validity and key-rotation timing.

    This validates timing parameters only. It does not perform token
    verification, expiry checking, key-age validation, HMAC operations, or
    replay protection.
    """
    validated_t_token = _coerce_finite_real(t_token, name="t_token")
    validated_t_rot = _coerce_finite_real(t_rot, name="t_rot")

    if validated_t_token <= 0:
        raise ValueError("t_token must be positive")
    if validated_t_rot <= 0:
        raise ValueError("t_rot must be positive")
    if validated_t_token >= validated_t_rot:
        raise ValueError("t_token must be less than t_rot")

    return TokenTiming(
        t_token=validated_t_token,
        t_rot=validated_t_rot,
    )


def validate_backhaul_capacity(
    b_curr: Real,
    b_nominal: Real,
) -> BackhaulCapacity:
    """Validate current measured and nominal expected backhaul capacities."""
    validated_b_curr = _coerce_finite_real(b_curr, name="b_curr")
    validated_b_nominal = _coerce_finite_real(
        b_nominal,
        name="b_nominal",
    )

    if validated_b_curr < 0:
        raise ValueError("b_curr must be non-negative")
    if validated_b_nominal <= 0:
        raise ValueError("b_nominal must be positive")

    return BackhaulCapacity(
        b_curr=validated_b_curr,
        b_nominal=validated_b_nominal,
    )