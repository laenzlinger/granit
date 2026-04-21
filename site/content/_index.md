---
title: Overview
weight: 10
---

![PCB 3D Render](3D/granit-3D_blender_1_top.png)

Custom carrier board for the Raspberry Pi CM4 Compute Module, designed as a
minimal offsite backup appliance.

## Why Granit?

The **3-2-1 backup rule** says: keep **3** copies of your data, on **2**
different media, with **1** copy offsite. The first two are easy — a NAS with
mirrored disks covers them. The offsite copy is the hard part.

Cloud storage works, but means trusting a third party with your data, paying
recurring fees, and accepting upload speed limits. Granit takes a different
approach: a small, silent box you leave at a friend's or family member's house.
It connects to their network, receives encrypted backups over a VPN, and stores
them on a local hard disk. You keep full control of your data.

The device is designed to be deployed once and forgotten — no monitor, no
keyboard, no maintenance. The RTC alarm wakes it on schedule, the HDD spins up
only during backup windows, and everything is managed remotely over SSH.

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

![Architecture Diagram](https://raw.githubusercontent.com/laenzlinger/granit/main/images/architecture.drawio.svg)
