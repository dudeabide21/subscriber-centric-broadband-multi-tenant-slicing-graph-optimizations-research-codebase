# Subscriber-Centric Broadband Research

Research workflow for **Safety-Constrained Subscriber-Centric Broadband Infrastructure for Emerging Economies: Edge-Aware Slicing, Two-Timescale Control, and Nepal as an Empirical Testbed**.

This repository is a research pipeline, not a product app. It is organized around safe sample parsing, explicit evidence classes, queueing/control analysis, and controlled experiment artifacts.

## What’s In Scope

- federated AAA and subscriber-centric policy enforcement
- OpenWrt-class edge telemetry and Linux traffic control
- queueing, effective-bandwidth, and overflow-risk analysis
- safe action filtering and CMDP-style control
- optional LEO backhaul resilience studies
- later-stage graph learning, ns-3, Mininet-WiFi, and Rust edge-agent work

## Repository Layout

- `configs/` contains example network and policy artifacts.
- `scripts/` contains safe setup, experiment, and utility scripts.
- `src/scb/` contains the Python research package.
- `tests/` contains parser and math unit tests.
- `data/samples/` contains synthetic sample logs only.
- `data/raw/`, `data/processed/`, `data/results/`, and `data/external/` stay local by default.
- `paper/latex/` is for manuscript work on the secondary machine.
- `rust/` is currently optional scaffold material for future edge-agent work.

## Language Choices

- Python: primary research and experimentation language.
- Bash/POSIX shell: setup, traffic-control, and OpenWrt workflows.
- Rust: future production-oriented safe edge agent only.
- C++: reserved for later ns-3 modules if needed.

## Quickstart

If you have `make` available:

```bash
make check-env
make test
make parse-samples
```

If you do not have `make`, run the underlying commands directly:

```bash
python -m pytest
python -m scb.telemetry.sample_processing
```

## Fedora-First Setup

```bash
sudo dnf install -y git make python3 python3-pip python3-virtualenv
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev,stats,notebooks]"
```

## Running Tests

```bash
make test
```

or:

```bash
python -m pytest
```

## Parsing Synthetic Logs

```bash
make parse-samples
```

or:

```bash
python -m scb.telemetry.sample_processing
```

Parsed outputs are written to `data/processed/` and can be safely deleted and regenerated.

## Evidence-Class Rules

- Use only synthetic logs in `data/samples/` unless a task explicitly says otherwise.
- Mark every parsed record with an evidence class.
- Allowed evidence classes: `Measured`, `Emulated`, `Simulated`, `Contextual`, `Synthetic`.
- Synthetic sample parsers must tag records as `Synthetic`.
- Do not commit raw logs, large outputs, or any field result that is not actually measured.

## Safety Rules

- Shell scripts in `scripts/openwrt/` and `configs/tc/` are safe by default.
- Scripts that would modify live networking must require `APPLY=1`.
- Scripts that support dry runs should honor `DRY_RUN=1`.
- Do not treat generated outputs as field measurements unless the data was actually measured.

## Workflow Summary

1. Collect synthetic or controlled telemetry.
2. Parse telemetry into typed records with provenance and evidence classes.
3. Estimate queueing, effective bandwidth, and overflow risk.
4. Filter actions through explicit safety predicates.
5. Score candidate policies and experiment tracks.
6. Extend toward graph learning, simulation, and optional Rust edge control later.

## Current Status

- telemetry schemas and sample parsers are implemented
- parser and math unit tests are in place
- safe-by-default shell scripting is enforced for network-affecting tasks
- Rust is still a skeleton/optional track rather than a compiled module

## Roadmap

1. Scaffold and environment setup.
2. Synthetic telemetry parsing and sample processing.
3. Queueing/control/LEO starter functions.
4. Graph and learning placeholders.
5. Simulation and later experimental tracks.

## Project Notes

- See `docs/architecture.md` for the high-level system layout.
- See `docs/experiment_protocol.md` for evidence-class and output rules.
- See `docs/mathematical_model.md` for the formulas used by the starter analysis code.
