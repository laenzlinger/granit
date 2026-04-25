---
title: Assembly
type: assembly
weight: 45
---

The PCB (92 × 99.5mm) fits both Hammond 1455 enclosure variants. PCB and HDD
sit side-by-side with the SATA connector direct-mating between them. The lid
(U-channel) is shown offset to reveal the internals.

> ⚠️ **v0.3.0 slim variant:** The PCB does not fit the Hammond 1455L2201 slim case — some components are too close to the board edge and interfere with the internal walls. Use the wide case (1455T2601) as a workaround. See [issue #1](https://github.com/laenzlinger/granit/issues/1).

## End Plate

The connector-side end plate has cutouts for:
barrel jack (12V DC), RJ45 (Ethernet), USB-C (OTG), tactile button, and RGB LED (light pipe).

Parametric design in OpenSCAD — generate for CNC machining or 3D printing:

```bash
# DXF for CNC laser/mill
openscad -o end-plate-slim.dxf -D 'variant="slim"' -D 'mode="2d"' end-plate.scad

# STL for 3D printing
openscad -o end-plate-slim.stl -D 'variant="slim"' -D '$fn=64' end-plate.scad
```

## Downloads

| File | Format | Description |
|------|--------|-------------|
| [end-plate-slim.dxf](https://github.com/laenzlinger/granit/raw/main/mechanical/end-plate-slim.dxf) | DXF | Slim end plate — CNC cutting |
| [end-plate-wide.dxf](https://github.com/laenzlinger/granit/raw/main/mechanical/end-plate-wide.dxf) | DXF | Wide end plate — CNC cutting |
| [end-plate-slim.stl](https://github.com/laenzlinger/granit/raw/main/mechanical/end-plate-slim.stl) | STL | Slim end plate — 3D printing |
| [end-plate-wide.stl](https://github.com/laenzlinger/granit/raw/main/mechanical/end-plate-wide.stl) | STL | Wide end plate — 3D printing |
| [assembly-slim.step](https://github.com/laenzlinger/granit/raw/main/mechanical/assembly-slim.step) | STEP | Full slim assembly |
| [assembly-wide.step](https://github.com/laenzlinger/granit/raw/main/mechanical/assembly-wide.step) | STEP | Full wide assembly |
| [end-plate.scad](https://github.com/laenzlinger/granit/raw/main/mechanical/end-plate.scad) | OpenSCAD | Parametric end plate source |
| [stencil jig (top)](Assembly/granit-stencil_3d_top.stl) | STL | 3D-printable solder paste stencil jig |

## Enclosure Variants

| Variant | Case | HDD | Internal dimensions |
|---------|------|-----|---------------------|
| Slim | Hammond 1455L2201 | 2.5" | 103 × 220 × 30.5mm |
| Wide | Hammond 1455T2601 | 3.5" | 165 × 252 × 51.5mm |
