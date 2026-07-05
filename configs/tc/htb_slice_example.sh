#!/usr/bin/env bash
set -euo pipefail

: "${DRY_RUN:=1}"
: "${APPLY:=0}"

if [[ "${APPLY}" != "1" ]]; then
  echo "DRY_RUN=${DRY_RUN}: would configure HTB slice shaping."
  exit 0
fi

echo "Applying HTB slice shaping on the current host."
