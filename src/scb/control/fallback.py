"""Deterministic safe-action fallback code mirror.

This module implements the Draft 10 fallback behavior when the caller has
already computed an empty state-dependent safe action set:

    U_safe(x) = empty set

It does not compute safety predicates, verify cached tokens, install network
rules, or write accounting records. Safety filtering must occur before this
module is called.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from numbers import Real


class SurvivabilityState(str, Enum):
    """Access-point survivability state."""

    ONLINE = "online"
    DEGRADED = "degraded"
    ISOLATED = "isolated"


class FallbackDecision(str, Enum):
    """Deterministic decision after safe-action-set evaluation."""

    USE_SAFE_ACTION = "use_safe_action"
    REJECT_NEW_ADMISSION = "reject_new_admission"
    PRESERVE_EXISTING_SESSION = "preserve_existing_session"
    CAPPED_DEGRADED_SERVICE = "capped_degraded_service"
    GUEST_DEGRADED_SERVICE = "guest_degraded_service"
    DENY_SUBSCRIBER_SERVICE = "deny_subscriber_service"


@dataclass(frozen=True)
class FallbackResult:
    """Result of safe-action selection or deterministic fallback."""

    decision: FallbackDecision
    reason: str
    selected_action: object | None = None
    requires_signed_offline_accounting: bool = False
    bandwidth_cap_fraction: float | None = None


_ADMISSION_ALLOWED_DECISIONS = frozenset(
    {
        FallbackDecision.USE_SAFE_ACTION,
        FallbackDecision.PRESERVE_EXISTING_SESSION,
        FallbackDecision.CAPPED_DEGRADED_SERVICE,
        FallbackDecision.GUEST_DEGRADED_SERVICE,
    }
)


def _validate_safe_actions(
    safe_actions: Sequence[object] | None,
) -> tuple[object, ...]:
    """Validate and snapshot an ordered safe-action sequence."""
    if safe_actions is None:
        raise ValueError("safe_actions must not be None")

    if isinstance(safe_actions, (str, bytes, bytearray)):
        raise ValueError(
            "safe_actions must be an ordered action sequence"
        )

    if not isinstance(safe_actions, Sequence):
        raise ValueError(
            "safe_actions must be an ordered action sequence"
        )

    return tuple(safe_actions)


def _validate_state(
    survivability_state: SurvivabilityState,
) -> SurvivabilityState:
    """Require a known survivability-state enum value."""
    if not isinstance(
        survivability_state,
        SurvivabilityState,
    ):
        raise ValueError(
            "survivability_state must be a SurvivabilityState value"
        )

    return survivability_state


def _validate_flag(value: bool, *, name: str) -> bool:
    """Require an explicit boolean fallback flag."""
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be a boolean")

    return value


def _validate_bandwidth_cap(value: Real) -> float:
    """Validate a finite degraded-service cap in the interval (0, 1]."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(
            "degraded_bandwidth_cap must be a real numeric value"
        )

    try:
        converted = float(value)
    except (OverflowError, TypeError, ValueError):
        raise ValueError(
            "degraded_bandwidth_cap must be finite"
        ) from None

    if not math.isfinite(converted):
        raise ValueError(
            "degraded_bandwidth_cap must be finite"
        )

    if not 0.0 < converted <= 1.0:
        raise ValueError(
            "degraded_bandwidth_cap must be in the interval (0, 1]"
        )

    return converted


def select_action_or_fallback(
    safe_actions: Sequence[object] | None,
    survivability_state: SurvivabilityState,
    *,
    cached_token_valid: bool = False,
    existing_session_feasible: bool = False,
    guest_policy_enabled: bool = False,
    degraded_bandwidth_cap: Real = 0.5,
) -> FallbackResult:
    """Select the first safe action, otherwise apply branch-local fallback."""
    actions = _validate_safe_actions(safe_actions)
    state = _validate_state(survivability_state)

    if actions:
        return FallbackResult(
            decision=FallbackDecision.USE_SAFE_ACTION,
            reason=(
                "safe action set is non-empty; "
                "selected the first safe action"
            ),
            selected_action=actions[0],
        )

    if state is SurvivabilityState.ONLINE:
        session_feasible = _validate_flag(
            existing_session_feasible,
            name="existing_session_feasible",
        )

        if session_feasible:
            return FallbackResult(
                decision=FallbackDecision.PRESERVE_EXISTING_SESSION,
                reason=(
                    "no safe action exists; preserving an explicitly "
                    "feasible existing session"
                ),
            )

        return FallbackResult(
            decision=FallbackDecision.REJECT_NEW_ADMISSION,
            reason=(
                "no safe action exists in online state; "
                "reject new admission"
            ),
        )

    if state is SurvivabilityState.DEGRADED:
        token_valid = _validate_flag(
            cached_token_valid,
            name="cached_token_valid",
        )
        cap = _validate_bandwidth_cap(
            degraded_bandwidth_cap
        )

        if token_valid:
            return FallbackResult(
                decision=FallbackDecision.CAPPED_DEGRADED_SERVICE,
                reason=(
                    "no safe action exists; a valid cached token "
                    "permits capped degraded service"
                ),
                requires_signed_offline_accounting=True,
                bandwidth_cap_fraction=cap,
            )

        return FallbackResult(
            decision=FallbackDecision.REJECT_NEW_ADMISSION,
            reason=(
                "no safe action exists and no valid cached token "
                "is available"
            ),
        )

    guest_enabled = _validate_flag(
        guest_policy_enabled,
        name="guest_policy_enabled",
    )

    if guest_enabled:
        return FallbackResult(
            decision=FallbackDecision.GUEST_DEGRADED_SERVICE,
            reason=(
                "isolated state permits only explicitly configured "
                "guest-degraded local service"
            ),
        )

    return FallbackResult(
        decision=FallbackDecision.DENY_SUBSCRIBER_SERVICE,
        reason=(
            "isolated state denies subscriber service without an "
            "enabled guest-degraded policy"
        ),
    )


def is_admission_allowed(
    result: FallbackResult,
) -> bool:
    """Return whether the decision permits the specified service."""
    if not isinstance(result, FallbackResult):
        raise ValueError(
            "result must be a FallbackResult"
        )

    return result.decision in _ADMISSION_ALLOWED_DECISIONS