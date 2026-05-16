#!/usr/bin/env python3
"""Granit mechanical assembly — FreeCAD script.

Run with: freecadcmd mechanical/assembly.py

Builds STEP assembly files for both slim and wide enclosure variants.
End plate with connector cutouts is imported from OpenSCAD STL.
"""

import sys
import FreeCAD
import Import
import Mesh
import Part

STANDOFF = 5.0
GAP = 2.0

# SATA connector center position on the HDD, measured from the drive edge.
# The connector is approximately centered on the drive width.
# Verified by physical measurement (2.5" HDD: ~35mm from edge = centered).
VARIANTS = {
    "slim": {
        "case_file": "mechanical/out/1455L2201-body.stl",
        "lid_file": "mechanical/out/1455L2201-lid.stl",
        "endplate_file": "mechanical/out/1455L2201-end_plate.stl",
        "endplate_cutout_file": "mechanical/out/end-plate-slim.stl",
        "hdd_file": "mechanical/out/2.5inch_HDD.step",
        "hdd_dims": (100.2, 69.85, 9.5),
        "hdd_sata_center_y": 24.41,  # SFF-8201: 7.11 + 34.6/2
        "case_belly_y": -32.5,
        "case_h": 30.5,
        "case_length": 220.0,
        "output": "mechanical/out/assembly-slim.step",
    },
    "wide": {
        "case_file": "mechanical/out/1455T2601-body.stl",
        "lid_file": "mechanical/out/1455T2601-lid.stl",
        "endplate_file": "mechanical/out/1455T2601-end_plate.stl",
        "endplate_cutout_file": "mechanical/out/end-plate-wide.stl",
        "hdd_file": "mechanical/out/3.5inch_HDD_NAS.step",
        "hdd_dims": (147.0, 101.6, 26.1),
        "hdd_sata_center_y": 28.4,  # SFF-8301: 11.1 + 34.6/2
        "case_belly_y": -53.6,
        "case_h": 51.5,
        "case_length": 260.0,
        "output": "mechanical/out/assembly-wide.step",
    },
}

PCB_FILE = "mechanical/granit-pcb.step"


def place(doc, filepath, label, placement):
    shape = Part.read(filepath)
    obj = doc.addObject("Part::Feature", label)
    obj.Shape = shape
    obj.Placement = placement
    return obj


def rot(*steps):
    r = steps[0]
    for s in steps[1:]:
        r = s.multiply(r)
    return r


RX = lambda a: FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), a)
RY = lambda a: FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), a)
RZ = lambda a: FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), a)


