#!/usr/bin/env bash
set -euo pipefail

: "${DRY_RUN:=1}"

if [[ "${DRY_RUN}" != "1" ]]; then
  echo "Stage 2.6 supports report-only dry runs; set DRY_RUN=1." >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOSITORY_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${REPOSITORY_ROOT}"

PYTHONPATH=src python3 scripts/prototype/summarize_run.py \
  --run-dir data/samples/prototype_run_001 \
  --output reports/prototype_run_001.md
