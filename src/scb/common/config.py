"""Config helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    """Repository paths derived from a project root."""

    root: Path

    @property
    def samples(self) -> Path:
        return self.root / "data" / "samples"
