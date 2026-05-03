// Granit — simplified HDD models with SATA connector slot
//
// SATA connector position per SFF-8201 (2.5") and SFF-8301 (3.5").
// Pin positions from SFF-8223 (SATA connector specification).
//
// Usage:
//   openscad -o 2.5inch_HDD.stl -D 'drive="2.5"' hdd.scad
//   openscad -o 3.5inch_HDD_NAS.stl -D 'drive="3.5"' hdd.scad

/* [Drive Selection] */
drive = "2.5"; // [2.5, 3.5]

/* [2.5" Drive — SFF-8201] */
len_25    = 100.2;
width_25  = 69.85;
height_25 = 9.5;
// SATA connector offset per SFF-8201: pin S1 at 7.11mm from reference edge
slot_y_min_25 = 7.11;
slot_y_max_25 = 7.11 + 34.6;

/* [3.5" Drive — SFF-8301] */
len_35    = 147.0;
width_35  = 101.6;
height_35 = 26.1;
// SATA connector offset per SFF-8301: pin S1 at 11.1mm from reference edge
slot_y_min_35 = 11.1;
slot_y_max_35 = 11.1 + 34.6;

/* [SATA Receptacle — SFF-8223] */
slot_depth  = 5.0;  // depth into drive face
slot_height = 8.6;  // receptacle opening height

// ============================================================

l  = (drive == "2.5") ? len_25    : len_35;
w  = (drive == "2.5") ? width_25  : width_35;
h  = (drive == "2.5") ? height_25 : height_35;
sy = (drive == "2.5") ? slot_y_min_25 : slot_y_min_35;
sw = (drive == "2.5") ? slot_y_max_25 - slot_y_min_25
                      : slot_y_max_35 - slot_y_min_35;

difference() {
    cube([l, w, h]);
    translate([l - slot_depth, sy, 0])
        cube([slot_depth + 1, sw, slot_height]);
}
