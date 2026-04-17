#!/bin/bash -e
# Security hardening and system defaults

on_chroot << 'EOF'

# --- SSH hardening ---
sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config

# --- Firewall (allow SSH only) ---
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw --force enable

# --- Kernel hardening ---
cat > /etc/sysctl.d/90-granit-hardening.conf << 'SYSCTL'
net.ipv4.ip_forward=1
net.ipv4.conf.all.rp_filter=1
net.ipv4.conf.all.accept_source_route=0
net.ipv4.conf.all.send_redirects=0
net.ipv4.icmp_echo_ignore_broadcasts=1
net.ipv4.tcp_syncookies=1
SYSCTL

# --- Automatic security updates ---
cat > /etc/apt/apt.conf.d/20auto-upgrades << 'APT'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
APT
EOF
