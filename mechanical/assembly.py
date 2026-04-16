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

# Colors per object label (RGBA hex)
COLORS = {
    "Case": "#C8C8C880",
    "PCB":  "#1B5E20",
    "HDD":  "#505050",
}

VARIANTS = {
    "slim": {
        "case_file": "hardware/3d-models/1455L2201.stp",
        "hdd_file": "mechanical/2.5inch_HDD.step",
        "hdd_dims": (100.2, 69.85, 9.5),
        "case_belly_y": -32.5,
        "output": "mechanical/assembly-slim.3mf",
    },
    "wide": {
        "case_file": "hardware/3d-models/1455T2601.stp",
        "hdd_file": "mechanical/3.5inch_HDD_NAS.step",
        "hdd_dims": (147.0, 101.6, 26.1),
        "case_belly_y": -53.6,
        "output": "mechanical/assembly-wide.3mf",
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
    case_shape = Part.read(cfg["case_file"])
    lid_vol = max(s.Volume for s in case_shape.Solids)
    open_solids = [s for s in case_shape.Solids if s.Volume < lid_vol]
    case_obj = doc.addObject("Part::Feature", "Case")
    case_obj.Shape = Part.makeCompound(open_solids)

    pcb_rot = rot(RZ(90), RX(-90), RY(180))
    pcb_x = 70.0
    pcb_y = belly_y + STANDOFF + 3
    pcb_z = pcb_z_sata - 20
    place(doc, PCB_FILE, "PCB",
          FreeCAD.Placement(FreeCAD.Vector(pcb_x, pcb_y, pcb_z), pcb_rot))

    hdd_rot = rot(RZ(90), RX(-90), RY(180))
    hdd_x = -hdd_width / 2
    hdd_y = belly_y + STANDOFF + 4
    hdd_z = hdd_z_sata - hdd_length
    place(doc, cfg["hdd_file"], "HDD",
          FreeCAD.Placement(FreeCAD.Vector(hdd_x, hdd_y, hdd_z), hdd_rot))

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

    Mesh.export(mesh_objects, cfg["output"])
    inject_colors_3mf(cfg["output"], labels)

    sys.stdout.write(f"{name}: PCB Z={pcb_z_sata:.1f}..{pcb_z_conn:.1f}, HDD Z={hdd_z_far:.1f}..{hdd_z_sata:.1f}\n")
    sys.stdout.flush()
    FreeCAD.closeDocument(doc.Name)


for name, cfg in VARIANTS.items():
    build_variant(name, cfg)
