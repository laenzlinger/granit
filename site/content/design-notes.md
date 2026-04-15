---
title: Design Notes
weight: 50
---

See [hardware/DESIGN.md](https://github.com/laenzlinger/granit/blob/main/hardware/DESIGN.md)
for detailed circuit design notes, PCB routing guidelines, and netclass definitions.

## Key Design Decisions

- **ASM1061 over USB-to-SATA bridges**: Native PCIe SATA controller using the
  standard Linux `ahci` driver. No proprietary firmware blob required.
- **12V DC input**: Required for 3.5" HDD support. AP64501SP-13 accepts 3.8–28V.
- **SATA power control**: 12V and 5V to SATA connector are software-controlled
  via GPIO5. HDD is off by default at boot.
- **USB-C OTG**: For eMMC flashing (`rpiboot`) and USB mass storage gadget mode.
- **Boot strategy**: Full OS on CM4 eMMC, SATA HDD dedicated to LUKS-encrypted
  backup storage only.
