#!/usr/bin/env python3
"""Granit mechanical assembly — FreeCAD script.

Run with: freecadcmd mechanical/assembly.py

Case coordinate system: X=width, Y=height (belly at -Y), Z=length (centered)
"""

import sys
import xml.etree.ElementTree as ET
import zipfile
import io
import FreeCAD
import Import
import Mesh
import Part

STANDOFF = 5.0
GAP = 2.0

# Colors per object label
COLORS = {
    "Case":       "#C8C8C8",
    "Lid":        "#C8C8C8",
    "EndPlate":   "#C8C8C8",
    "PCB_Board":  "#2E7D32",
    "PCB_ICs":    "#1A1A1A",
    "PCB_Parts":  "#3E2723",
    "PCB_Conn":   "#787878",
    "HDD":        "#505050",
}

VARIANTS = {
    "slim": {
        "case_file": "hardware/3d-models/1455L2201.stp",
        "hdd_file": "mechanical/2.5inch_HDD.step",
        "hdd_dims": (100.2, 69.85, 9.5),
        "case_belly_y": -32.5,
        "output": "mechanical/assembly-slim.3mf",
        "end_plate": "mechanical/end-plate-slim.stl",
    },
    "wide": {
        "case_file": "hardware/3d-models/1455T2601.stp",
        "hdd_file": "mechanical/3.5inch_HDD_NAS.step",
        "hdd_dims": (147.0, 101.6, 26.1),
        "case_belly_y": -53.6,
        "output": "mechanical/assembly-wide.3mf",
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
    """Chain rotations left-to-right (first applied first)."""
    r = steps[0]
    for s in steps[1:]:
        r = s.multiply(r)
    return r


RX = lambda a: FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), a)
RY = lambda a: FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), a)
RZ = lambda a: FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), a)


def inject_colors_3mf(path, labels):
    """Post-process a 3MF file to add per-object colors."""
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    mat_ns = "http://schemas.microsoft.com/3dmanufacturing/material/2015/02"

    with zipfile.ZipFile(path, "r") as zin:
        model_xml = zin.read("3D/3dmodel.model")
        other_files = {n: zin.read(n) for n in zin.namelist() if n != "3D/3dmodel.model"}

    ET.register_namespace("", ns)
    ET.register_namespace("m", mat_ns)
    root = ET.fromstring(model_xml)

    # Round vertex coordinates to reduce XML size
    for v in root.iter(f"{{{ns}}}vertex"):
        for attr in ("x", "y", "z"):
            v.set(attr, f"{float(v.get(attr)):.2f}")

    resources = root.find(f"{{{ns}}}resources")

    # Add basematerials
    basemats = ET.SubElement(resources, f"{{{mat_ns}}}basematerials")
    basemats.set("id", "100")
    for i, label in enumerate(labels):
        color = COLORS.get(label, "#808080")
        base = ET.SubElement(basemats, f"{{{mat_ns}}}base")
        base.set("name", label)
        base.set("displaycolor", color)

    # Assign material to each object
    objects = resources.findall(f"{{{ns}}}object")
    for i, obj in enumerate(objects):
        if i < len(labels):
            obj.set("pid", "100")
            obj.set("pindex", str(i))

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        zout.writestr("3D/3dmodel.model", ET.tostring(root, xml_declaration=True, encoding="unicode"))
        for name, data in other_files.items():
            zout.writestr(name, data)

    with open(path, "wb") as f:
        f.write(buf.getvalue())


