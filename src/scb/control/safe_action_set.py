"""State-dependent safe action set for the Draft 10 CMDP."""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass
from numbers import Real


@dataclass(frozen=True)
class EdgeState:
    """Edge-resource snapshot used by the hard feasibility predicate."""

    cpu_percent: float
    cpu_max: float
    ram_used_mb: float
    ram_max_mb: float
    irq_rate: float
    irq_max: float
    omega: float
    omega_max: float
    c_eff_mbps: float
    e_bandwidth_mbps: float


@dataclass(frozen=True)
class SafetyFlags:
    """Boolean predicates that must all hold for an action to be safe."""

    auth: bool
    pol: bool
    iso: bool
    acct: bool


@dataclass(frozen=True)
class Action:
    """Candidate control action and its evaluated safety state."""

    action_id: str
    safety: SafetyFlags
    edge: EdgeState


def _valid_real(value: object, *, positive: bool = False) -> bool:
    if isinstance(value, bool) or not isinstance(value, Real):
        return False

    try:
        converted = float(value)
    except (OverflowError, TypeError, ValueError):
        return False

    if not math.isfinite(converted):
        return False

    return converted > 0.0 if positive else converted >= 0.0


def edge_feasible(state: EdgeState) -> bool:
    """Return whether the exact hard predicates of Draft 10 Eq. 4.24 hold.

    Invalid numeric state fails closed. No tolerance, clamping, or repair is
    applied to any hard boundary.
    """
    if not isinstance(state, EdgeState):
        return False

    usage_values = (
        state.cpu_percent,
        state.ram_used_mb,
        state.irq_rate,
        state.omega,
        state.c_eff_mbps,
        state.e_bandwidth_mbps,
    )
    maxima = (
        state.cpu_max,
        state.ram_max_mb,
        state.irq_max,
        state.omega_max,
    )

    if not all(_valid_real(value) for value in usage_values):
        return False

    if not all(_valid_real(value, positive=True) for value in maxima):
        return False

    return (
        state.cpu_percent <= state.cpu_max
        and state.ram_used_mb <= state.ram_max_mb
        and state.irq_rate <= state.irq_max
        and state.omega <= state.omega_max
        and state.c_eff_mbps > state.e_bandwidth_mbps
    )


def is_safe(action: Action) -> bool:
    """Return whether all federated and edge predicates hold."""
    if not isinstance(action, Action):
        return False

    if not isinstance(action.safety, SafetyFlags):
        return False

    flags = (
        action.safety.auth,
        action.safety.pol,
        action.safety.iso,
        action.safety.acct,
    )

    if not all(isinstance(flag, bool) for flag in flags):
        return False

    return (
        action.safety.auth
        and action.safety.pol
        and action.safety.iso
        and action.safety.acct
        and edge_feasible(action.edge)
    )


def safe_action_set(actions: Iterable[Action]) -> list[Action]:
    """Return actions belonging to the state-dependent safe set."""
    return [action for action in actions if is_safe(action)]