"""Overflow-risk indicator.

Formula:
    risk_indicator = exp(-theta_star * B)

Units:
    * ``theta_star`` is in 1/bits.
    * ``buffer_bits`` is in bits.
    * The result is a unitless scalar in (0, 1].

Assumptions:
    * The indicator is an exponential-order surrogate for buffer overflow
      probability. It is **not** a calibrated finite-buffer probability
      unless it has been validated against measured loss traces.
    * ``theta_star`` is positive; ``buffer_bits`` is non-negative.

Failure cases:
    * Non-positive ``theta_star`` raises :class:`ValueError`.
    * Negative ``buffer_bits`` raises :class:`ValueError`.
"""

from __future__ import annotations

import math


def overflow_risk_indicator(theta_star: float, buffer_bits: float) -> float:
    """Return the exponential-order overflow-risk indicator.

    Args:
        theta_star: The supremum of admissible effective-bandwidth slopes.
        buffer_bits: Buffer size in bits.

    Returns:
        A unitless risk indicator in (0, 1].

    Raises:
        ValueError: If ``theta_star <= 0`` or ``buffer_bits < 0``.
    """

    if theta_star <= 0:
        raise ValueError("theta_star must be positive")
    if buffer_bits < 0:
        raise ValueError("buffer_bits must be non-negative")
    return math.exp(-theta_star * buffer_bits)
