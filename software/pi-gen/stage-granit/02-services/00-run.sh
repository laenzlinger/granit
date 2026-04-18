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

SYNC_START=$(date +%s)
rclone copy "$SYNC_REMOTE" /mnt/backup/ \
    --transfers 1 \
    --log-file "$LOG" \
    --log-level INFO \
    --stats 1m \
    --stats-one-line
SYNC_EXIT=$?
SYNC_DURATION=$(( $(date +%s) - SYNC_START ))

echo "Sync completed at $(date) (exit=$SYNC_EXIT, duration=${SYNC_DURATION}s)" | tee -a "$LOG"

# Push metrics to Prometheus remote-write endpoint (if configured)
if [ -n "${METRICS_URL:-}" ]; then
    DISK_USED=$(df /mnt/backup --output=used | tail -1 | tr -d ' ')
    DISK_TOTAL=$(df /mnt/backup --output=size | tail -1 | tr -d ' ')
    curl -s --max-time 5 -d "granit_sync_duration_seconds $SYNC_DURATION
granit_sync_success $([ $SYNC_EXIT -eq 0 ] && echo 1 || echo 0)
granit_sync_last_timestamp $(date +%s)
granit_disk_used_bytes $((DISK_USED * 1024))
granit_disk_total_bytes $((DISK_TOTAL * 1024))" \
        "$METRICS_URL" || true
fi

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

# --- RPi undervoltage/throttle metrics (for node-exporter) ---
mkdir -p /var/lib/node_exporter/textfile_collector

cat > /usr/local/bin/rpi-throttle-metrics.sh << 'SCRIPT'
#!/bin/bash
hex=$(vcgencmd get_throttled | cut -d= -f2)
val=$((hex))
cat <<METRICS
# HELP rpi_throttled Raspberry Pi throttle status bitfield
# TYPE rpi_throttled gauge
rpi_throttled ${val}
# HELP rpi_under_voltage Under-voltage currently detected (bit 0)
# TYPE rpi_under_voltage gauge
rpi_under_voltage $(( (val >> 0) & 1 ))
# HELP rpi_under_voltage_occurred Under-voltage occurred since boot (bit 16)
# TYPE rpi_under_voltage_occurred gauge
rpi_under_voltage_occurred $(( (val >> 16) & 1 ))
METRICS
SCRIPT
chmod +x /usr/local/bin/rpi-throttle-metrics.sh

cat > /etc/systemd/system/rpi-throttle-metrics.service << 'UNIT'
[Unit]
Description=Collect RPi throttle metrics

[Service]
Type=oneshot
ExecStart=/bin/bash -c '/usr/local/bin/rpi-throttle-metrics.sh > /var/lib/node_exporter/textfile_collector/rpi_throttle.prom.$$ && mv /var/lib/node_exporter/textfile_collector/rpi_throttle.prom.$$ /var/lib/node_exporter/textfile_collector/rpi_throttle.prom'
UNIT

cat > /etc/systemd/system/rpi-throttle-metrics.timer << 'UNIT'
[Unit]
Description=Collect RPi throttle metrics every 30s

[Timer]
OnBootSec=10
OnUnitActiveSec=30

[Install]
WantedBy=timers.target
UNIT

# Configure node-exporter textfile collector
cat > /etc/default/prometheus-node-exporter << 'CONF'
ARGS="--collector.textfile.directory=/var/lib/node_exporter/textfile_collector"
CONF

systemctl enable rpi-throttle-metrics.timer

EOF
