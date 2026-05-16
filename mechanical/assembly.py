#!/usr/bin/env python3
"""Granit mechanical assembly — FreeCAD script.

Run with: freecadcmd mechanical/assembly.py

Builds STEP assembly files for all enclosure variants.
Case parts generated from parametric OpenSCAD models.
"""

import sys
import FreeCAD
import Import
import Mesh
import Part

PCB_FILE = "mechanical/granit-pcb.step"

RX = lambda a: FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), a)
RY = lambda a: FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), a)
RZ = lambda a: FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), a)


def rot(*steps):
    r = steps[0]
    for s in steps[1:]:
        r = s.multiply(r)
    return r


VARIANTS = {
    "slim": {
        "case_file": "mechanical/out/1455L2201-body.stl",
        "lid_file": "mechanical/out/1455L2201-lid.stl",
        "endplate_file": "mechanical/out/1455L2201-end_plate.stl",
        "endplate_cutout_file": "mechanical/out/end-plate-slim.stl",
        "hdd_file": "mechanical/out/2.5inch_HDD.step",
        "case_h": 30.5,
        "case_length": 220.0,
        "layout": "side_by_side",
        "hdd_dims": (100.2, 69.85, 9.5),
        "hdd_sata_center_y": 24.41,
        "output": "mechanical/out/assembly-slim.step",
    },
    "wide": {
        "case_file": "mechanical/out/1455T2601-body.stl",
        "lid_file": "mechanical/out/1455T2601-lid.stl",
        "endplate_file": "mechanical/out/1455T2601-end_plate.stl",
        "endplate_cutout_file": "mechanical/out/end-plate-wide.stl",
        "hdd_file": "mechanical/out/3.5inch_HDD_NAS.step",
        "case_h": 51.5,
        "case_length": 260.0,
        "layout": "side_by_side",
        "hdd_dims": (147.0, 101.6, 26.1),
        "hdd_sata_center_y": 28.4,
        "output": "mechanical/out/assembly-wide.step",
    },
    "compact": {
        "case_file": "mechanical/out/1455T1601-body.stl",
        "lid_file": "mechanical/out/1455T1601-lid.stl",
        "endplate_file": "mechanical/out/1455T1601-end_plate.stl",
        "endplate_cutout_file": "mechanical/out/end-plate-compact.stl",
        "hdd_file": "mechanical/out/3.5inch_HDD_NAS.step",
        "case_h": 51.5,
        "case_length": 160.0,
        "layout": "sandwich",
        "hdd_dims": (147.0, 101.6, 26.1),
        "hdd_sata_center_y": 28.4,
        "output": "mechanical/out/assembly-compact.step",
    },
}


def load_stl_solid(filepath):
    """Load an STL file and return a Part solid."""
    mesh = Mesh.Mesh(filepath)
    shape = Part.Shape()
    shape.makeShapeFromMesh(mesh.Topology, 0.01)
    return Part.makeSolid(shape)


def split_pcb(pcb_shape):
    """Split PCB STEP into board, ICs, parts, connectors by volume."""
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
    return [("PCB_Board", board), ("PCB_ICs", ics),
            ("PCB_Parts", parts), ("PCB_Conn", conns)]


