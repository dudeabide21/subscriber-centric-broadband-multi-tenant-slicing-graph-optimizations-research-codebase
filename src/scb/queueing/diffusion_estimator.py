"""Diffusion coefficient estimator for incremental arrivals.

Formula:
    sigma^2 = (1 / Delta) * Var(A(t+Delta) - A(t) - lambda_hat * Delta)

Units:
    * ``increments_bits`` is an iterable of bit-counts over a uniform window
      of length ``delta_seconds`` seconds.
    * ``lambda_hat`` is the mean arrival rate in bits/second.
    * The returned variance is in (bits/second)^2, matching the canonical
      diffusion coefficient units.

Assumptions:
    * Increments correspond to a single homogeneous observation window.
    * ``lambda_hat`` has been estimated from the same increments (for
      example via ``sum(increments) / (N * delta_seconds)``).
    * The estimator is a sample variance and is therefore biased for
      small samples.

Failure cases:
    * Fewer than two increments raise :class:`ValueError`.
    * Non-positive ``delta_seconds`` raises :class:`ValueError`.
"""

from __future__ import annotations

import statistics
from collections.abc import Sequence


def diffusion_coefficient(
    increments_bits: Sequence[float],
    delta_seconds: float,
    lambda_hat: float,
) -> float:
    """Return the diffusion coefficient of the arrival process.

    Args:
        increments_bits: Bit-counts observed over ``delta_seconds`` windows.
        delta_seconds: Length of each observation window in seconds.
        lambda_hat: Mean arrival rate estimate in bits/second.

    Returns:
        The diffusion coefficient in (bits/second)^2.

    Raises:
        ValueError: If fewer than two increments are provided or the
            observation window is non-positive.
    """

    if len(increments_bits) < 2:
        raise ValueError("at least two increments are required")
    if delta_seconds <= 0:
        raise ValueError("delta_seconds must be positive")
    centred = [incr - lambda_hat * delta_seconds for incr in increments_bits]
    return statistics.variance(centred) / delta_seconds


def mean_arrival_rate(
    increments_bits: Sequence[float],
    delta_seconds: float,
) -> float:
    """Estimate the mean arrival rate in bits/second from increments.

    Formula:
        lambda_hat = sum(A_i) / (N * Delta)

    Units:
        * ``increments_bits`` are bit counts over a common window.
        * ``delta_seconds`` is the window length in seconds.
        * The returned rate is in bits/second.

    Assumptions:
        * The increments are sampled over a uniform observation window.
        * The estimator is the empirical mean arrival rate, not a drift-corrected
          or seasonally adjusted model.
    """

    if delta_seconds <= 0:
        raise ValueError("delta_seconds must be positive")
    if not increments_bits:
        raise ValueError("at least one increment is required")
    return sum(increments_bits) / (len(increments_bits) * delta_seconds)
