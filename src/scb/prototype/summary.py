"""Render deterministic Markdown summaries of aggregate prototype evidence."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from math import isfinite

from scb.prototype.evidence import (
    PrototypeRun,
    classify_evidence_record,
    validate_required_fields,
)

Record = Mapping[str, object]

_FAMILY_MARKERS = {
    "identity": "auth_result",
    "slice": "slice_id",
    "edge": "cpu_ratio",
    "accounting": "radius_bytes_in",
}

_REQUIRED_FIELDS = {
    "identity": (
        "run_id",
        "scenario_id",
        "evidence_class",
        "timestamp",
        "source",
        "subscriber_id",
        "realm",
        "visited_ap",
        "home_domain",
        "eap_method",
        "auth_result",
        "failure_reason",
        "auth_latency_ms",
        "session_id",
        "accounting_id",
    ),
    "slice": (
        "run_id",
        "scenario_id",
        "evidence_class",
        "timestamp",
        "source",
        "subscriber_id",
        "slice_id",
        "vlan_id",
        "vni",
        "rate_limit_mbps",
        "throughput_mbps",
        "latency_ms",
        "jitter_ms",
        "loss_rate",
        "queue_occupancy",
        "sla_status",
    ),
    "edge": (
        "run_id",
        "scenario_id",
        "evidence_class",
        "timestamp",
        "source",
        "ap_id",
        "cpu_ratio",
        "ram_ratio",
        "irq_rate",
        "crypto_throughput_mbps",
        "tunnel_overhead_ratio",
        "queueing_overhead_ratio",
        "telemetry_interval_s",
    ),
    "accounting": (
        "run_id",
        "scenario_id",
        "evidence_class",
        "timestamp",
        "source",
        "subscriber_id",
        "session_id",
        "radius_bytes_in",
        "radius_bytes_out",
        "gateway_bytes_in",
        "gateway_bytes_out",
        "byte_mismatch",
        "within_tolerance",
        "termination_cause",
        "offline_signature_present",
    ),
}


@dataclass(frozen=True)
class _CategorizedRecords:
    identities: tuple[Record, ...]
    slices: tuple[Record, ...]
    edges: tuple[Record, ...]
    accounting: tuple[Record, ...]


@dataclass(frozen=True)
class _ReportContext:
    scenario_id: str
    evidence_classes: tuple[str, ...]
    sources: tuple[str, ...]
    timestamps: tuple[str, ...]
    accepted: tuple[Record, ...]
    rejected: tuple[Record, ...]
    slices: tuple[Record, ...]
    edges: tuple[Record, ...]
    accounting: tuple[Record, ...]


def _string(record: Record, field: str, family: str) -> str:
    value = record[field]
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"invalid {family} record: {field} must be a non-empty string")
    return value


def _nullable_string(record: Record, field: str, family: str) -> str | None:
    value = record[field]
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"invalid {family} record: {field} must be null or a " "non-empty string"
        )
    return value


def _number(
    record: Record,
    field: str,
    family: str,
    *,
    minimum: float = 0.0,
    maximum: float | None = None,
    exclusive_minimum: bool = False,
) -> float:
    value = record[field]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"invalid {family} record: {field} must be a finite number")

    number = float(value)
    if not isfinite(number):
        raise ValueError(f"invalid {family} record: {field} must be a finite number")
    if exclusive_minimum and number <= minimum:
        raise ValueError(
            f"invalid {family} record: {field} must be greater than {minimum}"
        )
    if not exclusive_minimum and number < minimum:
        raise ValueError(f"invalid {family} record: {field} must be at least {minimum}")
    if maximum is not None and number > maximum:
        raise ValueError(f"invalid {family} record: {field} must be at most {maximum}")
    return number


def _integer(
    record: Record,
    field: str,
    family: str,
    *,
    minimum: int = 0,
    maximum: int | None = None,
) -> int:
    value = record[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"invalid {family} record: {field} must be an integer")
    if value < minimum:
        raise ValueError(f"invalid {family} record: {field} must be at least {minimum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"invalid {family} record: {field} must be at most {maximum}")
    return value


def _optional_integer(
    record: Record,
    field: str,
    family: str,
    *,
    minimum: int,
    maximum: int,
) -> int | None:
    if record[field] is None:
        return None
    return _integer(
        record,
        field,
        family,
        minimum=minimum,
        maximum=maximum,
    )


def _boolean(record: Record, field: str, family: str) -> bool:
    value = record[field]
    if not isinstance(value, bool):
        raise ValueError(f"invalid {family} record: {field} must be a boolean")
    return value


def _validate_common(record: Record, family: str) -> None:
    for field in (
        "run_id",
        "scenario_id",
        "evidence_class",
        "timestamp",
        "source",
    ):
        _string(record, field, family)
    classify_evidence_record(record)


def _validate_identity(record: Record) -> None:
    family = "identity"
    for field in (
        "subscriber_id",
        "realm",
        "visited_ap",
        "home_domain",
        "eap_method",
    ):
        _string(record, field, family)

    auth_result = _string(record, "auth_result", family)
    if auth_result not in {"accept", "reject", "error"}:
        raise ValueError(
            "invalid identity record: auth_result must be accept, reject, " "or error"
        )

    failure_reason = _nullable_string(record, "failure_reason", family)
    session_id = _nullable_string(record, "session_id", family)
    accounting_id = _nullable_string(record, "accounting_id", family)
    _number(record, "auth_latency_ms", family)

    if auth_result == "accept":
        if failure_reason is not None:
            raise ValueError(
                "invalid identity record: accepted identity must not have "
                "a failure_reason"
            )
        if session_id is None or accounting_id is None:
            raise ValueError(
                "invalid identity record: accepted identity requires "
                "session_id and accounting_id"
            )
    else:
        if failure_reason is None:
            raise ValueError(
                "invalid identity record: rejected identity requires " "failure_reason"
            )
        if session_id is not None or accounting_id is not None:
            raise ValueError(
                "invalid identity record: rejected identity must not have "
                "session_id or accounting_id"
            )


def _validate_slice(record: Record) -> None:
    family = "slice"
    _string(record, "subscriber_id", family)
    _string(record, "slice_id", family)
    _optional_integer(
        record,
        "vlan_id",
        family,
        minimum=1,
        maximum=4094,
    )
    _optional_integer(
        record,
        "vni",
        family,
        minimum=1,
        maximum=16_777_215,
    )
    for field in (
        "rate_limit_mbps",
        "throughput_mbps",
        "latency_ms",
        "jitter_ms",
    ):
        _number(record, field, family)
    _number(record, "loss_rate", family, maximum=1.0)
    _number(record, "queue_occupancy", family, maximum=1.0)

    sla_status = _string(record, "sla_status", family)
    if sla_status not in {"pass", "fail", "unknown"}:
        raise ValueError(
            "invalid slice record: sla_status must be pass, fail, or unknown"
        )


def _validate_edge(record: Record) -> None:
    family = "edge"
    _string(record, "ap_id", family)
    for field in (
        "cpu_ratio",
        "ram_ratio",
        "tunnel_overhead_ratio",
        "queueing_overhead_ratio",
    ):
        _number(record, field, family, maximum=1.0)
    _number(record, "irq_rate", family)
    _number(record, "crypto_throughput_mbps", family)
    _number(
        record,
        "telemetry_interval_s",
        family,
        exclusive_minimum=True,
    )


def _validate_accounting(record: Record) -> None:
    family = "accounting"
    for field in (
        "subscriber_id",
        "session_id",
        "termination_cause",
    ):
        _string(record, field, family)
    for field in (
        "radius_bytes_in",
        "radius_bytes_out",
        "gateway_bytes_in",
        "gateway_bytes_out",
        "byte_mismatch",
    ):
        _integer(record, field, family)
    _boolean(record, "within_tolerance", family)
    _boolean(record, "offline_signature_present", family)


def _record_sort_key(record: Record) -> tuple[str, ...]:
    return (
        str(record.get("subscriber_id", "")),
        str(record.get("session_id", "")),
        str(record.get("slice_id", "")),
        str(record.get("ap_id", "")),
        str(record.get("auth_result", "")),
        str(record.get("timestamp", "")),
    )


def _categorize_records(run: PrototypeRun) -> _CategorizedRecords:
    buckets: dict[str, list[Record]] = {family: [] for family in _FAMILY_MARKERS}

    validators = {
        "identity": _validate_identity,
        "slice": _validate_slice,
        "edge": _validate_edge,
        "accounting": _validate_accounting,
    }

    for position, record in enumerate(run.records, start=1):
        matches = sorted(
            family for family, marker in _FAMILY_MARKERS.items() if marker in record
        )
        if not matches:
            raise ValueError(
                f"record {position} has no recognized prototype " "record signature"
            )
        if len(matches) != 1:
            raise ValueError(
                f"record {position} has ambiguous prototype record "
                f"signatures: {', '.join(matches)}"
            )

        family = matches[0]
        try:
            validate_required_fields(record, _REQUIRED_FIELDS[family])
        except ValueError as exc:
            raise ValueError(f"invalid {family} record: {exc}") from exc

        _validate_common(record, family)
        validators[family](record)
        buckets[family].append(record)

    return _CategorizedRecords(
        identities=tuple(sorted(buckets["identity"], key=_record_sort_key)),
        slices=tuple(sorted(buckets["slice"], key=_record_sort_key)),
        edges=tuple(sorted(buckets["edge"], key=_record_sort_key)),
        accounting=tuple(sorted(buckets["accounting"], key=_record_sort_key)),
    )


def _prepare_context(run: PrototypeRun) -> _ReportContext:
    categorized = _categorize_records(run)

    accepted = tuple(
        record for record in categorized.identities if record["auth_result"] == "accept"
    )
    rejected = tuple(
        record
        for record in categorized.identities
        if record["auth_result"] in {"reject", "error"}
    )

    if not accepted:
        raise ValueError("prototype report requires an accepted identity")
    if not rejected:
        raise ValueError("prototype report requires a rejected identity")
    if not categorized.slices:
        raise ValueError("prototype report requires a slice record")
    if not categorized.accounting:
        raise ValueError("prototype report requires an accounting record")
    if not categorized.edges:
        raise ValueError("prototype report requires an edge record")

    all_records = (
        categorized.identities
        + categorized.slices
        + categorized.edges
        + categorized.accounting
    )

    run_ids = {_string(record, "run_id", "prototype") for record in all_records}
    if run_ids != {run.run_id}:
        raise ValueError("prototype report records must match PrototypeRun.run_id")

    scenario_ids = {
        _string(record, "scenario_id", "prototype") for record in all_records
    }
    if len(scenario_ids) != 1:
        raise ValueError("prototype report requires one shared scenario_id")

    accepted_subscribers = {
        _string(record, "subscriber_id", "identity") for record in accepted
    }
    rejected_subscribers = {
        _string(record, "subscriber_id", "identity") for record in rejected
    }
    overlap = sorted(accepted_subscribers & rejected_subscribers)
    if overlap:
        raise ValueError(
            "subscriber cannot be both accepted and rejected: " f"{', '.join(overlap)}"
        )

    accepted_sessions = {
        (
            _string(record, "subscriber_id", "identity"),
            _string(record, "session_id", "identity"),
        )
        for record in accepted
    }
    edge_ap_ids = {_string(record, "ap_id", "edge") for record in categorized.edges}

    for record in accepted:
        subscriber_id = _string(record, "subscriber_id", "identity")
        visited_ap = _string(record, "visited_ap", "identity")
        if not any(
            slice_record["subscriber_id"] == subscriber_id
            for slice_record in categorized.slices
        ):
            raise ValueError(
                f"accepted subscriber {subscriber_id!r} has no slice record"
            )
        if not any(
            accounting_record["subscriber_id"] == subscriber_id
            for accounting_record in categorized.accounting
        ):
            raise ValueError(
                f"accepted subscriber {subscriber_id!r} has no " "accounting record"
            )
        if visited_ap not in edge_ap_ids:
            raise ValueError(
                f"accepted subscriber {subscriber_id!r} references "
                f"unreported AP {visited_ap!r}"
            )

    for record in categorized.slices:
        subscriber_id = _string(record, "subscriber_id", "slice")
        if subscriber_id not in accepted_subscribers:
            raise ValueError(
                f"slice record references non-accepted subscriber " f"{subscriber_id!r}"
            )

    for record in categorized.accounting:
        relationship = (
            _string(record, "subscriber_id", "accounting"),
            _string(record, "session_id", "accounting"),
        )
        if relationship not in accepted_sessions:
            raise ValueError(
                "accounting record does not match an accepted "
                f"subscriber session: {relationship!r}"
            )

    for subscriber_id in rejected_subscribers:
        if any(
            record["subscriber_id"] == subscriber_id
            for record in categorized.slices + categorized.accounting
        ):
            raise ValueError(
                f"rejected subscriber {subscriber_id!r} has service or "
                "accounting evidence"
            )

    actual_class_set = {classify_evidence_record(record) for record in all_records}
    if actual_class_set != set(run.evidence_classes):
        raise ValueError("PrototypeRun.evidence_classes does not match its records")
    actual_classes = tuple(sorted(actual_class_set, key=lambda item: item.value))

    return _ReportContext(
        scenario_id=next(iter(scenario_ids)),
        evidence_classes=tuple(
            evidence_class.value for evidence_class in actual_classes
        ),
        sources=tuple(
            sorted({_string(record, "source", "prototype") for record in all_records})
        ),
        timestamps=tuple(
            sorted(
                {_string(record, "timestamp", "prototype") for record in all_records}
            )
        ),
        accepted=accepted,
        rejected=rejected,
        slices=categorized.slices,
        edges=categorized.edges,
        accounting=categorized.accounting,
    )


def _cell(value: object) -> str:
    if value is None:
        return "not configured"
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("\r\n", "<br>")
        .replace("\r", "<br>")
        .replace("\n", "<br>")
    )


def _number_text(value: object) -> str:
    assert isinstance(value, (int, float)) and not isinstance(value, bool)
    if isinstance(value, int):
        return str(value)
    return format(value, ".6g")


def _ratio_text(value: object) -> str:
    assert isinstance(value, (int, float)) and not isinstance(value, bool)
    return f"{float(value):.2%}"


def _boolean_text(value: object) -> str:
    assert isinstance(value, bool)
    return "yes" if value else "no"


def _table(headers: tuple[str, ...], rows: list[tuple[object, ...]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend(
        "| " + " | ".join(_cell(value) for value in row) + " |" for row in rows
    )
    return lines


def render_prototype_summary(run: PrototypeRun) -> str:
    """Render a deterministic Markdown acceptance report for ``run``.

    The function validates the report-level relationships required by
    Stage 2.6. It does not mutate input records, repair evidence, execute
    prototype services, or upgrade the evidence classification.
    """

    context = _prepare_context(run)
    lines: list[str] = [
        f"# Prototype Acceptance Report — {_cell(run.run_id)}",
        "",
        "## Acceptance statement",
        "",
        "The repository contains a deterministic acceptance report generated",
        "from the Stage 2 emulated prototype evidence scaffold. It traces",
        "accepted and rejected subscriber paths through represented policy,",
        "slice, shaping, accounting, and edge-resource records. It does not",
        "constitute measured, isolation, hardware-feasibility, or production",
        "validation.",
        "",
        "## Run identity and provenance",
        "",
    ]

    lines.extend(
        _table(
            ("Field", "Value"),
            [
                ("Run ID", run.run_id),
                ("Scenario ID", context.scenario_id),
                ("Evidence class", ", ".join(context.evidence_classes)),
                ("Source", ", ".join(context.sources)),
                ("Record count", len(run.records)),
                ("First fixture timestamp", context.timestamps[0]),
                ("Last fixture timestamp", context.timestamps[-1]),
            ],
        )
    )

    lines.extend(
        [
            "",
            "All values below are fixture-represented. The timestamps are",
            "evidence timestamps, not report-generation timestamps.",
            "",
            "## Accepted subscriber path",
            "",
        ]
    )

    accepted_rows: list[tuple[object, ...]] = []
    for identity in context.accepted:
        subscriber_id = identity["subscriber_id"]
        subscriber_slices = tuple(
            record
            for record in context.slices
            if record["subscriber_id"] == subscriber_id
        )
        accepted_rows.append(
            (
                subscriber_id,
                identity["realm"],
                identity["eap_method"],
                identity["auth_result"],
                identity["session_id"],
                identity["accounting_id"],
                ", ".join(_cell(record["slice_id"]) for record in subscriber_slices),
                ", ".join(_cell(record["vlan_id"]) for record in subscriber_slices),
                ", ".join(_cell(record["vni"]) for record in subscriber_slices),
                ", ".join(
                    f"{_number_text(record['rate_limit_mbps'])} Mbps"
                    for record in subscriber_slices
                ),
                identity["visited_ap"],
            )
        )

    lines.extend(
        _table(
            (
                "Subscriber",
                "Realm",
                "EAP method",
                "Auth",
                "Session",
                "Accounting ID",
                "Slice",
                "VLAN",
                "VNI",
                "Rate limit",
                "Visited AP",
            ),
            accepted_rows,
        )
    )

    lines.extend(
        [
            "",
            "The accepted path has matching slice and accounting records.",
            "This represents the intended control path; it does not prove",
            "that the configuration was installed or enforced.",
            "",
            "## Rejected subscriber path",
            "",
        ]
    )

    lines.extend(
        _table(
            (
                "Subscriber",
                "Auth",
                "Failure reason",
                "Session",
                "Accounting ID",
                "Slice installed",
                "Accounting started",
            ),
            [
                (
                    record["subscriber_id"],
                    record["auth_result"],
                    record["failure_reason"],
                    record["session_id"] or "not applicable",
                    record["accounting_id"] or "not applicable",
                    "no",
                    "no",
                )
                for record in context.rejected
            ],
        )
    )

    lines.extend(
        [
            "",
            "Rejected identities have no matching slice or accounting record.",
            "",
            "## Slice and shaping representation",
            "",
            "The rate and performance values are emulated aggregate evidence.",
            "They represent shaping intent and do not validate enforcement.",
            "",
        ]
    )

    lines.extend(
        _table(
            (
                "Subscriber",
                "Slice",
                "VLAN",
                "VNI",
                "Rate limit",
                "Throughput",
                "Latency",
                "Jitter",
                "Loss",
                "Queue occupancy",
                "SLA",
            ),
            [
                (
                    record["subscriber_id"],
                    record["slice_id"],
                    record["vlan_id"],
                    record["vni"],
                    f"{_number_text(record['rate_limit_mbps'])} Mbps",
                    f"{_number_text(record['throughput_mbps'])} Mbps",
                    f"{_number_text(record['latency_ms'])} ms",
                    f"{_number_text(record['jitter_ms'])} ms",
                    _ratio_text(record["loss_rate"]),
                    _ratio_text(record["queue_occupancy"]),
                    record["sla_status"],
                )
                for record in context.slices
            ],
        )
    )

    lines.extend(
        [
            "",
            "## Accounting consistency",
            "",
            "The mismatch and tolerance status are fixture-provided values.",
            "No unrecorded tolerance threshold is inferred.",
            "",
        ]
    )

    lines.extend(
        _table(
            (
                "Subscriber",
                "Session",
                "RADIUS in",
                "RADIUS out",
                "Gateway in",
                "Gateway out",
                "Byte mismatch",
                "Within tolerance",
                "Termination",
                "Offline signature",
            ),
            [
                (
                    record["subscriber_id"],
                    record["session_id"],
                    record["radius_bytes_in"],
                    record["radius_bytes_out"],
                    record["gateway_bytes_in"],
                    record["gateway_bytes_out"],
                    record["byte_mismatch"],
                    _boolean_text(record["within_tolerance"]),
                    record["termination_cause"],
                    _boolean_text(record["offline_signature_present"]),
                )
                for record in context.accounting
            ],
        )
    )

    lines.extend(
        [
            "",
            "## Edge-resource snapshot",
            "",
            "These values are emulated observations. They do not establish",
            "physical access-point feasibility.",
            "",
        ]
    )

    lines.extend(
        _table(
            (
                "AP",
                "CPU",
                "RAM",
                "IRQ rate",
                "Crypto throughput",
                "Tunnel overhead",
                "Queueing overhead",
                "Telemetry interval",
            ),
            [
                (
                    record["ap_id"],
                    _ratio_text(record["cpu_ratio"]),
                    _ratio_text(record["ram_ratio"]),
                    _number_text(record["irq_rate"]),
                    f"{_number_text(record['crypto_throughput_mbps'])} Mbps",
                    _ratio_text(record["tunnel_overhead_ratio"]),
                    _ratio_text(record["queueing_overhead_ratio"]),
                    f"{_number_text(record['telemetry_interval_s'])} s",
                )
                for record in context.edges
            ],
        )
    )

    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- This run is an emulated scaffold.",
            "- It is not measured evidence.",
            "- It does not validate FreeRADIUS execution.",
            "- It does not validate OpenWrt behavior.",
            "- It does not validate dynamic VLAN enforcement.",
            "- It does not validate traffic-shaping enforcement.",
            "- It does not validate cross-slice isolation.",
            "- It does not validate Wi-Fi airtime.",
            "- It does not prove AP CPU, RAM, or IRQ feasibility.",
            "- It is not production-ready.",
            "",
            "## Next live-lab steps",
            "",
            "1. Complete the Stage 2.7 live-lab checklist and command guide.",
            "2. Back up the lab configuration and identify every interface.",
            "3. Execute authentication, shaping, accounting, and resource",
            "   collection procedures only in the approved lab environment.",
            "4. Preserve raw logs and normalize them into a new run directory;",
            "   do not overwrite `prototype_run_001`.",
            "5. Assign `M = Measured` only to observations produced by an",
            "   identifiable live collection procedure.",
            "6. Regenerate this report for the new run and retain the same",
            "   evidence and claim boundaries.",
            "",
        ]
    )

    return "\n".join(lines)
