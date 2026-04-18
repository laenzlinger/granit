#!/bin/bash -e
# Install packages needed for Granit appliance

on_chroot << 'EOF'
apt-get install -y --no-install-recommends \
    smartmontools \
    hdparm \
    rclone \
    prometheus-node-exporter \
    unattended-upgrades \
    fail2ban \
    ufw \
    i2c-tools \
    python3-smbus \
    ansible
EOF
