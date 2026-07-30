# Stage 2.7 Measurement Command Guide

Status: **command reference only; nothing in this document is executed by the
repository**

## Safety legend

- **READ-ONLY** — inspects state or writes only to a new evidence file.
- **SERVICE-AFFECTING** — starts a diagnostic process or bounded traffic test;
  requires an approved maintenance window.
- **MUTATING** — changes packages, configuration, services, interfaces, or
  traffic control; requires explicit operator approval and a tested rollback.
- **ROLLBACK** — restores the recorded pre-run state.

Never paste a block until every `<PLACEHOLDER>` has been resolved in the
private run log. Never put a RADIUS secret directly on a command line.

## 1. Local run workspace

**READ-ONLY / local evidence preparation**

```bash
umask 077
RUN_ID='<RUN_ID>'
LOCAL_EVIDENCE_DIR='<LOCAL_EVIDENCE_DIR>'
test -n "${RUN_ID}"
test -n "${LOCAL_EVIDENCE_DIR}"
mkdir -p "${LOCAL_EVIDENCE_DIR}/${RUN_ID}"/{controller,ap,client,accounting}
date -u +'%Y-%m-%dT%H:%M:%SZ'
```

`mkdir` changes only the new local evidence directory. It must not point into
the repository.

## 2. Version and clock inventory

**READ-ONLY — controller/client**

```bash
uname -a
date -u +'%Y-%m-%dT%H:%M:%SZ'
timedatectl status
python3 --version
radiusd -v 2>/dev/null || freeradius -v
tc -Version
iperf3 --version
wg --version
```

**READ-ONLY — OpenWrt**

```sh
ubus call system board
date -u +'%Y-%m-%dT%H:%M:%SZ'
opkg list-installed 2>/dev/null || apk list --installed
tc -Version
```

Package-manager output can contain local feed information; keep it in the
private evidence directory.

## 3. Interface and route identification

**READ-ONLY — Linux/controller/client**

```bash
ip -details link show
ip -details address show
ip route show table all
bridge -details link show
bridge vlan show
```

**READ-ONLY — OpenWrt**

```sh
ip -details link show
ip -details address show
ip route show table all
bridge -details link show
bridge vlan show
ubus call network.interface dump
ubus call network.device status
uci show network
uci show wireless
uci show firewall
```

Record `<AP_INTERFACE>`, `<UPLINK_INTERFACE>`, and `<TC_INTERFACE>` only after
matching persistent UCI names to runtime devices.

## 4. Backup commands

**READ-ONLY — FreeRADIUS syntax and paths**

```bash
sudo radiusd -XC 2>/dev/null || sudo freeradius -XC
sudo find '<RADIUS_CONFIG_DIR>' -xdev -type f -print
```

**MUTATING — creates new backup files only**

```bash
umask 077
sudo tar --xattrs --acls -czf '<LOCAL_EVIDENCE_DIR>/<RUN_ID>/controller/freeradius-config.tar.gz' '<RADIUS_CONFIG_DIR>'
sha256sum '<LOCAL_EVIDENCE_DIR>/<RUN_ID>/controller/freeradius-config.tar.gz'
```

**MUTATING — OpenWrt creates a configuration archive in `/tmp`**

```sh
sysupgrade --list-backup
sysupgrade -b '/tmp/<RUN_ID>-openwrt-backup.tar.gz'
sha256sum '/tmp/<RUN_ID>-openwrt-backup.tar.gz'
uci export network >'/tmp/<RUN_ID>-network.uci'
uci export wireless >'/tmp/<RUN_ID>-wireless.uci'
uci export firewall >'/tmp/<RUN_ID>-firewall.uci'
uci export dhcp >'/tmp/<RUN_ID>-dhcp.uci'
uci export system >'/tmp/<RUN_ID>-system.uci'
```

Copy and hash-verify those files on the workstation before any further
mutation.

## 5. Runtime log collection

**READ-ONLY — controller**

```bash
sudo journalctl -u freeradius --since '<UTC_START>' --until '<UTC_END>' --no-pager
sudo find '<RADIUS_LOG_DIR>' -xdev -type f -name 'detail-*' -print
```

FreeRADIUS accounting paths are configuration-dependent. Discover the active
`radacctdir` or detail-module expansion; do not assume one distribution path.

**READ-ONLY — OpenWrt**

```sh
logread -e hostapd
logread -e radius
logread -e netifd
```

OpenWrt commonly stores logs in an in-memory `logd` buffer accessible through
`logread`; do not assume `/var/log/messages` exists.

## 6. Authentication checks

**READ-ONLY — validate candidate configuration**

```bash
sudo radiusd -XC 2>/dev/null || sudo freeradius -XC
```

**SERVICE-AFFECTING — foreground debug server**

```bash
sudo radiusd -X 2>/dev/null || sudo freeradius -X
```

Run foreground debug only when the normal service has been handled according
to the maintenance plan; do not start a second listener on active ports.

**SERVICE-AFFECTING — controlled RADIUS request**

```bash
radclient -x -S '<SECRET_FILE>' '<CONTROLLER_HOST>:1812' auth <'<ACCESS_REQUEST_FILE>'
```

Use separate request files for the expected reject and expected accept paths.
Run reject first. Verify packet result, policy attributes, session identity,
and absence or presence of service state as appropriate.

## 7. VLAN, qdisc, class, and filter verification

**READ-ONLY**

