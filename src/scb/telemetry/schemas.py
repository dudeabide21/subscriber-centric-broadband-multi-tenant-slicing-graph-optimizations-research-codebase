"""Validated schemas for provenance-bearing telemetry records."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from scb.telemetry.parser_common import validate_aware_timestamp


class EvidenceClass(StrEnum):
    """Allowed evidence classes for parsed telemetry."""

    MEASURED = "Measured"
    EMULATED = "Emulated"
    SIMULATED = "Simulated"
    CONTEXTUAL = "Contextual"
    SYNTHETIC = "Synthetic"


class BaseTelemetryRecord(BaseModel):
    """Common provenance fields carried by every parsed record."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    evidence_class: EvidenceClass
    source_file: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    parser_version: str = Field(min_length=1)
    parsed_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat().replace("+00:00", "Z")
    )

    @field_validator("parsed_at")
    @classmethod
    def _aware_parse_time(cls, value: str) -> str:
        return validate_aware_timestamp(value, field="parsed_at")


class RadiusRecord(BaseTelemetryRecord):
    """A single RADIUS authentication or accounting event."""

    timestamp: str
    event_type: str = Field(min_length=1)
    subscriber_id_hash: str | None = Field(default=None, min_length=1)
    ap_id: str | None = Field(default=None, min_length=1)
    auth_result: str | None = Field(default=None, min_length=1)
    auth_latency_ms: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    accounting_session_id: str | None = Field(default=None, min_length=1)
    input_octets: int | None = Field(default=None, ge=0)
    output_octets: int | None = Field(default=None, ge=0)

    @field_validator("timestamp")
    @classmethod
    def _aware_event_time(cls, value: str) -> str:
        return validate_aware_timestamp(value, field="timestamp")


class TcStatsRecord(BaseTelemetryRecord):
    """A single Linux ``tc`` class statistics sample."""

    interface: str = Field(min_length=1)
    class_id: str = Field(min_length=1)
    rate_mbit: float = Field(gt=0, allow_inf_nan=False)
    ceil_mbit: float = Field(gt=0, allow_inf_nan=False)
    sent_bytes: int = Field(ge=0)
    packets: int = Field(ge=0)
    drops: int = Field(ge=0)
    backlog_bytes: int = Field(ge=0)
    backlog_packets: int = Field(ge=0)
    requeues: int = Field(ge=0)


class OpenWrtMetricRecord(BaseTelemetryRecord):
    """A single OpenWrt CPU/RAM/IRQ sample."""

    timestamp: str
    ap_id: str = Field(min_length=1)
    cpu_percent: float = Field(ge=0, le=100, allow_inf_nan=False)
    ram_used_mb: float = Field(ge=0, allow_inf_nan=False)
    ram_total_mb: float = Field(gt=0, allow_inf_nan=False)
    irq_rate: float = Field(ge=0, allow_inf_nan=False)
    load_avg: float = Field(ge=0, allow_inf_nan=False)

    @field_validator("timestamp")
    @classmethod
    def _aware_metric_time(cls, value: str) -> str:
        return validate_aware_timestamp(value, field="timestamp")


class WireGuardStatsRecord(BaseTelemetryRecord):
    """A single WireGuard transfer sample."""

    interface: str = Field(min_length=1)
    peer_id_hash: str = Field(min_length=1)
    transfer_rx_bytes: int = Field(ge=0)
    transfer_tx_bytes: int = Field(ge=0)
    latest_handshake: str

    @field_validator("latest_handshake")
    @classmethod
    def _aware_handshake_time(cls, value: str) -> str:
        return validate_aware_timestamp(value, field="latest_handshake")


class ParsedDatasetSummary(BaseModel):
    """Manifest for one deterministic telemetry parsing run."""

    model_config = ConfigDict(extra="forbid")

    sample_count: int = Field(ge=0)
    files: int = Field(ge=0)
    evidence_classes: dict[str, int]
    parser_version: str = Field(min_length=1)
    source_sha256: dict[str, str]
    generated_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat().replace("+00:00", "Z")
    )

    @field_validator("generated_at")
    @classmethod
    def _aware_generated_time(cls, value: str) -> str:
        return validate_aware_timestamp(value, field="generated_at")
