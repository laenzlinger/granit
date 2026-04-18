#!/bin/bash -e
# Hardware boot config (must be in image, can't be done via Ansible)

on_chroot << 'EOF'

cat >> /boot/firmware/config.txt << 'BOOT'

# Granit carrier board
dtparam=pciex1
dtparam=pciex1_gen=2
dtparam=i2c_arm=on
dtoverlay=i2c-rtc,ds3231
dtparam=watchdog=on
dtparam=spi=off
enable_uart=1
BOOT

raspi-config nonint do_i2c 0

# RTC hwclock sync on boot
cat > /etc/udev/rules.d/85-hwclock.rules << 'UDEV'
KERNEL=="rtc0", RUN+="/sbin/hwclock --hctosys"
UDEV

EOF
