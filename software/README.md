# Granit OS Image

Custom Raspberry Pi OS Lite image for the Granit offsite backup appliance.

Built with [pi-gen](https://github.com/RPi-Distro/pi-gen) — adds a `stage-granit` on top of the standard Lite image.

## What's included

- **Hardware support**: PCIe SATA (ASM1061), DS3231 RTC, GPIO HDD power control
- **Backup**: rclone-based sync with configurable remote, daily RTC wake cycle
- **Security**: SSH hardened, fail2ban, UFW firewall, automatic security updates
- **Monitoring**: prometheus-node-exporter, smartmontools

## Build

```bash
# Requires: Docker or Debian/Ubuntu with debootstrap
make build
```

Output: `pi-gen-upstream/deploy/granit-*.img.xz`

## First boot

1. Flash image to CM4 eMMC (via `rpiboot` + `rpi-imager`) or SD card
2. Connect Ethernet, power on
3. SSH in: `ssh granit@granit.local`
4. Configure: `sudo nano /etc/granit/sync.conf`
5. Mount backup disk and enable cycle:
   ```bash
   sudo mkfs.ext4 /dev/sda1
   echo "UUID=$(blkid -s UUID -o value /dev/sda1) /mnt/backup ext4 defaults 0 2" | sudo tee -a /etc/fstab
   sudo mount /mnt/backup
   sudo systemctl enable --now granit-cycle.timer
   ```

## Services

| Service | Description |
|---------|-------------|
| `granit-hdd-power` | Controls SATA power via GPIO5 |
| `granit-hdd-shutdown` | Safe unmount + spindown before poweroff |
| `granit-cycle.timer` | Daily backup cycle (sync → RTC wake → poweroff) |
| `granit-sync.sh` | Backup sync script (rclone) |

## Configuration

`/etc/granit/sync.conf` — set `SYNC_REMOTE` and `WAKE_HOUR`.

Maintenance mode: `touch /var/lib/granit-maintenance` to skip the poweroff cycle.
