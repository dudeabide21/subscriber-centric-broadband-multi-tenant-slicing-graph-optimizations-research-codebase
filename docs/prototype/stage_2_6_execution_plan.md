# Stage 2.6 Execution Plan — Deterministic Prototype Acceptance Report

Status: **next sub-stage; planning complete; implementation not started**

## 1. Purpose

Stage 2.6 converts the validated Stage 2.4 fixture run into a deterministic,
human-readable acceptance report.

The report closes the current prototype evidence path:

```text
subscriber identity
-> authentication outcome
-> policy/slice and shaping intent
-> accounting comparison
-> edge-resource snapshot
-> evidence-qualified report
```

This sub-stage reports existing aggregate evidence. It does not execute
FreeRADIUS, OpenWrt, `hostapd`, VLAN, `tc`, WireGuard, VXLAN, or Docker.

## 2. Authority and reconciliation decisions

The implementation must use the following precedence:

1. The local `prototype` branch is the source-code authority because it
   contains unpushed Stage 2 work.
2. `paper/latex/PDFs/draft_10.pdf` is the theoretical and claim-boundary
   authority.
3. The Stage 2.5 handover is the detailed continuation specification.
4. The initial Stage 2 master plan controls stage order and scope boundaries.
5. Historical test counts and archived payloads are records, not current
   implementation truth.

Resolved differences:

| Topic | Initial direction | Later direction | Single adopted direction |
|---|---|---|---|
| Summary script | Optional | Required | Required |
| Summary test | Conditional | Required | Required |
| Library renderer | Not specified | `render_prototype_summary()` | Required public API |
| Determinism | General dry run | Byte-for-byte regeneration gate | Byte-for-byte gate |
| Docker | Recommended for RADIUS validation | Optional Fedora-only validation track | Excluded from Stage 2.6 |
| Evidence wording | Prototype eventually measured | Current fixture explicitly emulated | Report only `E = Emulated` |
| Record identification | Not specified | Categorize without mutation | Unique field-signature categorization |
| Git publication | Expected final push | Do not push unless requested | No push in this sub-stage |

No archived implementation payload may overwrite a newer local file.

## 3. Inputs and invariants

Stage 2.6 must consume:

- `src/scb/prototype/evidence.py`;
- `data/samples/prototype_run_001/*.json`;
- the four schemas in `data/schemas/`;
- `docs/prototype/evidence_plan.md`;
- `docs/prototype/stage_2_acceptance_criteria.md`.

The Stage 2.5 boundary remains unchanged:

```python
load_prototype_run(run_dir: Path) -> PrototypeRun
```

`PrototypeRun.records` is treated as immutable input. Stage 2.6 must not:

- inject record-type fields;
- rewrite fixture records;
- infer record type from source filenames;
- relabel evidence;
- silently repair missing values;
- turn emulated evidence into measured evidence.

## 4. Files in scope

Create:

```text
src/scb/prototype/summary.py
scripts/prototype/summarize_run.py
reports/prototype_run_001.md
tests/test_prototype_summary.py
```

Update:

```text
src/scb/prototype/__init__.py
scripts/experiments/run_track1_prototype.sh
```

Do not modify Stage 1 mathematical modules, Stage 2 schemas, fixtures, or the
Stage 2.5 loader unless a reproducible defect is first demonstrated by a
failing test.

## 5. Pre-implementation gate

Run from the repository root:

```bash
git branch --show-current
git status --short
git log --oneline --decorate -n 15
```

Required state:

- branch is `prototype`;
- working tree contains no unexpected edits;
- Stage 2.5 loader and fixture commits are present.

The current Windows `.venv` is not a valid WSL environment. If
`.venv-wsl` is absent, create a separate WSL environment:

