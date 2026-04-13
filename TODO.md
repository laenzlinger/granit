# Granit — TODO

## Schematic ✅

### Done

- [x] PSU: AP64501SP-13 buck + NCP1117 LDO + FDS4435BZ reverse polarity + 3A SMD fuse
- [x] CM4 Connector 1: power, GND, NC flags, global labels, Ethernet, GLOBAL_EN
- [x] CM4 Connector 2: power, GND, NC flags, global labels, USB, PCIe
- [x] Peripherals: SK6812MINI-E NeoPixel + 74AHCT1G32 level shifter
- [x] Peripherals: status LEDs (nLED_PWR, nLED_ACT, DNP)
- [x] Peripherals: tactile button (GPIO17) + pull-up
- [x] Peripherals: nRPIBOOT PCM12SMTR slide switch
- [x] Peripherals: UART debug JST-SH 3-pin (BM03B-SRSS-TB vertical), pinout: GND-TX-RX
- [x] Peripherals: DS3231MZ RTC + CR2032 battery
- [x] Peripherals: USB-C OTG + USBLC6-2SC6 ESD protection + solder jumper
- [x] Ethernet: RB1-125B8G1A Gigabit MagJack + LEDs
- [x] SATA: ASM1061 PCIe-to-SATA bridge + 25MHz crystal
- [x] SATA: add 100nF AC coupling caps (0805) in series on SATA TX pair (STXP_A, STXN_A), placed near ASM1061 — required by SATA spec (ASM1061 datasheet CTX = 75–200nF)
- [x] SATA: add 100nF AC coupling caps (0805) in series on SATA RX pair (SRXP_A, SRXN_A), placed near ASM1061 — defensive, external interface can't guarantee drive-side caps
- [x] PCIe: add 100nF AC coupling caps (0805) in series on PCIe RX pair (PCIE_RX_P, PCIE_RX_N), placed near ASM1061 TX output — CM4 datasheet: "external AC coupling capacitor required"
- [x] SATA: 7-pin data connector + 4-pin power connector
- [x] SATA: power switching (FDS4435BZ on 5V/12V, GPIO5 controlled, solder jumper bypass)
- [x] SATA: add 100K pull-down on N-FET gate (Net-(Q5-G) to GND) — ensures SATA power OFF during boot before GPIO5 is configured
- [x] Wake: hardware power-off wake (2N7002 + 74AHCT1G32 OR gate, DNP for v1)
- [x] All footprints assigned
- [x] All component descriptions filled
- [x] Resistor values consolidated (9 unique)
- [x] All decoupling caps verified
- [x] ERC: 0 errors, 0 warnings
- [x] ERC enabled in CI

## PCB Layout

Side-by-side layout inside Hammond 1455L2201 (220mm length):

- HDD occupies 147mm, PCB sits in the remaining space
- SATA connector on PCB edge mates directly with HDD
- External connectors (RJ45, USB-C, barrel jack, button) on opposite end panel

Max PCB size: **92 × 99.5mm** (fits Hammond 1455 card guides at 100.00 ±0.51mm)

Both PCB and HDD mount independently to the belly plate (slide-out for servicing).

### Component floorplan

```
                    SATA edge (faces HDD)
    ┌─────────────────────────────────────────┐
    │                                         │
    │   ASM1061        SATA connector         │
    │   (7×7mm)        (42mm wide, edge)      │
    │      ↕ short SATA diff pairs            │
    │                                         │
    │   ────── PCIe diff pairs (~20mm) ────── │
    │                                         │
    │          CM4 module (55×40mm)            │
    │          (center of board)              │
    │                                         │
    │   ↕ short ETH     ↕ USB        PSU     │
    │   diff pairs       diff        area    │
    │                                         │
    │  RJ45  USB-C  Barrel  BTN  LED  CR2032 │
    │                                         │
    └─────────────────────────────────────────┘
                 Connector edge (end plate)
```

Placement rationale:

- ASM1061 near SATA edge → shortest SATA differential pairs
- CM4 center → PCIe north to ASM1061, Ethernet south to RJ45
- RJ45 + USB-C on connector edge → short diff pairs from CM4
- PSU in corner → switching noise away from high-speed signals
- DS3231 + CR2032 → quiet area near CM4 I2C pins
- Button + LED → connector edge, accessible through end plate

### Pre-routing: stackup and impedance (JLCPCB 4-layer)

