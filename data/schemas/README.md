# Prototype Evidence Schemas

This directory contains aggregate evidence schemas for the Stage 2 prototype
spine.

Available schemas:

- `identity_session.schema.json`;
- `slice_performance.schema.json`;
- `edge_resource.schema.json`;
- `accounting_consistency.schema.json`.

These schemas describe experiment-level evidence records. They do not replace
the raw telemetry models and parsers under `src/scb/telemetry/`.

## Common fields

Every Stage 2 aggregate evidence record requires:

- `run_id`;
- `scenario_id`;
- `evidence_class`;
- `timestamp`;
- `source`.

Evidence classes:

- `M` — measured;
- `E` — emulated;
- `S` — simulated;
- `C` — contextual.

## Strictness

Each schema:

- uses JSON Schema Draft 2020-12;
- requires its common and record-specific fields;
- rejects undeclared top-level properties;
- uses explicit enums where applicable;
- constrains ratios to valid ranges;
- does not repair, normalize, clamp, or impute evidence values.

## Evidence boundary

These schemas define aggregate experiment evidence.

Existing source-level telemetry parsing remains under:

`src/scb/telemetry/`

The initial Stage 2 sample fixtures will be added separately in Stage 2.4 and
must use evidence class `E`.