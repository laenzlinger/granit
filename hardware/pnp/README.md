# Pick and Place Assembly Plan

OpenPnP job files and documentation for Granit v0.3 prototype assembly.

## Overview

- **Total SMD placements:** ~93 (machine) + ~7 (hand)
- **Stencil:** Yes (from JLCPCB)
- **Reflow:** Hot plate or hot air

## Generate Position File

```bash
cd hardware
make pos
```

This exports the KiCad position CSV, remaps footprints to OpenPnP package IDs
via `~/.openpnp2/remap-pnp.py`, and writes `out/granit.pos.csv`.

## Feeder Layout

### Passive Feeders (0805 tape, high volume)

| Feeder | Value   | Qty | IPN   | Tape width |
|--------|---------|-----|-------|------------|
| P1     | 100nF   | 24  | C-001 | 8mm        |
| P2     | 10µF    | 15  | C-003 | 8mm        |

### Strip Feeders — Resistors (0805)

| Feeder | Value | Qty | IPN   |
|--------|-------|-----|-------|
| S1     | 10K   | 6   | R-002 |
| S2     | 330R  | 5   | R-018 |
| S3     | 100K  | 3   | R-004 |
| S4     | 4K7   | 2   | R-003 |
| S5     | 5K1   | 2   | R-019 |
| S6     | 750R  | 2   | R-020 |
| S7     | 12K   | 2   | R-007 |
| S8     | 10R   | 2   | R-001 |
| S9     | 20K   | 1   | R-006 |
| S10    | 2K2   | 1   | R-005 |

### Strip Feeders — Capacitors (0805)

| Feeder | Value | Qty | IPN   |
|--------|-------|-----|-------|
| S11    | 1nF   | 2   | C-004 |
| S12    | 18pF  | 2   | C-015 |
| S13    | 1.2nF | 1   | C-005 |

### Strip Feeders — ICs & Discrete

| Feeder | Part           | Qty | Package    | IPN   |
|--------|----------------|-----|------------|-------|
| S14    | 2N7002         | 3   | SOT-23     | Q-003 |
| S15    | FDS4435BZ      | 3   | SOIC-8     | Q-001 |
| S16    | 74AHCT1G125    | 1   | SOT-23-5   | U-008 |
| S17    | 74AHCT1G32     | 1   | SOT-23-5   | U-003 |
| S18    | USBLC6-2SC6    | 1   | SOT-23-6   | U-011 |
| S19    | DS3231MZ       | 1   | SOIC-8     | U-010 |
| S20    | AP64501SP-13   | 1   | SOIC-8-EP  | U-001 |
| S21    | NCP1117-3.3    | 1   | SOT-223    | U-002 |
| S22    | ASM1061        | 1   | QFN-48 7×7 | U-009 |

### Strip Feeders — Other

| Feeder | Part           | Qty | Package     | IPN   |
|--------|----------------|-----|-------------|-------|
| S23    | LED R          | 1   | 0805        | D-002 |
| S24    | LED G          | 1   | 0805        | D-001 |
| S25    | WS2812B        | 1   | PLCC4 5050  | D-007 |
| S26    | 25MHz crystal  | 1   | 2016        | Y-003 |
| S27    | 3A fuse        | 1   | 2512        | F-002 |
| S28    | 100µF tantalum | 1   | 7343-D      | C-006 |
| S29    | 3.3µH inductor | 1   | 6045        | L-001 |

## Hand-Place Components

These are placed after reflow or require manual alignment:

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

1. **Stencil** — Apply solder paste using JLCPCB stencil
2. **Machine place** — Run OpenPnP job (~93 placements)
3. **Inspect** — Check QFN-48 (U3) alignment under microscope
4. **Reflow** — Hot plate reflow profile (peak ~245°C for lead-free)
5. **Inspect** — Check for bridges on QFN-48, SOIC-8-EP, fine-pitch
6. **Hand-solder** — Place CM1, connectors (J1–J4), SW1, C26
7. **Clean** — IPA wash if using flux

## OpenPnP Package Map

All KiCad footprints are mapped to OpenPnP packages in
`~/.openpnp2/openpnp-package-map.csv`. The part-id convention is
`{openpnp_package}-{value}` (e.g. `C_0805-100n`, `R_0805-10K`).

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

## Drag Feeders

High-volume 0805 parts to set up as passive/drag feeders instead of strip feeders:

| Part | Qty | Feeder |
|------|-----|--------|
| C_0805-100n | 24 | Drag feeder |
| C_0805-10u | 15 | Drag feeder |
| R_0805-10K | 10 | Drag feeder |

## Feeder Map

After setting up feeders in OpenPnP, generate a visual SVG map:

1. Open OpenPnP scripting menu → `project/generate_map`
2. Enter project name: `Granit v0.3`
3. Save as: `pnp/feed_map.svg`

This uses the [psypnp](https://inductive-kickback.com/2020/10/psypnp-for-openpnp/)
`generate_map.py` script (`~/.openpnp2/scripts/project/generate_map.py`) which reads
live feeder positions and generates an SVG showing part names, locations, and feed
directions.

## Notes

- The QFN-48 ASM1061 (U3) is 0.5mm pitch — same as USB2514B successfully
  placed on pedalboard-hw. Bottom vision handles orientation.
- D1 (WS2812B), L1 (inductor), C38 (tantalum) are machine-placed —
  confirmed working from previous pedalboard builds.
- Fiducials (FID1–FID4) are used for board alignment.
