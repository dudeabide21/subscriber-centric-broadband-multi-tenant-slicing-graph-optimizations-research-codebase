# Measurement schema

## Evidence and provenance contract

Every parsed record includes:

- `evidence_class`: `Measured`, `Emulated`, `Simulated`, `Contextual`, or
  `Synthetic`;
- `source_file`: repository-relative POSIX path;
- `source_type`: parser family;
- `parser_version`: semantic parser contract version;
- `parsed_at`: timezone-aware ISO-8601 run timestamp.

The synthetic sample driver always emits `Synthetic`. A live collector must
explicitly supply `Measured`; filenames or execution location never determine
the evidence class.

Every parse-run summary includes record/file counts, evidence-class counts, the
parser version, one `generated_at` timestamp, and a `source_sha256` mapping for
the exact raw source bytes.

## Source fields

### RADIUS authentication

`timestamp`, `event_type`, `subscriber_id_hash`, `ap_id`, `auth_result`, and
`auth_latency_ms`.

### RADIUS accounting

`timestamp`, `event_type`, `subscriber_id_hash`, `ap_id`,
`accounting_session_id`, `input_octets`, and `output_octets`.

### Linux traffic control

`interface`, `class_id`, `rate_mbit`, `ceil_mbit`, `sent_bytes`, `packets`,
`drops`, `backlog_bytes`, `backlog_packets`, and `requeues`.

### OpenWrt

`timestamp`, `ap_id`, `cpu_percent`, `ram_used_mb`, `ram_total_mb`, `irq_rate`,
and `load_avg`.

### WireGuard

`interface`, `peer_id_hash`, `transfer_rx_bytes`, `transfer_tx_bytes`, and
`latest_handshake`.

## Accounting reconciliation fields

The reconciliation result preserves `radius_bytes_in`, `radius_bytes_out`,
`gateway_bytes_in`, `gateway_bytes_out`, `input_mismatch`, `output_mismatch`,
`byte_mismatch`, `tolerance_bytes`, and `within_tolerance`.

See `docs/telemetry/stage_3_parser_contract.md` for validation, determinism,
formula, and acceptance details.
