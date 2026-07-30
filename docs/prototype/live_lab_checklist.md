# Stage 2.7 Live-Lab Readiness Checklist

Status: **readiness documentation only; no live execution authorized**

## Purpose and evidence boundary

This checklist prepares the Track 1 OpenWrt and FreeRADIUS lab without
changing a live system. It covers prerequisites, inventory, backups, evidence
capture, stop conditions, and rollback.

Completing this checklist does not produce measured evidence. A record may be
classified as `M = Measured` only after a controlled procedure has actually
run against identified lab equipment and retained its raw source evidence.

Do not overwrite `prototype_run_001`; use a new run identifier and directory.

Docker is not part of this path. Container validation remains deferred to the
separate Fedora-server activity.

## Lab roles and required placeholders

Record these values outside Git before using any command:

| Placeholder | Meaning |
|---|---|
| `<RUN_ID>` | New run identifier; never reuse `prototype_run_001` |
| `<CONTROLLER_HOST>` | FreeRADIUS/controller hostname or lab IP |
| `<AP_HOST>` | OpenWrt management hostname or lab IP |
| `<CLIENT_HOST>` | Controlled test-client hostname or lab IP |
| `<AP_INTERFACE>` | Subscriber-facing wireless or bridge interface |
| `<UPLINK_INTERFACE>` | AP/gateway upstream interface |
| `<TC_INTERFACE>` | Interface whose classes and qdiscs are inspected |
| `<RADIUS_CONFIG_DIR>` | Distribution-specific FreeRADIUS configuration root |
| `<RADIUS_LOG_DIR>` | Path discovered from the active FreeRADIUS configuration |
| `<LOCAL_EVIDENCE_DIR>` | Local, access-controlled raw-evidence directory |
| `<SECRET_FILE>` | Mode-`0600` local file outside the repository |

Use documentation-only addresses such as `192.0.2.0/24`, `198.51.100.0/24`,
and `203.0.113.0/24` in committed examples. Do not commit live addresses,
subscriber identities, shared secrets, certificates, packet captures, or raw
logs.

## Gate A — Workstation and branch

- [ ] Work in WSL Ubuntu or the designated Linux workstation.
- [ ] Activate `.venv-wsl` for repository validation.
- [ ] Confirm the Git branch is not `main`.
- [ ] Confirm the repository test suite passes.
- [ ] Confirm `prototype_run_001` remains classified as emulated evidence.
- [ ] Create a new external raw-evidence directory for `<RUN_ID>`.
- [ ] Ensure workstation, controller, AP, and client clocks use UTC and are
      synchronized.
- [ ] Record OS, kernel, firmware, FreeRADIUS, hostapd/wpad, iproute2,
      WireGuard, and iperf3 versions.

## Gate B — Package inventory

Do not install packages until the device role and rollback window are
approved.

### Controller or Linux gateway

Verify availability of:

- FreeRADIUS server and client utilities (`radclient` or equivalent);
- hostapd only where the Linux node is the authenticator;
- iproute2 (`ip`, `tc`);
- `iperf3`, `ping`, `tcpdump`, and `jq`;
- WireGuard tools if the scenario uses WireGuard;
- Python 3.12 and the repository `.venv-wsl` environment.

Distribution package names differ. The operator must verify names against the
active Ubuntu or Fedora release before installation.

### OpenWrt AP/gateway

Verify availability of:

- the device-appropriate full `wpad` variant with required 802.1X/RADIUS
  support;
- `ip`, `tc`, `iw`, `logread`, `ubus`, and `uci`;
- `iperf3`, `tcpdump`, and WireGuard tools only when required by the scenario.

OpenWrt `wpad` variants can conflict. Record the currently installed variant
and device release before selecting a replacement. Do not blindly install a
generic package list.

## Gate C — Read-only topology inventory

- [ ] Record controller, AP, client, management, subscriber-facing, and uplink
      interfaces.
- [ ] Record interface MAC addresses in the private run inventory.
- [ ] Record routes, bridges, VLAN devices, qdiscs, classes, and filters.
- [ ] Record active SSID/BSSID and radio channel without collecting unrelated
      subscriber identifiers.
- [ ] Record the active FreeRADIUS configuration and log roots.
- [ ] Record current firewall implementation and ruleset summary.
- [ ] Record WireGuard/VXLAN interfaces only if enabled for `<RUN_ID>`.
- [ ] Verify a separate management path remains available during AP changes.

The corresponding read-only commands are in
`docs/prototype/measurement_commands.md`.

## Gate D — Secret and privacy controls

- [ ] Store the RADIUS shared secret in `<SECRET_FILE>` outside Git with mode
      `0600`.
- [ ] Do not pass the shared secret as a command-line argument where process
      listings or shell history can expose it.
- [ ] Use pseudonymous subscriber identifiers.
- [ ] Limit packet capture to the controlled interfaces, hosts, ports, and
      duration required by the scenario.
