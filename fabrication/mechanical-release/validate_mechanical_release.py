#!/usr/bin/env python3
"""Validate the iM2300 mechanical data package and optional release evidence."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "mechanical-release-a2.json"
REGISTER_PATH = ROOT / "im2300-measurement-register.csv"
MEASUREMENT_COUNT = 80


def load_inputs() -> tuple[dict, list[dict[str, str]]]:
    with DATA_PATH.open(encoding="utf-8") as stream:
        data = json.load(stream)
    with REGISTER_PATH.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    return data, rows


def require(condition: bool, message: str, failures: list[str]) -> None:
    if condition:
        print(f"PASS: {message}")
    else:
        failures.append(message)
        print(f"FAIL: {message}")


def present(value: object) -> bool:
    return value not in (None, "", "TBD")


def validate_package(data: dict, rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    ids = [row["id"] for row in rows]
    require(len(rows) == MEASUREMENT_COUNT, f"measurement register contains {MEASUREMENT_COUNT} controlled checks", failures)
    require(len(ids) == len(set(ids)), "measurement IDs are unique", failures)
    require(ids == [f"M{index:03d}" for index in range(1, MEASUREMENT_COUNT + 1)], "measurement IDs are contiguous", failures)
    require(data.get("revision") == "A2", "release data revision is A2", failures)
    hard = data.get("hard_constraints", {})
    require(hard.get("minimum_perimeter_no_pcb_band_mm") >= 15.0, "perimeter no-PCB band is at least 15 mm", failures)
    require(hard.get("audio_pcb_max_width_mm") <= 78.0, "audio PCB width is limited to 78 mm", failures)
    require(hard.get("audio_pcb_max_height_mm") <= 268.0, "audio PCB height is limited to 268 mm", failures)
    require(hard.get("carrier_pcb_max_width_mm") <= 166.0, "carrier PCB width is limited to 166 mm", failures)
    require(hard.get("carrier_pcb_max_height_mm") <= 268.0, "carrier PCB height is limited to 268 mm", failures)
    require(hard.get("minimum_audio_pcb_support_count") >= 6, "audio PCB uses at least six supports", failures)
    require(hard.get("minimum_carrier_pcb_support_count") >= 6, "carrier PCB uses at least six supports", failures)
    require(hard.get("minimum_closed_lid_dynamic_clearance_mm") >= 8.0, "closed-lid dynamic clearance target is at least 8 mm", failures)
    require(hard.get("minimum_psu_guard_vertical_clearance_mm") >= 10.0, "PSU guard vertical clearance target is at least 10 mm", failures)
    require(hard.get("maximum_installed_psu_guard_height_above_deepest_floor_mm") <= 48.0, "installed PSU guard envelope is limited to 48 mm above the deepest floor", failures)
    require(hard.get("minimum_dedicated_fan_inlet_clearance_mm") >= 10.0, "dedicated fan inlet clearance is at least 10 mm", failures)
    require(hard.get("minimum_fan_audio_separation_mm") >= 100.0, "fan/audio separation target is at least 100 mm", failures)
    require(hard.get("minimum_psu_audio_separation_mm") >= 125.0, "PSU/audio separation target is at least 125 mm", failures)
    require(hard.get("minimum_lid_harness_psu_guard_clearance_mm") >= 15.0, "lid-harness/PSU guard clearance target is at least 15 mm", failures)
    require(hard.get("battery_engagement_direction") == "LEFT_TO_RIGHT", "battery engagement direction is locked left to right", failures)
    require(data.get("battery_dock", {}).get("removal_direction") == "RIGHT_TO_LEFT", "battery removal direction is locked right to left", failures)
    require(data.get("transport_configuration", {}).get("battery") == "REMOVE_BEFORE_CLOSING", "transport closure requires battery removal", failures)
    require(data.get("transport_configuration", {}).get("external_rf_antennas") == "REMOVE_AND_INSTALL_DUST_CAPS_BEFORE_CLOSING", "transport closure requires antennas removed and capped", failures)
    require(data.get("released_panel", {}).get("target_thickness_mm") == 3.175, "panel target thickness is 3.175 mm", failures)
    require(data.get("bottom_equipment_tray", {}).get("target_thickness_mm") == 2.0, "bottom equipment tray target thickness is 2.0 mm", failures)
    thermal = data.get("thermal_release", {})
    require(thermal.get("qualification_ambient_c") >= 45.0, "thermal qualification ambient is at least 45 C", failures)
    require(thermal.get("minimum_clean_filter_through_case_cfm") >= 15.0, "clean-filter through-case airflow target is at least 15 CFM", failures)
    require(thermal.get("maximum_psu_inlet_air_temperature_c") <= 50.0, "PSU inlet-air release limit is at most 50 C", failures)
    return failures


def validate_release(data: dict, rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    required_paths = [
        ("panel recess", data.get("panel_recess_mm")),
        ("case asset ID", data["actual_case"].get("serial_or_asset_id")),
        ("opening width minimum", data["actual_case"].get("opening_width_min_mm")),
        ("opening width maximum", data["actual_case"].get("opening_width_max_mm")),
        ("opening depth minimum", data["actual_case"].get("opening_depth_min_mm")),
        ("opening depth maximum", data["actual_case"].get("opening_depth_max_mm")),
        ("diagonal difference", data["actual_case"].get("diagonal_difference_mm")),
        ("panel width", data["released_panel"].get("width_mm")),
        ("panel depth", data["released_panel"].get("depth_mm")),
        ("panel corner radius", data["released_panel"].get("corner_radius_mm")),
        ("panel thickness", data["released_panel"].get("thickness_mm")),
        ("deepest-floor to panel top", data["actual_case"].get("deepest_floor_to_panel_top_mm")),
        ("deepest-floor to panel underside", data["actual_case"].get("deepest_floor_to_panel_underside_mm")),
        ("bottom tray top elevation", data["bottom_equipment_tray"].get("measured_top_above_deepest_floor_mm")),
        ("bottom tray drawing ID", data["bottom_equipment_tray"].get("drawing_id")),
        ("frame drawing ID", data["frame"].get("drawing_id")),
        ("minimum frame support", data["frame"].get("minimum_support_width_mm")),
        ("minimum closed-lid clearance", data["closed_lid"].get("minimum_dynamic_clearance_mm")),
        ("closed-lid inspection record", data["closed_lid"].get("inspection_record")),
        ("monitor body width", data["display"].get("body_width_mm")),
        ("monitor body height", data["display"].get("body_height_mm")),
        ("monitor body depth", data["display"].get("body_depth_mm")),
        ("monitor total protrusion", data["display"].get("total_lid_protrusion_mm")),
        ("monitor connector keepout record", data["display"].get("connector_keepout_record")),
        ("monitor mounting drawing ID", data["display"].get("mounting_drawing_id")),
        ("battery slide travel", data["battery_dock"].get("slide_travel_mm")),
        ("battery left insertion corridor", data["battery_dock"].get("measured_left_insertion_corridor_mm")),
        ("battery dock backplate installed", data["battery_dock"].get("backplate_installed")),
        ("battery engagement inspection record", data["battery_dock"].get("inspection_record")),
        ("thermal airflow record", data["thermal_release"].get("airflow_record")),
        ("PSU bay temperature record", data["thermal_release"].get("psu_bay_temperature_record")),
        ("measurement signoff", data["signoff"].get("measured_by")),
        ("mechanical review signoff", data["signoff"].get("mechanical_reviewed_by")),
        ("electrical review signoff", data["signoff"].get("electrical_reviewed_by")),
        ("thermal review signoff", data["signoff"].get("thermal_reviewed_by")),
    ]
    for name, value in required_paths:
        require(present(value), f"release evidence present: {name}", failures)

    complete_rows = [row for row in rows if row["status"] == "COMPLETE"]
    require(len(complete_rows) == len(rows), "all measurement-register rows are COMPLETE", failures)
    require(data.get("release_state") == "RELEASED_FOR_LAYOUT", "release state is RELEASED_FOR_LAYOUT", failures)

    if present(data["frame"].get("minimum_support_width_mm")):
        require(float(data["frame"]["minimum_support_width_mm"]) >= 15.0, "measured frame support is at least 15 mm", failures)
    if present(data["closed_lid"].get("minimum_dynamic_clearance_mm")):
        require(float(data["closed_lid"]["minimum_dynamic_clearance_mm"]) >= 8.0, "measured closed-lid clearance is at least 8 mm", failures)
    if present(data["actual_case"].get("diagonal_difference_mm")):
        require(float(data["actual_case"]["diagonal_difference_mm"]) <= 1.0, "case opening diagonal difference is at most 1 mm", failures)
    if present(data["battery_dock"].get("measured_left_insertion_corridor_mm")):
        require(float(data["battery_dock"]["measured_left_insertion_corridor_mm"]) >= 20.0, "battery left insertion corridor is at least 20 mm", failures)
    if present(data["actual_case"].get("deepest_floor_to_panel_underside_mm")) and present(data["bottom_equipment_tray"].get("measured_top_above_deepest_floor_mm")):
        available = float(data["actual_case"]["deepest_floor_to_panel_underside_mm"]) - float(data["bottom_equipment_tray"]["measured_top_above_deepest_floor_mm"])
        require(available >= 62.0, "released tray-top to panel-underside height is at least 62 mm", failures)
    require(data["battery_dock"].get("backplate_installed") is True, "QRC-GOLD backplate installation is confirmed", failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", action="store_true", help="require completed physical measurement and signoff evidence")
    args = parser.parse_args()
    data, rows = load_inputs()
    failures = validate_package(data, rows)
    if args.release:
        failures.extend(validate_release(data, rows))
    if failures:
        print(f"RESULT: {len(failures)} failure(s)")
        return 1
    print("RESULT: mechanical package is internally consistent" + (" and released" if args.release else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
