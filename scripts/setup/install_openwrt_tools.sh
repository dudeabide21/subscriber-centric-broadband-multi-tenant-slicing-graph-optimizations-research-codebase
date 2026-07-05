#!/usr/bin/env bash
set -euo pipefail

: "${DRY_RUN:=1}"
: "${APPLY:=0}"

if [[ "${DRY_RUN}" == "1" || "${APPLY}" != "1" ]]; then
  echo "DRY_RUN=${DRY_RUN}: would install OpenWrt helper tools."
  exit 0
fi

echo "Install OpenWrt tools manually as needed for your host environment."
