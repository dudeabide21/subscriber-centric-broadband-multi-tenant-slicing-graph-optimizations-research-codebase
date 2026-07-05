"""Parse synthetic OpenWrt CPU/RAM/IRQ metrics.

Synthetic format:

    <ISO-timestamp> ap_id=<id> cpu_percent=<float>
        ram_used_mb=<float> ram_total_mb=<float>
        irq_rate=<float> load_avg=<float>

The parser is strict: a missing field causes a parse error rather than a
silent zero.
"""

from __future__ import annotations

from pathlib import Path

from scb.telemetry.schemas import EvidenceClass, OpenWrtMetricRecord

_REQUIRED_KEYS = {
    "ap_id",
    "cpu_percent",
    "ram_used_mb",
    "ram_total_mb",
    "irq_rate",
    "load_avg",
}


def _iter_lines(text: str) -> list[list[str]]:
    out: list[list[str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line.split())
    return out


def _parse_key_values(tokens: list[str], record: OpenWrtMetricRecord) -> None:
    found: set[str] = set()
    for token in tokens:
        if "=" not in token:
            continue
        key, raw = token.split("=", 1)
        key = key.strip()
        value = raw.strip()
        found.add(key)
        if key == "ap_id":
            record.ap_id = value
        elif key == "cpu_percent":
            record.cpu_percent = float(value)
        elif key == "ram_used_mb":
            record.ram_used_mb = float(value)
        elif key == "ram_total_mb":
            record.ram_total_mb = float(value)
        elif key == "irq_rate":
            record.irq_rate = float(value)
        elif key == "load_avg":
            record.load_avg = float(value)
    missing = _REQUIRED_KEYS - found
    if missing:
        raise ValueError(f"missing openwrt metric keys: {sorted(missing)}")


def parse_openwrt_metrics(
    path: Path,
    repo_root: Path,
    parser_version: str,
    evidence_class: EvidenceClass = EvidenceClass.SYNTHETIC,
) -> list[OpenWrtMetricRecord]:
    """Parse a synthetic OpenWrt metrics file.

    Args:
        path: Path to the file.
        repo_root: Repository root used to compute the relative source path.
        parser_version: Parser version stamp.
        evidence_class: Defaults to :attr:`EvidenceClass.SYNTHETIC`.

    Returns:
        A list of :class:`OpenWrtMetricRecord` objects.

    Raises:
        ValueError: If a line is malformed or required keys are missing.
    """

    text = path.read_text(encoding="utf-8")
    records: list[OpenWrtMetricRecord] = []
    for tokens in _iter_lines(text):
        if len(tokens) < 1:
            raise ValueError("invalid openwrt metrics line")
        timestamp = tokens[0]
        record = OpenWrtMetricRecord(
            evidence_class=evidence_class,
            source_file=path.relative_to(repo_root).as_posix(),
            source_type="openwrt_metrics",
            parser_version=parser_version,
            timestamp=timestamp,
            ap_id="",
            cpu_percent=0.0,
            ram_used_mb=0.0,
            ram_total_mb=0.0,
            irq_rate=0.0,
            load_avg=0.0,
        )
        _parse_key_values(tokens[1:], record)
        records.append(record)
    return records
