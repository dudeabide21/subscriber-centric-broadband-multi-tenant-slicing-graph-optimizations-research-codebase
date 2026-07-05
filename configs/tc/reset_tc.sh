#!/usr/bin/env bash
set -euo pipefail

: "${DRY_RUN:=1}"
: "${APPLY:=0}"

if [[ "${APPLY}" != "1" ]]; then
  echo "DRY_RUN=${DRY_RUN}: would reset tc configuration."
  exit 0
fi

echo "Resetting tc configuration on the current host."
