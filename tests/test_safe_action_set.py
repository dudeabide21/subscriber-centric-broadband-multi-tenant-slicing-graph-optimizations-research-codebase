from __future__ import annotations

import math
from dataclasses import replace

import pytest

from scb.control.safe_action_set import (
    Action,
    EdgeState,
    SafetyFlags,
    edge_feasible,
    safe_action_set,
)


BASE = EdgeState(
    cpu_percent=50.0,
    cpu_max=100.0,
    ram_used_mb=256.0,
    ram_max_mb=512.0,
    irq_rate=1000.0,
    irq_max=2000.0,
    omega=0.5,
    omega_max=1.0,
    c_eff_mbps=10.0,
    e_bandwidth_mbps=9.0,
)


@pytest.mark.parametrize(
    ("field", "maximum"),
    [
        ("cpu_percent", "cpu_max"),
        ("ram_used_mb", "ram_max_mb"),
        ("irq_rate", "irq_max"),
        ("omega", "omega_max"),
    ],
)
def test_exact_maximum_feasible_and_next_float_infeasible(
    field: str,
    maximum: str,
) -> None:
    limit = getattr(BASE, maximum)

    assert edge_feasible(
        replace(BASE, **{field: limit})
    )
    assert not edge_feasible(
        replace(
            BASE,
            **{
                field: math.nextafter(
                    limit,
                    math.inf,
                )
            },
        )
    )


def test_effective_capacity_strict_boundary() -> None:
    assert not edge_feasible(
        replace(
            BASE,
            c_eff_mbps=BASE.e_bandwidth_mbps,
        )
    )

    assert edge_feasible(
        replace(
            BASE,
            c_eff_mbps=math.nextafter(
                BASE.e_bandwidth_mbps,
                math.inf,
            ),
        )
    )


@pytest.mark.parametrize(
    "field",
    BASE.__dataclass_fields__,
)
def test_nan_in_any_edge_field_fails_closed(
    field: str,
) -> None:
    assert not edge_feasible(
        replace(
            BASE,
            **{field: math.nan},
        )
    )


def test_infinity_fails_closed() -> None:
    assert not edge_feasible(
        replace(
            BASE,
            irq_rate=math.inf,
        )
    )


@pytest.mark.parametrize(
    "field",
    [
        "cpu_percent",
        "ram_used_mb",
        "irq_rate",
        "omega",
        "c_eff_mbps",
        "e_bandwidth_mbps",
    ],
)
def test_negative_state_value_fails_closed(
    field: str,
) -> None:
    assert not edge_feasible(
        replace(
            BASE,
            **{field: -1.0},
        )
    )


@pytest.mark.parametrize(
    "field",
    [
        "cpu_max",
        "ram_max_mb",
        "irq_max",
        "omega_max",
    ],
)
def test_nonpositive_maximum_fails_closed(
    field: str,
) -> None:
    assert not edge_feasible(
        replace(
            BASE,
            **{field: 0.0},
        )
    )


@pytest.mark.parametrize(
    "failed",
    [
        "auth",
        "pol",
        "iso",
        "acct",
    ],
)
def test_failed_federated_predicate_never_enters_safe_set(
    failed: str,
) -> None:
    flags = SafetyFlags(
        auth=True,
        pol=True,
        iso=True,
        acct=True,
    )
    action = Action(
        action_id="a",
        safety=replace(
            flags,
            **{failed: False},
        ),
        edge=BASE,
    )

    assert safe_action_set([action]) == []


def test_bool_numeric_state_fails_closed() -> None:
    assert not edge_feasible(
        replace(
            BASE,
            cpu_percent=True,
        )
    )