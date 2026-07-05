#!/usr/bin/env bash
set -euo pipefail

: "${DRY_RUN:=1}"
: "${APPLY:=0}"

if [[ "${DRY_RUN}" == "1" || "${APPLY}" != "1" ]]; then
  echo "DRY_RUN=${DRY_RUN}: would create a Python virtual environment and install the package."
  exit 0
fi

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,notebooks,stats]"
