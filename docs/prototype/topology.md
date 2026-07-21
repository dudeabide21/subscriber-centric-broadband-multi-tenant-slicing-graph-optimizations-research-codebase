# Stage 2 Prototype Topology

## Prototype goal

The Stage 2 prototype establishes the minimum evidence spine:

`subscriber identity -> authentication -> policy and slice assignment
-> traffic-shaping intent -> accounting and evidence records`

This is a controlled laboratory scaffold. It is not a production broadband
controller, live ISP federation, or deployment-ready system.

## Minimum lab topology

```text
+------------------+
| Test client      |
|                  |
| Pseudonymous     |
| subscriber       |
+--------+---------+
         |
         | 802.1X / controlled authentication
         |
+--------v---------+       RADIUS authentication/accounting
| AP / gateway     +----------------------------------------+
| node             |                                        |
|                  |                              +---------v---------+
| hostapd/OpenWrt  |                              | RADIUS/controller |
| policy result    |                              | node              |
| VLAN/slice       |                              |                   |
| tc shaping       |                              | FreeRADIUS        |
| counters         |                              | policy mapping    |
| edge telemetry   |                              | accounting sink   |
+--------+---------+                              | evidence storage  |
         |                                        +-------------------+
         |
         | controlled shaped traffic
         |
+--------v---------+
| Test destination|
+------------------+