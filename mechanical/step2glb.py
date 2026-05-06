#!/usr/bin/env python3
"""Convert assembly STEP files to GLB with per-part colors.

Requires: pip install trimesh numpy cascadio scipy

Usage: python3 mechanical/step2glb.py [mechanical/assembly-*.step ...]
       (defaults to all assembly-*.step in the script's directory)
"""

import sys
from pathlib import Path

import numpy as np
import trimesh

COLORS = {
    "Case": [180, 180, 185, 255],
    "Lid": [180, 180, 185, 255],
    "PCB_Board": [35, 100, 60, 255],
    "PCB_ICs": [30, 30, 30, 255],
    "PCB_Parts": [180, 160, 100, 255],
    "PCB_Conn": [40, 40, 40, 255],
    "HDD": [60, 60, 65, 255],
    "EndPlate": [180, 180, 185, 255],
}


def convert(step_path: Path) -> Path:
    scene = trimesh.load(str(step_path))
    for name, mesh in scene.geometry.items():
        color = COLORS.get(name, [128, 128, 128, 255])
        mesh.visual.vertex_colors = np.array(
            [color] * len(mesh.vertices), dtype=np.uint8
        )
    glb_path = step_path.with_suffix(".glb")
    scene.export(str(glb_path))
    print(f"{step_path.name} -> {glb_path.name} ({glb_path.stat().st_size // 1024} KB)")
    return glb_path


if __name__ == "__main__":
    if len(sys.argv) > 1:
        files = [Path(p) for p in sys.argv[1:]]
    else:
        files = sorted(Path(__file__).parent.glob("assembly-*.step"))

    if not files:
        sys.exit("No assembly STEP files found")

    for f in files:
        convert(f)
