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

VARIANTS = {
    "slim": {
        "case_file": "hardware/3d-models/1455L2201.stp",
        "hdd_file": "mechanical/2.5inch_HDD.step",
        "hdd_dims": (100.2, 69.85, 9.5),
        "case_belly_y": -32.5,
        "output": "mechanical/assembly-slim.step",
        "end_plate": "mechanical/end-plate-slim.stl",
    },
    "wide": {
        "case_file": "hardware/3d-models/1455T2601.stp",
        "hdd_file": "mechanical/3.5inch_HDD_NAS.step",
        "hdd_dims": (147.0, 101.6, 26.1),
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

    # HDD
    hdd_rot = rot(RZ(90), RX(-90), RY(180))
    place(doc, cfg["hdd_file"], "HDD", FreeCAD.Placement(
        FreeCAD.Vector(-hdd_width / 2, belly_y + STANDOFF + 4, hdd_z_sata - hdd_length),
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
