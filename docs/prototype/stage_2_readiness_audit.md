# Stage 2 Readiness Audit

## Baseline

- Working branch: `prototype`
- Baseline branch: `main`
- Stage 1 is complete, merged, and preserved.
- Verified full-suite baseline before Stage 2: `405 passed`.

## Confirmed Stage 1 modules

- `src/scb/common/weights.py`
- `src/scb/common/parameters.py`
- `src/scb/queueing/effective_service.py`
- `src/scb/control/cost.py`
- `src/scb/control/fallback.py`
- `src/scb/telemetry/throttle.py`
- `src/scb/leo/cost.py`
- `src/scb/leo/backoff.py`

Stage 2 must not redesign or duplicate these modules.

## Existing prototype structure to reuse

- `configs/freeradius/`
- `configs/openwrt/`
- `configs/tc/`
- `configs/vxlan/`
- `configs/wireguard/`
- `scripts/experiments/run_track1_prototype.sh`
- `docs/measurement_schema.md`
- `src/scb/telemetry/`

## Stage 2.0 boundaries

Stage 2.0 introduces no GNN, PPO, NS-3, Mininet-WiFi, live LEO
experiments, router flashing, ISP federation, certificate automation,
or production deployment automation.

## Acceptance

Stage 2.0 is accepted because:

1. The branch is `prototype`.
2. The working tree was clean before this note.
3. The full Stage 1 suite passed.
4. Required Stage 1 modules exist.
5. Existing prototype conventions were identified for reuse.
6. No later-stage scope was introduced.

Stage 2.1 may now begin with topology and evidence planning only.