[JLCPCB JLC04161H-7628 standard 4-layer stackup](https://jlcpcb.com/impedance) (1.6mm):

| Layer | Material | Thickness | Er |
|---|---|---|---|
| Solder mask | — | 0.6mil above trace | 3.8 |
| L1 (Top signal) | Copper | 35µm (1oz) | — |
| Prepreg | 7628 | 0.2104mm | 4.4 |
| L2 (GND plane) | Copper | 35µm (1oz) | — |
| Core | — | 1.065mm | 4.6 |
| L3 (Power plane) | Copper | 35µm (1oz) | — |
| Prepreg | 7628 | 0.2104mm | 4.4 |
| L4 (Bottom signal) | Copper | 35µm (1oz) | — |
| Solder mask | — | 0.6mil above trace | 3.8 |

Trace geometry from [JLCPCB impedance calculator](https://jlcpcb.com/impedance)
(L1 signal, L2 GND reference, 0.2104mm prepreg, Er=4.6, 1oz outer / 0.5oz inner copper):
- 100Ω differential (PCIe, SATA, Ethernet): **0.2205mm trace, 0.2032mm gap**
- 90Ω differential (USB): **0.2860mm trace, 0.2032mm gap**

[JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities):
min 0.09mm trace/space, 0.2mm drill, 0.13mm annular ring.

- [x] Choose fab house: JLCPCB (prototype)
- [x] Update KiCad net classes with calculated values:
  - PCIe: diff_pair_width=0.2205, diff_pair_gap=0.2032
  - SATA: diff_pair_width=0.2205, diff_pair_gap=0.2032
  - Ethernet: diff_pair_width=0.2205, diff_pair_gap=0.2032
  - USB: diff_pair_width=0.2860, diff_pair_gap=0.2032
- [ ] Select impedance control when ordering (+~$10)
- [x] PCB thickness: 1.6mm (standard)

### Checklist

PCB standoff height must match HDD SATA connector vertical position (~3.5mm above belly plate).

- [x] Board outline: 92 × 99.5mm (fits Hammond 1455 card guides at 100.00 ±0.51mm)
- [x] Verify PCB standoff height aligns SATA connector with HDD receptacle
- [x] 4-layer stackup (signal/GND/power/signal)
- [x] SATA connector: replaced J4+J5 with single 22-pin Amphenol 10029364-001LF (horizontal/right-angle)
  - Footprint: `Connector_SATA_SAS:SATA_Amphenol_10029364-001LF_Horizontal`
  - Symbol: `granit:SATA_22pin`
- [x] External connectors (RJ45, USB-C, barrel jack, button, LED) on opposite edge
- [x] Place CM4 module and all components on top side (facing lid, for thermal contact)
- [x] SATA connector vertical alignment: HDD connector center is 3.50mm above mounting surface (SFF-8301)
  - Use matching standoff height for PCB and HDD (e.g. 5mm) — keeps SATA aligned
  - 5mm standoffs: CR2032 (3.4mm) fits on bottom side ✅
  - 1455L: 5mm + 9.5mm (2.5" HDD) = 14.5mm, 12.5mm to ceiling ✅
  - 1455T: 5mm + 26.1mm (3.5" HDD) = 31.1mm, 17mm to ceiling ✅
- [x] CR2032 holder on bottom side (fits under 5mm standoffs)
- [x] Place ASM1061 near SATA connector (short differential pairs)
- [ ] HDD mounting holes: M4 (4.3mm drill, `MountingHole:MountingHole_4.3mm_M4_Pad_Via`)
- [x] PCB standoff holes: M3 (3.2mm drill, `MountingHole:MountingHole_3.2mm_M3_Pad_Via`)
- [ ] Mounting hole keepout: 7.0mm clearance on pads (prevent screw heads shorting 12V traces)
- [x] Route PCIe differential pairs (100Ω impedance)
- [x] Route SATA differential pairs
- [x] Route Ethernet differential pairs
- [x] Route USB differential pairs
- [x] Power trace width: ≥1.0mm (40 mil) for short branches to pads
- [ ] Power planes on L3: split into 5V and 3.3V zones
- [ ] 12V: copper pour on L4 from barrel jack to SATA power (2A+ spin-up)
- [x] GND: solid plane on L2, stitching vias throughout
- [x] GND stitching: increase via density to 3–5/cm² (currently 1.2/cm²). 3mm grid near high-speed (PCIe/SATA/ETH), 5mm elsewhere. Use Place → Add Board Stitching Vias.
- [x] DRC clean (0 violations, 46 justified exclusions)
- [x] DRC enabled in CI
- [x] Silkscreen: add labels for switch positions (RUN/BOOT), jumper functions (JP1–JP6), connector pinouts (J8 UART), polarity markings, and board name/revision
- [x] Silkscreen front: add QR code or barcode linking to project URL (https://github.com/laenzlinger/granit)
- [x] Silkscreen back: add stackup info (layer order, impedance targets, fab spec JLC04161H-7628)
- [x] Reference designators reannotated by PCB position (top-to-bottom, left-to-right)

## PCB Respin (v0.3.0)

- [x] RJ45: swapped to HR911130A (Hanrun GbE) — widely available, future-proof
- [x] Crystal Y1: swap 3215 2-pin → 2016 4-pin footprint — easier to source, smaller
- [x] Cap C26: swap CP_Elec_6.3x5.8 → CP_Elec_6.3x7.7 — common size on LCSC
- [x] Board width: shrink Y axis from 100mm to 99.5mm — Hammond 1455 card guide slot is 100.00 ±0.51mm

## Enclosure

- [x] Case: Hammond 1455T2201 (3.5" HDD) or 1455L2201 (2.5" HDD only)
- [ ] 3D-printed internal frame (slides into case card guide grooves)
  - Holds PCB and HDD at correct height (5mm standoff equivalent)
  - Different frame variants for 2.5" vs 3.5" HDD
  - No belly plate drilling, no standoffs, no CNC needed
- [ ] CNC end plate: cutouts for RJ45, USB-C, barrel jack, button, LED
- [ ] Thermal pad from CM4 SoC to enclosure lid

## Future Improvements

- [ ] TPM/crypto chip (e.g. ATECC608) for secure LUKS key storage (I2C)
- [ ] Evaluate CM5 compatibility (power budget validation)
- [ ] Power LED on fused 12V rail (troubleshooting: PSU present but buck failed)
- [ ] Review fuse rating: 3A may be tight for 3.5" NAS drives (1.8–2.5A spin-up) + CM4 on same rail — consider 4A or inrush limiter
- [ ] Verify ASM1061 exposed pad thermal vias to ground plane (0.5W under sustained SATA III)
- [ ] Read-only root filesystem (overlayfs) to survive power loss — eMMC-only boot has no fallback
- [ ] Second SATA data connector (7-pin) for ASM1061 port B — enables RAID1 or dual-drive backup

## CI/CD

- [x] KiBot artifact generation with KiCad 10
- [x] GitHub Pages deployment (<https://laenzlinger.github.io/granit/>)
- [x] ERC check in KiBot preflight
- [x] Enable DRC check when PCB layout is complete
- [x] Tag-based release workflow (semver, GitHub Releases with Gerbers/BOM/iBOM)
- [x] Schematic and PCB diff outputs (vs previous tag)
- [ ] Switch to kicad10_auto container when available
- [ ] Add 3D renders (blender_export) once ghcr.io/inti-cmnb/kicad10_auto_full image exists (see pedalboard-hw)

## Software

- [ ] Raspberry Pi OS Lite base image
- [ ] Enable BCM2711 hardware watchdog (`bcm2835_wdt`) — critical for unattended remote device
- [ ] Device tree overlay for ASM1061
- [ ] DS3231 RTC driver + alarm configuration
- [ ] DS3231 OSF flag check on boot (warn if battery failed, report via healthcheck)
- [ ] GPIO_HOLD (GPIO6) assertion on boot
- [ ] SATA_PWR_EN (GPIO5) control
- [ ] NeoPixel status daemon
- [ ] Button handler (shutdown/backup/maintenance)
- [ ] WireGuard VPN configuration
- [ ] Restic backup automation
- [ ] LUKS encrypted backup partition
- [ ] Healthcheck dead man's switch
- [ ] SMART disk monitoring
- [ ] rtcwake integration for scheduled power-off/wake

## Pre-Order Checklist

### Design Verification
- [ ] ERC: 0 errors, 0 warnings
- [ ] DRC: 0 violations, 0 unconnected, 0 parity issues
- [ ] All diff pairs at correct width (PCIe/SATA/ETH: 0.2205mm, USB: 0.286mm)
- [ ] Board dimensions: 92 × 99.5mm (fits Hammond 1455 card guides)
- [ ] All footprints match ordered parts (check LCSC cart vs schematic)
- [ ] No DNP parts accidentally included in BOM
- [ ] IPN field present on all BOM components

### PCB Order (JLCPCB)
- [ ] Upload Gerbers from tagged release
- [ ] Select 4-layer stackup: JLC04161H-7628
- [ ] Select impedance control (+~$10)
- [ ] Board thickness: 1.6mm
- [ ] Copper weight: 1oz outer, 0.5oz inner
- [ ] Surface finish: HASL or ENIG
- [ ] Quantity: 5

### Component Order (LCSC)
- [ ] All LCSC part numbers verified against footprints
- [ ] Quantities sufficient for planned build count + spares
- [ ] Ship with JLCPCB order (combined shipping)

### Separate Sourcing
- [ ] ASM1061 QFN-48 (AliExpress)
- [ ] Hammond 1455 enclosure (Mouser)
- [ ] CM4 module
- [ ] 2.5" or 3.5" SATA HDD
- [ ] 12V DC power supply (3A+)
- [ ] CR2032 coin cell battery

### Post-Arrival
- [ ] Visual inspection of PCB
- [ ] Check impedance control marking on PCB edge
- [ ] Assemble one board
- [ ] Run hardware-test.sh
- [ ] Tag release with test results
