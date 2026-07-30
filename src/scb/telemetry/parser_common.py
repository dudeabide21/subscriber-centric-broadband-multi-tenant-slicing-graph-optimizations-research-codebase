"""Shared fail-loud utilities for raw telemetry parsers."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from datetime import datetime
from math import isfinite
from pathlib import Path
from typing import TypeVar

T = TypeVar("T")


def read_utf8_text(path: Path) -> str:
    """Read one regular UTF-8 file without repairing invalid input."""

    if not path.exists():
        raise FileNotFoundError(f"missing telemetry source: {path}")
    if not path.is_file():
        raise IsADirectoryError(f"telemetry source is not a file: {path}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"telemetry source is not valid UTF-8: {path}") from exc


def repository_relative_source(path: Path, repo_root: Path) -> str:
    """Return a resolved POSIX source path confined to ``repo_root``."""

    resolved_path = path.resolve(strict=True)
    resolved_root = repo_root.resolve(strict=True)
    try:
        relative = resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(
            f"telemetry source is outside repository root: {path}"
        ) from exc
    return relative.as_posix()


def validate_aware_timestamp(value: str, *, field: str = "timestamp") -> str:
    """Require a non-empty ISO-8601 timestamp with an explicit UTC offset."""

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be a valid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include a timezone offset")
    return value


def iter_data_lines(text: str) -> Iterable[tuple[int, str]]:
    """Yield one-based line numbers and non-comment, non-blank data lines."""

    for line_number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        yield line_number, line


def parse_strict_key_values(
    tokens: Iterable[str],
    *,
    allowed_keys: Iterable[str],
    required_keys: Iterable[str],
    aliases: Mapping[str, str] | None = None,
    context: str,
) -> dict[str, str]:
    """Parse strict ``key=value`` tokens with aliases and duplicate checks."""

    allowed = set(allowed_keys)
    required = set(required_keys)
    if not required <= allowed:
        raise ValueError("required parser keys must be allowed")

    alias_map = dict(aliases or {})
    values: dict[str, str] = {}
    for token in tokens:
        if "=" not in token:
            raise ValueError(f"{context}: malformed token {token!r}")
        key, raw = token.split("=", 1)
        key = key.strip()
        raw = raw.strip()
        if not key or not raw:
            raise ValueError(f"{context}: empty key or value in {token!r}")

        canonical = alias_map.get(key, key)
        if canonical not in allowed:
            raise ValueError(f"{context}: unknown key {key!r}")
        if canonical in values:
            raise ValueError(f"{context}: duplicate key {canonical!r}")
        values[canonical] = raw

    missing = sorted(required - set(values))
    if missing:
        raise ValueError(f"{context}: missing keys: {', '.join(missing)}")
    return values


def nonnegative_int(value: str, *, field: str) -> int:
    """Parse a non-negative base-10 integer without accepting booleans."""

    try:
        parsed = int(value, 10)
    except ValueError as exc:
        raise ValueError(f"{field} must be an integer") from exc
    if parsed < 0:
        raise ValueError(f"{field} must be non-negative")
    return parsed


def finite_float(
    value: str,
    *,
    field: str,
    minimum: float = 0.0,
    maximum: float | None = None,
    exclusive_minimum: bool = False,
) -> float:
    """Parse a finite float within explicit bounds."""

    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be a number") from exc
    if not isfinite(parsed):
        raise ValueError(f"{field} must be finite")
    if exclusive_minimum and parsed <= minimum:
        raise ValueError(f"{field} must be greater than {minimum}")
    if not exclusive_minimum and parsed < minimum:
        raise ValueError(f"{field} must be at least {minimum}")
    if maximum is not None and parsed > maximum:
        raise ValueError(f"{field} must be at most {maximum}")
    return parsed


def require_records(records: list[T], *, context: str) -> list[T]:
    """Reject a source that contains no data records."""

    if not records:
        raise ValueError(f"{context}: source contains no data records")
    return records


def source_sha256(path: Path) -> str:
    """Return the SHA-256 digest of the exact raw source bytes."""

    if not path.is_file():
        raise FileNotFoundError(f"missing telemetry source: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()
