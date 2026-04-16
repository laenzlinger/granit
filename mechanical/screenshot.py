#!/usr/bin/env python3
"""Render assembly screenshot with original 3D model colors.

Run with:
  LIBGL_ALWAYS_SOFTWARE=1 ASSEMBLY_FILE=... \
    xvfb-run -a -s "-screen 0 2160x2160x24" freecad screenshot.py
"""

import os
import sys
import FreeCAD
import FreeCADGui
import Import
import Part

assembly_file = os.environ.get("ASSEMBLY_FILE", "mechanical/assembly-wide.3mf")
output_png = os.path.splitext(assembly_file)[0] + ".png"

doc = FreeCAD.newDocument("render")
Import.insert(assembly_file, doc.Name)
doc.recompute()

for obj in doc.Objects:
    if not (hasattr(obj, "Shape") and obj.Shape.Solids and hasattr(obj, "ViewObject")):
        continue
    bb = obj.Shape.BoundBox
    try:
        # PCB board (thin, ~100x92): green
        if bb.YLength < 5 and bb.XLength > 80 and bb.ZLength > 80:
            obj.ViewObject.ShapeColor = (0.0, 0.55, 0.15)
            continue
        # HDD: red-ish, Y height 9-27mm, not as wide as case
        if bb.ZLength > 90 and bb.ZLength < 150 and bb.YLength > 5 and bb.YLength < 40 and bb.XLength < 110:
            obj.ViewObject.ShapeColor = (0.75, 0.75, 0.78)
            continue
        # Components on PCB: dark gray (small-ish parts)
        vol = bb.XLength * bb.YLength * bb.ZLength
        if vol < 50000 and bb.XLength < 60 and bb.ZLength < 60:
            obj.ViewObject.ShapeColor = (0.2, 0.2, 0.2)
            continue
        # Case end panels: tall-ish Y, thin Z, wide X
        if bb.YLength > 20 and bb.ZLength < 20 and bb.XLength > 80:
            if bb.ZMin > 0:
                obj.ViewObject.Visibility = False  # hide connector-side end panel
            else:
                obj.ViewObject.ShapeColor = (0.7, 0.7, 0.72)
                obj.ViewObject.Transparency = 70
            continue
        # Case lid (thin, near Y=0): hide
        if bb.YLength < 6 and bb.XLength > 100 and bb.ZLength > 100 and bb.YMax > -5:
            obj.ViewObject.Visibility = False
            continue
        # Case body: light gray, transparent
        if bb.XLength > 100 and bb.ZLength > 100:
            obj.ViewObject.ShapeColor = (0.7, 0.7, 0.72)
            obj.ViewObject.Transparency = 85
            continue
        # Fallback: medium gray
        obj.ViewObject.ShapeColor = (0.4, 0.4, 0.4)
    except Exception:
        pass

view = FreeCADGui.ActiveDocument.ActiveView
from pivy import coin
cam = view.getCameraNode()

# Camera: on a table, lid removed, looking down from above-rear, PCB components visible
rot = coin.SbRotation(coin.SbVec3f(1, 0, 0), -0.65)    # look down from above
rot *= coin.SbRotation(coin.SbVec3f(0, 1, 0), -0.35)    # slight side angle
rot *= coin.SbRotation(coin.SbVec3f(0, 0, 1), 0.0)      # HDD at back, PCB toward viewer
cam.orientation.setValue(rot)
view.fitAll()

view.saveImage(output_png, 2160, 2160, "White")
sys.stdout.write(f"saved {output_png}\n")
sys.stdout.flush()
sys.exit(0)
