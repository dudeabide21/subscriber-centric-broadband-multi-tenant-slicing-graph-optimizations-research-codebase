"""Static acceptance tests for Stage 2.7 live-lab documentation."""

from __future__ import annotations

from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = REPOSITORY_ROOT / "docs" / "prototype" / "live_lab_checklist.md"
COMMANDS = REPOSITORY_ROOT / "docs" / "prototype" / "measurement_commands.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_stage2_7_documents_exist() -> None:
    assert CHECKLIST.is_file()
    assert COMMANDS.is_file()


def test_checklist_contains_required_readiness_topics() -> None:
    text = _text(CHECKLIST).lower()
    for topic in (
        "package inventory",
        "interface",
        "backup",
        "log collection",
        "authentication",
        "traffic control",
        "accounting",
        "rollback",
        "secret",
        "stop conditions",
    ):
        assert topic in text


def test_command_guide_uses_explicit_safety_labels() -> None:
    text = _text(COMMANDS)
    for label in (
        "**READ-ONLY",
        "**SERVICE-AFFECTING",
        "**MUTATING",
        "**ROLLBACK",
    ):
        assert label in text


def test_documents_preserve_evidence_boundaries() -> None:
    combined = f"{_text(CHECKLIST)}\n{_text(COMMANDS)}".lower()
    assert "does not produce measured evidence" in combined
    assert "m = measured" in combined
    assert "do not overwrite `prototype_run_001`" in combined
    assert "docker is not part of this path" in combined


def test_command_guide_uses_placeholders_and_secret_file() -> None:
    text = _text(COMMANDS)
    assert "<TC_INTERFACE>" in text
    assert "<CONTROLLER_HOST>" in text
    assert "<SECRET_FILE>" in text
    assert "radclient -x -S '<SECRET_FILE>'" in text


def test_command_guide_contains_backup_before_restore() -> None:
    text = _text(COMMANDS)
    assert text.index("sysupgrade -b") < text.index("sysupgrade -r")
    assert text.index("**READ-ONLY — validate candidate configuration**") < (
        text.index("**SERVICE-AFFECTING — foreground debug server**")
    )


def test_documents_link_authoritative_references() -> None:
    combined = f"{_text(CHECKLIST)}\n{_text(COMMANDS)}"
    assert "https://www.freeradius.org/" in combined
    assert "https://openwrt.org/" in combined
    assert "https://man7.org/" in combined
    assert "https://software.es.net/iperf/" in combined


def test_no_private_key_material_is_embedded() -> None:
    combined = f"{_text(CHECKLIST)}\n{_text(COMMANDS)}"
    assert "BEGIN PRIVATE KEY" not in combined
    assert "BEGIN OPENSSH PRIVATE KEY" not in combined
