#!/bin/bash -e
# Configure Granit hardware: PCIe SATA, I2C RTC, GPIO

on_chroot << 'EOF'

# --- /boot/firmware/config.txt additions ---
cat >> /boot/firmware/config.txt << 'BOOT'

# Granit carrier board hardware config
# PCIe: ASM1061 SATA bridge (Gen 2 x1)
dtparam=pciex1
dtparam=pciex1_gen=2

# I2C1: DS3231 RTC
dtparam=i2c_arm=on
dtoverlay=i2c-rtc,ds3231

# Hardware watchdog (auto-reboot on hang — critical for unattended device)
dtparam=watchdog=on

# SPI: disabled (not used)
dtparam=spi=off

# UART: debug console on GPIO14/15
enable_uart=1
BOOT

# --- Enable I2C ---
raspi-config nonint do_i2c 0

# --- RTC: use DS3231 as system clock ---
cat > /etc/udev/rules.d/85-hwclock.rules << 'UDEV'
KERNEL=="rtc0", RUN+="/sbin/hwclock --hctosys"
UDEV

# --- Watchdog: reboot if system hangs for 15 seconds ---
mkdir -p /etc/systemd/system/watchdog.conf.d
cat > /etc/systemd/system/watchdog.conf.d/granit.conf << 'WDT'
[Manager]
RuntimeWatchdogSec=15
RebootWatchdogSec=10min
WDT
mkdir -p /etc/systemd/system/watchdog.conf.d

EOF
