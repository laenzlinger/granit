// Granit — Hammond 1455 end plate with connector cutouts
// Parametric: works for both slim (1455L) and wide (1455T) variants
//
// Usage:
//   3D (STL for printing):  openscad -o plate.stl -D 'variant="slim"' end-plate.scad
//   2D (DXF for CNC):       openscad -o plate.dxf -D 'variant="slim"' -D 'mode="2d"' end-plate.scad

/* [Output Mode] */
mode = "3d"; // [3d, 2d]

/* [Case Variant] */
variant = "slim"; // [slim, wide, compact]

/* [Plate Dimensions (from Hammond STEP)] */
plate_w = (variant == "slim") ? 103 : 165;
plate_h = (variant == "slim") ? 30.5 : 51.5;
plate_t = 1.5;

// Screw holes (Hammond 1455: #4-40 UNC ≈ M3, 4mm inset)
screw_d = 3.5;
screw_cs_d = 6.5;
screw_inset_x = 4.0;
screw_inset_y = 4.0;

// Corner radius (from Hammond STEP: 3.94mm)
corner_r = 3.94;

/* [PCB Position Inside Case] */
board_len = 99.5;
pcb_offset_x = 0;
// PCB bottom height from plate bottom:
//   slim/wide: 5.0mm (standoffs from belly plate)
//   compact: 31.6mm (wall + rail + HDD + gap)
pcb_bottom_y = (variant == "compact") ? 31.6 : 5.0;
pcb_t = 1.6;
pcb_surface_y = pcb_bottom_y + pcb_t;

/* [Connector Cutouts — from KiCad PCB dimensions] */
// Barrel Jack (J7) — 17mm from connector edge
bj_pcb_y = 103;
bj_w     = 9.0;  // datasheet: body width
bj_h     = 9.0;  // datasheet: body height above PCB

// RJ45 Ethernet (J8) — 50mm from connector edge
rj45_pcb_y = 70;
rj45_w     = 16.2;
rj45_h     = 13.1;

// USB-C (J1) — 86mm from connector edge
usbc_pcb_y = 34;
usbc_w     = 9.0;
usbc_h     = 3.2;

// Button (SW1) — 64mm from connector edge
btn_pcb_y = 56;
btn_d     = 3.0;

// NeoPixel LED (D1) — 73mm from connector edge
led_pcb_y = 47;
led_d     = 3.0;

// Button and LED center height above PCB surface
btn_led_center_h = 1.5;

/* [Tolerances] */
clearance = 0.5;

// ============================================================

function pcb_y_to_plate_x(kicad_y) =
    (plate_w - board_len) / 2 + pcb_offset_x + (board_len - (kicad_y - 20.5));

// 2D profile (used for both DXF export and 3D extrusion)
module plate_2d() {
    difference() {
        // Rounded rectangle outline
        offset(r=corner_r) offset(delta=-corner_r)
            square([plate_w, plate_h]);

        // Screw holes
        for (px = [screw_inset_x, plate_w - screw_inset_x])
            for (py = [screw_inset_y, plate_h - screw_inset_y])
                translate([px, py])
                    circle(d=screw_d, $fn=24);

        // Rectangular cutouts (bottom-aligned to PCB surface)
        for (p = [[bj_pcb_y, bj_w, bj_h],
                   [rj45_pcb_y, rj45_w, rj45_h],
                   [usbc_pcb_y, usbc_w, usbc_h]]) {
            c = clearance;
            px = pcb_y_to_plate_x(p[0]);
            translate([px - (p[1]+c)/2, pcb_surface_y])
                square([p[1]+c, p[2]+c]);
        }

        // Round cutouts (button + LED at same height)
        for (ky = [btn_pcb_y, led_pcb_y]) {
            c = clearance;
            px = pcb_y_to_plate_x(ky);
            py = pcb_surface_y + btn_led_center_h;
            translate([px, py])
                circle(d=btn_d+c, $fn=32);
        }
    }
}

if (mode == "2d") {
    plate_2d();
} else {
    linear_extrude(plate_t) plate_2d();
}
