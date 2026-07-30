from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIRECTORY = (
    REPOSITORY_ROOT / "data" / "samples" / "prototype_run_001"
)
SCHEMA_DIRECTORY = REPOSITORY_ROOT / "data" / "schemas"

EXPECTED_JSON_FILES = {
    "accounting_consistency.json",
    "edge_resource.json",
    "identity_session_accept.json",
    "identity_session_reject.json",
    "slice_performance.json",
}

FIXTURE_SCHEMA_MAP = {
    "accounting_consistency.json": "accounting_consistency.schema.json",
    "edge_resource.json": "edge_resource.schema.json",
    "identity_session_accept.json": "identity_session.schema.json",
    "identity_session_reject.json": "identity_session.schema.json",
    "slice_performance.json": "slice_performance.schema.json",
}

EXPECTED_RUN_ID = "prototype_run_001"
EXPECTED_SCENARIO_ID = "single-subscriber-policy-path"
EXPECTED_SOURCE = "stage2-emulated-fixture"


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), f"{path} must contain a JSON object"
    return value


def _load_fixture(name: str) -> dict[str, Any]:
    return _load_json(FIXTURE_DIRECTORY / name)


def _matches_json_type(value: object, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "number":
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
        )
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "null":
        return value is None
    raise AssertionError(f"unsupported JSON Schema type: {expected_type}")


def _schema_accepts_value(
    value: object,
    schema: dict[str, Any],
) -> bool:
    if "anyOf" in schema:
        alternatives = schema["anyOf"]
        assert isinstance(alternatives, list)
        return any(
            _schema_accepts_value(value, alternative)
            for alternative in alternatives
        )

    if "oneOf" in schema:
        alternatives = schema["oneOf"]
        assert isinstance(alternatives, list)
        return (
            sum(
                _schema_accepts_value(value, alternative)
                for alternative in alternatives
            )
            == 1
        )

    expected_types = schema.get("type")
    if expected_types is not None:
        if isinstance(expected_types, str):
            expected_types = [expected_types]

        assert isinstance(expected_types, list)

        if not any(
            _matches_json_type(value, expected_type)
            for expected_type in expected_types
        ):
            return False

    if "const" in schema and value != schema["const"]:
        return False

    if "enum" in schema and value not in schema["enum"]:
        return False

    if (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
    ):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        exclusive_minimum = schema.get("exclusiveMinimum")
        exclusive_maximum = schema.get("exclusiveMaximum")

        if minimum is not None and value < minimum:
            return False
        if maximum is not None and value > maximum:
            return False
        if (
            exclusive_minimum is not None
            and value <= exclusive_minimum
        ):
            return False
        if (
            exclusive_maximum is not None
            and value >= exclusive_maximum
        ):
            return False

    if isinstance(value, str):
        minimum_length = schema.get("minLength")
        maximum_length = schema.get("maxLength")

        if minimum_length is not None and len(value) < minimum_length:
            return False
        if maximum_length is not None and len(value) > maximum_length:
            return False

    return True


def _assert_record_matches_schema(
    record: dict[str, Any],
    schema: dict[str, Any],
) -> None:
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    assert isinstance(required, list)
    assert isinstance(properties, dict)

    missing = sorted(set(required) - set(record))
    assert missing == [], f"missing required fields: {missing}"

    if schema.get("additionalProperties") is False:
        unexpected = sorted(set(record) - set(properties))
        assert unexpected == [], f"unexpected fields: {unexpected}"

    for field_name, value in record.items():
        property_schema = properties.get(field_name)
        assert isinstance(
            property_schema,
            dict,
        ), f"schema missing property definition for {field_name}"

        assert _schema_accepts_value(
            value,
            property_schema,
        ), f"invalid value for {field_name}: {value!r}"


def test_expected_stage2_sample_files_exist() -> None:
    actual_json_files = {
        path.name
        for path in FIXTURE_DIRECTORY.glob("*.json")
        if path.is_file()
    }

    assert actual_json_files == EXPECTED_JSON_FILES
    assert (FIXTURE_DIRECTORY / "README.md").is_file()


def test_all_fixture_files_parse_as_json_objects() -> None:
    for name in sorted(EXPECTED_JSON_FILES):
        record = _load_fixture(name)
        assert record


