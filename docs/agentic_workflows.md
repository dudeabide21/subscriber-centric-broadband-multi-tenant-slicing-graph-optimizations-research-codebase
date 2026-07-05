# Agentic workflows

## Workflow A: Add a parser
1. Define input log format.
2. Add or update the Pydantic schema.
3. Implement the parser.
4. Add a unit test.
5. Add a synthetic sample log.
6. Add documentation.
7. Ensure parsed output includes `evidence_class` and metadata.

## Workflow B: Add a mathematical estimator
1. Write the formula in the docstring.
2. Define units and assumptions.
3. Implement a pure function.
4. Add normal-case tests.
5. Add edge-case tests.
6. Update `docs/mathematical_model.md`.

## Workflow C: Add an experiment
1. Create a config file.
2. Create a runner script.
3. Require `DRY_RUN=1` by default.
4. Define raw output path.
5. Define processed output path.
6. Write `metadata.json`.
7. Tag the evidence class.
8. Update `experiment_protocol.md`.

## Workflow D: Add GNN experiment
1. Define graph schema.
2. Normalize edge features by scenario class.
3. Split by scenario class.
4. Train baseline.
5. Compare against a non-learning baseline.
6. Save metrics and checkpoint.
7. Do not claim field validity from simulation-only results.

## Workflow E: Add Rust edge-agent feature
1. Implement deterministic logic only.
2. Do not put ML inference in Rust initially.
3. Add unit tests.
4. Add CLI flag.
5. Add dry-run mode.
6. Never apply tc or network changes without `APPLY=1`.
