// Hammond 1455 series parametric case model
// Accurate cross-section from STEP analysis of real 1455L/N/T parts.
//
// The 1455 is an extruded aluminium U-channel body with:
//   - Removable belly plate (bottom lid, slides in from end)
//   - Lip at top for snap/screw lid retention
//   - PCB card guide slots on both side walls
//   - End frames with screw bosses for end plates
//
// Usage:
//   Full case:    openscad -o case.stl 1455-case.scad
//   Body only:    openscad -o body.stl -D 'render_part="body"' 1455-case.scad
//   Lid only:     openscad -o lid.stl -D 'render_part="lid"' 1455-case.scad
//   End plate:    openscad -o plate.stl -D 'render_part="end_plate"' 1455-case.scad
//
//   Profile:      -D 'profile="N"'
//   Length:       -D 'length=160'

// ── Parameters ──────────────────────────────────────────────────────────────

profile = "N";          // J=78x27, K=78x43, L=103x30.5, N=103x53, T=165x51.5
length  = 160;          // body length (mm)
render_part = "all";    // all, body, lid, end_plate, exploded

// ── Profile Lookup ──────────────────────────────────────────────────────────

function profile_dims(p) =
    p == "J" ? [78, 27] :
    p == "K" ? [78, 43] :
    p == "L" ? [103, 30.5] :
    p == "N" ? [103, 53] :
    p == "T" ? [165, 51.5] :
    [103, 53];

dims  = profile_dims(profile);
W     = dims[0];        // outer width
H     = dims[1];        // outer height (depth)

// ── Dimensions (from STEP analysis of Hammond 1455L) ────────────────────────

wall        = 1.5;      // wall thickness (sides and top)
corner_r    = 4.0;      // outer corner radius
inner_r     = corner_r - wall;  // inner corner radius (2.5mm)

// Belly plate (removable bottom lid)
belly_w     = W - 2*5.55;      // 91.9mm for 103mm wide
belly_t     = 1.5;             // plate thickness
belly_groove_d = 4.22;         // groove depth in body (plate + clearance)
belly_lip   = 0.38;            // retention lip height

// Top lip (body overhangs inward at top opening)
lip_h       = 1.5;     // lip height
lip_w       = (W - 89.14) / 2; // ~6.93mm overhang each side

// PCB card guide slots (on both side walls)
slot_w      = 1.5;      // slot width (accepts 1.6mm PCB with clearance)
slot_d      = 2.0;      // slot depth into wall (from inner face)
slot_spacing = 3.5;     // spacing between slot centers

// End plate guide channels (wider grooves between PCB slots)
// The end plate slides into these channels from the end of the extrusion.
// They run between each pair of PCB slots and extend to the inner wall face.
channel_d   = 2.5;      // channel depth (slightly deeper than PCB slots)
channel_w   = 2.0;      // channel width (gap between adjacent slots)

// Slot count and first position per profile (from STEP measurements):
//   First slot: 8.18mm from top (lip), last slot: 8.32mm from bottom (open side)
//   Spacing: 3.50mm, consistent across all profiles.
function slot_config(p) =
    p == "J" ? [1, 13.5] :
    p == "K" ? [8, 8.18] :
    p == "L" ? [5, 8.19] :
    p == "N" ? [12, 8.18] :
    p == "T" ? [11, 8.18] :
    [12, 8.18];

_sc = slot_config(profile);
slot_count = _sc[0];
slot_first = _sc[1];
slot_from_top = [for (i = [0:slot_count-1]) slot_first + i * slot_spacing];

