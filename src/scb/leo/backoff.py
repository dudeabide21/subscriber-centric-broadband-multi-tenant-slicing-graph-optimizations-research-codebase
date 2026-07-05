"""LEO backoff control helpers.

Formula:
    Delta_t_eff_LEO = clip_[Delta_t_macro, Delta_t_max](
        Delta_t_macro * exp(
            psi1 * sigma2_RTT / (sigma2_RTT_ref + eps)
            + psi2 * Drop_LEO / (Drop_ref + eps)
        )
    )

Units:
    * ``delta_t_macro`` and ``delta_t_max`` are in seconds.
    * ``sigma2_rtt`` and ``sigma2_rtt_ref`` are RTT-variance surrogates in
      squared milliseconds or an equivalent consistent variance unit.
    * ``drop_leo`` and ``drop_ref`` are dimensionless loss ratios.
    * ``psi1`` and ``psi2`` are dimensionless sensitivity weights.

Assumptions:
    * The expression is a research control heuristic, not a validated network
      control law.
    * The clipped delay must stay within ``[delta_t_macro, delta_t_max]``.
    * ``delta_t_macro`` is positive, ``delta_t_max`` is at least
      ``delta_t_macro``, and reference denominators are stabilized by
      ``EPS`` to avoid division by zero.

Failure cases:
    * Non-positive ``delta_t_macro`` or ``delta_t_max`` raises
      :class:`ValueError`.
    * ``delta_t_max < delta_t_macro`` raises :class:`ValueError`.
"""

from __future__ import annotations

import math

from scb.common.constants import EPS


def leo_backoff_delay(
    *,
    delta_t_macro: float,
    sigma2_rtt: float,
    sigma2_rtt_ref: float,
    drop_leo: float,
    drop_ref: float,
    psi1: float,
    psi2: float,
    delta_t_max: float,
) -> float:
    """Return the clipped LEO backoff delay in seconds.

    Args:
        delta_t_macro: Baseline delay in seconds.
        sigma2_rtt: Observed RTT variance surrogate.
        sigma2_rtt_ref: Reference RTT variance surrogate.
        drop_leo: Observed LEO drop ratio.
        drop_ref: Reference drop ratio.
        psi1: RTT-variance sensitivity coefficient.
        psi2: Drop-ratio sensitivity coefficient.
        delta_t_max: Maximum allowed delay in seconds.

    Returns:
        A delay in seconds clipped to ``[delta_t_macro, delta_t_max]``.

    Raises:
        ValueError: If the delay bounds are invalid.
    """

    if delta_t_macro <= 0:
        raise ValueError("delta_t_macro must be positive")
    if delta_t_max <= 0:
        raise ValueError("delta_t_max must be positive")
    if delta_t_max < delta_t_macro:
        raise ValueError("delta_t_max must be greater than or equal to delta_t_macro")

    scaled_delay = delta_t_macro * math.exp(
        psi1 * sigma2_rtt / (sigma2_rtt_ref + EPS) + psi2 * drop_leo / (drop_ref + EPS)
    )
    return min(max(scaled_delay, delta_t_macro), delta_t_max)
