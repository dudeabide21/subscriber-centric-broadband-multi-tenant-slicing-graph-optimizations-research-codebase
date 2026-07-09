#!/usr/bin/env bash
# scripts/setup/check_environment.sh
# Thin wrapper — activates venv (if present) and delegates to the real
# Python file so __file__, linting, and tracebacks all work correctly.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Optional: activate a project venv if one exists
if [ -f "${SCRIPT_DIR}/../../.venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "${SCRIPT_DIR}/../../.venv/bin/activate"
fi

python3 "${SCRIPT_DIR}/check_environment.py"