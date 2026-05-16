---
title: Assembly
type: assembly
weight: 45
---

The PCB (92 × 99.5mm) supports three enclosure layouts using standard Hammond 1455 cases.

## Enclosure Variants

| Variant | Layout | Case | HDD | Dimensions (W×H×L) |
|---------|--------|------|-----|---------------------|
| Slim | side-by-side | Hammond 1455L2201 | 2.5" | 103 × 30.5 × 220mm |
| Compact | sandwich | Hammond 1455T1601 | 3.5" | 165 × 51.5 × 160mm |
| Wide | side-by-side | Hammond 1455T2601 | 3.5" | 165 × 51.5 × 260mm |

**Slim variant (2.5" SSD):** PCB and drive sit side-by-side with the SATA connector
direct-mating between them.

**Compact variant (3.5" HDD):** PCB stacks on top of the HDD (sandwich layout),
connected with a short 22-pin SATA extension cable (right-angle end on HDD side).

**Wide variant (3.5" HDD):** PCB and drive sit side-by-side in a wider case.

## Compact Variant — SATA Cabling

The sandwich layout requires a short SATA cable between the PCB (on top) and the HDD (below).

**Parts needed:**
1. SATA 22-pin right-angle adapter (male-to-female, 90° bend) — mounts on the HDD
2. SATA 22-pin extension cable (~10cm, straight connectors)

**Assembly:**
- Push the HDD to the front of the case (SATA connector facing the end plate)
- Attach the right-angle adapter to the HDD's SATA port (bends the connector flat against the drive top, ~12mm height)
- Route the extension cable from the adapter up to the PCB's J4 connector
- The 13mm space behind the HDD (case is 160mm, drive is 147mm) provides room for the cable to fold

**Clearance budget:**
- HDD top to PCB bottom: ~21mm available
- Right-angle adapter height: ~12mm
- Cable bend: ~5mm
- Margin: ~4mm

## End Plate

The connector-side end plate has cutouts for:
barrel jack (12V DC), RJ45 (Ethernet), USB-C (OTG), tactile button, and RGB LED (light pipe).

Parametric design in OpenSCAD — generate for CNC machining or 3D printing:

```bash
# DXF for CNC laser/mill (variants: slim, compact, wide)
openscad -o end-plate-compact.dxf -D 'variant="compact"' -D 'mode="2d"' end-plate.scad

# STL for 3D printing
openscad -o end-plate-compact.stl -D 'variant="compact"' -D '$fn=64' end-plate.scad
```

## Pick and Place

Interactive [feeder map](/granit/latest/feeder-map.html) showing the OpenPnP feeder allocation for machine placement.

## Downloads

| File | Format | Description |
|------|--------|-------------|
| [end-plate.scad](https://github.com/laenzlinger/granit/raw/main/mechanical/end-plate.scad) | OpenSCAD | Parametric end plate source |
| [1455-case.scad](https://github.com/laenzlinger/granit/raw/main/mechanical/1455-case.scad) | OpenSCAD | Parametric Hammond 1455 case |