def build_variant(name, cfg):
    doc = FreeCAD.newDocument(f"Granit_{name}")
    belly_y = cfg["case_belly_y"]
    hdd_length, hdd_width, hdd_height = cfg["hdd_dims"]

    pcb_len = 92.0
    total_z = hdd_length + GAP + pcb_len
    hdd_z_far = -total_z / 2
    hdd_z_sata = hdd_z_far + hdd_length
    pcb_z_sata = hdd_z_sata + GAP
    pcb_z_conn = pcb_z_sata + pcb_len

    # Place case without lid — skip the U-channel (largest solid) to show internals
    # Also remove the connector-side flat end plate (replaced by cutout version)
    case_shape = Part.read(cfg["case_file"])
    lid_vol = max(s.Volume for s in case_shape.Solids)

    # Find the connector-side flat end plate: thin in Z, at max Z position
    flat_plates = [s for s in case_shape.Solids
                   if s.Volume < lid_vol and s.BoundBox.ZLength < 5
                   and s.BoundBox.XLength > 50 and s.BoundBox.YLength > 20]
    conn_plate = max(flat_plates, key=lambda s: s.BoundBox.ZMax) if flat_plates else None
    conn_plate_id = id(conn_plate) if conn_plate else None

    open_solids = [s for s in case_shape.Solids
                   if s.Volume < lid_vol and id(s) != conn_plate_id]
    lid_solids = [s for s in case_shape.Solids if s.Volume >= lid_vol]
    case_obj = doc.addObject("Part::Feature", "Case")
    case_obj.Shape = Part.makeCompound(open_solids)

    # Build cutout end plate using Part primitives (clean B-rep for STEP)
    if conn_plate:
        cp_bb = conn_plate.BoundBox
        pw, ph, pt = cp_bb.XLength, cp_bb.YLength, cp_bb.ZLength
        cr = 3.94  # corner radius from Hammond STEP

        # Rounded rectangle plate
        plate_wire = Part.Wire([
            Part.makeLine((-pw/2+cr, -ph/2, 0), (pw/2-cr, -ph/2, 0)),
            Part.Arc(FreeCAD.Vector(pw/2-cr,-ph/2,0), FreeCAD.Vector(pw/2,-ph/2+cr*0.293,0), FreeCAD.Vector(pw/2,-ph/2+cr,0)).toShape(),
            Part.makeLine((pw/2, -ph/2+cr, 0), (pw/2, ph/2-cr, 0)),
            Part.Arc(FreeCAD.Vector(pw/2,ph/2-cr,0), FreeCAD.Vector(pw/2-cr*0.293,ph/2,0), FreeCAD.Vector(pw/2-cr,ph/2,0)).toShape(),
            Part.makeLine((pw/2-cr, ph/2, 0), (-pw/2+cr, ph/2, 0)),
            Part.Arc(FreeCAD.Vector(-pw/2+cr,ph/2,0), FreeCAD.Vector(-pw/2,ph/2-cr*0.293,0), FreeCAD.Vector(-pw/2,ph/2-cr,0)).toShape(),
            Part.makeLine((-pw/2, ph/2-cr, 0), (-pw/2, -ph/2+cr, 0)),
            Part.Arc(FreeCAD.Vector(-pw/2,-ph/2+cr,0), FreeCAD.Vector(-pw/2+cr*0.293,-ph/2,0), FreeCAD.Vector(-pw/2+cr,-ph/2,0)).toShape(),
        ])
        plate_face = Part.Face(plate_wire)
        plate_solid = plate_face.extrude(FreeCAD.Vector(0, 0, pt))

        # PCB surface Y relative to plate center
        board_len = 99.5
        pcb_surface = cp_bb.YMin + 5.0 + 1.6  # belly + standoff + PCB thickness
        clr = 0.5

        def pcb_y_to_x(ky):
            return (board_len - (ky - 20.5)) - board_len/2

        # Rectangular cutouts (bottom-aligned to PCB surface)
        for ky, w, h in [(103, 11.0, 11.0), (70, 16.2, 13.1), (34, 9.0, 3.2)]:
            cx = pcb_y_to_x(ky)
            box = Part.makeBox(w+clr, h+clr, pt+2,
                FreeCAD.Vector(cx-(w+clr)/2, pcb_surface, -1))
            plate_solid = plate_solid.cut(box)

        # Round cutouts (button and LED at same height)
        btn_led_y = pcb_surface + 1.5
        for ky in [56, 47]:
            cx = pcb_y_to_x(ky)
            cyl = Part.makeCylinder((3.0+clr)/2, pt+2,
                FreeCAD.Vector(cx, btn_led_y, -1))
            plate_solid = plate_solid.cut(cyl)

        # Screw holes with countersink (4mm inset, M3)
        for sx in [-pw/2+4, pw/2-4]:
            for sy in [-ph/2+4, ph/2-4]:
                hole = Part.makeCylinder(3.5/2, pt+2, FreeCAD.Vector(sx, sy, -1))
                cs = Part.makeCone(3.5/2, 6.5/2, (6.5-3.5)/2,
                    FreeCAD.Vector(sx, sy, pt-(6.5-3.5)/2))
                plate_solid = plate_solid.cut(hole).cut(cs)

        ep_obj = doc.addObject("Part::Feature", "EndPlate")
        ep_obj.Shape = plate_solid
        ep_obj.Placement = FreeCAD.Placement(
            FreeCAD.Vector(
                cp_bb.XMin + pw/2,
                cp_bb.YMin + ph/2,
                cp_bb.ZMin,
            ), FreeCAD.Rotation())

    # Place lid/frame offset to the side
    lid_obj = doc.addObject("Part::Feature", "Lid")
    lid_obj.Shape = Part.makeCompound(lid_solids)
    lid_bb = case_shape.BoundBox
    lid_obj.Placement = FreeCAD.Placement(
        FreeCAD.Vector(lid_bb.XLength + 20, 0, 0), FreeCAD.Rotation())

    pcb_rot = rot(RZ(90), RX(-90), RY(180))
    pcb_x = 70.0
    pcb_y = belly_y + STANDOFF + 3
    pcb_z = pcb_z_sata - 20
    pcb_pl = FreeCAD.Placement(FreeCAD.Vector(pcb_x, pcb_y, pcb_z), pcb_rot)

    # Split PCB solids into categories by bounding box
    pcb_shape = Part.read(PCB_FILE)
    board, ics, parts, conns = [], [], [], []
    for s in pcb_shape.Solids:
        bb = s.BoundBox
        vol = bb.XLength * bb.YLength * bb.ZLength
        if vol > 10000:            # board substrate (largest)
            board.append(s)
        elif bb.ZLength > 8 or bb.XLength > 15 or bb.YLength > 15:
            conns.append(s)       # connectors (tall or wide)
        elif vol > 50:
            ics.append(s)         # ICs (medium)
        else:
            parts.append(s)       # passives (small)

    for label, solids in [("PCB_Board", board), ("PCB_ICs", ics),
                          ("PCB_Parts", parts), ("PCB_Conn", conns)]:
        if solids:
            obj = doc.addObject("Part::Feature", label)
            obj.Shape = Part.makeCompound(solids)
            obj.Placement = pcb_pl

    hdd_rot = rot(RZ(90), RX(-90), RY(180))
    hdd_x = -hdd_width / 2
    hdd_y = belly_y + STANDOFF + 4
    hdd_z = hdd_z_sata - hdd_length
    place(doc, cfg["hdd_file"], "HDD",
          FreeCAD.Placement(FreeCAD.Vector(hdd_x, hdd_y, hdd_z), hdd_rot))

    doc.recompute()

    # Rotate entire assembly: Y-up (FreeCAD/case) → Z-up (viewer convention)
    # so the bottom plate rests on the ground plane
    flip = FreeCAD.Placement(FreeCAD.Vector(), RX(90))
    for obj in doc.Objects:
        if hasattr(obj, "Placement"):
            obj.Placement = flip.multiply(obj.Placement)
    doc.recompute()

    # Tessellate and export as 3MF (supports per-object colors)
    labels = []
    mesh_objects = []
    for obj in doc.Objects:
        if hasattr(obj, "Shape") and obj.Shape.Faces:
            mesh_obj = doc.addObject("Mesh::Feature", obj.Label + "_mesh")
            mesh_obj.Mesh = Mesh.Mesh(obj.Shape.tessellate(0.5))
            mesh_objects.append(mesh_obj)
            labels.append(obj.Label)
        elif hasattr(obj, "Mesh") and obj.Mesh.CountFacets > 0 and "_mesh" not in obj.Label:
            mesh_objects.append(obj)
            labels.append(obj.Label)

    Mesh.export(mesh_objects, cfg["output"])
    inject_colors_3mf(cfg["output"], labels)

    # Also export STEP for CAD viewers
    step_path = cfg["output"].replace(".3mf", ".step")
    part_objects = [o for o in doc.Objects if hasattr(o, "Shape") and o.Shape.Faces]
    Import.export(part_objects, step_path)

    sys.stdout.write(f"{name}: PCB Z={pcb_z_sata:.1f}..{pcb_z_conn:.1f}, HDD Z={hdd_z_far:.1f}..{hdd_z_sata:.1f}\n")
    sys.stdout.flush()
    FreeCAD.closeDocument(doc.Name)


for name, cfg in VARIANTS.items():
    build_variant(name, cfg)