def build_variant(name, cfg):
    doc = FreeCAD.newDocument(f"Granit_{name}")
    hdd_length, hdd_width, hdd_height = cfg["hdd_dims"]
    pcb_len = 92.0
    case_length = cfg["case_length"]
    case_h = cfg["case_h"]

    # Case coordinate system (from OpenSCAD, centered):
    # Bottom of internal cavity
    belly_y = -case_h / 2 + 4.22  # top of belly groove = bottom of cavity

    # Case body from our parametric STL — offset to the side
    case_mesh = Mesh.Mesh(cfg["case_file"])
    case_shape = Part.Shape()
    case_shape.makeShapeFromMesh(case_mesh.Topology, 0.01)
    case_solid = Part.makeSolid(case_shape)
    case_bb = case_solid.BoundBox
    case_obj = doc.addObject("Part::Feature", "Case")
    case_obj.Shape = case_solid
    case_obj.Placement = FreeCAD.Placement(
        FreeCAD.Vector(case_bb.XLength + 20, 0, 0), FreeCAD.Rotation())

    # PCB connector edge flush with case end (+Z)
    pcb_z_conn = case_length / 2
    pcb_z_sata = pcb_z_conn - pcb_len
    hdd_z_sata = pcb_z_sata - GAP
    hdd_z_far = hdd_z_sata - hdd_length

    # PCB (split into categories for visual distinction)
    pcb_rot = rot(RZ(90), RX(-90), RY(180))
    pcb_pl = FreeCAD.Placement(
        FreeCAD.Vector(70.3, belly_y + STANDOFF + 0.5, pcb_z_sata - 21.5), pcb_rot)

    pcb_shape = Part.read(PCB_FILE)
    board, ics, parts, conns = [], [], [], []
    for s in pcb_shape.Solids:
        bb = s.BoundBox
        vol = bb.XLength * bb.YLength * bb.ZLength
        if vol > 10000:
            board.append(s)
        elif bb.ZLength > 8 or bb.XLength > 15 or bb.YLength > 15:
            conns.append(s)
        elif vol > 50:
            ics.append(s)
        else:
            parts.append(s)

    for label, solids in [("PCB_Board", board), ("PCB_ICs", ics),
                          ("PCB_Parts", parts), ("PCB_Conn", conns)]:
        if solids:
            obj = doc.addObject("Part::Feature", label)
            obj.Shape = Part.makeCompound(solids)
            obj.Placement = pcb_pl

    # HDD — align SATA connector with PCB connector (J4), not drive center.
    # The connector is offset from the drive center (see issue #27).
    sata_y = cfg["hdd_sata_center_y"]
    hdd_rot = rot(RZ(90), RX(-90), RY(180))
    place(doc, cfg["hdd_file"], "HDD", FreeCAD.Placement(
        FreeCAD.Vector(-sata_y, belly_y + STANDOFF + 4, hdd_z_sata - hdd_length),
        hdd_rot))

    # End plates — cutout plate at front (connector side), blank at back
    if cfg.get("endplate_file"):
        # Back plate (blank)
        ep_mesh = Mesh.Mesh(cfg["endplate_file"])
        ep_shape = Part.Shape()
        ep_shape.makeShapeFromMesh(ep_mesh.Topology, 0.01)
        ep_solid = Part.makeSolid(ep_shape)
        ep_obj = doc.addObject("Part::Feature", "EndPlate_Back")
        ep_obj.Shape = ep_solid
        ep_obj.Placement = FreeCAD.Placement(
            FreeCAD.Vector(0, 0, -(case_length/2 + 0.75)),
            FreeCAD.Rotation())

        # Front plate (with connector cutouts — origin at corner, needs centering)
        front_file = cfg.get("endplate_cutout_file", cfg["endplate_file"])
        fp_mesh = Mesh.Mesh(front_file)
        fp_shape = Part.Shape()
        fp_shape.makeShapeFromMesh(fp_mesh.Topology, 0.01)
        fp_solid = Part.makeSolid(fp_shape)
        fp_bb = fp_solid.BoundBox
        fp_obj = doc.addObject("Part::Feature", "EndPlate_Front")
        fp_obj.Shape = fp_solid
        fp_obj.Placement = FreeCAD.Placement(
            FreeCAD.Vector(-fp_bb.XLength/2, -fp_bb.YLength/2, case_length/2 + 0.75),
            FreeCAD.Rotation())

    # Belly plate (from OpenSCAD STL) — in assembly position
    if cfg.get("lid_file"):
        lid_mesh = Mesh.Mesh(cfg["lid_file"])
        lid_shape = Part.Shape()
        lid_shape.makeShapeFromMesh(lid_mesh.Topology, 0.01)
        lid_solid = Part.makeSolid(lid_shape)
        lid_obj = doc.addObject("Part::Feature", "BellyPlate")
        lid_obj.Shape = lid_solid

    doc.recompute()
    part_objects = [o for o in doc.Objects if hasattr(o, "Shape") and o.Shape.Faces]
    Import.export(part_objects, cfg["output"])

    sys.stdout.write(f"{name}: PCB Z={pcb_z_sata:.1f}..{pcb_z_conn:.1f}, "
                     f"HDD Z={hdd_z_far:.1f}..{hdd_z_sata:.1f}\n")
    sys.stdout.flush()
    FreeCAD.closeDocument(doc.Name)


for name, cfg in VARIANTS.items():
    build_variant(name, cfg)


# ── Compact (sandwich) variant ──────────────────────────────────────────────
# PCB stacked on top of 3.5" HDD inside a 1455T1601 (165×51.5×160mm)

COMPACT_CFG = {
    "case_file": "mechanical/out/1455T1601-body.stl",
    "lid_file": "mechanical/out/1455T1601-lid.stl",
    "endplate_file": "mechanical/out/1455T1601-end_plate.stl",
    "hdd_file": "mechanical/out/3.5inch_HDD_NAS.step",
    "output": "mechanical/out/assembly-compact.step",
}

# Dimensions from 1455T profile
CASE_W = 165.0
CASE_H = 51.5
CASE_INNER_W = CASE_W - 2 * 1.5   # 162mm
CASE_INNER_D = CASE_H - 2 * 1.5   # 48.5mm
CASE_LENGTH = 160.0
HDD_DIMS = (147.0, 101.6, 26.1)  # L x W x H
PCB_DIMS = (92.0, 99.5, 1.6)     # L x W x H

# Stack-up from bottom of case interior
HDD_RAIL_H = 1.0       # feet/rails
HDD_H = 26.1
GAP_H = 3.0            # clearance between HDD top and PCB bottom
PCB_H = 1.6
CM4_H = 8.0            # tallest component on top


