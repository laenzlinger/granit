---
title: Software
weight: 55
---

The device runs Raspberry Pi OS Lite (headless).

## Planned Stack

- Restic backup repository (encryption built-in)
- rsync to receive backups from NAS
- `smartmontools` for disk health monitoring (`smartctl /dev/sda`)
- WireGuard VPN for remote management
- RTC-based scheduled wake: DS3231 alarm → GPIO4 interrupt → CM wakes from suspend → backup runs → suspend
- LUKS full-disk encryption on the backup drive
- Automatic drive mount and health monitoring

## HDD Power Control

GPIO5 (`SATA_PWR_EN`) controls the P-FET power switches for the SATA 12V and 5V rails.
The boot default is selected by solder jumpers JP5 and JP6.

**Connect sequence** (power on → detect → mount):

```bash
#!/bin/bash
gpioset gpiochip0 5=1
sleep 2
echo "- - -" > /sys/class/scsi_host/host0/scan
sleep 3
cryptsetup luksOpen /dev/sda1 backup
mount /dev/mapper/backup /mnt/backup
```

**Disconnect sequence** (unmount → spin down → power off):

```bash
#!/bin/bash
umount /mnt/backup
cryptsetup luksClose backup
hdparm -Y /dev/sda
sleep 1
echo 1 > /sys/block/sda/device/delete
gpioset gpiochip0 5=0
```

## Deployment

1. Initial backup on-site: connect Granit to local network, run full backup over LAN
2. Move device to offsite location (friend's house, office, etc.)
3. Plug in Ethernet + power — done
4. Subsequent backups are incremental and run automatically over WireGuard

## Monitoring & Alerting

Monitoring must live outside the Granit device — if the device fails, it can't alert
about its own failure. The device reports in after each backup run using a dead man's
switch pattern:

- After each successful backup, Granit pings a healthcheck endpoint
- If the expected ping doesn't arrive, an alert is triggered
- Reported metrics: backup success/failure, SMART disk health, disk space remaining
- WireGuard connectivity is implicitly monitored — no tunnel means no ping
