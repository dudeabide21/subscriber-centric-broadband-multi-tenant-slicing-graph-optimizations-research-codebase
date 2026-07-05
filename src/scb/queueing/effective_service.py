"""Effective service capacity (bottleneck) estimator.

Formula:
    C_eff = min(C_tc, C_air, C_cpu, C_tun, C_bh)

Units:
    All inputs and the returned value are in megabits per second (Mbps).

Assumptions:
    * Inputs are non-negative finite rates.
    * The estimator is a pure bottleneck selector; it does not attempt to
      model protocol overhead, retransmissions, or radio contention.

Failure cases:
    * An empty argument list raises :class:`ValueError`.
    * A negative input raises :class:`ValueError`.
"""

from __future__ import annotations

from collections.abc import Sequence


def effective_service_capacity(*capacities_mbps: float) -> float:
    """Return the bottleneck service capacity in Mbps.

    Args:
        *capacities_mbps: Two or more non-negative capacity values in Mbps.

    Returns:
        The minimum of the supplied capacities.

    Raises:
        ValueError: If no capacity is provided or any capacity is negative.
    """

    if not capacities_mbps:
        raise ValueError("at least one capacity must be provided")
    if any(capacity < 0 for capacity in capacities_mbps):
        raise ValueError("capacities must be non-negative")
    return min(capacities_mbps)


def effective_service_capacity_from_sequence(
    capacities_mbps: Sequence[float],
) -> float:
    """Sequence-friendly wrapper for :func:`effective_service_capacity`."""

    return effective_service_capacity(*capacities_mbps)