```bash
ip -details link show dev '<TC_INTERFACE>'
bridge vlan show dev '<TC_INTERFACE>'
tc -j -s qdisc show dev '<TC_INTERFACE>'
tc -j -s class show dev '<TC_INTERFACE>'
tc -j -s filter show dev '<TC_INTERFACE>'
```

Capture state before authentication, after rejection, after acceptance, after
the bounded traffic test, and after rollback. A class existing in output is
not by itself proof of subscriber classification or cross-slice isolation.

## 8. Accounting request and reconciliation inputs

**SERVICE-AFFECTING — controlled accounting request**

```bash
radclient -x -S '<SECRET_FILE>' '<CONTROLLER_HOST>:1813' acct <'<ACCOUNTING_REQUEST_FILE>'
```

**READ-ONLY — capture comparison counters**

```bash
tc -j -s class show dev '<TC_INTERFACE>'
ip -s -j link show dev '<TC_INTERFACE>'
wg show all dump
```

Retain RADIUS input/output octets and the corresponding gateway-direction
counters. Stage 3 computes:

```text
byte_mismatch = abs(radius_in - gateway_in)
              + abs(radius_out - gateway_out)
```

The tolerance must be an explicit non-negative integer fixed before the run.
Do not infer it from the observed mismatch.

## 9. Edge-resource snapshot

**READ-ONLY — OpenWrt/Linux AP**

```sh
date -u +'%Y-%m-%dT%H:%M:%SZ'
cat /proc/stat
cat /proc/meminfo
cat /proc/interrupts
cat /proc/loadavg
ip -s -j link show
```

Sampling CPU usage requires two timestamped `/proc/stat` observations and an
explicit interval. RAM ratios require recorded used and total definitions.
Do not equate one scaffold value with hardware feasibility.

## 10. Bounded latency and throughput tests

**SERVICE-AFFECTING — server**

```bash
iperf3 --server --one-off --port '<IPERF_PORT>'
```

**SERVICE-AFFECTING — client**

```bash
ping -n -c '<PING_COUNT>' -I '<CLIENT_INTERFACE>' '<TEST_SERVER>'
iperf3 --client '<TEST_SERVER>' --port '<IPERF_PORT>' --time '<SECONDS>' --json
iperf3 --client '<TEST_SERVER>' --port '<IPERF_PORT>' --time '<SECONDS>' --reverse --json
```

Record duration, direction, transport, offered load, interface, concurrency,
and whether slow-start samples are omitted. Do not run unbounded traffic.

## 11. Optional bounded packet metadata capture

**SERVICE-AFFECTING — privacy-sensitive**

```bash
sudo timeout '<SECONDS>' tcpdump -i '<CAPTURE_INTERFACE>' -nn -s 128 -c '<PACKET_LIMIT>' -w '<LOCAL_EVIDENCE_DIR>/<RUN_ID>/controller/radius-metadata.pcap' 'udp port 1812 or udp port 1813'
```

Use the smallest snap length, duration, packet count, and filter that answer
the test question. Do not capture subscriber payloads. Packet captures remain
outside Git.

## 12. Hash and normalize raw evidence

**READ-ONLY / writes manifest only**

```bash
find '<LOCAL_EVIDENCE_DIR>/<RUN_ID>' -type f ! -name hashes.sha256 -print0 | sort -z | xargs -0 sha256sum >'<LOCAL_EVIDENCE_DIR>/<RUN_ID>/hashes.sha256'
sha256sum --check '<LOCAL_EVIDENCE_DIR>/<RUN_ID>/hashes.sha256'
```

Copy supported raw files into an ignored processing workspace only after the
hash manifest is complete. Use the Stage 3 parser contract; preserve originals.

## 13. Rollback

**ROLLBACK — traffic control**

Use the exact inverse commands recorded for the approved candidate. Do not use
a generic `tc qdisc del` unless the pre-run state proves the root qdisc was
absent and the target interface has been re-confirmed.

**ROLLBACK — FreeRADIUS**

```bash
sudo radiusd -XC 2>/dev/null || sudo freeradius -XC
sudo systemctl restart freeradius
sudo systemctl --no-pager --full status freeradius
```

Restore the archived configuration before validation and restart. Service
names vary by distribution and must be confirmed before the window.

**ROLLBACK — OpenWrt configuration archive**

```sh
sysupgrade -r '/tmp/<RUN_ID>-openwrt-backup.tar.gz'
```

Restoring can disrupt connectivity and may require reboot. Use only on the
same approved device/firmware with an independent management path and the
OpenWrt recovery procedure available.

## References

- [FreeRADIUS configuration validation](https://www.freeradius.org/documentation/freeradius-server/4.0.0/reference/raddb/index.html)
- [FreeRADIUS `radclient`](https://www.freeradius.org/documentation/freeradius-server/4.0.0/reference/man/radclient.html)
- [FreeRADIUS accounting records](https://www.freeradius.org/documentation/freeradius-server/4.0.0/tutorials/accounting.html)
- [OpenWrt backup and restore](https://openwrt.org/docs/guide-user/troubleshooting/backup_restore)
- [OpenWrt system logging](https://openwrt.org/docs/guide-user/base-system/system_configuration)
- [Linux `tc`](https://man7.org/linux/man-pages/man8/tc.8.html)
- [Linux `tcpdump`](https://man7.org/linux/man-pages/man8/tcpdump.8.html)
- [iperf3 command reference](https://software.es.net/iperf/invoking.html)
