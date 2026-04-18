---
title: Software
weight: 55
---

Custom Raspberry Pi OS Lite image for the Granit offsite backup appliance,
built with [pi-gen](https://github.com/RPi-Distro/pi-gen).
Source: [`software/`](https://github.com/laenzlinger/granit/tree/main/software)

## Hardware Support

### PCIe SATA (ASM1061)

The ASM1061 PCIe-to-SATA bridge is enabled via device tree:

```
dtparam=pciex1
dtparam=pciex1_gen=2
```

The SATA drive appears as `/dev/sda` once connected and powered.

### DS3231 RTC

The DS3231 real-time clock on I2C1 keeps time across power cycles:

```
dtparam=i2c_arm=on
dtoverlay=i2c-rtc,ds3231
```

On boot, the system clock is set from the RTC via udev rule. The RTC alarm
is used for scheduled wake — the CM4 powers off after backup and the RTC
alarm triggers the next boot.

### HDD Power Control

GPIO5 (`SATA_PWR_EN`) controls the P-FET power switches for the SATA 12V
and 5V rails. The `granit-hdd-power` service manages this automatically:

- **Boot**: GPIO5 high → SATA power on
- **Shutdown**: unmount → spindown → GPIO5 low → SATA power off

### Hardware Watchdog

The BCM2835 hardware watchdog auto-reboots the device if the system hangs —
critical for an unattended remote device:

```
dtparam=watchdog=on
```

systemd pings the watchdog every 15 seconds. If the system becomes
unresponsive, the watchdog triggers a hardware reset.

### UART Debug Console

A serial console is available on GPIO14 (TX) / GPIO15 (RX) at 115200 baud,
accessible via the JST-SH 3-pin header (J3). Pinout: GND, TX, RX.

```
enable_uart=1
```

## Backup Cycle

Once enabled, the device runs a daily cycle:

1. **Boot** — RTC alarm wakes the CM4
2. **Wait** — 2 minutes for network to settle
3. **Sync** — rclone pulls from configured remote to `/mnt/backup`
4. **Schedule** — sets RTC wake alarm for next day at configured hour
5. **Poweroff** — safe HDD shutdown, then power off

The cycle is managed by `granit-cycle.timer` (triggers 2 min after boot)
and `granit-cycle.service` (sync → alarm → poweroff).

### Maintenance Mode

To keep the device running (skip the poweroff cycle):

```bash
# Local: create flag file
touch /var/lib/granit-maintenance

# Remote: create .maintenance file on the NAS
# The sync script checks for this before powering off
```

## Security

- **SSH**: key-only authentication, root login disabled
- **Firewall**: UFW, deny all incoming except SSH (port 22)
- **fail2ban**: 5 failed attempts → 1 hour ban
- **Automatic updates**: unattended-upgrades for security patches
- **Kernel hardening**: sysctl settings for network stack protection

## Monitoring

- **prometheus-node-exporter** on port 9100 — system metrics
- **smartmontools** — disk health (`smartctl -a /dev/sda`)
- **RPi throttle metrics** — under-voltage detection via `vcgencmd`

For remote monitoring, install a VPN:

```bash
curl -fsSL https://pkgs.netbird.io/install.sh | sudo sh
sudo netbird up --setup-key YOUR_KEY
```

## Services

| Service | Description |
|---------|-------------|
| `granit-hdd-power` | SATA power on/off via GPIO5 |
| `granit-hdd-shutdown` | Safe unmount + spindown before poweroff |
| `granit-cycle.timer` | Triggers backup cycle 2 min after boot |
| `granit-cycle.service` | Sync → set RTC alarm → poweroff |

## Configuration

`/etc/granit/sync.conf`:

```bash
# rclone remote path to pull backups from
SYNC_REMOTE=":sftp,host=100.x.x.x,user=backup,key_file=/home/granit/.ssh/id_ed25519:/backups"

# Hour to wake up for daily sync (24h format)
WAKE_HOUR=04
```

## First Boot

1. Flash image to CM4 eMMC via `rpiboot` + `rpi-imager`, or to SD card
2. Connect Ethernet, power on
3. SSH in: `ssh granit@granit.local`
4. Configure backup source: `sudo nano /etc/granit/sync.conf`
5. Format and mount backup disk:
   ```bash
   sudo mkfs.ext4 /dev/sda1
   UUID=$(blkid -s UUID -o value /dev/sda1)
   echo "UUID=$UUID /mnt/backup ext4 defaults 0 2" | sudo tee -a /etc/fstab
   sudo mount /mnt/backup
   ```
6. Enable the backup cycle:
   ```bash
   sudo systemctl enable --now granit-cycle.timer
   ```

## Building the Image

```bash
cd software
make build   # clones pi-gen, builds image via Docker
# Output: pi-gen-upstream/deploy/granit-*.img.xz
```

Requires Docker and QEMU user-static for ARM emulation on x86 hosts.
