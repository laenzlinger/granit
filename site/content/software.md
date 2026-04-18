---
title: Software
weight: 55
---

Custom Raspberry Pi OS Lite image with Ansible-based provisioning.
Source: [`software/`](https://github.com/laenzlinger/granit/tree/main/software)

## Architecture

- **pi-gen**: builds a minimal image (packages + boot config)
- **Ansible**: configures all services, security, and monitoring

You can also skip the custom image and provision stock Raspberry Pi OS directly.

## Hardware Support

### PCIe SATA (ASM1061)

```
dtparam=pciex1
dtparam=pciex1_gen=2
```

The SATA drive appears as `/dev/sda` once connected and powered.

### DS3231 RTC

```
dtparam=i2c_arm=on
dtoverlay=i2c-rtc,ds3231
```

System clock is set from the RTC on boot. The RTC alarm triggers scheduled wake.

### HDD Power Control

GPIO5 (`SATA_PWR_EN`) controls the P-FET power switches for SATA 12V and 5V.
Managed by `granit-hdd-power` and `granit-hdd-shutdown` services.

### Hardware Watchdog

```
dtparam=watchdog=on
```

systemd pings the watchdog every 15 seconds. If the system hangs, the watchdog
triggers a hardware reset. Critical for an unattended remote device.

### UART Debug Console

Serial console on GPIO14/15 at 115200 baud via JST-SH 3-pin header (J3).

## Backup Cycle

1. **Boot** — RTC alarm wakes the CM4
2. **Wait** — 2 minutes for network
3. **Sync** — rclone pulls from configured remote
4. **Schedule** — sets RTC wake alarm for next day
5. **Poweroff** — safe HDD shutdown, then power off

Maintenance mode: `touch /var/lib/granit-maintenance` to skip poweroff.

## Monitoring

**Push (default)**: after each sync, metrics are pushed to a configurable
Prometheus remote-write endpoint (`METRICS_URL`). Works with VictoriaMetrics,
Prometheus Pushgateway, or any compatible receiver.

Metrics: `granit_sync_duration_seconds`, `granit_sync_success`,
`granit_disk_used_bytes`, `granit_disk_total_bytes`.

**Pull (optional)**: `prometheus-node-exporter` on port 9100 with RPi
throttle/undervoltage metrics. Disabled by default — enable if you have a
scraper that can reach the device.

## Security

- SSH key-only, root login disabled
- UFW firewall (SSH only)
- fail2ban (5 attempts → 1h ban)
- Automatic security updates
- Kernel hardening (sysctl)

## Configuration

`/etc/granit/sync.conf`:

```bash
SYNC_REMOTE=":sftp,host=100.x.x.x,user=backup,key_file=..."
WAKE_HOUR=04
METRICS_URL="http://192.168.1.x:8428/api/v1/import/prometheus"
```

## Provisioning

```bash
# Flash image, boot, then:
cd software
make provision  # runs Ansible playbook
```

Ansible variables can be set in the inventory or passed on the command line:

| Variable | Default | Description |
|----------|---------|-------------|
| `granit_timezone` | `UTC` | System timezone |
| `granit_wake_hour` | `04` | RTC wake hour |
| `granit_sync_remote` | `""` | rclone remote path |
| `granit_metrics_url` | `""` | Prometheus push URL |

## Building the Image

```bash
cd software
make build   # pi-gen via Docker
```

The image includes packages and boot config. Run `make provision` after
flashing to configure services.
