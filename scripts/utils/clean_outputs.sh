#!/usr/bin/env bash
set -euo pipefail

: "${DRY_RUN:=1}"

if [[ "${DRY_RUN}" == "1" ]]; then
  echo "DRY_RUN=${DRY_RUN}: would remove data/processed/* and data/results/*"
  exit 0
fi

rm -f data/processed/* data/results/*
echo "Cleaned processed and results outputs."
