# Stage 2 Acceptance Criteria

## Purpose

These criteria define the minimum evidence-producing prototype spine and the
claims Stage 2 may make.

## Accepted-subscriber path

Stage 2 must represent at least one valid subscriber path containing:

1. pseudonymous subscriber identity;
2. authentication request;
3. `accept` result;
4. policy result;
5. slice identifier;
6. traffic-shaping intent;
7. session identifier;
8. accounting identifier;
9. accounting evidence record.

## Rejected-subscriber path

Stage 2 must represent at least one invalid subscriber path containing:

1. pseudonymous subscriber identity;
2. authentication request;
3. `reject` or `error` result;
4. failure reason;
5. no successful subscriber slice;
6. no installed subscriber shaping class;
7. no successful accounting-start identity.

## Policy-to-slice mapping

An accepted subscriber must have a deterministic represented mapping to:

- slice ID;
- optional VLAN ID;
- optional VNI;
- configured rate limit;
- accounting ID.

The initial mapping may be scaffolded but must be explicit.

## Traffic-shaping intent

Stage 2 must represent:

- HTB or equivalent class hierarchy;
- per-slice rate or ceiling;
- fq_codel or equivalent leaf queue;
- safe dry-run behavior before live use.

Represented shaping intent is not equivalent to measured enforcement.

## Accounting evidence

Stage 2 must include:

- RADIUS byte counters;
- gateway byte counters;
- calculated mismatch;
- tolerance status;
- termination cause;
- offline-signature presence.

## Edge-resource evidence

Stage 2 must include:

- AP ID;
- CPU ratio;
- RAM ratio;
- IRQ rate;
- cryptographic throughput;
- tunnel overhead ratio;
- queueing overhead ratio;
- telemetry interval.

## Evidence classification

Each aggregate record must use:

- `M` measured;
- `E` emulated;
- `S` simulated;
- `C` contextual.

The initial sample run must use `E`.

## Documentation acceptance

Stage 2 must document:

- prototype topology;
- node roles;
- Linux-only and OpenWrt modes;
- trust boundaries;
- evidence sources;
- schemas;
- fixture limitations;
- live-lab transition;
- rollback;
- secret handling.

## Code and test acceptance

Stage 2 is accepted only when:

- all Stage 2 targeted tests pass;
- the full repository test suite passes;
- Stage 1 tests remain green;
- records load deterministically;
- malformed records fail explicitly;
- the report regenerates from fixtures;
- `git diff --check main..HEAD` is clean;
- the working branch is not `main`;
- no secrets are committed.

## Claim restrictions

Stage 2 must not claim:

- cross-slice isolation before negative packet tests;
- production readiness;
- live ISP federation;
- national deployment validation;
- statistically significant improvement;
- optimization improvement;
- GNN or PPO validation;
- live LEO validation.

## Permitted completion statement

> The repository contains a reproducible prototype evidence scaffold that
> traces accepted and rejected subscriber identities through authentication,
> policy mapping, slice and shaping intent, accounting consistency, and
> edge-resource records. The initial run is emulated and does not constitute
> production or cross-slice-isolation validation.