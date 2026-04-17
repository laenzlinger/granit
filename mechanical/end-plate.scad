// Granit — Hammond 1455 end plate with connector cutouts
// Parametric: works for both slim (1455L) and wide (1455T) variants
//
// Coordinate system: X = plate width, Y = plate height (0 = bottom)
// PCB connector edge is at X=112 in KiCad (right edge of board).
// PCB Y-axis maps to end plate X-axis.
// Connector height above PCB maps to end plate Y-axis.

/* [Case Variant] */
variant = "slim"; // [slim, wide]

/* [Plate Dimensions (from Hammond datasheet)] */
plate_w = (variant == "slim") ? 103 : 165;
plate_h = (variant == "slim") ? 30.5 : 51.5;
plate_t = 1.5;

// Screw holes
screw_d = 3.2;
screw_inset_x = 5.0;
screw_inset_y = 5.0;

/* [PCB Position Inside Case] */
// PCB Y range in KiCad: 20.5..120 (99.5mm)
// Board sits in case card guides, centered on plate width
board_len = 99.5;  // PCB Y dimension (maps to plate X)
pcb_offset_x = 0;  // PCB center offset from plate center
pcb_bottom_y = 5.0; // standoff height
pcb_t = 1.6;

/* [Connector Positions] */
// From KiCad: connectors are near X=112 (right board edge = end plate side)
// PCB Y coordinate maps to end plate X position
// end_plate_x = board_len - (kicad_Y - 20.5)
// Heights are from component datasheets (above PCB surface)

// Barrel Jack (J7) — KiCad Y=40.6, Wuerth 694106301002
bj_pcb_y   = 40.6;
bj_w       = 11.0;  // cutout width
bj_h       = 11.0;  // cutout height
bj_center_h = 5.5;  // center height above PCB

// RJ45 Ethernet (J8) — KiCad Y=50.3, HR911130A
rj45_pcb_y   = 50.3;
rj45_w       = 16.2;
rj45_h       = 13.5;
rj45_center_h = 8.0;

// USB-C (J1) — KiCad Y=22.5, USB4105-GF-A
usbc_pcb_y   = 22.5;
usbc_w       = 9.5;
usbc_h       = 3.5;
usbc_center_h = 1.8;

// Button (SW1) — KiCad Y=58.7, SKRTLAE010
btn_pcb_y   = 58.7;
btn_d       = 4.0;
btn_center_h = 2.0;

// NeoPixel LED (D1) — KiCad Y=58.7, light pipe hole
led_pcb_y   = 58.7;
led_d       = 5.0;
led_center_h = 2.5;

/* [Tolerances] */
clearance = 0.5;

// ============================================================

// Convert KiCad PCB Y to end plate X
function pcb_y_to_plate_x(kicad_y) =
    (plate_w - board_len) / 2 + pcb_offset_x + (board_len - (kicad_y - 20.5));

// Convert height above PCB to plate Y
function height_to_plate_y(h) =
    pcb_bottom_y + pcb_t + h;

module plate() {
    cube([plate_w, plate_h, plate_t]);
}

module screw_holes() {
    for (px = [screw_inset_x, plate_w - screw_inset_x])
        for (py = [screw_inset_y, plate_h - screw_inset_y])
            translate([px, py, -1])
                cylinder(d=screw_d, h=plate_t+2, $fn=24);
}

module rect_cutout(kicad_y, center_h, w, h) {
    px = pcb_y_to_plate_x(kicad_y);
    py = height_to_plate_y(center_h);
    translate([px - (w+clearance)/2, py - (h+clearance)/2, -1])
        cube([w+clearance, h+clearance, plate_t+2]);
}

module round_cutout(kicad_y, center_h, d) {
    px = pcb_y_to_plate_x(kicad_y);
    py = height_to_plate_y(center_h);
    translate([px, py, -1])
        cylinder(d=d+clearance, h=plate_t+2, $fn=32);
}

difference() {
    plate();
    screw_holes();
    rect_cutout(bj_pcb_y,   bj_center_h,   bj_w,   bj_h);
    rect_cutout(rj45_pcb_y, rj45_center_h, rj45_w, rj45_h);
    rect_cutout(usbc_pcb_y, usbc_center_h, usbc_w, usbc_h);
    round_cutout(btn_pcb_y, btn_center_h,  btn_d);
    round_cutout(led_pcb_y, led_center_h,  led_d);
}
