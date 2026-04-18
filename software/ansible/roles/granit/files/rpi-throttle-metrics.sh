#!/bin/bash
hex=$(vcgencmd get_throttled | cut -d= -f2)
val=$((hex))
cat <<EOF
# HELP rpi_throttled Raspberry Pi throttle status bitfield
# TYPE rpi_throttled gauge
rpi_throttled ${val}
# HELP rpi_under_voltage Under-voltage currently detected (bit 0)
# TYPE rpi_under_voltage gauge
rpi_under_voltage $(( (val >> 0) & 1 ))
# HELP rpi_under_voltage_occurred Under-voltage occurred since boot (bit 16)
# TYPE rpi_under_voltage_occurred gauge
rpi_under_voltage_occurred $(( (val >> 16) & 1 ))
EOF
