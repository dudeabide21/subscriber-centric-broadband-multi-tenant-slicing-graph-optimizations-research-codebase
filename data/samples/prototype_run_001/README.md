# Prototype Run 001 

## Purpose

 This directory contains the deterministic Stage 2.4 aggregate evidence fixtures for one prototype subscriber-policy scenario.
 
The fixtures demonstrate the intended evidence relationships: 

`identity decision -> slice assignment -> service representation -> edge-resource representation -> accounting comparison` 

## Evidence classification

Evidence class: `E` 

`E` means emulated.

This run is an emulated scaffold and not measured evidence. The values are source-controlled examples selected to exercise the Stage 2 evidence schemas and the later prototype evidence loader. 

## Scenario Run ID: `prototype_run_001` 
Scenario ID: `single-subscriber-policy-path` The scenario contains: - one accepted pseudonymous subscriber; - one explicitly rejected pseudonymous subscriber; - one basic subscriber slice; - one AP resource snapshot; - one accounting-consistency record for the accepted session. ## Accepted path The accepted subscriber is: `subscriber-demo-001` The accepted path assigns: - session ID `stage2-session-001`; - accounting ID `acct-prototype-basic-001`; - slice `slice-basic`; - VLAN `110`; - rate-limit representation `20 Mbps`. ## Rejected path The rejected subscriber is: `subscriber-demo-invalid` The rejected record contains: - authentication result `reject`; - failure reason `invalid-subscriber`; - null session ID; - null accounting ID. The rejected subscriber has no slice-performance record and no accounting-consistency record. ## Record relationships | Record | Entity | Relationship | |---|---|---| | `identity_session_accept.json` | accepted subscriber | creates the session identity used by service and accounting records | | `identity_session_reject.json` | rejected subscriber | terminates without session, slice, or accounting evidence | | `slice_performance.json` | accepted subscriber | represents the basic slice and VLAN policy path | | `edge_resource.json` | AP | represents a run-level edge-resource snapshot | | `accounting_consistency.json` | accepted session | compares RADIUS and gateway byte counters | ## Validation boundaries This fixture set does not validate FreeRADIUS execution. It does not validate OpenWrt behavior. It does not validate dynamic VLAN enforcement. It does not validate traffic-shaping enforcement. It does not validate cross-slice isolation. It does not validate Wi-Fi airtime, AP CPU feasibility, IRQ pressure, or production security. Docker is not required for Stage 2.4. Optional Docker validation will be performed separately on the Fedora Server environment. ## Provenance All records use: `source = stage2-emulated-fixture` No live subscriber identity, deployment credential, or production secret is included.