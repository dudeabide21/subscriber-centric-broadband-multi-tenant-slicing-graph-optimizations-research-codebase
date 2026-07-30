# OpenWrt examples

These are example network, wireless, and firewall fragments for controlled lab use only.
Do not apply them to live systems without review.

## Stage 2 prototype role

The OpenWrt examples represent the AP/gateway side of the minimum subscriber
evidence spine:

`802.1X authenticator -> RADIUS result -> VLAN/slice intent
-> tc shaping intent -> counters and edge telemetry`

Stage 2 must support documentation for:

- Linux-only dry-run mode;
- controlled OpenWrt hardware mode;
- subscriber-facing interface placeholders;
- HTB and fq_codel shaping intent;
- accounting and edge-resource collection points.

No configuration in this directory may apply firewall, network, wireless, or
traffic-control changes automatically.

Operational templates are added in Stage 2.3. Live application requires a
separate reviewed checklist and rollback plan.

## Stage 2.3 template inventory

The controlled-lab template set contains:

- `wireless.example` — enterprise wireless and RADIUS intent;
- `network.example` — bridge, VLAN, and interface intent;
- `firewall.example` — forwarding-boundary intent;
- `hostapd_8021x.example` — raw hostapd authenticator example;
- `tc_slices.example.sh` — HTB and fq_codel shaping intent.

`tc_slices.example.sh` defaults to:

```text
DRY_RUN=1