// Decorative grooves on outer side walls (semicircular notches)
groove_r    = 0.38;     // groove radius (from STEP: R=0.380 arcs)
// Grooves are evenly spaced in the flat wall zone between corners.
// From STEP: first groove ~(corner_r + 1.84)mm from top
groove_zone_top = corner_r + 1.84;
groove_zone_bot = H - corner_r - 1.84;
// Groove count: ~1 per 4.9mm of flat zone (from 1455T measurement)
groove_count = max(2, floor((groove_zone_bot - groove_zone_top) / 4.9) + 1);
groove_spacing_actual = (groove_zone_bot - groove_zone_top) / (groove_count - 1);
groove_from_top = [for (i = [0:groove_count-1]) groove_zone_top + i * groove_spacing_actual];

// Screw boss geometry
// Each corner has a solid block (rounded on outside) with a screw hole.
// The cavity cut removes the inner portion, leaving material around the hole.
boss_hole_d = 3.5;      // screw hole diameter (#4-40 / M3 clearance)
boss_size   = 6.8;      // boss block size (measured from real case)

// End plate
plate_t     = 1.5;
plate_w     = W - 0.13; // 102.87mm (slight clearance)
plate_h     = H - 0.03; // 30.48mm for 1455L
plate_corner_r = 3.94;  // from Hammond STEP
plate_screw_d  = 3.5;   // clearance for #4-40 / M3
plate_screw_inset_x = 4.0;
plate_screw_inset_y = 4.0;

$fn = 48;

// ── Modules ─────────────────────────────────────────────────────────────────

// Rounded rectangle (2D)
module rrect(w, h, r) {
    offset(r=r) offset(delta=-r)
        square([w, h], center=true);
}

// Screw boss rails are just regular horizontal ridges at the corner positions.
// No special module needed — they're part of the rail zone material.

// Complete body cross-section (2D) — everything that comes out of the extrusion die
// Approach: thick side walls (wall + rail zone), then cut slots where PCB goes.
// The boss areas are simply uncut sections of the rail zone.
module body_profile_2d() {
    rail_zone = channel_d;

    difference() {
        union() {
            // Solid outer shell (thick walls include rail material)
            rrect(W, H, corner_r);

            // Corner boss blocks (all 4 corners, rounded to match case profile)
            for (sx = [-1, 1])
                for (sy = [-1, 1])
                    translate([sx * (W/2 - corner_r), sy * (H/2 - corner_r)])
                        offset(r=2) offset(delta=-2)
                            square([boss_size, boss_size], center=true);
        }

        // Main inner cavity (stops at boss blocks on both ends)
        boss_inner_x = (W/2 - corner_r) - boss_size/2;
        boss_top_y = -(H/2 - corner_r) + boss_size/2;   // top edge of bottom boss
        boss_bot_y_top = (H/2 - corner_r) - boss_size/2; // bottom edge of top boss
        cavity_w = W - 2*(wall + rail_zone);
        cavity_bot = boss_top_y;
        cavity_top = boss_bot_y_top;
        cavity_h = cavity_top - cavity_bot;
        cavity_cy = (cavity_top + cavity_bot) / 2;
        translate([0, cavity_cy])
            square([cavity_w, cavity_h], center=true);

        // Open the bottom of the U between the boss blocks
        opening_w = boss_inner_x * 2;
        opening_top = H/2 - lip_h;
        translate([0, (-H/2 + opening_top) / 2])
            square([opening_w, opening_top + H/2 + 0.01], center=true);

        // Belly plate channel (stops at boss blocks)
        belly_channel_w = W - 2*(corner_r + boss_size/2);
        translate([0, -H/2 + belly_groove_d/2])
            square([belly_channel_w, belly_groove_d + 0.01], center=true);

        // Screw holes through corner bosses (all 4 corners)
        for (sx = [-1, 1])
            for (sy = [-1, 1])
                translate([sx * (W/2 - corner_r), sy * (H/2 - corner_r)])
                    circle(d=boss_hole_d, $fn=24);

        // Belly plate slot through bottom boss blocks (from inner edge to center)
        for (sx = [-1, 1])
            translate([sx * (W/2 - corner_r - boss_size/4), -(H/2 - corner_r)])
                square([boss_size/2 + 0.01, belly_t + 0.2], center=true);

        // Diagonal slot through top boss blocks (45° toward interior)
        for (sx = [-1, 1]) {
            bx = sx * (W/2 - corner_r);
            by = (H/2 - corner_r);
            translate([bx, by])
                rotate(sx > 0 ? 180+45 : -45)
                    translate([boss_size/2.5, 0])
                        square([boss_size*0.8, belly_t + 0.2], center=true);
        }

        // PCB slot cuts — narrow gaps through the rail zone
        // Only cut where there's no boss block
        for (pos = slot_from_top) {
            slot_cy = H/2 - pos;
            if (slot_cy > -H/2 + corner_r + boss_size/2)  // above bottom boss
            for (side = [-1, 1])
                translate([side * (W/2 - wall - rail_zone/2), slot_cy])
                    square([rail_zone + 0.01, slot_w], center=true);
        }

        // Decorative grooves on outer side walls
        for (g = groove_from_top) {
            gy = H/2 - g;
            for (side = [-1, 1])
                translate([side * W/2, gy])
                    circle(r=groove_r, $fn=16);
        }
    }
}

