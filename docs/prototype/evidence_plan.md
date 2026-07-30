# Stage 2 Prototype Evidence Plan

## Objective

The evidence plan defines the minimum records needed to trace:

`subscriber -> authentication -> policy/slice -> shaping
-> accounting -> edge state`

It separates evidence provenance from research claims.

## Evidence-class labels

Every aggregate Stage 2 record must contain one of:

- `M` — measured;
- `E` — emulated;
- `S` — simulated;
- `C` — contextual.

### Measured evidence

`M` is reserved for data observed during a controlled physical or software
lab execution with an identifiable source and collection procedure.

### Emulated evidence

`E` covers scaffolded or dry-run records, including sample authentication,
shaping, accounting, and resource fixtures.

### Simulated evidence

`S` is reserved for later simulation tracks. Stage 2 does not produce
simulation evidence.

### Contextual evidence

`C` covers deployment context or external observations. Contextual evidence
must not be represented as prototype measurement.

## Common record fields

Every aggregate evidence record must include:

- `run_id`;
- `scenario_id`;
- `evidence_class`;
- `timestamp`;
- `source`.

Where applicable, records also include:

- `subscriber_id`;
- `ap_id`;
- `result`.

## Run and scenario identity

Example run ID:

`prototype_run_001`

Example scenario IDs:

- `valid-subscriber-basic-slice`;
- `invalid-subscriber-rejection`;
- `accepted-session-accounting-check`.

## Identity-session evidence

### Purpose

Associate subscriber identity with authentication outcome and, for accepted
sessions, session and accounting identities.

### Minimum information

- pseudonymous subscriber ID;
- realm;
- visited AP;
- home domain;
- EAP method;
- accept, reject, or error result;
- failure reason;
- authentication latency;
- session ID;
- accounting ID.

### Sources

- FreeRADIUS authentication logs;
- hostapd logs;
- RADIUS detail records;
- controlled scaffold fixtures.

### Accepted-path requirement

An accepted record must represent:

- successful authentication;
- non-empty session ID;
- non-empty accounting ID;
- a policy result suitable for slice mapping.

### Rejected-path requirement

A rejected record must represent:

- authentication or policy failure;
- a failure reason;
- no successful subscriber slice;
- no successful accounting-start identity.

## Slice-performance evidence

### Purpose

Associate an accepted subscriber and policy result with a represented or
applied traffic class.

### Minimum information

- subscriber ID;
- slice ID;
- VLAN ID where used;
- VNI where used;
- configured rate limit;
- throughput;
- latency;
- jitter;
- loss rate;
- queue occupancy;
- SLA status.

### Sources

- Linux `tc -s` output;
- controlled traffic-generator output;
- AP interface counters;
- scaffold fixtures.

### Claim boundary

A slice-performance record does not by itself prove cross-slice isolation.

## Edge-resource evidence

### Purpose

Record AP/gateway state for later edge-feasibility analysis.

### Minimum information

- AP ID;
- CPU ratio;
- RAM ratio;
- IRQ rate;
- cryptographic throughput;
- tunnel overhead ratio;
- queueing overhead ratio;
- telemetry interval.

### Sources

- OpenWrt system metrics;
- Linux host metrics;
- existing OpenWrt telemetry parsers;
- scaffold fixtures.

Stage 2 does not redefine Stage 1 feasibility limits.

## Accounting-consistency evidence

### Purpose

Compare subscriber-session byte counters from RADIUS accounting and the
gateway data plane.

### Minimum information

- subscriber ID;
- session ID;
- RADIUS bytes in;
- RADIUS bytes out;
- gateway bytes in;
- gateway bytes out;
- byte mismatch;
- tolerance result;
- termination cause;
- offline-signature presence.

### Sources

- FreeRADIUS accounting records;
- gateway interface counters;
- `tc` class counters;
- signed offline accounting records;
- scaffold fixtures.

Raw compared counters must be retained. Byte values must not be silently
repaired or normalized.

## Collection points

### RADIUS/controller node

Collect:

- authentication outcome;
- authentication latency;
- policy attributes;
- session and accounting IDs;
- accounting counters;
- termination cause.

### AP/gateway node

Collect:

- hostapd events;
- mapped VLAN or slice identifiers;
- `tc` class and qdisc counters;
- interface counters;
- CPU, RAM, IRQ, and load information;
- tunnel counters where used.

### Test client

Collect:

- scenario identifier;
- traffic-generator output;
- throughput, latency, jitter, and loss.

## Provenance requirements

Every record must identify:

- run;
- scenario;
- evidence class;
- timestamp;
- source.

Sample fixtures must use `E`.

A fixture must not be relabelled as measured merely by changing its evidence
class.

## Storage plan

Aggregate schemas:

`data/schemas/`

Sample run:

`data/samples/prototype_run_001/`

Dry-run report:

`reports/prototype_run_001.md`

Existing raw telemetry parsers remain under:

`src/scb/telemetry/`

The aggregate evidence layer does not replace the raw parser layer.

## Minimum Stage 2 evidence set

A complete initial run contains:

1. one accepted identity-session record;
2. one rejected identity-session record;
3. one slice-performance record for the accepted subscriber;
4. one edge-resource record;
5. one accounting-consistency record;
6. one report identifying the run as emulated scaffold evidence.

## Unsupported claims

Stage 2 evidence must not be presented as proof of:

- production readiness;
- real ISP federation;
- national-scale deployment;
- cross-slice isolation without negative packet tests;
- optimization gain;
- GNN or PPO effectiveness;
- live LEO performance.