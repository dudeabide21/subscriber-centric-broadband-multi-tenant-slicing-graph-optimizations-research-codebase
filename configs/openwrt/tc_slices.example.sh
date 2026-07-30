#!/usr/bin/env bash
set -euo pipefail

# Stage 2 traffic-shaping intent.
#
# Default execution is non-mutating. Live execution requires both:
#
#   DRY_RUN=0
#   CONFIRM_LIVE_TC=APPLY_STAGE2_TC
#
# The interface and rates must be reviewed before live use.

: "${DRY_RUN:=1}"
: "${AP_INTERFACE:=<AP_INTERFACE>}"

: "${ROOT_RATE:=1000mbit}"
: "${ROOT_CEIL:=1000mbit}"

: "${BASIC_RATE:=20mbit}"
: "${BASIC_CEIL:=25mbit}"

: "${PRIORITY_RATE:=40mbit}"
: "${PRIORITY_CEIL:=50mbit}"

: "${GUEST_RATE:=5mbit}"
: "${GUEST_CEIL:=5mbit}"

print_command() {
    printf ' '
    printf '%q ' "$@"
    printf '\n'
}

run_tc() {
    if [[ "$DRY_RUN" == "1" ]]; then
        printf 'DRY-RUN:'
        print_command "$@"
        return 0
    fi

    if [[ "${CONFIRM_LIVE_TC:-}" != "APPLY_STAGE2_TC" ]]; then
        echo "ERROR: live tc execution requires:" >&2
        echo "  CONFIRM_LIVE_TC=APPLY_STAGE2_TC" >&2
        exit 2
    fi

    if [[ "$EUID" -ne 0 ]]; then
        echo "ERROR: live tc execution requires root." >&2
        exit 2
    fi

    if [[ "$AP_INTERFACE" == "<AP_INTERFACE>" ]]; then
        echo "ERROR: replace <AP_INTERFACE> before live execution." >&2
        exit 2
    fi

    "$@"
}

if [[ "$AP_INTERFACE" == "<AP_INTERFACE>" ]]; then
    echo "NOTICE: using unresolved <AP_INTERFACE> in dry-run output." >&2
fi

# Root HTB hierarchy.
run_tc tc qdisc replace \
    dev "$AP_INTERFACE" \
    root handle 1: \
    htb default 30

run_tc tc class replace \
    dev "$AP_INTERFACE" \
    parent 1: \
    classid 1:1 \
    htb rate "$ROOT_RATE" \
    ceil "$ROOT_CEIL"

# Basic subscriber slice.
run_tc tc class replace \
    dev "$AP_INTERFACE" \
    parent 1:1 \
    classid 1:10 \
    htb rate "$BASIC_RATE" \
    ceil "$BASIC_CEIL" \
    prio 2

run_tc tc qdisc replace \
    dev "$AP_INTERFACE" \
    parent 1:10 \
    handle 110: \
    fq_codel

# Priority subscriber slice.
run_tc tc class replace \
    dev "$AP_INTERFACE" \
    parent 1:1 \
    classid 1:20 \
    htb rate "$PRIORITY_RATE" \
    ceil "$PRIORITY_CEIL" \
    prio 1

run_tc tc qdisc replace \
    dev "$AP_INTERFACE" \
    parent 1:20 \
    handle 120: \
    fq_codel

# Guest/degraded slice.
run_tc tc class replace \
    dev "$AP_INTERFACE" \
    parent 1:1 \
    classid 1:30 \
    htb rate "$GUEST_RATE" \
    ceil "$GUEST_CEIL" \
    prio 3

run_tc tc qdisc replace \
    dev "$AP_INTERFACE" \
    parent 1:30 \
    handle 130: \
    fq_codel

echo
echo "Stage 2 shaping intent:"
echo "  slice-basic    -> class 1:10 -> ${BASIC_RATE}/${BASIC_CEIL}"
echo "  slice-priority -> class 1:20 -> ${PRIORITY_RATE}/${PRIORITY_CEIL}"
echo "  slice-guest    -> class 1:30 -> ${GUEST_RATE}/${GUEST_CEIL}"
echo
echo "Packet classification is intentionally not installed by this template."
echo "Classification and rollback must be reviewed in the controlled live lab."
