from __future__ import annotations

import math
from dataclasses import FrozenInstanceError

import pytest

from scb.control.fallback import (
    FallbackDecision,
    FallbackResult,
    SurvivabilityState,
    is_admission_allowed,
    select_action_or_fallback,
)


def test_non_empty_safe_set_returns_use_safe_action() -> None:
    result = select_action_or_fallback(
        ["action-a"],
        SurvivabilityState.ONLINE,
    )

    assert result.decision is FallbackDecision.USE_SAFE_ACTION


def test_non_empty_safe_set_selects_first_action() -> None:
    actions = [
        "action-a",
        "action-b",
        "action-c",
    ]

    result = select_action_or_fallback(
        actions,
        SurvivabilityState.DEGRADED,
    )

    assert result.selected_action == "action-a"


def test_non_empty_safe_set_does_not_require_offline_accounting() -> None:
    result = select_action_or_fallback(
        ["action-a"],
        SurvivabilityState.DEGRADED,
        cached_token_valid=True,
    )

    assert result.requires_signed_offline_accounting is False


def test_non_empty_safe_set_has_no_bandwidth_cap() -> None:
    result = select_action_or_fallback(
        ["action-a"],
        SurvivabilityState.DEGRADED,
        cached_token_valid=True,
    )

    assert result.bandwidth_cap_fraction is None


def test_online_empty_safe_set_rejects_new_admission() -> None:
    result = select_action_or_fallback(
        [],
        SurvivabilityState.ONLINE,
    )

    assert (
        result.decision
        is FallbackDecision.REJECT_NEW_ADMISSION
    )


def test_online_preserves_feasible_existing_session() -> None:
    result = select_action_or_fallback(
        [],
        SurvivabilityState.ONLINE,
        existing_session_feasible=True,
    )

    assert (
        result.decision
        is FallbackDecision.PRESERVE_EXISTING_SESSION
    )


def test_degraded_valid_cached_token_returns_capped_service() -> None:
    result = select_action_or_fallback(
        [],
        SurvivabilityState.DEGRADED,
        cached_token_valid=True,
    )

    assert (
        result.decision
        is FallbackDecision.CAPPED_DEGRADED_SERVICE
    )


def test_degraded_cached_token_requires_signed_accounting() -> None:
    result = select_action_or_fallback(
        [],
        SurvivabilityState.DEGRADED,
        cached_token_valid=True,
    )

    assert result.requires_signed_offline_accounting is True


def test_degraded_cached_token_uses_default_cap() -> None:
    result = select_action_or_fallback(
        [],
        SurvivabilityState.DEGRADED,
        cached_token_valid=True,
    )

    assert result.bandwidth_cap_fraction == 0.5


def test_degraded_cached_token_uses_custom_cap() -> None:
    result = select_action_or_fallback(
        [],
        SurvivabilityState.DEGRADED,
        cached_token_valid=True,
        degraded_bandwidth_cap=0.25,
    )

    assert result.bandwidth_cap_fraction == 0.25


def test_degraded_invalid_cached_token_rejects_admission() -> None:
    result = select_action_or_fallback(
        [],
        SurvivabilityState.DEGRADED,
        cached_token_valid=False,
    )

    assert (
        result.decision
        is FallbackDecision.REJECT_NEW_ADMISSION
    )


def test_isolated_valid_cached_token_denies_subscriber_service() -> None:
    result = select_action_or_fallback(
        [],
        SurvivabilityState.ISOLATED,
        cached_token_valid=True,
    )

    assert (
        result.decision
        is FallbackDecision.DENY_SUBSCRIBER_SERVICE
    )


def test_isolated_guest_policy_returns_guest_service() -> None:
    result = select_action_or_fallback(
        [],
        SurvivabilityState.ISOLATED,
        guest_policy_enabled=True,
    )

    assert (
        result.decision
        is FallbackDecision.GUEST_DEGRADED_SERVICE
    )


def test_isolated_without_guest_policy_denies_service() -> None:
    result = select_action_or_fallback(
        [],
        SurvivabilityState.ISOLATED,
    )

    assert (
        result.decision
        is FallbackDecision.DENY_SUBSCRIBER_SERVICE
    )


def test_isolated_guest_service_is_not_cached_token_service() -> None:
    result = select_action_or_fallback(
        [],
        SurvivabilityState.ISOLATED,
        cached_token_valid=True,
        guest_policy_enabled=True,
    )

    assert (
        result.decision
        is FallbackDecision.GUEST_DEGRADED_SERVICE
    )
    assert result.requires_signed_offline_accounting is False
    assert result.bandwidth_cap_fraction is None


def test_unknown_survivability_state_fails() -> None:
    with pytest.raises(ValueError):
        select_action_or_fallback(
            [],
            "online",  # type: ignore[arg-type]
        )


def test_safe_actions_none_fails() -> None:
    with pytest.raises(ValueError):
        select_action_or_fallback(
            None,
            SurvivabilityState.ONLINE,
        )


