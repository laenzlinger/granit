// Simplified parametric Hammond 1455 series case
// Dimensions from datasheet + measured from 1455L cross-section
//
// Usage:
//   openscad -o 1455N1601.stl -D 'profile="N"' -D 'length=160' 1455-case.scad

// Parameters
profile = "N";  // J=27, K=43, L=30.5, N=53, P=30.5(125w), T=51.5(165w)
length  = 160;  // body length in mm

// Profile dimensions (width x depth)
function profile_dims(p) =
    p == "J" ? [78, 27] :
    p == "K" ? [78, 43] :
    p == "L" ? [103, 30.5] :
    p == "N" ? [103, 53] :
    p == "T" ? [165, 51.5] :
    [103, 53];  // default N

dims = profile_dims(profile);
width = dims[0];
depth = dims[1];

// Common dimensions (from cross-section analysis of 1455L)
wall = 1.5;           // wall thickness
slot_width = 1.6;     // PCB slot width (fits 1.6mm board)
slot_depth = 2.5;     // how far slot protrudes from inner wall
slot_inset = 5.0;     // slot rail starts this far from side wall (inner)

// Belly plate groove
belly_width = width - 2*5.5;  // ~91.9 for 103mm wide
belly_depth = 4.2;            // groove depth at bottom

// PCB slot positions (measured from INNER bottom)
// These are the same for all 103mm-wide profiles (L, N)
// For the 1455N (53mm deep), slots are near the top (lid side)
// The profile is NOT symmetric - slots are only on the lid side
// From outer bottom: slot centers at 10.06, 15.31, 20.56mm
// From inner bottom (subtract wall): 8.56, 13.81, 19.06mm
slot_from_inner_bottom = [8.56, 13.81, 19.06];

$fn = 32;

module case_body() {
    inner_w = width - 2*wall;
    inner_d = depth - 2*wall;

    difference() {
        // Outer shell
        cube([width, depth, length], center=true);

        // Hollow interior
        cube([inner_w, inner_d, length + 1], center=true);

        // Belly plate groove (bottom)
        translate([0, -depth/2 + belly_depth/2, 0])
            cube([belly_width, belly_depth + 0.1, length + 1], center=true);
    }

    // PCB card slot rails (both sides)
    for (slot_y = slot_from_inner_bottom) {
        y_pos = -depth/2 + wall + slot_y;
        for (side = [-1, 1]) {
            x_pos = side * (width/2 - wall - slot_inset - slot_depth/2);
            translate([x_pos, y_pos, 0])
                cube([slot_depth, slot_width, length], center=true);
        }
    }
}

module end_plate() {
    // Simple flat aluminium end plate
    plate_t = 1.5;
    translate([0, 0, length/2 + plate_t/2])
        cube([width, depth, plate_t], center=true);
}

// Render
case_body();
end_plate();
mirror([0, 0, 1]) end_plate();
