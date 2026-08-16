// ProComm iM2300 cooling and vertical-stack concept Rev D / mechanical gate A2.
// All dimensions are millimeters and remain preliminary until the actual case is measured.
$fn = 48;

inner_x = 431.8;
inner_y = 298.0;
bottom_depth = 106.7;
panel_below_parting = 38.1;
panel_top_z = bottom_depth - panel_below_parting; // 68.6 mm above nominal deepest floor.
panel_t = 3.175;
panel_underside_z = panel_top_z - panel_t; // 65.425 mm.
tray_t = 2.0;
tray_top_z = 3.0; // Includes any released rigid mounting/isolator stack.
carrier_z = 58.0;
carrier_t = 1.6;
standoff_h = panel_underside_z - (carrier_z + carrier_t);
audio_supports = [[47,21],[87,21],[47,149],[87,149],[47,277],[87,277]];
carrier_supports = [[225,21],[379,21],[225,149],[331,149],[225,277],[379,205]];

cpu_cm5_bottom_z = 53.4;
cpu_sink_h = 10.0;
cpu_adapter_h = 3.0;
cpu_fan_h = 28.0;
cpu_fan_bottom_z = cpu_cm5_bottom_z - cpu_sink_h - cpu_adapter_h - cpu_fan_h;
cpu_floor_gap = cpu_fan_bottom_z;

modem_card_bottom_z = 53.0;
modem_sink_h = 8.0;
modem_adapter_h = 4.0;
modem_fan_h = 15.0; // Delta AFB0412SHB-SP04.
modem_fan_bottom_z = modem_card_bottom_z - modem_sink_h - modem_adapter_h - modem_fan_h;
modem_floor_gap = modem_fan_bottom_z;

audio_quiet_boundary_x = 98.0;
psu_guard_x = 244.0;
psu_audio_gap = psu_guard_x - audio_quiet_boundary_x;
psu_guard_top_z = 48.0;
psu_carrier_gap = carrier_z - psu_guard_top_z;
lid_harness_corridor_right_x = 229.0;
lid_harness_psu_gap = psu_guard_x - lid_harness_corridor_right_x;

assert(cpu_floor_gap >= 10.0, "CM5 dedicated fan inlet clearance is below 10 mm");
assert(modem_floor_gap >= 10.0, "Modem dedicated fan inlet clearance is below 10 mm");
assert(abs(panel_underside_z - 65.425) < 0.001, "Panel underside nominal stack is inconsistent");
assert(tray_top_z <= 3.0, "Bottom equipment tray top exceeds the 3 mm limit");
assert(psu_guard_top_z <= 48.0, "Installed PSU/guard envelope exceeds 48 mm");
assert(panel_underside_z - (carrier_z + carrier_t) >= 4.0, "Carrier F.Cu gap to panel underside is below 4 mm");
assert(psu_audio_gap >= 125.0, "PSU guard is less than 125 mm from the audio quiet boundary");
assert(psu_carrier_gap >= 10.0, "PSU guard clearance to the carrier is below 10 mm");
assert(lid_harness_psu_gap >= 15.0, "Lid-harness corridor is less than 15 mm from the PSU guard");
assert(standoff_h > 0, "PCB standoff stack has no positive height");
assert(len(audio_supports) == 6, "AUDIO-8X8 must have six controlled supports");
assert(len(carrier_supports) == 6, "CM5-CARRIER must have six controlled supports");
echo(str("Panel top above floor: ", panel_top_z, " mm"));
echo(str("Panel underside above floor: ", panel_underside_z, " mm"));
echo(str("Tray top to panel underside: ", panel_underside_z - tray_top_z, " mm"));
echo(str("CM5 fan inlet gap: ", cpu_floor_gap, " mm"));
echo(str("Modem fan inlet gap: ", modem_floor_gap, " mm"));
echo(str("PSU guard to audio quiet boundary: ", psu_audio_gap, " mm"));
echo(str("PSU guard to carrier clearance: ", psu_carrier_gap, " mm"));
echo(str("Lid-harness corridor to PSU guard: ", lid_harness_psu_gap, " mm"));
echo(str("PCB standoff body height: ", standoff_h, " mm"));

module colored_box(size, color_value, alpha = 1.0) {
  color([color_value[0], color_value[1], color_value[2], alpha]) cube(size);
}

