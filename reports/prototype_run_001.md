# Prototype Acceptance Report — prototype_run_001

## Acceptance statement

The repository contains a deterministic acceptance report generated
from the Stage 2 emulated prototype evidence scaffold. It traces
accepted and rejected subscriber paths through represented policy,
slice, shaping, accounting, and edge-resource records. It does not
constitute measured, isolation, hardware-feasibility, or production
validation.

## Run identity and provenance

| Field | Value |
| --- | --- |
| Run ID | prototype_run_001 |
| Scenario ID | single-subscriber-policy-path |
| Evidence class | Emulated |
| Source | stage2-emulated-fixture |
| Record count | 5 |
| First fixture timestamp | 2026-07-27T00:00:00Z |
| Last fixture timestamp | 2026-07-27T00:02:00Z |

All values below are fixture-represented. The timestamps are
evidence timestamps, not report-generation timestamps.

## Accepted subscriber path

| Subscriber | Realm | EAP method | Auth | Session | Accounting ID | Slice | VLAN | VNI | Rate limit | Visited AP |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| subscriber-demo-001 | prototype.test | EAP-TTLS/PAP | accept | stage2-session-001 | acct-prototype-basic-001 | slice-basic | 110 | not configured | 20 Mbps | ap-lab-001 |

The accepted path has matching slice and accounting records.
This represents the intended control path; it does not prove
that the configuration was installed or enforced.

## Rejected subscriber path

| Subscriber | Auth | Failure reason | Session | Accounting ID | Slice installed | Accounting started |
| --- | --- | --- | --- | --- | --- | --- |
| subscriber-demo-invalid | reject | invalid-subscriber | not applicable | not applicable | no | no |

Rejected identities have no matching slice or accounting record.

## Slice and shaping representation

The rate and performance values are emulated aggregate evidence.
They represent shaping intent and do not validate enforcement.

| Subscriber | Slice | VLAN | VNI | Rate limit | Throughput | Latency | Jitter | Loss | Queue occupancy | SLA |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| subscriber-demo-001 | slice-basic | 110 | not configured | 20 Mbps | 18.6 Mbps | 24.5 ms | 2.8 ms | 0.10% | 22.00% | pass |

## Accounting consistency

The mismatch and tolerance status are fixture-provided values.
No unrecorded tolerance threshold is inferred.

| Subscriber | Session | RADIUS in | RADIUS out | Gateway in | Gateway out | Byte mismatch | Within tolerance | Termination | Offline signature |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| subscriber-demo-001 | stage2-session-001 | 2500000 | 4500000 | 2500000 | 4500000 | 0 | yes | User-Request | no |

## Edge-resource snapshot

These values are emulated observations. They do not establish
physical access-point feasibility.

| AP | CPU | RAM | IRQ rate | Crypto throughput | Tunnel overhead | Queueing overhead | Telemetry interval |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ap-lab-001 | 32.00% | 45.00% | 940 | 72 Mbps | 4.00% | 8.00% | 5 s |

## Limitations

- This run is an emulated scaffold.
- It is not measured evidence.
- It does not validate FreeRADIUS execution.
- It does not validate OpenWrt behavior.
- It does not validate dynamic VLAN enforcement.
- It does not validate traffic-shaping enforcement.
- It does not validate cross-slice isolation.
- It does not validate Wi-Fi airtime.
- It does not prove AP CPU, RAM, or IRQ feasibility.
- It is not production-ready.

## Next live-lab steps

1. Complete the Stage 2.7 live-lab checklist and command guide.
2. Back up the lab configuration and identify every interface.
3. Execute authentication, shaping, accounting, and resource
   collection procedures only in the approved lab environment.
4. Preserve raw logs and normalize them into a new run directory;
   do not overwrite `prototype_run_001`.
5. Assign `M = Measured` only to observations produced by an
   identifiable live collection procedure.
6. Regenerate this report for the new run and retain the same
   evidence and claim boundaries.
