#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[2]
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
    sys.exit(1)
print("Environment check passed: repository skeleton is present.")
PY
