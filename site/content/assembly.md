---
title: Assembly
type: assembly
weight: 45
---

The PCB (92 × 99.5mm) supports three enclosure layouts using standard Hammond 1455 cases.

**Slim variant (2.5" SSD):** PCB and drive sit side-by-side with the SATA connector
direct-mating between them. Case: Hammond 1455L2201 (103 × 30.5 × 220mm).

**Compact variant (3.5" HDD):** PCB stacks on top of the HDD (sandwich layout),
connected with a short 22-pin SATA extension cable (right-angle end on HDD side).
Case: Hammond 1455T1601 (165 × 51.5 × 160mm).

**Wide variant (3.5" HDD):** PCB and drive sit side-by-side in a wider case.
Case: Hammond 1455T2601 (165 × 51.5 × 260mm).

## Pick and Place

Interactive [feeder map](/granit/latest/feeder-map.html) showing the OpenPnP feeder allocation for machine placement.

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

## Downloads

| File | Format | Description |
|------|--------|-------------|
| [end-plate.scad](https://github.com/laenzlinger/granit/raw/main/mechanical/end-plate.scad) | OpenSCAD | Parametric end plate source |
| [1455-case.scad](https://github.com/laenzlinger/granit/raw/main/mechanical/1455-case.scad) | OpenSCAD | Parametric Hammond 1455 case |
| [stencil holder (top)](../Assembly/granit-stencil_for_jig_top.stl) | STL | PCB holder for steel stencil alignment |

## Enclosure Variants

| Variant | Layout | Case | HDD | Dimensions (W×H×L) |
|---------|--------|------|-----|---------------------|
| Slim | side-by-side | Hammond 1455L2201 | 2.5" | 103 × 30.5 × 220mm |
| Compact | sandwich | Hammond 1455T1601 | 3.5" | 165 × 51.5 × 160mm |
| Wide | side-by-side | Hammond 1455T2601 | 3.5" | 165 × 51.5 × 260mm |