```bash
python3 -m venv .venv-wsl
. .venv-wsl/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Then run:

```bash
make check-env
make test
```

Record the actual test result. Do not use `364`, `445`, or `470` as the
current count unless the local command produces that count.

Stop Stage 2.6 if the pre-existing suite fails. Diagnose that failure
separately before adding summary code.

## 6. Step-by-step implementation

### Step 1 — Add deterministic record categorization

In `src/scb/prototype/summary.py`, classify each record by its unique
schema-specific marker:

| Record family | Marker |
|---|---|
| Identity session | `auth_result` |
| Slice performance | `slice_id` |
| Edge resource | `cpu_ratio` |
| Accounting consistency | `radius_bytes_in` |

For every record:

1. Determine which markers are present.
2. Require exactly one matching family.
3. Raise a deterministic `ValueError` for an unknown or ambiguous record.
4. Validate the fields needed to render that family.
5. Do not mutate the record.

Use content signatures rather than filenames because `PrototypeRun` does not
retain source paths and Stage 2.5 intentionally does not inject record types.

### Step 2 — Validate report-level relationships

Before rendering, require:

- at least one `accept` identity record;
- at least one `reject` or `error` identity record;
- at least one slice record;
- at least one accounting record;
- at least one edge-resource record;
- one scenario ID shared by all records in this Stage 2 fixture report;
- each slice subscriber to match an accepted subscriber;
- each accounting subscriber and session to match an accepted session;
- each rejected identity to have no matching slice or accounting record;
- the accepted identity's `visited_ap` to match a reported edge `ap_id`.

Sort repeated records by stable content keys such as subscriber ID, session
ID, AP ID, and timestamp. Do not depend on dictionary insertion order.

Do not invent an accounting-tolerance formula. Display:

- the four raw counters;
- the fixture-provided `byte_mismatch`;
- the fixture-provided `within_tolerance` result.

Any future tolerance calculation requires an explicit threshold in the
evidence model and is outside Stage 2.6.

### Step 3 — Implement the renderer

Required API:

```python
def render_prototype_summary(run: PrototypeRun) -> str:
    ...
```

The function must:

- return Markdown as `str`;
- end the document with exactly one newline;
- use stable heading and table order;
- use deterministic value formatting;
- represent `None` as `not configured` or `not applicable`;
- display evidence enum values as `Measured`, `Emulated`, `Simulated`, or
  `Contextual`;
- avoid current time, random values, hostnames, and absolute paths.

Export `render_prototype_summary` from `scb.prototype`.

Required report sections, in order:

1. `# Prototype Acceptance Report — prototype_run_001`
2. `## Acceptance statement`
3. `## Run identity and provenance`
4. `## Accepted subscriber path`
5. `## Rejected subscriber path`
6. `## Slice and shaping representation`
7. `## Accounting consistency`
8. `## Edge-resource snapshot`
9. `## Limitations`
10. `## Next live-lab steps`

The accepted path must trace subscriber, realm, EAP method, authentication
result, session, accounting identity, slice, VLAN, VNI, rate limit, and
accounting record.

The rejected path must show the failure reason and absence of session,
accounting, slice, and shaping installation.

### Step 4 — Enforce claim boundaries

The report must say all of the following:

- the run is an emulated scaffold;
- it is not measured evidence;
- it does not validate FreeRADIUS execution;
- it does not validate OpenWrt behavior;
- it does not validate dynamic VLAN enforcement;
- it does not validate traffic-shaping enforcement;
- it does not validate cross-slice isolation;
- it does not validate Wi-Fi airtime;
- it does not prove AP CPU, RAM, or IRQ feasibility;
- it is not production-ready.

Values may be described as represented, recorded, configured, or
fixture-declared. They must not be described as experimentally proven,
operationally enforced, or measured.

### Step 5 — Add the CLI

Implement `scripts/prototype/summarize_run.py` using the repository's
existing `argparse` convention.

Required arguments:

```text
--run-dir PATH
--output PATH
```

Execution flow:

1. Parse arguments.
2. Call `load_prototype_run()`.
3. Call `render_prototype_summary()`.
4. write UTF-8 text with LF line endings;
5. return zero on success;
6. report a concise error and return nonzero on invalid input.

Canonical command:

```bash
PYTHONPATH=src python3 scripts/prototype/summarize_run.py \
  --run-dir data/samples/prototype_run_001 \
  --output reports/prototype_run_001.md
```

### Step 6 — Integrate the Track 1 runner

Replace the current placeholder behavior in
`scripts/experiments/run_track1_prototype.sh` with the canonical report
generation command.

