// Granit — Hammond 1455 end plate with connector cutouts
// Parametric: works for both slim (1455L) and wide (1455T) variants
//
// PCB connector edge is at X=112 in KiCad (right edge of board).
// PCB Y-axis maps to end plate X-axis.
// All connector cutouts are bottom-aligned to PCB surface.

/* [Case Variant] */
variant = "slim"; // [slim, wide]

/* [Plate Dimensions (from Hammond datasheet)] */
plate_w = (variant == "slim") ? 103 : 165;
plate_h = (variant == "slim") ? 30.5 : 51.5;
plate_t = 1.5;

// Screw holes (Hammond 1455: #4-40 UNC ≈ M3, 4mm inset from edges)
screw_d = 3.5;      // M3 clearance hole
screw_cs_d = 6.5;   // countersink diameter
screw_inset_x = 4.0;
screw_inset_y = 4.0;

/* [PCB Position Inside Case] */
board_len = 99.5;
pcb_offset_x = 0;
pcb_bottom_y = 5.0;  // standoff height
pcb_t = 1.6;

// Y coordinate of PCB surface on the end plate
pcb_surface_y = pcb_bottom_y + pcb_t;

/* [Connector Cutouts] */
// Positions: KiCad Y from PCB dimension annotations (measured from board corner)
// Heights: from component datasheets (total body height above PCB)

// Barrel Jack (J7) — 694106301002, 17mm from connector edge
bj_pcb_y = 103;
bj_w     = 11.0;
bj_h     = 11.0;  // body height above PCB

// RJ45 Ethernet (J8) — HR911130A, 50mm from connector edge
rj45_pcb_y = 70;
rj45_w     = 16.2;
rj45_h     = 13.1;  // body height above PCB

// USB-C (J1) — USB4105-GF-A, 86mm from connector edge
usbc_pcb_y = 34;
usbc_w     = 9.0;
usbc_h     = 3.2;  // receptacle height

// Button (SW1) — SKRTLAE010, 64mm from connector edge
btn_pcb_y = 56;
btn_d     = 3.0;

// NeoPixel LED (D1) — WS2812B + light pipe, 73mm from connector edge
led_pcb_y = 47;
led_d     = 3.0;  // same as button for clean look

// Button and LED hole center height (same for both, custom light pipe)
btn_led_center_h = 1.5;  // above PCB surface

/* [Tolerances] */
clearance = 0.5;

// ============================================================

function pcb_y_to_plate_x(kicad_y) =
    (plate_w - board_len) / 2 + pcb_offset_x + (board_len - (kicad_y - 20.5));

module plate() {
    cube([plate_w, plate_h, plate_t]);
}

module screw_holes() {
    for (px = [screw_inset_x, plate_w - screw_inset_x])
        for (py = [screw_inset_y, plate_h - screw_inset_y])
            translate([px, py, 0]) {
                // Through hole
                translate([0, 0, -1])
                    cylinder(d=screw_d, h=plate_t+2, $fn=24);
                // 90° countersink from outside face
                translate([0, 0, plate_t - (screw_cs_d - screw_d)/2])
                    cylinder(d1=screw_d, d2=screw_cs_d, h=(screw_cs_d - screw_d)/2 + 0.1, $fn=32);
            }
}

// Rectangular cutout, bottom-aligned to PCB surface
module rect_cutout(kicad_y, w, h) {
    c = clearance;
    px = pcb_y_to_plate_x(kicad_y);
    translate([px - (w+c)/2, pcb_surface_y, -1])
        cube([w+c, h+c, plate_t+2]);
}

// Round cutout at fixed height above PCB
module round_cutout(kicad_y, d, center_h) {
    c = clearance;
    px = pcb_y_to_plate_x(kicad_y);
    py = pcb_surface_y + center_h;
    translate([px, py, -1])
        cylinder(d=d+c, h=plate_t+2, $fn=32);
}

difference() {
    plate();
    screw_holes();
    rect_cutout(bj_pcb_y,   bj_w,   bj_h);
    rect_cutout(rj45_pcb_y, rj45_w, rj45_h);
    rect_cutout(usbc_pcb_y, usbc_w, usbc_h);
    round_cutout(btn_pcb_y, btn_d, btn_led_center_h);
    round_cutout(led_pcb_y, led_d, btn_led_center_h);
}
