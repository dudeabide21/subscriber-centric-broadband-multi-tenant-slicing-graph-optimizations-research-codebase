from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIRECTORY = REPOSITORY_ROOT / "data" / "schemas"

SCHEMA_FILES = {
    "identity_session": SCHEMA_DIRECTORY / "identity_session.schema.json",
    "slice_performance": SCHEMA_DIRECTORY / "slice_performance.schema.json",
    "edge_resource": SCHEMA_DIRECTORY / "edge_resource.schema.json",
    "accounting_consistency": (
        SCHEMA_DIRECTORY / "accounting_consistency.schema.json"
    ),
}

COMMON_REQUIRED_FIELDS = {
    "run_id",
    "scenario_id",
    "evidence_class",
    "timestamp",
    "source",
}

SPECIFIC_REQUIRED_FIELDS = {
    "identity_session": {
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
    },
    "slice_performance": {
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
    },
    "edge_resource": {
        "ap_id",
        "cpu_ratio",
        "ram_ratio",
        "irq_rate",
        "crypto_throughput_mbps",
        "tunnel_overhead_ratio",
        "queueing_overhead_ratio",
        "telemetry_interval_s",
    },
    "accounting_consistency": {
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
    },
}


def _load_schema(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as schema_file:
        loaded = json.load(schema_file)

    assert isinstance(loaded, dict)
    return loaded


def test_exact_stage2_schema_files_exist() -> None:
    actual_files = {
        path.name
        for path in SCHEMA_DIRECTORY.glob("*.schema.json")
    }
    expected_files = {
        path.name
        for path in SCHEMA_FILES.values()
    }

    assert actual_files == expected_files


@pytest.mark.parametrize(
    "schema_path",
    SCHEMA_FILES.values(),
    ids=SCHEMA_FILES.keys(),
)
def test_schema_files_load_as_json_objects(
    schema_path: Path,
) -> None:
    schema = _load_schema(schema_path)

    assert schema


@pytest.mark.parametrize(
    "schema_name,schema_path",
    SCHEMA_FILES.items(),
)
def test_schema_common_structure_is_strict(
    schema_name: str,
    schema_path: Path,
) -> None:
    del schema_name

    schema = _load_schema(schema_path)

    assert schema["$schema"] == (
        "https://json-schema.org/draft/2020-12/schema"
    )
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False

    properties = schema["properties"]
    required = set(schema["required"])

    assert COMMON_REQUIRED_FIELDS <= required
    assert COMMON_REQUIRED_FIELDS <= set(properties)
    assert properties["evidence_class"]["enum"] == [
        "M",
        "E",
        "S",
        "C",
    ]


@pytest.mark.parametrize(
    "schema_name,schema_path",
    SCHEMA_FILES.items(),
)
def test_schema_specific_required_fields_are_defined(
    schema_name: str,
    schema_path: Path,
) -> None:
    schema = _load_schema(schema_path)

    properties = set(schema["properties"])
    required = set(schema["required"])
    expected = SPECIFIC_REQUIRED_FIELDS[schema_name]

    assert expected <= properties
    assert expected <= required


def test_identity_auth_result_enum_is_exact() -> None:
    schema = _load_schema(SCHEMA_FILES["identity_session"])

    assert schema["properties"]["auth_result"]["enum"] == [
        "accept",
        "reject",
        "error",
    ]


def test_slice_sla_status_enum_is_exact() -> None:
    schema = _load_schema(SCHEMA_FILES["slice_performance"])

    assert schema["properties"]["sla_status"]["enum"] == [
        "pass",
        "fail",
        "unknown",
    ]


def test_accounting_schema_contains_mismatch_fields() -> None:
    schema = _load_schema(
        SCHEMA_FILES["accounting_consistency"]
    )

    properties = schema["properties"]
    required = set(schema["required"])

    assert "byte_mismatch" in properties
    assert "within_tolerance" in properties
    assert "byte_mismatch" in required
    assert "within_tolerance" in required
    assert properties["byte_mismatch"]["minimum"] == 0
    assert properties["within_tolerance"]["type"] == "boolean"