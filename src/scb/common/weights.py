"""Validation helpers for simplex-constrained weights and sensitivity coefficients.

Formula:
    Simplex-constrained families (Eq. 4.8-4.11(as of draft_10)): for weights w_r,
        w_r >= 0  and  sum_r w_r == 1  (within an absolute tolerance).
    Nonnegative sensitivity coefficients (e.g. kappa_B, kappa_CPU, kappa_RTT,
    kappa_drop; Eq. 4.12): w_r >= 0, with no normalization requirement.

Scope:
    This module validates the four simplex-constrained weight families named
    in the manuscript notation convention section 4.1.1 plus a generic nonnegative-sensitivity
    validator for coefficients that are bounded below by zero but are not
    required to sum to one.

Assumptions:
    Booleans are rejected as coefficients even though bool is a subclass of
    int (and therefore of numbers.Real). Mapping values are validated in
    insertion order; mapping keys are ignored. Sequences are validated in
    order. str, bytes, and bytearray are rejected even though they satisfy
    collections.abc.Sequence, since they are not coefficient collections.
    No renormalization is performed on invalid input; validation fails
    explicitly instead.

Failure cases:
    Empty collections, non-real elements, NaN/infinite elements, negative
    values (for both simplex and sensitivity validators), and simplex sums
    outside [1 - atol, 1 + atol] all raise ValueError with the offending
    collection's name in the message.

Decimal inputs will be rejected:

Python’s decimal.Decimal is not generally registered as numbers.Real.

Therefore:
Decimal("0.5") may fail the Real check even though it is numeric.

That is acceptable for this project because the requirement is standard
Python numeric weights and all downstream calculations use floats.
It should simply be recognized as an intentional API boundary.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from numbers import Real
from typing import TypeAlias

WeightValues: TypeAlias = Sequence[Real] | Mapping[object, Real]


def _coerce_finite_values(
    values: WeightValues,
    *,
    name: str,
) -> tuple[float, ...]:
    """Coerce a sequence or mapping into a tuple of finite, real-valued floats.

    Mapping values are read via ``.values()``, preserving insertion order.
    Sequences are read in order. ``str``, ``bytes``, and ``bytearray`` are
    rejected even though they are technically sequences.
    """
    raw_values: Iterable[Real]
    if isinstance(values, Mapping):
        raw_values = values.values()
    elif isinstance(values, (str, bytes, bytearray)):
        raise ValueError(f"{name} must be a sequence or mapping")
    elif isinstance(values, Sequence):
        raw_values = values
    else:
        raise ValueError(f"{name} must be a sequence or mapping")

    coerced = tuple(raw_values)

    if not coerced:
        raise ValueError(f"{name} must not be empty")

    converted_values: list[float] = []
    for value in coerced:
        if isinstance(value, bool):
            raise ValueError(f"{name} must contain only real numeric values")
        if not isinstance(value, Real):
            raise ValueError(f"{name} must contain only real numeric values")
        converted = float(value)
        if not math.isfinite(converted):
            raise ValueError(f"{name} must contain only finite values")
        converted_values.append(converted)

    return tuple(converted_values)


def _validate_atol(atol: Real, *, name: str) -> float:
    """Validate an absolute tolerance: finite, non-negative, non-boolean real."""
    if isinstance(atol, bool):
        raise ValueError(f"{name} atol must be a finite non-negative real number")
    if not isinstance(atol, Real):
        raise ValueError(f"{name} atol must be a finite non-negative real number")

    converted = float(atol)

    if not math.isfinite(converted):
        raise ValueError(f"{name} atol must be a finite non-negative real number")
    if converted < 0:
        raise ValueError(f"{name} atol must be a finite non-negative real number")

    return converted


def validate_simplex_weights(
    weights: WeightValues,
    *,
    name: str = "weights",
    atol: Real = 1e-9,
) -> tuple[float, ...]:
    """Validate that weights are non-negative and sum to 1 within atol.

    Zero-valued weights are valid. Values below zero are always rejected,
    even if the shortfall is within ``atol`` - the tolerance applies only to
    the total sum, not to individual elements. Invalid weights are never
    renormalized; validation fails explicitly instead.
    """
    validated_atol = _validate_atol(atol, name=name)
    validated = _coerce_finite_values(weights, name=name)

    for value in validated:
        if value < 0:
            raise ValueError(f"{name} must contain only non-negative values")

    total = math.fsum(validated)
    if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=validated_atol):
        raise ValueError(f"{name} must sum to 1 within atol={validated_atol}")

    return validated


def is_simplex_weights(
    weights: WeightValues,
    *,
    atol: Real = 1e-9,
) -> bool:
    """Return True if ``weights`` passes :func:`validate_simplex_weights`.

    Only expected input-validation failures (``ValueError``) are caught;
    programming errors are left to propagate.
    """
    try:
        validate_simplex_weights(weights, atol=atol)
    except ValueError:
        return False
    return True


def validate_nonnegative_sensitivities(
    values: WeightValues,
    *,
    name: str = "sensitivities",
) -> tuple[float, ...]:
    """Validate non-negative, non-normalized sensitivity coefficients.

    Unlike :func:`validate_simplex_weights`, the sum is not inspected: e.g.
    ``(2.0, 3.0, 4.0)`` is valid even though it sums to 9.0.
    """
    validated = _coerce_finite_values(values, name=name)

    for value in validated:
        if value < 0:
            raise ValueError(f"{name} must contain only non-negative values")

    return validated


def validate_beta_weights(
    weights: WeightValues,
    *,
    atol: Real = 1e-9,
) -> tuple[float, ...]:
    """Validate the simplex-constrained graph-interference weights (Eq. 4.32/4.8)."""
    return validate_simplex_weights(weights, name="beta weights", atol=atol)


def validate_omega_weights(
    weights: WeightValues,
    *,
    atol: Real = 1e-9,
) -> tuple[float, ...]:
    """Validate the simplex-constrained CMDP cost weights (Eq. 4.39/4.9)."""
    return validate_simplex_weights(weights, name="omega weights", atol=atol)


def validate_psi_weights(
    weights: WeightValues,
    *,
    atol: Real = 1e-9,
) -> tuple[float, ...]:
    """Validate the simplex-constrained LEO cost weights from Eq. 4.43.

    These are distinct from the non-normalized LEO-backoff sensitivity
    coefficients kappa_RTT and kappa_drop (Eq. 3.9), which are calibrated,
    non-negative sensitivity parameters and are not required to sum to one.
    """
    return validate_simplex_weights(weights, name="psi weights", atol=atol)


def validate_zeta_weights(
    weights: WeightValues,
    *,
    atol: Real = 1e-9,
) -> tuple[float, ...]:
    """Validate the simplex-constrained composite-score weights (Eq. 5.3/4.11)."""
    return validate_simplex_weights(weights, name="zeta weights", atol=atol)