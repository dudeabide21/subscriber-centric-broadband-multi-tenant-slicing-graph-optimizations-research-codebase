# Experiment protocol

## Principles
- Do not commit raw logs.
- Mark every record with an evidence class.
- Keep synthetic sample logs clearly labeled as synthetic.
- Record configuration, host, date, and parser version for every processed run.

## Track structure
- Track 1: OpenWrt and Linux tc prototype.
- Track 2: edge overhead and safety filtering.
- Track 3: emulation and controlled backhaul experiments.
- Track 4: simulation and estimator validation.

## Outputs
- Raw outputs stay local in `data/raw/`.
- Processed artifacts go to `data/processed/`.
- Final figures and tables go to `data/results/`.

## Minimum metadata
- source files used
- parser version
- parsed timestamp
- evidence class
- experiment track name
- dry-run / apply mode
