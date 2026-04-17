---
title: Software
weight: 55
---

The device runs a custom Raspberry Pi OS Lite image, built with
[pi-gen](https://github.com/RPi-Distro/pi-gen). Source:
[`software/`](https://github.com/laenzlinger/granit/tree/main/software)

## What's Included

- **Hardware support**: PCIe SATA (ASM1061), DS3231 RTC, GPIO HDD power control
- **Backup**: rclone-based sync with configurable remote, daily RTC wake cycle
- **Security**: SSH hardened, fail2ban, UFW firewall, automatic security updates
- **Monitoring**: prometheus-node-exporter, smartmontools

## First Boot

1. Flash image to CM4 eMMC (via `rpiboot` + `rpi-imager`) or SD card
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

## Backup Cycle

Once enabled, the device runs a daily cycle:

1. **Boot** — RTC alarm wakes the CM4
2. **Wait** — 2 minutes for network to settle
3. **Sync** — rclone pulls from configured remote to `/mnt/backup`
4. **Schedule** — sets RTC wake alarm for next day
5. **Poweroff** — safe HDD shutdown, then power off

Maintenance mode: `touch /var/lib/granit-maintenance` to skip poweroff and keep the device running.

## Services

| Service | Description |
|---------|-------------|
| `granit-hdd-power` | Controls SATA power via GPIO5 (P-FET switches) |
| `granit-hdd-shutdown` | Safe unmount + spindown before poweroff |
| `granit-cycle.timer` | Triggers backup cycle 2 min after boot |
| `granit-cycle.service` | Sync → set RTC alarm → poweroff |

## HDD Power Control

GPIO5 (`SATA_PWR_EN`) controls the P-FET power switches for the SATA 12V and 5V rails.
The `granit-hdd-power` service enables power at boot and disables it at shutdown.

For manual control:

```bash
# Power on
echo 1 > /sys/class/gpio/gpio5/value

# Power off (unmount first!)
umount /mnt/backup
hdparm -Y /dev/sda
echo 0 > /sys/class/gpio/gpio5/value
```

## Configuration

`/etc/granit/sync.conf`:

```bash
# rclone remote path to pull backups from
SYNC_REMOTE=":sftp,host=100.x.x.x,user=backup,key_file=/home/granit/.ssh/id_ed25519:/backups"

# Hour to wake up for daily sync (24h format)
WAKE_HOUR=04
```

## Monitoring

The device exports Prometheus metrics via `node-exporter` (port 9100).
Disk health is monitored with `smartmontools`.

For remote monitoring, install a VPN (e.g. [Netbird](https://netbird.io/)):

```bash
curl -fsSL https://pkgs.netbird.io/install.sh | sudo sh
sudo netbird up --setup-key YOUR_KEY
```

## Building the Image

```bash
cd software
make build   # clones pi-gen, builds image
# Output: pi-gen-upstream/deploy/granit-*.img.xz
```

Requires Docker or a Debian/Ubuntu host with `debootstrap`.