def test_fixture_records_conform_to_stage2_schemas() -> None:
    for fixture_name, schema_name in FIXTURE_SCHEMA_MAP.items():
        record = _load_fixture(fixture_name)
        schema = _load_json(SCHEMA_DIRECTORY / schema_name)

        _assert_record_matches_schema(record, schema)


def test_fixture_records_share_deterministic_run_metadata() -> None:
    for name in sorted(EXPECTED_JSON_FILES):
        record = _load_fixture(name)

        assert record["run_id"] == EXPECTED_RUN_ID
        assert record["scenario_id"] == EXPECTED_SCENARIO_ID
        assert record["evidence_class"] == "E"
        assert record["source"] == EXPECTED_SOURCE


def test_fixture_timestamps_are_timezone_aware() -> None:
    for name in sorted(EXPECTED_JSON_FILES):
        timestamp = _load_fixture(name)["timestamp"]
        assert isinstance(timestamp, str)

        parsed = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )

        assert parsed.tzinfo is not None


def test_accepted_identity_has_session_and_accounting_ids() -> None:
    accepted = _load_fixture("identity_session_accept.json")

    assert accepted["subscriber_id"] == "subscriber-demo-001"
    assert accepted["auth_result"] == "accept"
    assert accepted["failure_reason"] is None
    assert accepted["session_id"] == "stage2-session-001"
    assert (
        accepted["accounting_id"]
        == "acct-prototype-basic-001"
    )


def test_rejected_identity_has_no_service_session() -> None:
    rejected = _load_fixture("identity_session_reject.json")

    assert rejected["subscriber_id"] == "subscriber-demo-invalid"
    assert rejected["auth_result"] == "reject"
    assert rejected["failure_reason"] == "invalid-subscriber"
    assert rejected["session_id"] is None
    assert rejected["accounting_id"] is None


def test_rejected_subscriber_has_no_service_or_accounting_record() -> None:
    rejected_subscriber = "subscriber-demo-invalid"

    service_records = [
        _load_fixture("slice_performance.json"),
        _load_fixture("accounting_consistency.json"),
    ]

    for record in service_records:
        assert record["subscriber_id"] != rejected_subscriber


def test_slice_record_matches_basic_policy_mapping() -> None:
    slice_record = _load_fixture("slice_performance.json")

    assert slice_record["subscriber_id"] == "subscriber-demo-001"
    assert slice_record["slice_id"] == "slice-basic"
    assert slice_record["vlan_id"] == 110
    assert slice_record["vni"] is None
    assert slice_record["rate_limit_mbps"] == 20.0
    assert slice_record["throughput_mbps"] <= 20.0
    assert slice_record["sla_status"] == "pass"


def test_edge_record_represents_the_same_lab_ap() -> None:
    edge_record = _load_fixture("edge_resource.json")
    accepted = _load_fixture("identity_session_accept.json")

    assert edge_record["ap_id"] == "ap-lab-001"
    assert edge_record["ap_id"] == accepted["visited_ap"]
    assert edge_record["telemetry_interval_s"] == 5.0


def test_accounting_record_is_internally_consistent() -> None:
    accounting = _load_fixture("accounting_consistency.json")
    accepted = _load_fixture("identity_session_accept.json")

    assert accounting["subscriber_id"] == accepted["subscriber_id"]
    assert accounting["session_id"] == accepted["session_id"]

    expected_mismatch = (
        abs(
            accounting["radius_bytes_in"]
            - accounting["gateway_bytes_in"]
        )
        + abs(
            accounting["radius_bytes_out"]
            - accounting["gateway_bytes_out"]
        )
    )


    assert accounting["byte_mismatch"] == expected_mismatch
    assert accounting["byte_mismatch"] == 0
    assert accounting["within_tolerance"] is True
    assert accounting["termination_cause"] == "User-Request"
    assert accounting["offline_signature_present"] is False


def test_fixture_readme_states_evidence_limitations() -> None:
    readme = (
        FIXTURE_DIRECTORY / "README.md"
    ).read_text(encoding="utf-8").lower()

    assert "evidence class: `e`" in readme
    assert "emulated scaffold" in readme
    assert "not measured evidence" in readme
    assert "does not validate freeradius" in readme
    assert "does not validate openwrt" in readme
    assert "does not validate cross-slice isolation" in readme
    assert "docker is not required" in readme
