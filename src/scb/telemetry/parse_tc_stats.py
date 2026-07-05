"""Parse synthetic Linux ``tc`` class/qdisc statistics.

The synthetic format mirrors the relevant fields of ``tc -s class show``:

    class htb <class_id> root rate <RATE>Mbit ceil <CEIL>Mbit
        sent <BYTES> bytes <PACKETS> packets <DROPS> drops
        backlog <BB>b <BP>p requeues <RQ>

Every record is validated against a strict regular expression so any drift
in the synthetic generator fails loudly during CI.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

from scb.telemetry.schemas import EvidenceClass, TcStatsRecord

_TC_LINE_RE = re.compile(
    r"^class\s+htb\s+(?P<class_id>\S+)\s+root\s+rate\s+"
    r"(?P<rate_mbit>\d+(?:\.\d+)?)Mbit\s+ceil\s+"
    r"(?P<ceil_mbit>\d+(?:\.\d+)?)Mbit\s+sent\s+"
    r"(?P<sent_bytes>\d+)\s+bytes\s+(?P<packets>\d+)\s+packets\s+"
    r"(?P<drops>\d+)\s+drops\s+backlog\s+"
    r"(?P<backlog_bytes>\d+)b\s+(?P<backlog_packets>\d+)p\s+requeues\s+"
    r"(?P<requeues>\d+)$"
)


def _iter_matches(text: str) -> Iterator[re.Match[str]]:
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = _TC_LINE_RE.fullmatch(line)
        if match is None:
            raise ValueError(f"invalid tc stats line: {line}")
        yield match


def parse_tc_stats(
    path: Path,
    repo_root: Path,
    parser_version: str,
    interface: str = "ifb0",
    evidence_class: EvidenceClass = EvidenceClass.SYNTHETIC,
) -> list[TcStatsRecord]:
    """Parse a synthetic ``tc`` class statistics file.

    Args:
        path: Path to the file.
        repo_root: Repository root used to compute the relative source path.
        parser_version: Parser version stamp.
        interface: The interface label to attach to every record. The
            synthetic samples do not encode this field.
        evidence_class: Defaults to :attr:`EvidenceClass.SYNTHETIC`.

    Returns:
        A list of :class:`TcStatsRecord` objects.

    Raises:
        ValueError: If a line does not match the expected format.
    """

    text = path.read_text(encoding="utf-8")
    records: list[TcStatsRecord] = []
    for match in _iter_matches(text):
        records.append(
            TcStatsRecord(
                evidence_class=evidence_class,
                source_file=path.relative_to(repo_root).as_posix(),
                source_type="tc_stats",
                parser_version=parser_version,
                interface=interface,
                class_id=match.group("class_id"),
                rate_mbit=float(match.group("rate_mbit")),
                ceil_mbit=float(match.group("ceil_mbit")),
                sent_bytes=int(match.group("sent_bytes")),
                packets=int(match.group("packets")),
                drops=int(match.group("drops")),
                backlog_bytes=int(match.group("backlog_bytes")),
                backlog_packets=int(match.group("backlog_packets")),
                requeues=int(match.group("requeues")),
            )
        )
    return records
