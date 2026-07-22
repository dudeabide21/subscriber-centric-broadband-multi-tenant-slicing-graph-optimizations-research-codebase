
from __future__ import annotations

import os
import subprocess
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

FREERADIUS_DIRECTORY = REPOSITORY_ROOT / "configs" / "freeradius"
OPENWRT_DIRECTORY = REPOSITORY_ROOT / "configs" / "openwrt"

EXPECTED_FILES = {
    FREERADIUS_DIRECTORY / "users.example",
    FREERADIUS_DIRECTORY / "clients.conf.example",
    FREERADIUS_DIRECTORY / "policy_mapping.example",
    FREERADIUS_DIRECTORY / "sites-enabled-default-notes.md",
    OPENWRT_DIRECTORY / "wireless.example",
    OPENWRT_DIRECTORY / "network.example",
    OPENWRT_DIRECTORY / "firewall.example",
    OPENWRT_DIRECTORY / "hostapd_8021x.example",
    OPENWRT_DIRECTORY / "tc_slices.example.sh",
}

REQUIRED_PLACEHOLDERS = {
    "<RADIUS_SECRET>",
    "<RADIUS_SERVER_IP>",
    "<AP_GATEWAY_IP>",
    "<CLIENT_CERT_PATH>",
    "<AP_INTERFACE>",
    "<WAN_INTERFACE>",
    "<LAN_INTERFACE>",
    "<SUBSCRIBER_REALM>",
    "<EXAMPLE_SUBSCRIBER_PASSWORD>",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _all_template_text() -> str:
    return "\n".join(
        _read(path)
        for path in sorted(EXPECTED_FILES)
    )


def test_expected_stage2_configuration_templates_exist() -> None:
    missing = sorted(
        str(path.relative_to(REPOSITORY_ROOT))
        for path in EXPECTED_FILES
        if not path.is_file()
    )

    assert missing == []


def test_required_placeholders_are_present() -> None:
    aggregate = _all_template_text()

    missing = sorted(
        placeholder
        for placeholder in REQUIRED_PLACEHOLDERS
        if placeholder not in aggregate
    )

    assert missing == []


def test_existing_readme_warnings_are_preserved() -> None:
    freeradius_readme = _read(FREERADIUS_DIRECTORY / "README.md")
    openwrt_readme = _read(OPENWRT_DIRECTORY / "README.md")

    assert "examples only" in freeradius_readme
    assert "not production policy" in freeradius_readme

    assert "controlled lab use only" in openwrt_readme
    assert "Do not apply them to live systems" in openwrt_readme


def test_freeradius_accept_path_has_required_policy_attributes() -> None:
    users = _read(FREERADIUS_DIRECTORY / "users.example")
    mapping = _read(
        FREERADIUS_DIRECTORY / "policy_mapping.example"
    )

    assert "subscriber-demo-001@<SUBSCRIBER_REALM>" in users
    assert 'Cleartext-Password := "<EXAMPLE_SUBSCRIBER_PASSWORD>"' in users
    assert 'Filter-Id := "slice-basic"' in users
    assert 'Tunnel-Private-Group-Id := "110"' in users
    assert 'Class := "acct-prototype-basic-001"' in users

    assert "auth_result = accept" in mapping
    assert "slice_id = slice-basic" in mapping
    assert "tc_class_id = 1:10" in mapping
    assert "rate_limit = 20mbit" in mapping
    assert "accounting_class = acct-prototype-basic-001" in mapping


def test_freeradius_reject_path_assigns_no_service() -> None:
    users = _read(FREERADIUS_DIRECTORY / "users.example")
    mapping = _read(
        FREERADIUS_DIRECTORY / "policy_mapping.example"
    )

    assert "subscriber-demo-invalid@<SUBSCRIBER_REALM>" in users
    assert "Auth-Type := Reject" in users

    invalid_section = mapping.split(
        "[subscriber-demo-invalid@<SUBSCRIBER_REALM>]",
        maxsplit=1,
    )[1].split("[default]", maxsplit=1)[0]

    assert "auth_result = reject" in invalid_section
    assert "slice_id = null" in invalid_section
    assert "tc_class_id = null" in invalid_section
    assert "accounting_class = null" in invalid_section


def test_openwrt_templates_contain_radius_and_vlan_intent() -> None:
    wireless = _read(OPENWRT_DIRECTORY / "wireless.example")
    network = _read(OPENWRT_DIRECTORY / "network.example")
    hostapd = _read(
        OPENWRT_DIRECTORY / "hostapd_8021x.example"
    )

    assert "auth_server '<RADIUS_SERVER_IP>'" in wireless
    assert "acct_server '<RADIUS_SERVER_IP>'" in wireless
    assert "dynamic_vlan '1'" in wireless

    assert "vlan '110'" in network
    assert "vlan '120'" in network
    assert "vlan '130'" in network

    assert "ieee8021x=1" in hostapd
    assert "auth_server_addr=<RADIUS_SERVER_IP>" in hostapd
    assert "acct_server_addr=<RADIUS_SERVER_IP>" in hostapd


def test_tc_template_contains_htb_and_fq_codel_classes() -> None:
    script = _read(
        OPENWRT_DIRECTORY / "tc_slices.example.sh"
    )

    assert "htb default 30" in script
    assert "classid 1:10" in script
    assert "classid 1:20" in script
    assert "classid 1:30" in script
    assert script.count("fq_codel") >= 3


def test_tc_template_has_valid_bash_syntax() -> None:
    script = OPENWRT_DIRECTORY / "tc_slices.example.sh"

    subprocess.run(
        ["bash", "-n", str(script)],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def test_tc_template_defaults_to_non_mutating_dry_run() -> None:
    script = OPENWRT_DIRECTORY / "tc_slices.example.sh"

    environment = os.environ.copy()
    environment.pop("DRY_RUN", None)
    environment.pop("CONFIRM_LIVE_TC", None)
    environment.pop("AP_INTERFACE", None)

    completed = subprocess.run(
        ["bash", str(script)],
        cwd=REPOSITORY_ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "DRY-RUN:" in completed.stdout
    assert "tc qdisc replace" in completed.stdout
    assert "tc class replace" in completed.stdout


def test_tc_live_mode_requires_explicit_confirmation() -> None:
    script = OPENWRT_DIRECTORY / "tc_slices.example.sh"

    environment = os.environ.copy()
    environment["DRY_RUN"] = "0"
    environment["AP_INTERFACE"] = "stage2-test-interface"
    environment.pop("CONFIRM_LIVE_TC", None)

    completed = subprocess.run(
        ["bash", str(script)],
        cwd=REPOSITORY_ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    assert "CONFIRM_LIVE_TC=APPLY_STAGE2_TC" in completed.stderr


def test_templates_contain_no_private_key_material() -> None:
    aggregate = _all_template_text()

    assert "-----BEGIN PRIVATE KEY-----" not in aggregate
    assert "-----BEGIN RSA PRIVATE KEY-----" not in aggregate
    assert "-----BEGIN OPENSSH PRIVATE KEY-----" not in aggregate


def test_templates_do_not_automatically_reload_network() -> None:
    aggregate = _all_template_text().lower()

    prohibited = {
        "uci commit",
        "/etc/init.d/network restart",
        "service network restart",
        "wifi reload",
        "\nreboot",
    }

    found = sorted(
        command
        for command in prohibited
        if command in aggregate
    )

    assert found == []