module fan_body(size = [40, 40, 20], axis = "z", body_color = [0.15, 0.32, 0.58]) {
  color(body_color) difference() {
    cube(size);
    if (axis == "z") translate([size[0] / 2, size[1] / 2, -1]) cylinder(h = size[2] + 2, d = min(size[0], size[1]) - 6);
    if (axis == "x") translate([-1, size[1] / 2, size[2] / 2]) rotate([0, 90, 0]) cylinder(h = size[0] + 2, d = min(size[1], size[2]) - 6);
    if (axis == "y") translate([size[0] / 2, -1, size[2] / 2]) rotate([-90, 0, 0]) cylinder(h = size[1] + 2, d = min(size[0], size[2]) - 6);
  }
}

module finned_sink(size = [55, 40, 10]) {
  color([0.88, 0.64, 0.18]) {
    cube([size[0], size[1], 2]);
    for (x = [2:6:size[0] - 2]) translate([x, 0, 2]) cube([2, size[1], size[2] - 2]);
  }
}

module pcb_standoff() {
  color([0.82, 0.84, 0.86]) difference() {
    cylinder(h = standoff_h, d = 7.0);
    translate([0, 0, -0.2]) cylinder(h = standoff_h + 0.4, d = 3.0);
  }
}

// Transparent nominal cavity. Z=0 is the deepest nominal interior floor.
color([0.75, 0.80, 0.84, 0.10]) difference() {
  translate([-4, -4, -3]) cube([inner_x + 8, inner_y + 8, bottom_depth + 3]);
  translate([0, 0, 0]) cube([inner_x, inner_y, bottom_depth + 1]);
}
color([0.20, 0.23, 0.27]) translate([0, 0, -3]) cube([inner_x, inner_y, 3]);

// Low-profile bottom equipment-tray reference. Actual outline follows measured floor ribs.
color([0.48, 0.52, 0.58, 0.40]) {
  translate([90, 15, tray_top_z - tray_t]) cube([258, 3, tray_t]);
  translate([90, 280, tray_top_z - tray_t]) cube([258, 3, tray_t]);
  translate([90, 15, tray_top_z - tray_t]) cube([3, 268, tray_t]);
  translate([345, 15, tray_top_z - tray_t]) cube([3, 268, tray_t]);
}

// Top-panel perimeter reference only, leaving the interior open for inspection.
// The actual panel is a solid plate with no cooling cutouts.
translate([0, 0, panel_underside_z]) {
  colored_box([inner_x, 8, panel_t], [0.70, 0.75, 0.80], 0.45);
  translate([0, inner_y - 8, 0]) colored_box([inner_x, 8, panel_t], [0.70, 0.75, 0.80], 0.45);
  colored_box([8, inner_y, panel_t], [0.70, 0.75, 0.80], 0.45);
  translate([inner_x - 8, 0, 0]) colored_box([8, inner_y, panel_t], [0.70, 0.75, 0.80], 0.45);
}

// Suspended PCBs.
translate([15, 15, carrier_z]) colored_box([78, 268, carrier_t], [0.12, 0.62, 0.70], 0.85); // AUDIO-8X8
// CM5 carrier is drawn as an outline so the B.Cu cooling hardware remains visible.
translate([219, 15, carrier_z]) {
  colored_box([166, 5, carrier_t], [0.15, 0.66, 0.38], 0.90);
  translate([0, 263, 0]) colored_box([166, 5, carrier_t], [0.15, 0.66, 0.38], 0.90);
  colored_box([5, 268, carrier_t], [0.15, 0.66, 0.38], 0.90);
  translate([161, 0, 0]) colored_box([5, 268, carrier_t], [0.15, 0.66, 0.38], 0.90);
}

// Controlled A1-A6 and C1-C6 rigid panel-to-PCB supports. Panel/frame screws
// and connector fasteners are separate systems and are not represented here.
for (p = audio_supports) translate([p[0], p[1], carrier_z + carrier_t]) pcb_standoff();
for (p = carrier_supports) translate([p[0], p[1], carrier_z + carrier_t]) pcb_standoff();

// Guarded hinge/display-side PSU bay on the bottom floor. The supply is rotated
// 90 degrees in plan and moved into the digital side to protect the audio zone.
translate([250, 21, tray_top_z]) colored_box([86, 130, 43], [0.82, 0.25, 0.20], 0.75);
color([0.95, 0.47, 0.39, 0.22]) translate([psu_guard_x, 15, 0]) cube([98, 142, psu_guard_top_z]);