def build_variant(name, cfg):
    doc = FreeCAD.newDocument(f"Granit_{name}")
    case_h = cfg["case_h"]
    case_length = cfg["case_length"]
    hdd_length, hdd_width, hdd_height = cfg["hdd_dims"]
    layout = cfg["layout"]

    # ── Case body (offset to side) ──
    case_solid = load_stl_solid(cfg["case_file"])
    case_obj = doc.addObject("Part::Feature", "Case")
    case_obj.Shape = case_solid
    case_obj.Placement = FreeCAD.Placement(
        FreeCAD.Vector(case_solid.BoundBox.XLength + 20, 0, 0),
        FreeCAD.Rotation())

    # ── Belly plate (in position) ──
    lid_solid = load_stl_solid(cfg["lid_file"])
    lid_obj = doc.addObject("Part::Feature", "BellyPlate")
    lid_obj.Shape = lid_solid

    # ── End plates ──
    # Back (blank)
    ep_solid = load_stl_solid(cfg["endplate_file"])
    ep_obj = doc.addObject("Part::Feature", "EndPlate_Back")
    ep_obj.Shape = ep_solid
    ep_obj.Placement = FreeCAD.Placement(
        FreeCAD.Vector(0, 0, -(case_length/2 + 0.75)),
        FreeCAD.Rotation())
    # Front (cutout)
    fp_solid = load_stl_solid(cfg["endplate_cutout_file"])
    fp_bb = fp_solid.BoundBox
    fp_obj = doc.addObject("Part::Feature", "EndPlate_Front")
    fp_obj.Shape = fp_solid
    fp_obj.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-fp_bb.XLength/2, -fp_bb.YLength/2, case_length/2 + 0.75),
        FreeCAD.Rotation())

    # ── PCB + HDD placement (layout-dependent) ──
    pcb_shape = Part.read(PCB_FILE)
    belly_y = -case_h / 2 + 4.22  # top of belly groove

    if layout == "sandwich":
        # HDD on bottom, PCB stacked above
        case_bottom = -case_h / 2 + 1.5
        hdd_rail_h = 1.0
        gap_h = 3.0

        # HDD
        hdd_rot = RZ(90).multiply(RY(90))
        hdd_placed = pcb_shape.transformed(
            FreeCAD.Placement(FreeCAD.Vector(0, 0, 0), hdd_rot).toMatrix())
        hdd_shape = Part.read(cfg["hdd_file"])
        hdd_placed = hdd_shape.transformed(
            FreeCAD.Placement(FreeCAD.Vector(0, 0, 0), hdd_rot).toMatrix())
        hbb = hdd_placed.BoundBox
        hdd_y_bottom = case_bottom + hdd_rail_h
        hdd_offset = FreeCAD.Vector(
            -(hbb.XMin + hbb.XMax) / 2,
            hdd_y_bottom - hbb.YMin,
            case_length/2 - hbb.ZMax)
        hdd_obj = doc.addObject("Part::Feature", "HDD")
        hdd_obj.Shape = hdd_shape
        hdd_obj.Placement = FreeCAD.Placement(hdd_offset, hdd_rot)

        # PCB (upside down, connectors face end plate)
        pcb_rot = RY(-90).multiply(RX(90))
        pcb_placed = pcb_shape.transformed(
            FreeCAD.Placement(FreeCAD.Vector(0, 0, 0), pcb_rot).toMatrix())
        pbb = pcb_placed.BoundBox
        pcb_y_bottom = hdd_y_bottom + hdd_height + gap_h - 2.5
        pcb_offset = FreeCAD.Vector(
            -(pbb.XMin + pbb.XMax) / 2,
            pcb_y_bottom - pbb.YMin,
            case_length/2 - pbb.ZMax)
        pcb_pl = FreeCAD.Placement(pcb_offset, pcb_rot)

    else:  # side_by_side
        standoff = 5.0
        gap = 2.0
        pcb_len = 92.0
        pcb_z_conn = case_length / 2
        pcb_z_sata = pcb_z_conn - pcb_len

        # PCB
        pcb_rot = rot(RZ(90), RX(-90), RY(180))
        pcb_pl = FreeCAD.Placement(
            FreeCAD.Vector(70.3, belly_y + standoff - 4.5, pcb_z_sata - 21.5),
            pcb_rot)

        # HDD
        sata_y = cfg["hdd_sata_center_y"]
        hdd_rot = rot(RZ(90), RX(-90), RY(180))
        hdd_shape = Part.read(cfg["hdd_file"])
        hdd_obj = doc.addObject("Part::Feature", "HDD")
        hdd_obj.Shape = hdd_shape
        hdd_obj.Placement = FreeCAD.Placement(
            FreeCAD.Vector(-sata_y, belly_y + standoff - 4,
                           pcb_z_sata - gap - hdd_length),
            hdd_rot)

    # Place PCB parts
    for label, solids in split_pcb(pcb_shape):
        if solids:
            obj = doc.addObject("Part::Feature", label)
            obj.Shape = Part.makeCompound(solids)
            obj.Placement = pcb_pl

    # ── Export ──
    doc.recompute()
    part_objects = [o for o in doc.Objects if hasattr(o, "Shape") and o.Shape.Faces]
    Import.export(part_objects, cfg["output"])
    sys.stdout.write(f"{name}: done\n")
    sys.stdout.flush()
    FreeCAD.closeDocument(doc.Name)


for name, cfg in VARIANTS.items():
    build_variant(name, cfg)
