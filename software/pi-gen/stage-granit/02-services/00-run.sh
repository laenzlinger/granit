#!/bin/bash -e
# Deploy Granit systemd services

on_chroot << 'EOF'

# --- HDD power control via GPIO5 (SATA_PWR_EN) ---
cat > /etc/systemd/system/granit-hdd-power.service << 'UNIT'
[Unit]
Description=Granit HDD power control (GPIO5)
DefaultDependencies=no
Before=local-fs-pre.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash -c 'echo 5 > /sys/class/gpio/export 2>/dev/null; echo out > /sys/class/gpio/gpio5/direction; echo 1 > /sys/class/gpio/gpio5/value'
ExecStop=/bin/bash -c 'echo 0 > /sys/class/gpio/gpio5/value'

[Install]
WantedBy=sysinit.target
UNIT

# --- HDD safe shutdown (unmount + spindown before poweroff) ---
cat > /etc/systemd/system/granit-hdd-shutdown.service << 'UNIT'
[Unit]
Description=Granit safe HDD shutdown
DefaultDependencies=no
Before=umount.target
After=granit-hdd-power.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStop=/bin/bash -c 'umount /mnt/backup 2>/dev/null; hdparm -Y /dev/sda 2>/dev/null; sleep 2; echo 0 > /sys/class/gpio/gpio5/value'

[Install]
WantedBy=multi-user.target
UNIT

# --- Backup disk mount point ---
mkdir -p /mnt/backup

# --- Offsite sync script ---
cat > /usr/local/bin/granit-sync.sh << 'SCRIPT'
#!/bin/bash
set -euo pipefail
LOG="/var/log/granit/sync-$(date +%Y%m%d-%H%M%S).log"
mkdir -p /var/log/granit

echo "Granit sync started at $(date)" | tee "$LOG"

if ! mountpoint -q /mnt/backup 2>/dev/null; then
    echo "SKIP: /mnt/backup not mounted" | tee -a "$LOG"
    exit 0
fi

# Source user config if present
[ -f /etc/granit/sync.conf ] && source /etc/granit/sync.conf

if [ -z "${SYNC_REMOTE:-}" ]; then
    echo "SKIP: SYNC_REMOTE not configured in /etc/granit/sync.conf" | tee -a "$LOG"
    exit 0
fi

rclone copy "$SYNC_REMOTE" /mnt/backup/ \
    --transfers 1 \
    --log-file "$LOG" \
    --log-level INFO \
    --stats 1m \
    --stats-one-line

echo "Sync completed at $(date)" | tee -a "$LOG"

# Cleanup old logs
find /var/log/granit -name "sync-*.log" -mtime +7 -delete 2>/dev/null || true
SCRIPT
chmod +x /usr/local/bin/granit-sync.sh

# --- Offsite schedule: sync then RTC wake + poweroff ---
cat > /etc/systemd/system/granit-cycle.service << 'UNIT'
[Unit]
Description=Granit backup cycle (sync → set wake alarm → poweroff)
After=network-online.target
Wants=network-online.target
ConditionPathExists=!/var/lib/granit-maintenance

[Service]
Type=oneshot
ExecStart=-/usr/local/bin/granit-sync.sh
ExecStart=/bin/bash -c 'WAKE_HOUR=${WAKE_HOUR:-04}; echo 0 > /sys/class/rtc/rtc0/wakealarm; echo $(date -d "tomorrow ${WAKE_HOUR}:00" +%%s) > /sys/class/rtc/rtc0/wakealarm; echo "Next wake: $(date -d @$(cat /sys/class/rtc/rtc0/wakealarm))"'
ExecStart=/usr/sbin/poweroff
UNIT

cat > /etc/systemd/system/granit-cycle.timer << 'UNIT'
[Unit]
Description=Start Granit backup cycle after boot

[Timer]
OnBootSec=120

[Install]
WantedBy=timers.target
UNIT

# --- Enable services ---
systemctl enable granit-hdd-power.service
systemctl enable granit-hdd-shutdown.service
# Timer disabled by default — user enables after first-boot setup
systemctl disable granit-cycle.timer

EOF
