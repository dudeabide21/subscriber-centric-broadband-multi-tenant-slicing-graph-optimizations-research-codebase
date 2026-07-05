#!/usr/bin/env bash
set -euo pipefail

: "${DRY_RUN:=1}"
: "${APPLY:=0}"

if [[ "${DRY_RUN}" == "1" || "${APPLY}" != "1" ]]; then
  echo "DRY_RUN=${DRY_RUN}: would collect OpenWrt metrics."
  exit 0
fi

echo "Collecting OpenWrt metrics from the target device."
