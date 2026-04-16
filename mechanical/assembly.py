#!/usr/bin/env python3
"""Granit mechanical assembly — FreeCAD script.

Run with: freecadcmd mechanical/assembly.py

Case coordinate system: X=width, Y=height (belly at -Y), Z=length (centered)
"""

import sys
import FreeCAD
import Import
import Part

STANDOFF = 5.0
GAP = 2.0

VARIANTS = {
    "slim": {
        "case_file": "hardware/3d-models/1455L2201.stp",
        "hdd_file": "mechanical/2.5inch_HDD.step",
        "hdd_dims": (100.2, 69.85, 9.5),
        "case_belly_y": -32.5,
        "output": "mechanical/assembly-slim.glb",
    },
    "wide": {
        "case_file": "hardware/3d-models/1455T2601.stp",
        "hdd_file": "mechanical/3.5inch_HDD_NAS.step",
        "hdd_dims": (147.0, 101.6, 26.1),
        "case_belly_y": -53.6,
        "output": "mechanical/assembly-wide.glb",
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


def build_variant(name, cfg):
    doc = FreeCAD.newDocument(f"Granit_{name}")
    belly_y = cfg["case_belly_y"]
    hdd_length, hdd_width, hdd_height = cfg["hdd_dims"]

    # Layout: [HDD far .. HDD SATA] [GAP] [PCB SATA .. PCB connectors]
    #          -Z                                                   +Z
    pcb_len = 92.0
    total_z = hdd_length + GAP + pcb_len
    hdd_z_far = -total_z / 2
    hdd_z_sata = hdd_z_far + hdd_length
    pcb_z_sata = hdd_z_sata + GAP
    pcb_z_conn = pcb_z_sata + pcb_len

    place(doc, cfg["case_file"], "Case", FreeCAD.Placement())

    # === PCB ===
    # 90Z, -90X, 180Y → Z=12..114, SATA at low Z, connectors at high Z
    pcb_rot = rot(RZ(90), RX(-90), RY(180))
    pcb_x = 70.0                        # X=-120..-20 → center at -70, shift +70
    pcb_y = belly_y + STANDOFF + 3      # Y=-3..16, shift so Y=-3 at belly+standoff
    pcb_z = pcb_z_sata - 20             # Z≈20 (SATA) → pcb_z_sata
    place(doc, PCB_FILE, "PCB",
          FreeCAD.Placement(FreeCAD.Vector(pcb_x, pcb_y, pcb_z), pcb_rot))

    # === HDD ===
    # 90Z, -90X, 180Y → X=0..W, Y=0..H, Z=0..L, recess at Z=L (high Z)
    hdd_rot = rot(RZ(90), RX(-90), RY(180))
    hdd_x = -hdd_width / 2             # X=0..W → center
    hdd_y = belly_y + STANDOFF + 4     # HDD raised to align SATA with PCB connector
    hdd_z = hdd_z_sata - hdd_length    # Z=L (recess) → hdd_z_sata
    place(doc, cfg["hdd_file"], "HDD",
          FreeCAD.Placement(FreeCAD.Vector(hdd_x, hdd_y, hdd_z), hdd_rot))

    doc.recompute()
    Import.export(doc.Objects, cfg["output"])
    sys.stdout.write(f"{name}: PCB Z={pcb_z_sata:.1f}..{pcb_z_conn:.1f}, HDD Z={hdd_z_far:.1f}..{hdd_z_sata:.1f}\n")
    sys.stdout.flush()
    FreeCAD.closeDocument(doc.Name)


for name, cfg in VARIANTS.items():
    build_variant(name, cfg)
