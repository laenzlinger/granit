#!/bin/bash -e
# First-boot setup: config directory and example config

on_chroot << 'EOF'

# --- Config directory ---
mkdir -p /etc/granit

cat > /etc/granit/sync.conf << 'CONF'
# Granit offsite backup configuration
# Edit this file after first boot, then enable the backup cycle:
#   sudo systemctl enable --now granit-cycle.timer
#
# SYNC_REMOTE: rclone remote path to pull backups from
# Examples:
#   SFTP:  ":sftp,host=100.x.x.x,user=backup,key_file=/home/granit/.ssh/id_ed25519:/backups"
#   S3:    "s3:mybucket/backups"
#   Local: "/mnt/usb/backups"
#
SYNC_REMOTE=""

# Hour to wake up for daily sync (24h format)
WAKE_HOUR=04
CONF

# --- First-boot message ---
cat > /etc/motd << 'MOTD'

  ╔═══════════════════════════════════════════╗
  ║         Granit Offsite Backup             ║
  ║   https://github.com/laenzlinger/granit  ║
  ╚═══════════════════════════════════════════╝

  First-time setup:
    1. Configure backup source:  sudo nano /etc/granit/sync.conf
    2. Format & mount disk:      sudo mkfs.ext4 /dev/sda1
                                 echo "UUID=... /mnt/backup ext4 defaults 0 2" | sudo tee -a /etc/fstab
    3. Enable backup cycle:      sudo systemctl enable --now granit-cycle.timer
    4. (Optional) Install VPN:   curl -fsSL https://pkgs.netbird.io/install.sh | sudo sh

  Status:   systemctl status granit-cycle.timer
  Logs:     ls /var/log/granit/
  Manual:   sudo /usr/local/bin/granit-sync.sh

MOTD

EOF
