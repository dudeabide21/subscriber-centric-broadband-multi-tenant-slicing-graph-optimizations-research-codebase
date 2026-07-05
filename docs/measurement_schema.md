# Measurement schema

All parsed records should include:
- `evidence_class`
- `source_file`
- `parser_version`
- `parsed_at`

Recommended fields by source:
- RADIUS: timestamp, subscriber hash, AP id, auth result, latency, session id, octets.
- tc: interface, class id, bytes, packets, drops, backlog, rate estimate.
- OpenWrt: timestamp, AP id, CPU, RAM, IRQ, load average.
- WireGuard: interface, peer hash, transfer bytes, latest handshake.
