# Architecture

The repository is organized around a safe research workflow:

1. Collect telemetry from synthetic or controlled experiments.
2. Parse telemetry into typed records with explicit evidence classes.
3. Estimate queueing, effective bandwidth, and overflow risk.
4. Filter actions through explicit safety predicates.
5. Score candidate policies and experiment tracks.
6. Extend toward graph learning, simulation, and optional Rust edge control later.

The architecture is intentionally modular so the same schema can support:
- OpenWrt prototype experiments;
- Linux traffic-control measurements;
- LEO backhaul sensitivity analysis;
- graph telemetry and future GNN work;
- later production-oriented edge enforcement.
