"""Parse synthetic WireGuard transfer statistics.

Synthetic format:

    interface=<ifname> peer_id_hash=<hash> rx_bytes=<int> tx_bytes=<int>
        latest_handshake=<ISO-timestamp>

The parser is strict: unknown keys are rejected so the researcher can never
accidentally invent peer fields.
"""

from __future__ import annotations

from pathlib import Path

from scb.telemetry.schemas import EvidenceClass, WireGuardStatsRecord

_ALLOWED_KEYS = {
    "interface",
    "peer_id_hash",
    "rx_bytes",
    "tx_bytes",
    "latest_handshake",
}


def _iter_lines(text: str) -> list[list[str]]:
    out: list[list[str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line.split())
    return out


def _parse_key_values(tokens: list[str], record: WireGuardStatsRecord) -> None:
    for token in tokens:
        if "=" not in token:
            continue
        key, raw = token.split("=", 1)
        key = key.strip()
        if key not in _ALLOWED_KEYS:
            raise ValueError(f"unknown wireguard key: {key}")
        value = raw.strip()
        if key == "interface":
            record.interface = value
        elif key == "peer_id_hash":
            record.peer_id_hash = value
        elif key == "rx_bytes":
            record.transfer_rx_bytes = int(value)
        elif key == "tx_bytes":
            record.transfer_tx_bytes = int(value)
        elif key == "latest_handshake":
            record.latest_handshake = value


def parse_wireguard_stats(
    path: Path,
    repo_root: Path,
    parser_version: str,
    evidence_class: EvidenceClass = EvidenceClass.SYNTHETIC,
) -> list[WireGuardStatsRecord]:
    """Parse a synthetic WireGuard transfer statistics file.

    Args:
        path: Path to the file.
        repo_root: Repository root used to compute the relative source path.
        parser_version: Parser version stamp.
        evidence_class: Defaults to :attr:`EvidenceClass.SYNTHETIC`.

    Returns:
        A list of :class:`WireGuardStatsRecord` objects.

    Raises:
        ValueError: If a line is malformed or contains an unknown key.
    """

    text = path.read_text(encoding="utf-8")
    records: list[WireGuardStatsRecord] = []
    for tokens in _iter_lines(text):
        record = WireGuardStatsRecord(
            evidence_class=evidence_class,
            source_file=path.relative_to(repo_root).as_posix(),
            source_type="wireguard_stats",
            parser_version=parser_version,
            interface="",
            peer_id_hash="",
            transfer_rx_bytes=0,
            transfer_tx_bytes=0,
            latest_handshake="",
        )
        _parse_key_values(tokens, record)
        if not record.interface or not record.peer_id_hash:
            raise ValueError(f"missing required wireguard keys: {tokens}")
        records.append(record)
    return records
