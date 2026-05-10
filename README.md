# Granit — Offsite Backup Device

Custom carrier board for the Raspberry Pi CM4 Compute Module, designed as a minimal offsite backup appliance.

📖 **[Documentation](https://laenzlinger.github.io/granit/latest/)**

[![Latest Release](https://img.shields.io/github/v/tag/laenzlinger/granit?label=release)](https://github.com/laenzlinger/granit/releases)
[![OSHWA CH000031](https://img.shields.io/badge/OSHWA-CH000031-blue)](https://certification.oshwa.org/ch000031.html)

## Overview

![PCB 3D Render](https://laenzlinger.github.io/granit/latest/3D/granit-3D_blender_1_top.png)

A compact, headless device that connects to a remote network and receives encrypted backups
onto an attached hard disk. Designed to be left at a trusted offsite location and managed remotely.

- Raspberry Pi CM4 with PCIe SATA (ASM1061)
- 2.5" or 3.5" HDD/SSD support
- Software-controlled HDD power (GPIO)
- RTC wake for scheduled backups
- USB-C OTG for eMMC flashing
- Hammond 1455 aluminium enclosure

## Roadmap

- **v0.3** — First production run (CM4, 4-layer PCB, JLCPCB)
- **v0.4** — Fix wake/shutdown latch (#31), barrel jack swap (#40), DF40C alignment bosses (#37)
- **v1.0** — Validated design with custom OS image and documentation
- **Future** — Investigating RISC-V SoM support for a fully blob-free variant

## License

[CERN Open Hardware Licence Version 2 - Permissive](https://ohwr.org/cern_ohl_p_v2.txt)
