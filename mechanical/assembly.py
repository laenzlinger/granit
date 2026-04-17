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
        "end_plate_3mf": "mechanical/end-plate-slim.3mf",
    },
    "wide": {
        "case_file": "hardware/3d-models/1455T2601.stp",
        "hdd_file": "mechanical/3.5inch_HDD_NAS.step",
        "hdd_dims": (147.0, 101.6, 26.1),
        "case_belly_y": -53.6,
        "output": "mechanical/assembly-wide.3mf",
        "end_plate": "mechanical/end-plate-wide.stl",
        "end_plate_3mf": "mechanical/end-plate-wide.3mf",
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


def inject_colors_3mf(path, labels, end_plate_3mf=None, ep_offset=None):
    """Post-process a 3MF file to add per-object colors and merge end plate."""
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

    # Merge end plate mesh from OpenSCAD 3MF (preserves hole topology)
    if end_plate_3mf and ep_offset:
        with zipfile.ZipFile(end_plate_3mf, "r") as ep_zip:
            ep_root = ET.fromstring(ep_zip.read("3D/3dmodel.model"))
        ep_obj = ep_root.find(f".//{{{ns}}}object")
        if ep_obj is not None:
            # Remap OpenSCAD coords to assembly coords (after RX90 flip)
            # OpenSCAD: X=width, Y=height, Z=thickness
            # Assembly: X=width, Y=length, Z=height (up)
            ox, oy, oz = ep_offset  # (plate X origin, plate Y origin, plate Z origin)
            for v in ep_obj.findall(f".//{{{ns}}}vertex"):
                sx, sy, sz = float(v.get('x')), float(v.get('y')), float(v.get('z'))
                v.set("x", f"{sx + ox:.2f}")
                v.set("y", f"{sz + oy:.2f}")   # OpenSCAD Z (thickness) → assembly Y (length)
                v.set("z", f"{-sy + oz:.2f}")   # OpenSCAD Y (height) → assembly -Z (flipped)
            # Axis remap includes negation → flip triangle winding to fix normals
            for tri in ep_obj.findall(f".//{{{ns}}}triangle"):
                v1, v2 = tri.get("v1"), tri.get("v2")
                tri.set("v1", v2)
                tri.set("v2", v1)
            # Assign new id
            max_id = max(int(o.get("id", 0)) for o in resources.findall(f"{{{ns}}}object"))
            ep_obj.set("id", str(max_id + 1))
            resources.append(ep_obj)
            labels.append("EndPlate")

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

    # End plate cutouts: merged directly from OpenSCAD 3MF in post-processing
    # (FreeCAD's mesh pipeline loses hole topology)

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

    # Compute end plate position (after Z-up flip)
    # OpenSCAD plate: X=0..plate_w, Y=0..plate_h, Z=0..plate_t
    # Assembly (after RX90): case X stays, original Y→-Z, original Z→Y
    # Original plate was at: X=cp.XMin..XMax, Y=cp.YMin..YMax, Z=cp.ZMin..ZMax
    # After flip: X=cp.XMin..XMax, Y=cp.ZMin..ZMax, Z=-cp.YMax..-cp.YMin
    ep_3mf = cfg.get("end_plate_3mf")
    ep_offset = None
    if conn_plate and ep_3mf:
        cp_bb = conn_plate.BoundBox
        ep_offset = (cp_bb.XMin, cp_bb.ZMin, -cp_bb.YMax)

    inject_colors_3mf(cfg["output"], labels, ep_3mf, ep_offset)

    sys.stdout.write(f"{name}: PCB Z={pcb_z_sata:.1f}..{pcb_z_conn:.1f}, HDD Z={hdd_z_far:.1f}..{hdd_z_sata:.1f}\n")
    sys.stdout.flush()
    FreeCAD.closeDocument(doc.Name)


for name, cfg in VARIANTS.items():
    build_variant(name, cfg)
