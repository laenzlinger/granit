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
        "case_file": "hardware/3d-models/1455L2201.stp",
        "hdd_file": "mechanical/2.5inch_HDD.step",
        "hdd_dims": (100.2, 69.85, 9.5),
        "hdd_sata_center_y": 24.41,  # SFF-8201: 7.11 + 34.6/2
        "case_belly_y": -32.5,
        "output": "mechanical/assembly-slim.step",
        "end_plate": "mechanical/end-plate-slim.stl",
    },
    "wide": {
        "case_file": "hardware/3d-models/1455T2601.stp",
        "hdd_file": "mechanical/3.5inch_HDD_NAS.step",
        "hdd_dims": (147.0, 101.6, 26.1),
        "hdd_sata_center_y": 28.4,  # SFF-8301: 11.1 + 34.6/2
        "case_belly_y": -53.6,
        "output": "mechanical/assembly-wide.step",
        "end_plate": "mechanical/end-plate-wide.stl",
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
    belly_y = cfg["case_belly_y"]
    hdd_length, hdd_width, hdd_height = cfg["hdd_dims"]
    pcb_len = 92.0

    # Read case and find connector-side end plate
    case_shape = Part.read(cfg["case_file"])
    lid_vol = max(s.Volume for s in case_shape.Solids)
    flat_plates = [s for s in case_shape.Solids
                   if s.Volume < lid_vol and s.BoundBox.ZLength < 5
                   and s.BoundBox.XLength > 50 and s.BoundBox.YLength > 20]
    conn_plate = max(flat_plates, key=lambda s: s.BoundBox.ZMax) if flat_plates else None
    conn_zmax = conn_plate.BoundBox.ZMax if conn_plate else 110

    # Align PCB connector edge to end plate inside face
    pcb_z_conn = conn_plate.BoundBox.ZMin if conn_plate else 110
    pcb_z_sata = pcb_z_conn - pcb_len
    hdd_z_sata = pcb_z_sata - GAP
    hdd_z_far = hdd_z_sata - hdd_length

    # Case without connector-side plate+frame (replaced by cutout end plate)
    open_solids = [s for s in case_shape.Solids
                   if s.Volume < lid_vol
                   and not (s.BoundBox.ZMin > conn_zmax - 15
                           and s.BoundBox.XLength > 50
                           and s.BoundBox.YLength > 20)]
    case_obj = doc.addObject("Part::Feature", "Case")
    case_obj.Shape = Part.makeCompound(open_solids)

    # Lid offset to the side
    lid_solids = [s for s in case_shape.Solids if s.Volume >= lid_vol]
    lid_obj = doc.addObject("Part::Feature", "Lid")
    lid_obj.Shape = Part.makeCompound(lid_solids)
    lid_obj.Placement = FreeCAD.Placement(
        FreeCAD.Vector(case_shape.BoundBox.XLength + 20, 0, 0), FreeCAD.Rotation())

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

    # End plate (from OpenSCAD STL → Part solid)
    if conn_plate and cfg.get("end_plate"):
        ep_mesh = Mesh.Mesh(cfg["end_plate"])
        ep_shape = Part.Shape()
        ep_shape.makeShapeFromMesh(ep_mesh.Topology, 0.01)
        ep_solid = Part.makeSolid(ep_shape)
        ep_obj = doc.addObject("Part::Feature", "EndPlate")
        ep_obj.Shape = ep_solid
        cp = conn_plate.BoundBox
        ep = ep_solid.BoundBox
        ep_obj.Placement = FreeCAD.Placement(
            FreeCAD.Vector(cp.XMin - ep.XMin, cp.YMin - ep.YMin, cp.ZMin - ep.ZMin),
            FreeCAD.Rotation())

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
# PCB stacked on top of 3.5" HDD inside a 1455N1601 (103×53×160mm)

COMPACT_CFG = {
    "case_file": "mechanical/1455N1601.step",
    "hdd_file": "mechanical/3.5inch_HDD_NAS.step",
    "output": "mechanical/assembly-compact.step",
}

# Dimensions from issue #30 stack-up
CASE_INNER_W = 103.0 - 2 * 1.5   # 100mm
CASE_INNER_D = 53.0 - 2 * 1.5    # 50mm
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
    #   X = width (103mm), Y = depth/height (53mm), Z = length (160mm)
    # Wall = 1.5mm, internal depth ~50mm

    # Case — cut top half for visibility
    case_shape = Part.read(COMPACT_CFG["case_file"])
    case_bb = case_shape.BoundBox
    cut_box = Part.makeBox(
        case_bb.XLength + 10, 53.0 / 2, case_bb.ZLength + 10,
        FreeCAD.Vector(case_bb.XMin - 5, 0, case_bb.ZMin - 5))
    case_cut = case_shape.cut(cut_box)
    case_obj = doc.addObject("Part::Feature", "Case")
    case_obj.Shape = case_cut

    # Bottom of internal cavity (wall=1.5mm from outer bottom at -53/2)
    case_bottom = -53.0 / 2 + 1.5  # = -25.0

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
        -(hbb.ZMin + hbb.ZMax) / 2)
    hdd_obj = doc.addObject("Part::Feature", "HDD")
    hdd_obj.Shape = hdd_shape
    hdd_obj.Placement = FreeCAD.Placement(hdd_offset, hdd_rot)

    # ── PCB ──
    # Model: X=101(W), Y=99.5(L, negative -120..-20.5), Z=18.2(H, -3..15.1)
    # Target: X=101(case width), Y=18.2(case up), Z=99.5(case length)
    # Verified rotation: RX(90)
    pcb_rot = RX(90)
    pcb_shape = Part.read(PCB_FILE)
    pcb_placed = pcb_shape.transformed(
        FreeCAD.Placement(FreeCAD.Vector(0, 0, 0), pcb_rot).toMatrix())
    pbb = pcb_placed.BoundBox
    pcb_y_bottom = hdd_y_bottom + 26.1 + GAP_H
    pcb_offset = FreeCAD.Vector(
        -(pbb.XMin + pbb.XMax) / 2,
        pcb_y_bottom - pbb.YMin,
        -(pbb.ZMin + pbb.ZMax) / 2)

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
    internal = 53.0 - 2 * 1.5
    margin = internal - total
    sys.stdout.write(f"compact: stack={total:.1f}mm, internal={internal:.1f}mm, "
                     f"margin={margin:.1f}mm\n")
    sys.stdout.flush()

    doc.recompute()
    part_objects = [o for o in doc.Objects if hasattr(o, "Shape") and o.Shape.Faces]
    Import.export(part_objects, COMPACT_CFG["output"])
    FreeCAD.closeDocument(doc.Name)


build_compact()
