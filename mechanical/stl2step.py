#!/usr/bin/env python3
"""Convert HDD STL files to STEP. Run with: freecadcmd mechanical/stl2step.py"""
import os
import Mesh
import Part

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SCRIPT_DIR, "out")
NAMES = ["2.5inch_HDD", "3.5inch_HDD_NAS"]

for name in NAMES:
    stl_path = os.path.join(OUT_DIR, name + ".stl")
    step_path = os.path.join(OUT_DIR, name + ".step")
    m = Mesh.Mesh(stl_path)
    s = Part.Shape()
    s.makeShapeFromMesh(m.Topology, 0.01)
    Part.makeSolid(s).exportStep(step_path)
    print(name + ".step")