// Body: pure extrusion — no post-machining operations
module body() {
    linear_extrude(length, center=true)
        body_profile_2d();
}

// Belly plate: U-profiled extrusion with edge flanges that slide into body groove
module belly_plate() {
    belly_wall = 1.3;
    belly_plate_w = belly_w - 2*belly_wall;  // U-profile outer width (inside groove)
    flange_w = belly_w;          // full width including flanges (fits groove)
    flange_t = belly_wall;       // flange thickness
    translate([0, -H/2 + belly_groove_d/2, 0])
        linear_extrude(length, center=true) {
            // Main U-profile
            difference() {
                square([belly_plate_w, belly_groove_d], center=true);
                // U cutout: leaves belly_wall at bottom, open at top
                translate([0, belly_wall])
                    square([belly_plate_w - 2*belly_wall, belly_groove_d], center=true);
            }
            // Flanges (from inner face of side wall outward into body groove)
            flange_ext = (flange_w - belly_plate_w)/2 + belly_wall*2;
            for (sx = [-1, 1])
                translate([sx * (belly_plate_w/2 - belly_wall + flange_ext/2), 1.9])
                    square([flange_ext, flange_t], center=true);
        }
}

// End plate with screw holes (blank — use end-plate.scad for cutouts)
module end_plate() {
    difference() {
        linear_extrude(plate_t)
            rrect(plate_w, plate_h, plate_corner_r);

        // Screw holes (4 corners)
        for (px = [-plate_w/2 + plate_screw_inset_x,
                    plate_w/2 - plate_screw_inset_x])
            for (py = [-plate_h/2 + plate_screw_inset_y,
                        plate_h/2 - plate_screw_inset_y])
                translate([px, py, -0.1])
                    cylinder(d=plate_screw_d, h=plate_t + 0.2, $fn=24);
    }
}

// ── Render ──────────────────────────────────────────────────────────────────

module render_all() {
    color("Silver") body();
    color("LightGray") belly_plate();
    for (z_sign = [-1, 1])
        color("DarkGray")
            translate([0, 0, z_sign * (length/2 + plate_t/2)])
                end_plate();
}

module render_exploded() {
    explode = 20;

    color("Silver") body();

    // Belly plate dropped down
    color("LightGray")
        translate([0, -explode, 0])
            belly_plate();

    // End plates pulled out
    for (z_sign = [-1, 1])
        color("DarkGray")
            translate([0, 0, z_sign * (length/2 + plate_t/2 + explode)])
                end_plate();
}

if (render_part == "body") {
    body();
} else if (render_part == "lid") {
    belly_plate();
} else if (render_part == "body_lid") {
    body();
    belly_plate();
} else if (render_part == "end_plate") {
    end_plate();
} else if (render_part == "exploded") {
    render_exploded();
} else {
    render_all();
}