- [ ] Do not capture subscriber payloads.
- [ ] Confirm raw evidence is excluded by `.gitignore` and separately access
      controlled.
- [ ] Define evidence retention and deletion dates before capture.

## Gate E — Backups before any mutation

- [ ] Export the active FreeRADIUS configuration tree and record its hash.
- [ ] Run the FreeRADIUS configuration check before and after any local edit.
- [ ] Create an OpenWrt `sysupgrade -b` configuration backup.
- [ ] Export `network`, `wireless`, `firewall`, `dhcp`, and `system` UCI
      configurations separately for inspection.
- [ ] Save the current traffic control (`tc`) qdisc, class, and filter state.
- [ ] Save the current route, address, bridge, and firewall state.
- [ ] Copy backups to the workstation and verify hashes before proceeding.
- [ ] Write the exact restoration commands in the private run log.

An OpenWrt backup is necessary but not sufficient: configuration compatibility
must be checked against the same device and firmware before restore.

## Gate F — Configuration review

- [ ] Copy repository examples to an external lab workspace; do not edit the
      examples in place.
- [ ] Replace every placeholder locally and verify no placeholder remains in
      the external candidate configuration.
- [ ] Confirm one accepted and one rejected pseudonymous subscriber path.
- [ ] Confirm a rejected subscriber receives no successful slice, shaping
      class, or accounting-start identity.
- [ ] Confirm accepted policy attributes map deterministically to the intended
      slice, VLAN/VNI, rate, and accounting identity.
- [ ] Confirm the management interface is excluded from subscriber shaping and
      firewall changes.
- [ ] Confirm rollback can be executed through an independent management path.

## Gate G — Staged execution and log collection order

The future live session must use this order:

1. Capture the pre-change inventory and hashes.
2. Validate FreeRADIUS syntax without starting or restarting it.
3. Start controller debug observation in an approved maintenance window.
4. Test the rejected authentication path first.
5. Test the accepted authentication and policy attributes.
6. Verify runtime VLAN/VNI state before testing traffic shaping.
7. Verify `tc` qdisc, class, filter, and counter state.
8. Run bounded latency and throughput tests with recorded parameters.
9. Capture RADIUS, AP, gateway, client, and edge-resource evidence.
10. Reconcile accounting counters using the Stage 3 reconciliation API.
11. Stop capture processes and restore the approved baseline.
12. Verify management, authentication, forwarding, and time synchronization
    after rollback.

Do not proceed to the next step after an unexplained failure.

## Gate H — Raw evidence layout

Use a new external run directory:

```text
<LOCAL_EVIDENCE_DIR>/<RUN_ID>/
  run_metadata.json
  controller/
  ap/
  client/
  accounting/
  hashes.sha256
  operator_notes.md
```

`run_metadata.json` must record:

- run and scenario identifiers;
- start and end time in UTC;
- node roles and pseudonymous IDs;
- tool and firmware versions;
- command parameters;
- source evidence class;
- known failures, omissions, and operator interventions.

Retain raw files unchanged. Normalized outputs belong under ignored processed
storage and must remain traceable to raw-file hashes.

## Stop conditions

Stop immediately if:

- the management path becomes unreliable;
- the backup cannot be copied and hash-verified;
- a secret appears in terminal capture or repository output;
- FreeRADIUS syntax validation fails;
- an unexpected subscriber or interface is affected;
- rejected credentials receive service state;
- accounting identities cannot be related to the accepted session;
- clocks are unsynchronized;
- a command target still contains an unresolved placeholder.

## Rollback acceptance

Rollback is complete only when:

- the original OpenWrt configuration is restored or the planned inverse
  changes have succeeded;
- controller and AP services are in their recorded pre-run state;
- management connectivity is stable;
- no test-only qdisc, class, filter, VLAN, tunnel, or credential remains;
- post-rollback state and logs are captured;
- unresolved differences are documented rather than hidden.

## Stage 2.7 exit gate

Stage 2.7 is complete when this checklist and the measurement command guide
are present, tested for required safety content, contain no real secret, and
have not been executed automatically.

## Authoritative operational references

- [FreeRADIUS configuration workflow](https://www.freeradius.org/documentation/freeradius-server/4.0.0/reference/raddb/index.html)
- [FreeRADIUS accounting tutorial](https://www.freeradius.org/documentation/freeradius-server/4.0.0/tutorials/accounting.html)
- [OpenWrt backup and restore](https://openwrt.org/docs/guide-user/troubleshooting/backup_restore)
- [OpenWrt UCI system](https://openwrt.org/docs/guide-user/base-system/uci)
- [Linux traffic-control manual](https://man7.org/linux/man-pages/man8/tc.8.html)
- [iperf3 invocation reference](https://software.es.net/iperf/invoking.html)
