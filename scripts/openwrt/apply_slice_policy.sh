#!/usr/bin/env bash
set -euo pipefail

: "${DRY_RUN:=1}"
: "${APPLY:=0}"

if [[ "${APPLY}" != "1" ]]; then
  echo "DRY_RUN=${DRY_RUN}: would apply slice policy."
  exit 0
fi

echo "Applying slice policy."
