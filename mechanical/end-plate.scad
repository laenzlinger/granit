// Granit — Hammond 1455 end plate with connector cutouts
// Parametric: works for both slim (1455L) and wide (1455T) variants
//
// Hammond end plates are flat aluminium panels held by screws.
// Dimensions from Hammond datasheets.
//
// Coordinate system: X = width, Y = height (0 = bottom of plate)

/* [Case Variant] */
variant = "slim"; // [slim, wide]

/* [Plate Dimensions (from Hammond datasheet)] */
// 1455L2201: 103 x 30.5mm, 1455T2601: 165 x 51.5mm
plate_w = (variant == "slim") ? 103 : 165;
plate_h = (variant == "slim") ? 30.5 : 51.5;
plate_t = 1.5; // end plate thickness

// Screw holes (M3, countersunk)
screw_d = 3.2;
screw_inset_x = 5.0;
screw_inset_y = 5.0;

/* [PCB Position Inside Case] */
// PCB center X relative to plate center (0 = centered)
pcb_offset_x = 0;
// PCB bottom Y relative to plate bottom (standoff height)
pcb_bottom_y = 5.0; // 5mm standoffs
// PCB thickness
pcb_t = 1.6;

/* [Connector Cutouts — positions relative to PCB left edge] */
// All Y values are height above PCB bottom surface

// Board dimensions (from KiCad: 92 x 99.5mm)
board_w = 92;

// KiCad coordinates: board X range 20..112, connector edge at Y=120
// Connector X positions (KiCad X - 20 = distance from board left edge)
// Connector Y positions = height above board bottom (component side)

// Barrel Jack (J7) — 694106301002
bj_x = 109.20 - 20;  // 89.2mm from board left
bj_w = 9.0;
bj_h = 11.0;
bj_y_center = 6.0;   // center height above PCB

// RJ45 Ethernet (J8) — HR911130A
rj45_x = 103.50 - 20; // 83.5mm from board left
rj45_w = 16.0;
rj45_h = 13.5;
rj45_y_center = 8.0;

// USB-C (J1) — USB4105-GF-A
usbc_x = 101.00 - 20; // 81.0mm from board left
usbc_w = 9.0;
usbc_h = 3.5;
usbc_y_center = 3.0;

// Tactile Button (SW1) — SKRTLAE010
btn_x = 43.40 - 20;   // 23.4mm from board left
btn_d = 4.0;           // round cutout
btn_y_center = 3.0;

// NeoPixel LED (D1) — light pipe hole
led_x = 106.47 - 20;  // 86.5mm from board left
led_d = 5.0;           // round cutout
led_y_center = 3.0;

/* [Tolerances] */
cutout_clearance = 0.5; // extra clearance around each cutout

// ============================================================

module plate() {
    cube([plate_w, plate_h, plate_t]);
}

module screw_holes() {
    positions = [
        [screw_inset_x, screw_inset_y],
        [plate_w - screw_inset_x, screw_inset_y],
        [screw_inset_x, plate_h - screw_inset_y],
        [plate_w - screw_inset_x, plate_h - screw_inset_y],
    ];
    for (p = positions) {
        translate([p[0], p[1], -1])
            cylinder(d=screw_d, h=plate_t+2, $fn=24);
    }
}

// Convert PCB-relative position to plate position
function pcb_to_plate_x(pcb_x) =
    (plate_w - board_w) / 2 + pcb_offset_x + pcb_x;

function pcb_to_plate_y(pcb_y_above_board) =
    pcb_bottom_y + pcb_t + pcb_y_above_board;

module rect_cutout(pcb_x, y_center, w, h) {
    c = cutout_clearance;
    px = pcb_to_plate_x(pcb_x);
    py = pcb_to_plate_y(y_center);
    translate([px - (w+c)/2, py - (h+c)/2, -1])
        cube([w+c, h+c, plate_t+2]);
}

module round_cutout(pcb_x, y_center, d) {
    c = cutout_clearance;
    px = pcb_to_plate_x(pcb_x);
    py = pcb_to_plate_y(y_center);
    translate([px, py, -1])
        cylinder(d=d+c, h=plate_t+2, $fn=32);
}

module end_plate() {
    difference() {
        plate();
        screw_holes();

        // Connector cutouts
        rect_cutout(bj_x, bj_y_center, bj_w, bj_h);
        rect_cutout(rj45_x, rj45_y_center, rj45_w, rj45_h);
        rect_cutout(usbc_x, usbc_y_center, usbc_w, usbc_h);
        round_cutout(btn_x, btn_y_center, btn_d);
        round_cutout(led_x, led_y_center, led_d);
    }
}

end_plate();