def build_compact():
    doc = FreeCAD.newDocument("Granit_compact")

    # Case coordinate system (from OpenSCAD, centered at origin):
    #   X = width (165mm), Y = depth/height (51.5mm), Z = length (160mm)
    # Wall = 1.5mm, internal: 162 x 48.5 x 160mm

    # Case body only — offset to the side for visibility
    case_mesh = Mesh.Mesh(COMPACT_CFG["case_file"])
    case_shape = Part.Shape()
    case_shape.makeShapeFromMesh(case_mesh.Topology, 0.01)
    case_solid = Part.makeSolid(case_shape)
    case_bb = case_solid.BoundBox
    case_obj = doc.addObject("Part::Feature", "Case")
    case_obj.Shape = case_solid
    case_obj.Placement = FreeCAD.Placement(
        FreeCAD.Vector(case_bb.XLength + 20, 0, 0), FreeCAD.Rotation())

    # Belly plate — in assembly position (bottom)
    belly_mesh = Mesh.Mesh(COMPACT_CFG["lid_file"])
    belly_shape = Part.Shape()
    belly_shape.makeShapeFromMesh(belly_mesh.Topology, 0.01)
    belly_solid = Part.makeSolid(belly_shape)
    belly_obj = doc.addObject("Part::Feature", "BellyPlate")
    belly_obj.Shape = belly_solid

    # End plates — at both ends
    ep_mesh = Mesh.Mesh(COMPACT_CFG["endplate_file"])
    ep_shape = Part.Shape()
    ep_shape.makeShapeFromMesh(ep_mesh.Topology, 0.01)
    ep_solid = Part.makeSolid(ep_shape)
    for z_sign, label in [(1, "EndPlate_Front"), (-1, "EndPlate_Back")]:
        ep_obj = doc.addObject("Part::Feature", label)
        ep_obj.Shape = ep_solid
        ep_obj.Placement = FreeCAD.Placement(
            FreeCAD.Vector(0, 0, z_sign * (CASE_LENGTH/2 + 0.75)),
            FreeCAD.Rotation())

    # Bottom of internal cavity (wall=1.5mm from outer bottom at -H/2)
    case_bottom = -CASE_H / 2 + 1.5

    # ── HDD ──
    # Model: X=147(L), Y=101.6(W), Z=26.1(H), origin at corner (0,0,0)
    # Target: X=101.6(case width), Y=26.1(case up), Z=147(case length)
    # Verified rotation: RZ(90).multiply(RY(90))
    hdd_rot = RZ(90).multiply(RY(90))
    hdd_shape = Part.read(COMPACT_CFG["hdd_file"])
    hdd_placed = hdd_shape.transformed(
        FreeCAD.Placement(FreeCAD.Vector(0, 0, 0), hdd_rot).toMatrix())
    hbb = hdd_placed.BoundBox
    hdd_y_bottom = case_bottom + HDD_RAIL_H
    hdd_offset = FreeCAD.Vector(
        -(hbb.XMin + hbb.XMax) / 2,
        hdd_y_bottom - hbb.YMin,
        CASE_LENGTH/2 - hbb.ZMax)  # flush with front end plate
    hdd_obj = doc.addObject("Part::Feature", "HDD")
    hdd_obj.Shape = hdd_shape
    hdd_obj.Placement = FreeCAD.Placement(hdd_offset, hdd_rot)

    # ── PCB ──
    # Model: X=101(W), Y=99.5(L, negative -120..-20.5), Z=18.2(H, -3..15.1)
    # Target: X=101(case width), Y=18.2(case up), Z=99.5(case length)
    # RY(-90) rotates so USB/network connectors face end plate, RX(90) lays flat
    pcb_rot = RY(-90).multiply(RX(90))
    pcb_shape = Part.read(PCB_FILE)
    pcb_placed = pcb_shape.transformed(
        FreeCAD.Placement(FreeCAD.Vector(0, 0, 0), pcb_rot).toMatrix())
    pbb = pcb_placed.BoundBox
    pcb_y_bottom = hdd_y_bottom + 26.1 + GAP_H
    pcb_offset = FreeCAD.Vector(
        -(pbb.XMin + pbb.XMax) / 2,
        pcb_y_bottom - pbb.YMin,
        CASE_LENGTH/2 - pbb.ZMax)  # connector edge flush with front end plate

    board, ics, parts, conns = [], [], [], []
    for s in pcb_shape.Solids:
        bb = s.BoundBox
        vol = bb.XLength * bb.YLength * bb.ZLength
        if vol > 10000:
            board.append(s)
        elif bb.ZLength > 8 or bb.XLength > 15 or bb.YLength > 15:
            conns.append(s)
        elif vol > 50:
            ics.append(s)
        else:
            parts.append(s)

    pcb_pl = FreeCAD.Placement(pcb_offset, pcb_rot)
    for label, solids in [("PCB_Board", board), ("PCB_ICs", ics),
                          ("PCB_Parts", parts), ("PCB_Conn", conns)]:
        if solids:
            obj = doc.addObject("Part::Feature", label)
            obj.Shape = Part.makeCompound(solids)
            obj.Placement = pcb_pl

    # Stack-up verification
    total = HDD_RAIL_H + HDD_H + GAP_H + PCB_H + CM4_H
    margin = CASE_INNER_D - total
    sys.stdout.write(f"compact: stack={total:.1f}mm, internal={CASE_INNER_D:.1f}mm, "
                     f"margin={margin:.1f}mm\n")
    sys.stdout.flush()

    doc.recompute()
    part_objects = [o for o in doc.Objects if hasattr(o, "Shape") and o.Shape.Faces]
    Import.export(part_objects, COMPACT_CFG["output"])
    FreeCAD.closeDocument(doc.Name)


build_compact()
