---
title: Overview
weight: 10
---

<div class="hero-layout">
<img src="3D/granit-3D_blender_1_top.png" alt="PCB 3D Render">
<div>

Custom carrier board for the Raspberry Pi CM4 Compute Module, designed as a
minimal offsite backup appliance.

**The 3-2-1 backup rule** says: keep **3** copies of your data, on **2**
different media, with **1** copy offsite. The first two are easy — a NAS with
mirrored disks covers them. The offsite copy is the hard part.

Granit takes a different approach: a small, silent box you leave at a friend's
or family member's house. It connects to their network, receives encrypted
backups over a VPN, and stores them on a local hard disk. You keep full control
of your data.

</div>
</div>

## Key Components

| Component | Description |
|---|---|
| Raspberry Pi CM4 | Compute module (PCIe Gen 2 x1) |
| ASM1061 | PCIe to 2-port SATA III controller |
| 2.5" or 3.5" SATA HDD/SSD | Backup storage |
| DS3231 RTC | Battery-backed real-time clock with alarm wake |
| AP64501SP-13 | 3.5A DC-DC buck converter |
| USB-C | USB 2.0 OTG with ESD protection |

## Architecture

![Architecture Diagram](images/architecture.drawio.svg)
