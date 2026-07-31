"""Deterministically reconcile RADIUS and gateway accounting counters."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AccountingReconciliation:
    """Directional and total byte differences for one accounting session."""

    radius_bytes_in: int
    radius_bytes_out: int
    gateway_bytes_in: int
    gateway_bytes_out: int
    input_mismatch: int
    output_mismatch: int
    byte_mismatch: int
    tolerance_bytes: int
    within_tolerance: bool

    def aggregate_fields(self) -> dict[str, int | bool]:
        """Return the fields used by Stage 2 aggregate evidence records."""

        return {
            "radius_bytes_in": self.radius_bytes_in,
            "radius_bytes_out": self.radius_bytes_out,
            "gateway_bytes_in": self.gateway_bytes_in,
            "gateway_bytes_out": self.gateway_bytes_out,
            "byte_mismatch": self.byte_mismatch,
            "within_tolerance": self.within_tolerance,
        }


def _counter(value: object, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
    return value


def reconcile_accounting_counters(
    radius_bytes_in: int,
    radius_bytes_out: int,
    gateway_bytes_in: int,
    gateway_bytes_out: int,
    *,
    tolerance_bytes: int = 0,
) -> AccountingReconciliation:
    """Compare directional counters using a predeclared byte tolerance.

    The total mismatch is the sum of the absolute directional differences.
    No counters are clamped, normalized, or repaired.
    """

    radius_in = _counter(radius_bytes_in, name="radius_bytes_in")
    radius_out = _counter(radius_bytes_out, name="radius_bytes_out")
    gateway_in = _counter(gateway_bytes_in, name="gateway_bytes_in")
    gateway_out = _counter(gateway_bytes_out, name="gateway_bytes_out")
    tolerance = _counter(tolerance_bytes, name="tolerance_bytes")

    input_mismatch = abs(radius_in - gateway_in)
    output_mismatch = abs(radius_out - gateway_out)
    byte_mismatch = input_mismatch + output_mismatch

    return AccountingReconciliation(
        radius_bytes_in=radius_in,
        radius_bytes_out=radius_out,
        gateway_bytes_in=gateway_in,
        gateway_bytes_out=gateway_out,
        input_mismatch=input_mismatch,
        output_mismatch=output_mismatch,
        byte_mismatch=byte_mismatch,
        tolerance_bytes=tolerance,
        within_tolerance=byte_mismatch <= tolerance,
    )
