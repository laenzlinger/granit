#!/usr/bin/env python3
"""Convert HDD STL files to STEP. Run with: freecadcmd mechanical/stl2step.py"""
import os
import Mesh
import Part

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NAMES = ["2.5inch_HDD", "3.5inch_HDD_NAS"]

for name in NAMES:
    path = os.path.join(SCRIPT_DIR, name)
    m = Mesh.Mesh(path + ".stl")
    s = Part.Shape()
    s.makeShapeFromMesh(m.Topology, 0.01)
    Part.makeSolid(s).exportStep(path + ".step")
    print(name + ".step")