// Carrier B.Cu keepout directly above the guarded PSU bay.
color([0.95, 0.47, 0.39, 0.52]) translate([psu_guard_x, 15, carrier_z - 0.3]) difference() {
  cube([98, 142, 0.6]);
  translate([2, 2, -0.1]) cube([94, 138, 0.8]);
}

// Power selector board remains in the center/operator-side floor bay.
translate([96, 190, tray_top_z]) colored_box([116, 80, 18], [0.62, 0.37, 0.80], 0.62);

// CM5 cooling cartridge on carrier B.Cu, facing down.
cpu_x = 318.5;
cpu_y = 240.0;
translate([cpu_x, cpu_y, 55.0]) colored_box([55, 40, 1.6], [0.12, 0.70, 0.38], 0.95);
translate([cpu_x, cpu_y, cpu_cm5_bottom_z - cpu_sink_h]) finned_sink([55, 40, cpu_sink_h]);
translate([cpu_x + 2, cpu_y + 1, cpu_cm5_bottom_z - cpu_sink_h - cpu_adapter_h]) colored_box([51, 38, cpu_adapter_h], [0.55, 0.30, 0.67], 0.75);
translate([cpu_x + 7.5, cpu_y, cpu_fan_bottom_z]) fan_body([40, 40, cpu_fan_h], "z");
color([0.78, 0.48, 0.90]) translate([cpu_x - 4, cpu_y - 4, cpu_fan_bottom_z]) difference() {
  cube([63, 48, 43]);
  translate([4, 4, -1]) cube([55, 40, 45]);
}

// Universal 3052 M.2 WWAN cooling cartridge on carrier B.Cu, facing down.
modem_x = 350.0;
modem_y = 116.0;
translate([modem_x, modem_y, 54.0]) colored_box([30, 52, 1.2], [0.83, 0.60, 0.18], 0.95);
translate([modem_x - 5, modem_y + 6, modem_card_bottom_z - modem_sink_h]) finned_sink([40, 40, modem_sink_h]);
translate([modem_x - 3, modem_y + 7, modem_card_bottom_z - modem_sink_h - modem_adapter_h]) colored_box([36, 38, modem_adapter_h], [0.55, 0.30, 0.67], 0.75);
translate([modem_x - 5, modem_y + 6, modem_fan_bottom_z]) fan_body([40, 40, modem_fan_h], "z", [0.22, 0.42, 0.62]);

// Right-side filtered intake and operator-side exhaust.
translate([inner_x - 20, 190, 24]) fan_body([20, 40, 40], "x", [0.18, 0.55, 0.34]);
translate([290, inner_y - 20, 24]) fan_body([40, 20, 40], "y", [0.72, 0.52, 0.20]);

// Audio quiet boundary and airflow guides.
color([0.12, 0.70, 0.78, 0.30]) translate([audio_quiet_boundary_x, 10, 0]) cube([2, 278, panel_underside_z]);
color([0.40, 0.72, 1.00, 0.28]) hull() {
  translate([406, 210, 44]) sphere(d = 8);
  translate([340, 180, 44]) sphere(d = 8);
}
color([0.40, 0.72, 1.00, 0.24]) hull() {
  translate([340, 180, 44]) sphere(d = 8);
  translate([310, 280, 44]) sphere(d = 8);
}
// Low-velocity clean-air wash through the perforated PSU guard.
color([0.40, 0.72, 1.00, 0.20]) hull() {
  translate([394, 205, 38]) sphere(d = 7);
  translate([332, 145, 38]) sphere(d = 7);
  translate([275, 80, 38]) sphere(d = 7);
}

// Protected HDMI, USB-touch, and 12 V lid-harness lane beside the PSU guard.
color([0.26, 0.56, 0.94, 0.34]) hull() {
  translate([205, 18, 53]) sphere(d = 8);
  translate([219, 70, 53]) sphere(d = 8);
  translate([219, 238, 53]) sphere(d = 8);
  translate([248, 260, 53]) sphere(d = 8);
}

// Reference labels are raised so they remain visible in preview renders.
color("white") translate([246, 9, 49]) linear_extrude(0.7) text("PSU GUARD <=48 / 146 mm AUDIO GAP", size = 3.9);
color("white") translate([307, 238, 66]) linear_extrude(0.7) text("CM5", size = 6);
color("white") translate([333, 113, 66]) linear_extrude(0.7) text("WWAN", size = 5);
color("white") translate([16, 145, 66]) linear_extrude(0.7) text("AUDIO QUIET", size = 5);
