// ProComm iM2300 cooling clearance concept Rev A.
// All dimensions are millimeters and remain preliminary until the actual case is measured.
$fn = 48;

inner_x = 431.8;
inner_y = 298.0;
bottom_depth = 106.7;
panel_below_parting = 38.1;
panel_z = bottom_depth - panel_below_parting; // 68.6 mm above nominal floor.
panel_t = 3.0;
carrier_z = 58.0;
carrier_t = 1.6;

cpu_cm5_bottom_z = 53.4;
cpu_sink_h = 10.0;
cpu_adapter_h = 5.0;
cpu_fan_h = 28.0;
cpu_fan_bottom_z = cpu_cm5_bottom_z - cpu_sink_h - cpu_adapter_h - cpu_fan_h;
cpu_floor_gap = cpu_fan_bottom_z;

modem_card_bottom_z = 53.0;
modem_sink_h = 8.0;
modem_adapter_h = 4.0;
modem_fan_h = 20.0;
modem_fan_bottom_z = modem_card_bottom_z - modem_sink_h - modem_adapter_h - modem_fan_h;
modem_floor_gap = modem_fan_bottom_z;

assert(cpu_floor_gap >= 10.0, "CM5 dedicated fan inlet clearance is below 10 mm");
assert(modem_floor_gap >= 10.0, "Modem dedicated fan inlet clearance is below 10 mm");
echo(str("Panel plane above floor: ", panel_z, " mm"));
echo(str("CM5 fan inlet gap: ", cpu_floor_gap, " mm"));
echo(str("Modem fan inlet gap: ", modem_floor_gap, " mm"));

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

// Transparent nominal cavity and floor.
color([0.75, 0.80, 0.84, 0.10]) difference() {
  translate([-4, -4, 0]) cube([inner_x + 8, inner_y + 8, bottom_depth]);
  translate([0, 0, 3]) cube([inner_x, inner_y, bottom_depth]);
}
color([0.20, 0.23, 0.27]) cube([inner_x, inner_y, 3]);

// Top-panel perimeter reference only, leaving the interior open for inspection.
// The actual panel is a solid plate with no cooling cutouts.
translate([0, 0, panel_z]) {
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

// Guarded hinge/display-side PSU bay on the bottom floor.
translate([125, 15, 3]) colored_box([130, 86, 43], [0.82, 0.25, 0.20], 0.75);
color([0.95, 0.47, 0.39, 0.22]) translate([119, 9, 3]) cube([142, 98, 47]);

// Power selector board remains in the center/operator-side floor bay.
translate([96, 190, 3]) colored_box([116, 80, 18], [0.62, 0.37, 0.80], 0.62);

// CM5 cooling cartridge on carrier B.Cu, facing down.
cpu_x = 318.5;
cpu_y = 240.0;
translate([cpu_x, cpu_y, 55.0]) colored_box([55, 40, 1.6], [0.12, 0.70, 0.38], 0.95);
translate([cpu_x, cpu_y, cpu_cm5_bottom_z - cpu_sink_h]) finned_sink([55, 40, cpu_sink_h]);
translate([cpu_x + 2, cpu_y + 1, cpu_cm5_bottom_z - cpu_sink_h - cpu_adapter_h]) colored_box([51, 38, cpu_adapter_h], [0.55, 0.30, 0.67], 0.75);
translate([cpu_x + 7.5, cpu_y, cpu_fan_bottom_z]) fan_body([40, 40, cpu_fan_h], "z");
color([0.78, 0.48, 0.90]) translate([cpu_x - 4, cpu_y - 4, cpu_fan_bottom_z]) difference() {
  cube([63, 48, 45]);
  translate([4, 4, -1]) cube([55, 40, 47]);
}

// Universal 3052 M.2 WWAN cooling cartridge on carrier B.Cu, facing down.
modem_x = 340.5;
modem_y = 116.0;
translate([modem_x, modem_y, 54.0]) colored_box([30, 52, 1.2], [0.83, 0.60, 0.18], 0.95);
translate([modem_x - 5, modem_y + 6, modem_card_bottom_z - modem_sink_h]) finned_sink([40, 40, modem_sink_h]);
translate([modem_x - 3, modem_y + 7, modem_card_bottom_z - modem_sink_h - modem_adapter_h]) colored_box([36, 38, modem_adapter_h], [0.55, 0.30, 0.67], 0.75);
translate([modem_x - 5, modem_y + 6, modem_fan_bottom_z]) fan_body([40, 40, modem_fan_h], "z", [0.22, 0.42, 0.62]);

// Right-side filtered intake and operator-side exhaust.
translate([inner_x - 20, 190, 24]) fan_body([20, 40, 40], "x", [0.18, 0.55, 0.34]);
translate([290, inner_y - 20, 24]) fan_body([40, 20, 40], "y", [0.72, 0.52, 0.20]);

// Audio quiet boundary and airflow guides.
color([0.12, 0.70, 0.78, 0.30]) translate([98, 10, 3]) cube([2, 278, panel_z - 3]);
color([0.40, 0.72, 1.00, 0.28]) hull() {
  translate([406, 210, 44]) sphere(d = 8);
  translate([340, 180, 44]) sphere(d = 8);
}
color([0.40, 0.72, 1.00, 0.24]) hull() {
  translate([340, 180, 44]) sphere(d = 8);
  translate([310, 280, 44]) sphere(d = 8);
}

// Reference labels are raised so they remain visible in preview renders.
color("white") translate([125, 7, 48]) linear_extrude(0.7) text("HINGE-SIDE PSU", size = 6);
color("white") translate([307, 238, 66]) linear_extrude(0.7) text("CM5", size = 6);
color("white") translate([333, 113, 66]) linear_extrude(0.7) text("WWAN", size = 5);
color("white") translate([16, 145, 66]) linear_extrude(0.7) text("AUDIO QUIET", size = 5);
