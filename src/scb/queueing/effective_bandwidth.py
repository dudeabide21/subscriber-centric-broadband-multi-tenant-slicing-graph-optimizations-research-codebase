"""Effective-bandwidth estimator.

Formula:
    E(theta) = (1 / (theta * t)) * log(E[exp(theta * A(t))])

Units:
    * ``arrivals_bits`` are bit-counts observed over a common horizon
      ``t_seconds``.
    * ``theta`` has units of 1/bits.
    * The returned effective bandwidth is in bits/second.

Assumptions:
    * All arrivals are non-negative.
    * ``theta`` is positive.
    * The implementation uses the empirical mean of ``exp(theta * A(t))``
      and is therefore a research estimator, not a calibrated production
      model.

Failure cases:
    * Empty ``arrivals_bits`` raises :class:`ValueError`.
    * Non-positive ``theta`` or ``t_seconds`` raises :class:`ValueError`.
    * Negative arrivals raise :class:`ValueError`.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from scb.common.constants import EPS


def effective_bandwidth(
    arrivals_bits: Sequence[float],
    theta: float,
    t_seconds: float,
) -> float:
    """Estimate the effective bandwidth of a flow.

    Args:
        arrivals_bits: Bit-counts observed over a common horizon.
        theta: Positive space parameter in 1/bits.
        t_seconds: Horizon length in seconds.

    Returns:
        Effective bandwidth in bits/second.
    """

    if not arrivals_bits:
        raise ValueError("arrivals_bits must not be empty")
    if theta <= 0:
        raise ValueError("theta must be positive")
    if t_seconds <= 0:
        raise ValueError("t_seconds must be positive")
    if any(arrival < 0 for arrival in arrivals_bits):
        raise ValueError("arrivals_bits must be non-negative")

    mean_exp = sum(math.exp(theta * arrival) for arrival in arrivals_bits) / len(
        arrivals_bits
    )
    return math.log(max(mean_exp, EPS)) / (theta * t_seconds)
