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
SUPPORT_PATH = ROOT / "pcb-support-pattern-a2.csv"
LOAD_PATH_PATH = ROOT / "connector-load-path-a2.csv"
MEASUREMENT_COUNT = 80


def load_inputs() -> tuple[dict, list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    with DATA_PATH.open(encoding="utf-8") as stream:
        data = json.load(stream)
    with REGISTER_PATH.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    with SUPPORT_PATH.open(newline="", encoding="utf-8") as stream:
        supports = list(csv.DictReader(stream))
    with LOAD_PATH_PATH.open(newline="", encoding="utf-8") as stream:
        load_paths = list(csv.DictReader(stream))
    return data, rows, supports, load_paths


def require(condition: bool, message: str, failures: list[str]) -> None:
    if condition:
        print(f"PASS: {message}")
    else:
        failures.append(message)
        print(f"FAIL: {message}")


def present(value: object) -> bool:
    return value not in (None, "", "TBD")


def validate_package(
    data: dict,
    rows: list[dict[str, str]],
    supports: list[dict[str, str]],
    load_paths: list[dict[str, str]],
) -> list[str]:
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
    require(hard.get("maximum_long_pcb_support_row_span_mm") <= 128.0, "long-PCB support-row span is limited to 128 mm", failures)
    require(hard.get("pcb_mount_finished_hole_diameter_mm") == 3.4, "PCB mount finished-hole target is 3.4 mm", failures)
    require(hard.get("pcb_mount_finished_hole_tolerance_mm") <= 0.1, "PCB mount finished-hole tolerance is at most 0.1 mm", failures)
    require(hard.get("minimum_pcb_mount_hole_center_edge_distance_mm") >= 5.0, "PCB mount hole centers remain at least 5.0 mm from board edges", failures)
    require(hard.get("minimum_pcb_mount_copper_keepout_diameter_mm") >= 8.0, "PCB mount all-layer copper keepout is at least 8.0 mm", failures)
    require(hard.get("minimum_pcb_mount_component_keepout_diameter_mm") >= 10.0, "PCB mount component keepout is at least 10.0 mm", failures)
    require(hard.get("minimum_closed_lid_dynamic_clearance_mm") >= 12.7, "closed-lid dynamic clearance target is at least 12.7 mm / 0.50 in", failures)
    require(hard.get("minimum_psu_guard_vertical_clearance_mm") >= 10.0, "PSU guard vertical clearance target is at least 10 mm", failures)
    require(hard.get("maximum_installed_psu_guard_height_above_deepest_floor_mm") <= 48.0, "installed PSU guard envelope is limited to 48 mm above the deepest floor", failures)
    require(hard.get("minimum_dedicated_fan_inlet_clearance_mm") >= 10.0, "dedicated fan inlet clearance is at least 10 mm", failures)
    require(hard.get("minimum_fan_audio_separation_mm") >= 100.0, "fan/audio separation target is at least 100 mm", failures)
    require(hard.get("minimum_psu_audio_separation_mm") >= 125.0, "PSU/audio separation target is at least 125 mm", failures)
    require(hard.get("minimum_lid_harness_psu_guard_clearance_mm") >= 15.0, "lid-harness/PSU guard clearance target is at least 15 mm", failures)
    require(hard.get("battery_engagement_direction") == "LEFT_TO_RIGHT", "battery engagement direction is locked left to right", failures)
    require(data.get("battery_dock", {}).get("removal_direction") == "RIGHT_TO_LEFT", "battery removal direction is locked right to left", failures)
    require(data.get("transport_configuration", {}).get("battery") == "REMOVE_BEFORE_CLOSING", "transport closure requires battery removal", failures)
    require(data.get("transport_configuration", {}).get("external_rf_antennas") == "KEEP_INSTALLED_AND_FOLD_INBOARD_BEFORE_CLOSING", "transport closure keeps the released antennas installed and folded inboard", failures)
    rf_antennas = data.get("rf_antennas", {})
    require(rf_antennas.get("wifi", {}).get("candidate_part") == "Taoglas GW.05.0153", "compact hinged Wi-Fi antenna candidate is controlled", failures)
    require(rf_antennas.get("wifi", {}).get("antenna_connector") == "RP-SMA(M)", "Wi-Fi antenna uses RP-SMA polarity", failures)
    require(rf_antennas.get("cellular", {}).get("candidate_part") == "Taoglas TG.66.A113", "compact hinged cellular antenna candidate is controlled", failures)
    require(rf_antennas.get("cellular", {}).get("antenna_connector") == "SMA(M)", "cellular antenna uses standard SMA polarity", failures)
    require(rf_antennas.get("transport_fold_direction") == "INBOARD_TOWARD_PANEL_CENTER", "all eight antennas fold inboard for transport", failures)
    require(rf_antennas.get("bulkhead_center_pitch_mm") >= 34.0, "RF bulkhead center pitch is at least 34 mm", failures)
    require(data.get("released_panel", {}).get("target_thickness_mm") == 3.175, "panel target thickness is 3.175 mm", failures)
    require(data.get("bottom_equipment_tray", {}).get("target_thickness_mm") == 2.0, "bottom equipment tray target thickness is 2.0 mm", failures)
    display = data.get("display", {})
    require(display.get("body_dimension_status") == "DOCUMENTED_NOMINAL", "monitor body envelope is controlled as documented nominal data", failures)
    require(display.get("body_width_mm") == 396.24, "monitor documented body width is 396.24 mm", failures)
    require(display.get("body_height_mm") == 203.2, "monitor documented body height is 203.20 mm", failures)
    require(display.get("body_depth_mm") == 20.32, "monitor documented body depth is 20.32 mm", failures)
    require(display.get("body_sample_measurement_required") is False, "monitor body dimensions do not require duplicate sample measurement", failures)
    require(display.get("installation_fit_verification_required") is True, "installed monitor stack still requires physical fit verification", failures)
    require(display.get("mounting_method") == "DIRECT_TO_LID_OUTSIDE_IN_SEALED_FASTENERS", "monitor uses the controlled direct-to-lid sealed mounting method", failures)
    require(display.get("vesa_pattern_used") is False, "monitor VESA pattern is explicitly not used", failures)
    require(display.get("connector_edge_orientation") == "HINGE_SIDE", "monitor connector edge faces the hinge-side harness corridor", failures)
    thermal = data.get("thermal_release", {})
    require(thermal.get("qualification_ambient_c") >= 45.0, "thermal qualification ambient is at least 45 C", failures)
    require(thermal.get("minimum_clean_filter_through_case_cfm") >= 15.0, "clean-filter through-case airflow target is at least 15 CFM", failures)
    require(thermal.get("maximum_psu_inlet_air_temperature_c") <= 50.0, "PSU inlet-air release limit is at most 50 C", failures)

    support_ids = [row["support_id"] for row in supports]
    require(len(support_ids) == len(set(support_ids)), "PCB support IDs are unique", failures)
    support_spec = data.get("pcb_supports", {})
    board_specs = {
        "AUDIO-8X8": (support_spec.get("audio_8x8", {}), "A", 6),
        "CM5-CARRIER": (support_spec.get("cm5_carrier", {}), "C", 6),
    }
    for board, (spec, prefix, count) in board_specs.items():
        board_rows = [row for row in supports if row["board"] == board]
        expected_ids = [f"{prefix}{index}" for index in range(1, count + 1)]
        require(len(board_rows) == count, f"{board} has exactly six controlled supports", failures)
        require(sorted(row["support_id"] for row in board_rows) == expected_ids, f"{board} support IDs are contiguous", failures)
        origin = spec.get("board_origin_panel_mm", [])
        size = spec.get("board_size_mm", [])
        require(len(origin) == 2 and len(size) == 2, f"{board} support datum and board size are defined", failures)
        if len(origin) != 2 or len(size) != 2:
            continue
        y_rows: set[float] = set()
        minimum_edge_distance = float(support_spec.get("mount_interface", {}).get("minimum_hole_center_edge_distance_mm", 5.0))
        for row in board_rows:
            x_board = float(row["x_board_mm"])
            y_board = float(row["y_board_mm"])
            x_panel = float(row["x_panel_mm"])
            y_panel = float(row["y_panel_mm"])
            y_rows.add(y_board)
            require(minimum_edge_distance <= x_board <= float(size[0]) - minimum_edge_distance, f'{row["support_id"]} keeps the controlled center distance from board X edges', failures)
            require(minimum_edge_distance <= y_board <= float(size[1]) - minimum_edge_distance, f'{row["support_id"]} keeps the controlled center distance from board Y edges', failures)
            require(abs(x_panel - (float(origin[0]) + x_board)) < 0.001, f'{row["support_id"]} panel X matches its board datum', failures)
            require(abs(y_panel - (float(origin[1]) + y_board)) < 0.001, f'{row["support_id"]} panel Y matches its board datum', failures)
            require(abs(float(row["hole_diameter_mm"]) - 3.4) < 0.001, f'{row["support_id"]} uses a 3.4 mm finished NPTH', failures)
            require(float(row["copper_keepout_diameter_mm"]) >= 8.0, f'{row["support_id"]} has at least an 8 mm copper keepout', failures)
            require(float(row["component_keepout_diameter_mm"]) >= 10.0, f'{row["support_id"]} has at least a 10 mm component keepout', failures)
            require(row["hardware"] == "M3_CAPTIVE_METAL_STANDOFF", f'{row["support_id"]} uses a rigid captive M3 metal standoff', failures)
        ordered_y = sorted(y_rows)
        spans = [right - left for left, right in zip(ordered_y, ordered_y[1:])]
        require(len(ordered_y) >= 3 and max(spans, default=0.0) <= 128.0, f"{board} uses at least three support rows with no span above 128 mm", failures)

    # Support component keepouts must not touch the verified Neutrik courtyards.
    audio_rows = [row for row in supports if row["board"] == "AUDIO-8X8"]
    xlr_courtyards = []
    for y in (19.0, 51.0, 83.0, 115.0, 147.0, 179.0, 211.0, 243.0):
        xlr_courtyards.append((-1.91, y - 13.3, 24.39, y + 14.5))  # NC3MAV
        xlr_courtyards.append((41.49, y - 13.3, 67.79, y + 14.5))  # NC3FAV

    def circle_clears_rect(x: float, y: float, radius: float, rect: tuple[float, float, float, float]) -> bool:
        left, top, right, bottom = rect
        nearest_x = min(max(x, left), right)
        nearest_y = min(max(y, top), bottom)
        return ((x - nearest_x) ** 2 + (y - nearest_y) ** 2) ** 0.5 >= radius

    audio_clear = all(
        circle_clears_rect(
            float(row["x_board_mm"]),
            float(row["y_board_mm"]),
            float(row["component_keepout_diameter_mm"]) / 2.0,
            courtyard,
        )
        for row in audio_rows
        for courtyard in xlr_courtyards
    )
    require(audio_clear, "AUDIO support component keepouts clear all verified Neutrik courtyards", failures)

    carrier_rows = [row for row in supports if row["board"] == "CM5-CARRIER"]
    modem_center = (146.0, 127.0)
    modem_clear = all(
        ((float(row["x_board_mm"]) - modem_center[0]) ** 2 + (float(row["y_board_mm"]) - modem_center[1]) ** 2) ** 0.5 >= 25.0
        for row in carrier_rows
    )
    require(modem_clear, "carrier support component keepouts clear the preliminary modem cooling keepout", failures)
    cm5_rect = (97.0, 222.5, 157.0, 267.5)
    cm5_clear = all(
        not (
            cm5_rect[0] - 5.0 < float(row["x_board_mm"]) < cm5_rect[2] + 5.0
            and cm5_rect[1] - 5.0 < float(row["y_board_mm"]) < cm5_rect[3] + 5.0
        )
        for row in carrier_rows
    )
    require(cm5_clear, "carrier support component keepouts clear the preliminary CM5 cooling cartridge", failures)

    load_policy = data.get("connector_load_policy", {})
    require(load_policy.get("policy") == "PANEL_OR_FRAME_CARRIES_ALL_USER_MATING_LOADS", "all user mating loads are assigned to panel or frame", failures)
    require(load_policy.get("forbidden_load_path") == "PCB_SOLDER_ONLY", "solder-only connector retention is explicitly forbidden", failures)
    required_interfaces = {
        "Balanced XLR", "RJ45", "CTIA headset", "Nano-SIM", "Fused C14 inlet",
        "LEMO backup inlet", "Main power rocker", "Panel lights and touch switch",
        "Status indicators", "RF bulkheads", "Gold Mount dock", "Display HDMI USB and 12 V",
    }
    require({row["interface"] for row in load_paths} == required_interfaces, "connector load-path matrix covers every controlled interface group", failures)
    external_rows = [row for row in load_paths if row["external_user_access"] == "YES"]
    require(all(row["primary_load_path"] != "PCB_SOLDER_ONLY" for row in external_rows), "no external connector uses solder-only retention", failures)
    require(all(row["status"] in {"CONTROLLED", "BRACKET_REQUIRED"} for row in external_rows), "every external connector has a controlled or required structural load path", failures)
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
        ("maximum folded RF antenna protrusion", data["closed_lid"].get("maximum_folded_rf_antenna_protrusion_mm")),
        ("folded RF antenna sweep record", data["closed_lid"].get("rf_folded_sweep_record")),
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
    data, rows, supports, load_paths = load_inputs()
    failures = validate_package(data, rows, supports, load_paths)
    if args.release:
        failures.extend(validate_release(data, rows))
    if failures:
        print(f"RESULT: {len(failures)} failure(s)")
        return 1
    print("RESULT: mechanical package is internally consistent" + (" and released" if args.release else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
