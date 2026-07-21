# Prototype Evidence Schemas

This directory contains aggregate evidence schemas for the Stage 2 prototype
spine.

Planned schemas:

- `identity_session.schema.json`;
- `slice_performance.schema.json`;
- `edge_resource.schema.json`;
- `accounting_consistency.schema.json`.

These schemas describe experiment-level evidence records. They do not replace
the existing raw telemetry parser models in `src/scb/telemetry/`.

## Common fields

Every Stage 2 aggregate evidence record must include:

- `run_id`;
- `scenario_id`;
- `evidence_class`;
- `timestamp`;
- `source`.

Evidence classes:

- `M` measured;
- `E` emulated;
- `S` simulated;
- `C` contextual.

## Stage boundary

Stage 2.1 defines the schema plan only.

The JSON Schema files are added in Stage 2.2.