Retain dry-run-only safety:

- accept only `DRY_RUN=1`;
- reject a live/apply request;
- perform no network, service, firewall, interface, or package mutation;
- generate only the local Markdown report.

This decision removes the optional runner branch and gives Track 1 one
documented entry point.

### Step 7 — Generate the committed report

Run the CLI once against `prototype_run_001` and commit the resulting:

```text
reports/prototype_run_001.md
```

The report is a reproducible generated artifact. Manual edits to it are not
authoritative; changes must originate in the renderer or fixtures.

### Step 8 — Add tests

`tests/test_prototype_summary.py` must cover:

1. the fixture run renders successfully;
2. the output contains every required section;
3. `E` is rendered as `Emulated`;
4. the accepted subscriber path is linked across identity, slice, and
   accounting records;
5. the rejected path has no service or accounting success;
6. all mandatory limitations are present;
7. record input order does not change output;
8. input records are unchanged after rendering;
9. an unknown signature fails;
10. an ambiguous signature fails;
11. missing report-required fields fail;
12. inconsistent scenario IDs fail;
13. broken subscriber/session/AP relationships fail;
14. CLI output equals library output;
15. committed report bytes equal freshly rendered bytes;
16. output contains no current timestamp or repository-local absolute path.

Tests should use temporary directories for generated files and must not
rewrite the committed report during routine test execution.

## 7. Verification sequence

Run checks in this order:

```bash
PYTHONPATH=src python3 -m pytest -q tests/test_prototype_summary.py
```

```bash
PYTHONPATH=src python3 -m pytest -q \
  tests/test_stage2_schemas.py \
  tests/test_stage2_config_templates.py \
  tests/test_stage2_sample_fixtures.py \
  tests/test_prototype_evidence.py \
  tests/test_prototype_summary.py
```

```bash
PYTHONPATH=src python3 scripts/prototype/summarize_run.py \
  --run-dir data/samples/prototype_run_001 \
  --output /tmp/prototype_run_001.md

diff -u reports/prototype_run_001.md /tmp/prototype_run_001.md
```

Expected result: `diff` produces no output.

Then run:

```bash
make lint
make test
git diff --check
git status --short
```

Inspect the final Stage 2.6 diff:

```bash
git diff -- \
  src/scb/prototype/summary.py \
  src/scb/prototype/__init__.py \
  scripts/prototype/summarize_run.py \
  scripts/experiments/run_track1_prototype.sh \
  reports/prototype_run_001.md \
  tests/test_prototype_summary.py
```

## 8. Acceptance gate

Stage 2.6 is complete only when:

- the public renderer exists;
- the CLI regenerates the report from the fixture directory;
- the Track 1 runner invokes the same path safely;
- the report contains accepted and rejected subscriber traces;
- provenance and evidence class are explicit;
- all mandatory limitations are present;
- two generations are byte-identical;
- targeted and full tests pass;
- lint and whitespace checks pass;
- Stage 1 tests remain green;
- no secret or machine-specific path is introduced;
- no Docker or live network operation is required.

Permitted completion statement:

> The repository contains a deterministic acceptance report generated from
> the Stage 2 emulated prototype evidence scaffold. It traces accepted and
> rejected subscriber paths through represented policy, slice, shaping,
> accounting, and edge-resource records. It does not constitute measured,
> isolation, hardware-feasibility, or production validation.

## 9. Commit boundary

Use one focused commit after every gate passes:

```text
Add deterministic prototype acceptance report
```

Do not push the branch or open a pull request unless explicitly requested.

## 10. Scope exclusions and handoff

Do not add:

- Docker or Compose files;
- FreeRADIUS container validation;
- live OpenWrt commands;
- router flashing or firewall mutation;
- telemetry collectors or raw-log parsers;
- negative packet-isolation experiments;
- NS-3, Mininet-WiFi, GNN, PPO, or live LEO work;
- production credentials.

After this gate, proceed to Stage 2.7:

```text
docs/prototype/live_lab_checklist.md
docs/prototype/measurement_commands.md
```

Stage 2.7 prepares safe live-lab execution and rollback documentation. It
does not retroactively convert `prototype_run_001` into measured evidence.
