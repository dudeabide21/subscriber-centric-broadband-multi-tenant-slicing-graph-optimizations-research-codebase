# Stage 3 telemetry parser and accounting contract

Status: implemented locally
Research evidence produced by this stage: `Synthetic` only
Live-lab execution: not performed
Dockerization: deferred to the Fedora server

## 1. Purpose and boundary

Stage 3 turns the existing raw telemetry parsers into a fail-loud,
provenance-bearing ingestion boundary. It does not claim that the synthetic
fixtures are measurements, and it does not implement the later control,
queueing, GNN, PPO, Mininet, ns-3, or LEO work.

The implementation follows the draft theoretical framework by preserving the
identity-session, slice-performance, edge-resource, and accounting-consistency
dimensions needed by the downstream matrices. Every record retains an explicit
evidence class so measured, emulated, simulated, contextual, and synthetic
claims cannot be silently merged.

Stage 2.7 is the operational prerequisite for later `Measured` ingestion. Its
checklist and command guide require inventory, backups, secret-safe execution,
raw collection, hashing, stop conditions, and rollback before live evidence can
enter this pipeline.

## 2. Implemented architecture

The existing parser modules remain the authoritative ingestion path:

1. `parse_radius_logs.py` parses authentication and accounting events.
2. `parse_tc_stats.py` parses Linux traffic-control class counters.
3. `parse_openwrt_metrics.py` parses access-point resource snapshots.
4. `parse_wireguard_stats.py` parses encrypted-tunnel peer counters.
5. `parser_common.py` supplies shared strict token, numeric, timestamp, source,
   UTF-8, empty-source, and SHA-256 checks.
6. `accounting_reconcile.py` computes transparent directional and total byte
   mismatches.
7. `sample_processing.py` dispatches the parsers and emits deterministic
   CSV/JSON outputs plus a source-hash manifest.

No parallel Stage 3 parser hierarchy was introduced. This avoids two competing
implementations for the same telemetry event.

## 3. Global parser invariants

All parsers:

- read regular files as strict UTF-8;
- reject sources outside the declared repository root;
- ignore only blank lines and lines whose first non-space character is `#`;
- reject malformed, unknown, duplicate, missing, or empty key/value fields;
- reject a source containing no data records;
- require timezone-aware ISO-8601 event and parse timestamps;
- reject negative counters, non-finite numeric values, and impossible ranges;
- preserve the exact repository-relative source path, parser version, parse
  time, source type, and evidence class;
- never clamp, infer, repair, or silently default missing telemetry.

Pydantic assignment validation is enabled so a valid record cannot later be
mutated into an invalid state without raising a validation error.

## 4. Source-specific contracts

### 4.1 RADIUS authentication

Required event token: `AUTH`

Required fields:

- `subscriber_id_hash`
- `ap_id`
- `result` or canonical `auth_result`
- `latency_ms` or canonical `auth_latency_ms`

Allowed results are `ACCEPT`, `REJECT`, and `ERROR`. Authentication latency must
be finite and non-negative.

### 4.2 RADIUS accounting

Required event token: `ACCT`

Required fields:

- `subscriber_id_hash`
- `ap_id`
- `session_id` or canonical `accounting_session_id`
- `input_octets`
- `output_octets`

Both octet counters must be non-negative integers.

### 4.3 Linux traffic control

The synthetic `tc` grammar is matched in full. The parser additionally requires:

- a non-empty interface label;
- unique class IDs within a source;
- positive `rate_mbit` and `ceil_mbit`;
- `rate_mbit <= ceil_mbit`;
- non-negative byte, packet, drop, backlog, and requeue counters.

### 4.4 OpenWrt resources

Every snapshot requires `ap_id`, CPU percentage, used and total RAM, interrupt
rate, and load average. CPU is bounded to 0–100 percent. Total RAM must be
positive, used RAM cannot exceed total RAM, and all rate/load metrics must be
finite and non-negative.

### 4.5 WireGuard

Every peer snapshot requires an interface, hashed peer identifier, receive and
transmit byte counters, and a timezone-aware latest-handshake timestamp. Byte
counters must be non-negative integers.

## 5. Accounting consistency

For one matched session, Stage 3 computes:

```text
input_mismatch  = abs(radius_bytes_in  - gateway_bytes_in)
output_mismatch = abs(radius_bytes_out - gateway_bytes_out)
byte_mismatch   = input_mismatch + output_mismatch
within_tolerance = byte_mismatch <= predeclared_tolerance_bytes
```

The tolerance defaults to zero and must itself be a non-negative integer.
Directional counters and mismatches are retained. No normalization or
counter-direction swapping occurs inside the reconciliation function.

## 6. Determinism and provenance

One timezone-aware `parsed_at` value is injected into all records and the
summary for a run. Supplying `--parsed-at` makes repeated processing
byte-identical for unchanged inputs.

The summary contains a SHA-256 digest of the exact bytes of every raw source.
CSV, JSON, and summary files are written through same-directory temporary files
and atomically replaced. Processed outputs remain regenerable artifacts; the
raw source and its hash are the audit anchors.

Example deterministic run:

```bash
source .venv-wsl/bin/activate
python -m scb.telemetry.sample_processing \
  --samples-dir data/samples \
  --output-dir data/processed/stage_3_check \
  --parsed-at 2026-07-30T12:00:00Z
```

This command processes the repository’s synthetic fixtures. It must not be
described as a live measurement run.

## 7. Verification sequence

Run from WSL Ubuntu with `.venv-wsl`:

1. Execute the Stage 2.7 documentation contract tests.
2. Execute parser utility and accounting unit tests.
3. Execute each source parser’s positive and negative tests.
4. Execute the Stage 3 adversarial contract tests.
5. Process the same sources twice with the same `--parsed-at` value and compare
   every output byte.
6. Run scoped Ruff and Black checks for the changed files.
7. Run the full repository test suite.
8. Inspect `git diff --check`, the changed-file list, and secret-pattern scans.

Acceptance requires all scoped tests and the full suite to pass, no temporary
or rejected patch artifacts, no evidence-class relabeling, and no changes
outside Stage 2.7/Stage 3 scope.

## 8. Deferred work

- Execute the Stage 2.7 checklist on the authorized live lab before collecting
  any `Measured` evidence.
- Add adapters for the exact live FreeRADIUS, OpenWrt, `tc`, and WireGuard
  command formats only after representative raw captures exist.
- Perform Dockerization on the Fedora server, as requested.
- Begin post-Stage-3 control and experimentation stages only under their own
  acceptance criteria.
