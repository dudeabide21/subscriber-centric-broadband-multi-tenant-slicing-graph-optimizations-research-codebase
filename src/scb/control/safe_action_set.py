"""State-dependent safe action set for the CMDP.

Formula:
    U_safe(x) = {u in U(x): Auth=1, Pol=1, Iso=1, Acct=1, EdgeFeas=1}

The implementation models the state vector as a dataclass with explicit
flags. The action space is represented as a list of candidate actions; the
filter returns only those actions that satisfy every safety predicate.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class EdgeState:
    """Edge resource snapshot used by the :func:`edge_feasible` predicate.

    Attributes:
        cpu_percent: Current CPU usage in percent (0-100).
        cpu_max: Maximum allowed CPU usage in percent.
        ram_used_mb: Current RAM usage in megabytes.
        ram_max_mb: Maximum allowed RAM usage in megabytes.
        irq_rate: Current IRQ rate (Hz, or any consistent non-negative unit).
        irq_max: Maximum allowed IRQ rate in the same unit.
        omega: Aggregated edge load index (unitless, non-negative).
        omega_max: Maximum allowed edge load index.
        c_eff_mbps: Effective service capacity in Mbps.
        e_bandwidth_mbps: Effective bandwidth estimate in Mbps at
            ``theta = 0+``.
    """

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
    """Boolean safety predicates that must all be 1 for an action to be safe."""

    auth: bool
    pol: bool
    iso: bool
    acct: bool


@dataclass(frozen=True)
class Action:
    """A candidate control action.

    Attributes:
        action_id: Stable identifier for logging and tests.
        safety: Aggregate :class:`SafetyFlags` from the federated AAA stack.
        edge: The :class:`EdgeState` snapshot at the moment the action
            was evaluated.
    """

    action_id: str
    safety: SafetyFlags
    edge: EdgeState


def edge_feasible(state: EdgeState) -> bool:
    """Return 1 iff every EdgeFeas predicate is satisfied.

    Predicates (from the spec):
        CPU_j <= CPU_j_max
        RAM_j <= RAM_j_max
        IRQ_j <= IRQ_j_max
        Omega_j <= Omega_j_max
        C_eff_k > E_k(0+)

    A small epsilon protects against floating point comparison noise.
    """

    from scb.common.constants import EPS

    if state.cpu_percent > state.cpu_max + EPS:
        return False
    if state.ram_used_mb > state.ram_max_mb + EPS:
        return False
    if state.irq_rate > state.irq_max + EPS:
        return False
    if state.omega > state.omega_max + EPS:
        return False
    return state.c_eff_mbps > state.e_bandwidth_mbps + EPS


def is_safe(action: Action) -> bool:
    """Return True iff the action passes the federated and edge predicates."""

    if not action.safety.auth:
        return False
    if not action.safety.pol:
        return False
    if not action.safety.iso:
        return False
    if not action.safety.acct:
        return False
    return edge_feasible(action.edge)


def safe_action_set(actions: Iterable[Action]) -> list[Action]:
    """Return the subset of ``actions`` that belong to ``U_safe(x)``."""

    return [action for action in actions if is_safe(action)]
