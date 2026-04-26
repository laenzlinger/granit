# Pick and Place Assembly Plan

OpenPnP job files and documentation for Granit v0.3 prototype assembly.

## Overview

- **Total SMD placements:** 90 (machine) + 7 (hand) + 4 (fiducials)
- **Stencil:** Yes (from JLCPCB, frameless)
- **Reflow:** Hot plate (peak ~245°C for lead-free)

## Generate PnP Files

```bash
cd hardware
make pnp        # generates pnp/granit.pos + pnp/granit.board.xml
make feeder-map  # generates pnp/feed_map.svg
```

## Feeder Allocation

### LV8 — Passives (front-left, 16×8mm)

| Slot | Part | Qty |
|------|------|-----|
| LV8-01 | C_0805-1n | 2 |
| LV8-02 | C_0805-1.2n | 1 |
| LV8-03 | C_0805-18p | 2 |
| LV8-04 | C_0805-100n | 24 |
| LV8-05 | C_0805-10u | 15 |
| LV8-06 | R_0805-10R | 2 |
| LV8-07 | R_0805-330R | 5 |
| LV8-08 | R_0805-750R | 2 |
| LV8-09 | R_0805-2K2 | 1 |
| LV8-10 | R_0805-4K7 | 2 |
| LV8-11 | R_0805-5K1 | 2 |
| LV8-12 | R_0805-10K | 5 |
| LV8-13 | R_0805-12K | 2 |
| LV8-14 | R_0805-20K | 1 |
| LV8-15 | R_0805-100K | 3 |
| LV8-16 | LED_0805-LED R | 1 |

### RV8 — Small ICs (front-right, 8×8mm)

| Slot | Part | Qty |
|------|------|-----|
| RV8-1 | LED_0805-LED G | 1 |
| RV8-2 | SOT-23-2N7002 | 3 |
| RV8-3 | SOT-23-5-74AHCT1G125 | 1 |
| RV8-4 | SOT-23-5-74AHCT1G32 | 1 |
| RV8-5 | SOT-23-6-USBLC6-2SC6 | 1 |
| RV8-6 | XTAL-2016-25MHz | 1 |

### RH12 — Larger ICs + passives (back-right, 6×12mm)

| Slot | Part | Qty |
|------|------|-----|
| RH12-1 | SOT-223-NCP1117-3.3 | 1 |
| RH12-2 | SOIC-8-FDS4435BZ | 3 |
| RH12-3 | SOIC-8-EP-AP64501SP-13 | 1 |
| RH12-4 | SOIC-8-DS3231MZ | 1 |
| RH12-5 | FUSE-2512-3A | 1 |
| RH12-6 | TANT-D-100u | 1 |

### RV16 — Large packages (front-right, 6×16mm)

| Slot | Part | Qty |
|------|------|-----|
| RV16-1 | QFN-48-7x7-ASM1061 | 1 |
| RV16-2 | WS2812B-5050-WS2812B-5mm | 1 |

### Drag Feeders (far left, 8 slots)

| Slot | Part | Qty |
|------|------|-----|
| DRAG-1 | C_0805-100n | 24 |
| DRAG-2 | C_0805-10u | 15 |
| DRAG-3 | R_0805-10K | 5 |

## Hand-Place Components

Placed after reflow or require manual alignment:

| Ref  | Part              | Package              | Reason                    |
|------|-------------------|----------------------|---------------------------|
| CM1  | Raspberry Pi CM4  | DF40 200-pin B2B     | Board-to-board connector  |
| J1   | USB-C receptacle  | GCT USB4105          | Mid-mount, alignment      |
| J2   | Slide switch      | PCM12SMTR            | Odd form factor           |
| J3   | UART connector    | JST-SH BM03B 3-pin  | Vertical                  |
| J4   | SATA 22-pin       | Amphenol horizontal  | Through-hole pins         |
| SW1  | Tactile button    | SKRTLAE010           | Side-mount                |
| C26  | 100µF/25V elec    | 6.3×7.7mm            | Tall electrolytic         |

## Assembly Sequence

1. **Stencil** — Apply solder paste (tape-hinge method, align under microscope)
2. **Machine place** — Run OpenPnP job (90 placements)
3. **Inspect** — Check QFN-48 (U3) alignment under microscope
4. **Reflow** — Hot plate reflow profile (peak ~245°C for lead-free)
5. **Inspect** — Check for bridges on QFN-48, SOIC-8-EP, fine-pitch
6. **Hand-solder** — Place CM1, connectors (J1–J4), SW1, C26
7. **Clean** — IPA wash if using flux

## Notes

- The QFN-48 ASM1061 (U3) is 0.5mm pitch — bottom vision handles orientation.
- D1 (WS2812B), L1 (inductor), C38 (tantalum) are machine-placed.
- Fiducials (FID1–FID4) are used for board alignment.
- Feeder layout and naming conventions documented in `~/.openpnp2/docs/feeder-layout.md`.
- When drag feeders are used for 100nF, 10µF, and 10K, remove those from the LV8 strip allocation.
