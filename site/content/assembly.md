---
title: Assembly
weight: 45
---

The PCB (92 × 99.5mm) supports two enclosure layouts using standard Hammond 1455 cases.

{{% callout type="warning" %}}
**v0.3.0 slim variant:** The PCB does not fit the Hammond 1455L2201 slim case — some components are too close to the board edge and interfere with the internal walls. Use the 1455T2201BK as a workaround. See [issue #1](https://github.com/laenzlinger/granit/issues/1).
{{% /callout %}}

## Enclosure Variants

{{< tabs items="Slim (2.5\" SSD),Compact (3.5\" HDD)" >}}
{{< tab >}}
PCB and drive sit side-by-side with the SATA connector direct-mating between them.

| Property | Value |
|----------|-------|
| Case | Hammond 1455T2201BK |
| Internal | 165 × 220 × 51.5mm |
| Drive | 2.5" SSD/HDD |
| Connection | Direct SATA mate |
{{< /tab >}}
{{< tab >}}
PCB stacks on top of the HDD (sandwich layout), connected with a short 22-pin SATA extension cable (right-angle end on HDD side). See [issue #30](https://github.com/laenzlinger/granit/issues/30).

| Property | Value |
|----------|-------|
| Case | Hammond 1455N1601BK |
| Internal | 103 × 160 × 53mm |
| Drive | 3.5" HDD |
| Connection | 22-pin SATA extension cable |
{{< /tab >}}
{{< /tabs >}}

## 3D Models

{{< call-partial "assembly.html" >}}

## DF40C Connector Alignment Jig

The DF40C 100-pin connectors (0.4mm pitch) are the most challenging components to place.
A PCB-based alignment jig solves this — see [df40c-jig](https://github.com/laenzlinger/df40c-jig) project.

## Pick and Place

Interactive [feeder map](/granit/latest/feeder-map.html) showing the OpenPnP feeder allocation for machine placement.

## End Plate

The connector-side end plate has cutouts for:
barrel jack (12V DC), RJ45 (Ethernet), USB-C (OTG), tactile button, and RGB LED (light pipe).

{{< tabs items="CNC (DXF),3D Print (STL)" >}}
{{< tab >}}
```bash
openscad -o end-plate-slim.dxf -D 'variant="slim"' -D 'mode="2d"' end-plate.scad
```
{{< /tab >}}
{{< tab >}}
```bash
openscad -o end-plate-slim.stl -D 'variant="slim"' -D '$fn=64' end-plate.scad
```
{{< /tab >}}
{{< /tabs >}}

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
| [stencil holder (top)](../Assembly/granit-stencil_for_jig_top.stl) | STL | PCB holder for steel stencil alignment |
