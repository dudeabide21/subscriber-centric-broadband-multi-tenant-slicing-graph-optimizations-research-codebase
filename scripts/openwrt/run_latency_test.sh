#!/usr/bin/env bash
set -euo pipefail

: "${DRY_RUN:=1}"
: "${APPLY:=0}"

if [[ "${DRY_RUN}" == "1" || "${APPLY}" != "1" ]]; then
  echo "DRY_RUN=${DRY_RUN}: would run latency test."
  exit 0
fi

echo "Running latency test."
