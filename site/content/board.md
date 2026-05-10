---
title: Board
type: board
weight: 20
---

For detailed circuit design notes, PCB routing guidelines, and netclass definitions,
see [hardware/DESIGN.md](https://github.com/laenzlinger/granit/blob/main/hardware/DESIGN.md).

{{% callout type="warning" %}}
**Power budget:** 12V @ 2A (3.5" HDD spin-up) + 5V @ 2.3A peak (CM4 + electronics) — use a 12V/3A+ PSU.
{{% /callout %}}

## Key Design Decisions

{{% details title="ASM1061 over USB-to-SATA bridges" %}}
Native PCIe SATA controller using the standard Linux `ahci` driver. No proprietary firmware blob required — the SPI flash footprint can be left unpopulated. SMART works natively without SAT translation hacks. Full SATA III throughput on both CM4 and CM5.
{{% /details %}}

{{% details title="12V DC input" %}}
Required for 3.5" HDD support (spindle motor needs 12V). AP64501SP-13 accepts 3.8–28V. Both barrel jack and screw terminal footprints provided — populate one at assembly time.
{{% /details %}}

{{% details title="USB-C OTG" %}}
Single USB-C connector for eMMC flashing (`rpiboot`) and USB mass storage gadget mode (initial backup seeding). USB 2.0 device mode only, with USBLC6-2SC6 ESD protection.
{{% /details %}}

{{% details title="SATA power control" %}}
12V and 5V to the SATA connector are software-controlled via GPIO5. HDD is off by default at boot — powered on explicitly by software. Solder jumpers (JP5, JP6) allow changing the default without a PCB respin.
{{% /details %}}

{{% details title="Boot and storage strategy" %}}
Full OS on CM4 eMMC (no SD card slot), SATA HDD dedicated to backup storage only. No SD card — eMMC is more reliable for a deploy-and-forget device. Backup data is encrypted client-side (e.g. by Restic or rclone crypt). Full-disk encryption via LUKS is optional.
{{% /details %}}

{{% details title="Reuse from pedalboard-hw" %}}
CM connector, power supply (AP64501SP-13 buck + NCP1117 LDO), USB power switch (AP2553W6), KiCad symbol/footprint library.
{{% /details %}}
