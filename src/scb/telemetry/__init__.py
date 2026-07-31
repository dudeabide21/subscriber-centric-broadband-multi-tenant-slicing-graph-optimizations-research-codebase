"""Strict telemetry parsing and accounting reconciliation utilities."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from scb.telemetry.accounting_reconcile import (
    AccountingReconciliation,
    reconcile_accounting_counters,
)
from scb.telemetry.parse_openwrt_metrics import parse_openwrt_metrics
from scb.telemetry.parse_radius_logs import parse_radius_acct_log, parse_radius_auth_log
from scb.telemetry.parse_tc_stats import parse_tc_stats
from scb.telemetry.parse_wireguard_stats import parse_wireguard_stats
from scb.telemetry.schemas import (
    BaseTelemetryRecord,
    EvidenceClass,
    OpenWrtMetricRecord,
    ParsedDatasetSummary,
    RadiusRecord,
    TcStatsRecord,
    WireGuardStatsRecord,
)

if TYPE_CHECKING:
    from scb.telemetry.sample_processing import ParsedTable


def main(argv: Sequence[str] | None = None) -> int:
    """Lazily invoke the sample-processing command."""

    from scb.telemetry.sample_processing import main as implementation

    return implementation(argv)


def parse_all_samples(
    samples_dir: Path,
    output_dir: Path,
    *,
    parsed_at: str | None = None,
    repo_root: Path | None = None,
) -> list[ParsedTable]:
    """Lazily parse a directory without importing the CLI during package load."""

    from scb.telemetry.sample_processing import parse_all_samples as implementation

    return implementation(
        samples_dir,
        output_dir,
        parsed_at=parsed_at,
        repo_root=repo_root,
    )


def parse_sample_file(
    root: Path,
    path: Path,
    *,
    parsed_at: str | None = None,
) -> ParsedTable:
    """Lazily parse one supported telemetry source."""

    from scb.telemetry.sample_processing import parse_sample_file as implementation

    return implementation(root, path, parsed_at=parsed_at)


__all__ = [
    "AccountingReconciliation",
    "BaseTelemetryRecord",
    "EvidenceClass",
    "OpenWrtMetricRecord",
    "ParsedDatasetSummary",
    "RadiusRecord",
    "TcStatsRecord",
    "WireGuardStatsRecord",
    "main",
    "parse_all_samples",
    "parse_openwrt_metrics",
    "parse_radius_acct_log",
    "parse_radius_auth_log",
    "parse_sample_file",
    "parse_tc_stats",
    "parse_wireguard_stats",
    "reconcile_accounting_counters",
]
