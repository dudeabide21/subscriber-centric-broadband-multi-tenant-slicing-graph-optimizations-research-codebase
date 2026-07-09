#!/usr/bin/env python3
"""
scripts/setup/check_environment.py

Verifies that the repository skeleton (required files/directories) is present
before development, testing, or CI proceeds.

Design notes (see project vault note for full rationale):
- Must be run as a script, not imported, without an explicit main() guard.
- Root discovery walks upward to pyproject.toml rather than assuming a fixed
  parents[N] depth, so this file can move without silently checking the
  wrong directory.
"""

from pathlib import Path
import sys


def find_root(start: Path) -> Path:
    """Walk upward from `start` until a directory containing pyproject.toml
    is found. Raises if no such directory exists (fails loudly instead of
    silently checking the wrong root)."""
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").exists():
            return candidate
    raise RuntimeError(
        f"Could not locate repo root: no pyproject.toml found above {start}"
    )


def main() -> int:
    root = find_root(Path(__file__).resolve())

    required = [
        root / "pyproject.toml",
        root / "README.md",
        root / "src" / "scb",
        root / "src" / "scb" / "telemetry" / "sample_processing.py",
        root / "tests",
        root / "data" / "samples",
    ]

    missing = [str(p) for p in required if not p.exists()]

    if missing:
        print("Missing required paths:")
        for item in missing:
            print(f" - {item}")
        return 1

    print("Environment check passed: repository skeleton is present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