def test_unordered_safe_action_set_fails() -> None:
    with pytest.raises(ValueError):
        select_action_or_fallback(
            {"action-a", "action-b"},  # type: ignore[arg-type]
            SurvivabilityState.ONLINE,
        )


def test_zero_degraded_bandwidth_cap_fails() -> None:
    with pytest.raises(ValueError):
        select_action_or_fallback(
            [],
            SurvivabilityState.DEGRADED,
            degraded_bandwidth_cap=0,
        )


def test_negative_degraded_bandwidth_cap_fails() -> None:
    with pytest.raises(ValueError):
        select_action_or_fallback(
            [],
            SurvivabilityState.DEGRADED,
            degraded_bandwidth_cap=-0.1,
        )


def test_degraded_bandwidth_cap_above_one_fails() -> None:
    with pytest.raises(ValueError):
        select_action_or_fallback(
            [],
            SurvivabilityState.DEGRADED,
            degraded_bandwidth_cap=1.01,
        )


def test_nan_degraded_bandwidth_cap_fails() -> None:
    with pytest.raises(ValueError):
        select_action_or_fallback(
            [],
            SurvivabilityState.DEGRADED,
            degraded_bandwidth_cap=math.nan,
        )


def test_infinite_degraded_bandwidth_cap_fails() -> None:
    with pytest.raises(ValueError):
        select_action_or_fallback(
            [],
            SurvivabilityState.DEGRADED,
            degraded_bandwidth_cap=math.inf,
        )


def test_non_numeric_degraded_bandwidth_cap_fails() -> None:
    with pytest.raises(ValueError):
        select_action_or_fallback(
            [],
            SurvivabilityState.DEGRADED,
            degraded_bandwidth_cap="0.5",  # type: ignore[arg-type]
        )


def test_non_boolean_fallback_flag_fails() -> None:
    with pytest.raises(ValueError):
        select_action_or_fallback(
            [],
            SurvivabilityState.DEGRADED,
            cached_token_valid=1,  # type: ignore[arg-type]
        )


def test_function_does_not_mutate_safe_action_list() -> None:
    actions = [
        {"name": "action-a"},
        {"name": "action-b"},
    ]
    original = list(actions)

    select_action_or_fallback(
        actions,
        SurvivabilityState.ONLINE,
    )

    assert actions == original


def test_fallback_results_do_not_select_an_action() -> None:
    result = select_action_or_fallback(
        [],
        SurvivabilityState.ONLINE,
    )

    assert result.selected_action is None


def test_is_admission_allowed_for_every_decision() -> None:
    allowed = {
        FallbackDecision.USE_SAFE_ACTION,
        FallbackDecision.PRESERVE_EXISTING_SESSION,
        FallbackDecision.CAPPED_DEGRADED_SERVICE,
        FallbackDecision.GUEST_DEGRADED_SERVICE,
    }
    denied = {
        FallbackDecision.REJECT_NEW_ADMISSION,
        FallbackDecision.DENY_SUBSCRIBER_SERVICE,
    }

    for decision in allowed:
        result = FallbackResult(
            decision=decision,
            reason="test",
        )
        assert is_admission_allowed(result) is True

    for decision in denied:
        result = FallbackResult(
            decision=decision,
            reason="test",
        )
        assert is_admission_allowed(result) is False


def test_is_admission_allowed_rejects_invalid_result() -> None:
    with pytest.raises(ValueError):
        is_admission_allowed(
            FallbackDecision.USE_SAFE_ACTION,  # type: ignore[arg-type]
        )


def test_fallback_result_is_frozen() -> None:
    result = select_action_or_fallback(
        [],
        SurvivabilityState.ONLINE,
    )

    with pytest.raises(FrozenInstanceError):
        result.reason = "changed"  # type: ignore[misc]


def test_full_survivability_state_matrix() -> None:
    cases = (
        (
            SurvivabilityState.ONLINE,
            {},
            FallbackDecision.REJECT_NEW_ADMISSION,
        ),
        (
            SurvivabilityState.ONLINE,
            {"existing_session_feasible": True},
            FallbackDecision.PRESERVE_EXISTING_SESSION,
        ),
        (
            SurvivabilityState.DEGRADED,
            {},
            FallbackDecision.REJECT_NEW_ADMISSION,
        ),
        (
            SurvivabilityState.DEGRADED,
            {"cached_token_valid": True},
            FallbackDecision.CAPPED_DEGRADED_SERVICE,
        ),
        (
            SurvivabilityState.ISOLATED,
            {},
            FallbackDecision.DENY_SUBSCRIBER_SERVICE,
        ),
        (
            SurvivabilityState.ISOLATED,
            {"cached_token_valid": True},
            FallbackDecision.DENY_SUBSCRIBER_SERVICE,
        ),
        (
            SurvivabilityState.ISOLATED,
            {"guest_policy_enabled": True},
            FallbackDecision.GUEST_DEGRADED_SERVICE,
        ),
    )

    for state, keyword_arguments, expected in cases:
        result = select_action_or_fallback(
            [],
            state,
            **keyword_arguments,
        )

        assert result.decision is expected