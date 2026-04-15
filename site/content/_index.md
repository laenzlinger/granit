---
title: Overview
weight: 10
---

![PCB 3D Render](https://raw.githubusercontent.com/laenzlinger/granit/main/images/granit-3d.png)

Custom carrier board for the Raspberry Pi CM4 Compute Module, designed as a
minimal offsite backup appliance.

A compact, headless device that connects to a remote network and receives
encrypted backups onto an attached hard disk. Designed to be left at a trusted
offsite location and managed remotely.

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
