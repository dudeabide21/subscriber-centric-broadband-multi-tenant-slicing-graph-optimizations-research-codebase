#!/usr/bin/env bash
set -euo pipefail

: "${DRY_RUN:=1}"
: "${APPLY:=0}"

commands=(
  "sudo dnf update -y"
  "sudo dnf groupinstall -y \"Development Tools\""
  "sudo dnf install -y git make cmake gcc gcc-c++ python3 python3-pip python3-virtualenv python3-devel iproute iperf3 tcpdump wireshark-cli freeradius freeradius-utils hostapd wireguard-tools bridge-utils jq curl wget podman podman-compose rust cargo openssl-devel pkg-config"
)

for cmd in "${commands[@]}"; do
  if [[ "${DRY_RUN}" == "1" || "${APPLY}" != "1" ]]; then
    echo "$cmd"
  else
    eval "$cmd"
  fi
done
