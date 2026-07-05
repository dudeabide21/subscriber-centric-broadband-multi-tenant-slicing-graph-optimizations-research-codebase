"""Pydantic schemas for parsed telemetry records.

All parsed records inherit from :class:`BaseTelemetryRecord`, which carries
provenance metadata. The evidence class is part of the public schema so the
caller can always distinguish synthetic samples from real measurements.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class EvidenceClass(StrEnum):
    """Allowed evidence classes for parsed telemetry."""

    MEASURED = "Measured"
    EMULATED = "Emulated"
    SIMULATED = "Simulated"
    CONTEXTUAL = "Contextual"
    SYNTHETIC = "Synthetic"


class BaseTelemetryRecord(BaseModel):
    """Common fields for every parsed telemetry record.

    Attributes:
        evidence_class: One of :class:`EvidenceClass`. Synthetic samples must
            always be tagged :attr:`EvidenceClass.SYNTHETIC`.
        source_file: Repository-relative POSIX path of the source file.
        source_type: Short free-form tag describing the parser family
            (for example ``"radius_auth"`` or ``"tc_stats"``).
        parser_version: Semantic version of the parser that produced the record.
        parsed_at: UTC ISO-8601 timestamp recording when parsing occurred.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    evidence_class: EvidenceClass
    source_file: str
    source_type: str
    parser_version: str
    parsed_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat().replace("+00:00", "Z")
    )


class RadiusRecord(BaseTelemetryRecord):
    """A single RADIUS authentication or accounting event."""

    timestamp: str
    event_type: str
    subscriber_id_hash: str | None = None
    ap_id: str | None = None
    auth_result: str | None = None
    auth_latency_ms: float | None = None
    accounting_session_id: str | None = None
    input_octets: int | None = None
    output_octets: int | None = None


class TcStatsRecord(BaseTelemetryRecord):
    """A single Linux ``tc`` class statistics sample."""

    interface: str
    class_id: str
    rate_mbit: float
    ceil_mbit: float
    sent_bytes: int
    packets: int
    drops: int
    backlog_bytes: int
    backlog_packets: int
    requeues: int


class OpenWrtMetricRecord(BaseTelemetryRecord):
    """A single OpenWrt CPU/RAM/IRQ sample."""

    timestamp: str
    ap_id: str
    cpu_percent: float
    ram_used_mb: float
    ram_total_mb: float
    irq_rate: float
    load_avg: float


class WireGuardStatsRecord(BaseTelemetryRecord):
    """A single WireGuard transfer sample."""

    interface: str
    peer_id_hash: str
    transfer_rx_bytes: int
    transfer_tx_bytes: int
    latest_handshake: str


class ParsedDatasetSummary(BaseModel):
    """Summary of a parsed sample directory run.

    Attributes:
        sample_count: Total number of records parsed.
        files: Number of files processed.
        evidence_classes: Counts of records grouped by evidence class.
        parser_version: Parser version used for the run.
        generated_at: UTC ISO-8601 timestamp.
    """

    sample_count: int
    files: int
    evidence_classes: dict[str, int]
    parser_version: str
    generated_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat().replace("+00:00", "Z")
    )
