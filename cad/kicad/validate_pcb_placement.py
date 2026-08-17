#!/usr/bin/env python3
"""Validate native PCB-A1 outlines and engineering placement.

Run with KiCad's bundled Python interpreter. This validator fails if a schematic
footprint leaves its board, violates the assembly-side contract, overlaps a
same-side courtyard, or changes any source-controlled mating geometry.
"""

from __future__ import annotations

import csv
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import pcbnew


ROOT = Path(__file__).resolve().parents[2]
KICAD_CLI = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
SUPPORT_CSV = ROOT / "fabrication/mechanical-release/pcb-support-pattern-a2.csv"
GLOBAL_FP = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")
LOCAL_FP = {
    "CM5Carrier": ROOT / "cad/kicad/CM5-CARRIER/CM5Carrier.pretty",
    "ProCommMechanical": ROOT / "cad/kicad/ProCommMechanical.pretty",
}


BOARD_CONTRACTS = {
    "AUDIO-8X8": {
        "board": ROOT / "cad/kicad/AUDIO-8X8/Audio-8x8.kicad_pcb",
        "schematic": ROOT / "cad/kicad/AUDIO-8X8/Audio-8x8.kicad_sch",
        "size": (78.0, 268.0),
        "layers": 6,
        "schematic_footprints": 572,
    },
    "CM5-CARRIER": {
        "board": ROOT / "cad/kicad/CM5-CARRIER/CM5-Carrier.kicad_pcb",
        "schematic": ROOT / "cad/kicad/CM5-CARRIER/CM5-Carrier.kicad_sch",
        "size": (166.0, 268.0),
        "layers": 10,
        "schematic_footprints": 504,
    },
    "SIM-SERVICE": {
        "board": ROOT / "cad/kicad/SIM-SERVICE/Sim-Service.kicad_pcb",
        "schematic": ROOT / "cad/kicad/SIM-SERVICE/Sim-Service.kicad_sch",
        "size": (76.0, 40.0),
        "layers": 4,
        "schematic_footprints": 5,
    },
    "PWR-SELECT": {
        "board": ROOT / "cad/kicad/PWR-SELECT/PowerSelector.kicad_pcb",
        "schematic": ROOT / "cad/kicad/PWR-SELECT/PowerSelector.kicad_sch",
        "size": (116.0, 80.0),
        "layers": 6,
        "schematic_footprints": 111,
    },
}


def check(name: str, condition: bool, detail: str) -> bool:
    print(f"{'PASS' if condition else 'FAIL'}  {name}: {detail}")
    return condition


def near(actual: float, expected: float, tolerance: float = 0.001) -> bool:
    return abs(actual - expected) <= tolerance


def position(footprint: pcbnew.FOOTPRINT) -> tuple[float, float]:
    point = footprint.GetPosition()
    return pcbnew.ToMM(point.x), pcbnew.ToMM(point.y)


def fpid(footprint: pcbnew.FOOTPRINT) -> str:
    identifier = footprint.GetFPID()
    return f"{identifier.GetLibNickname()}:{identifier.GetLibItemName()}"


def courtyard_bbox(footprint: pcbnew.FOOTPRINT) -> pcbnew.BOX2I:
    footprint.BuildCourtyardCaches()
    layer = pcbnew.B_CrtYd if footprint.GetLayer() == pcbnew.B_Cu else pcbnew.F_CrtYd
    courtyard = footprint.GetCourtyard(layer)
    return courtyard.BBox() if not courtyard.IsEmpty() else footprint.GetBoundingBox(False, False)


def bbox_mm(footprint: pcbnew.FOOTPRINT) -> tuple[float, float, float, float]:
    bbox = courtyard_bbox(footprint)
    return (
        pcbnew.ToMM(bbox.GetLeft()),
        pcbnew.ToMM(bbox.GetTop()),
        pcbnew.ToMM(bbox.GetRight()),
        pcbnew.ToMM(bbox.GetBottom()),
    )


def internal_footprints_are_inside(
    footprints: dict[str, pcbnew.FOOTPRINT],
    controlled: set[str],
    width: float,
    height: float,
) -> bool:
    for reference, footprint in footprints.items():
        if reference in controlled:
            continue
        left, top, right, bottom = bbox_mm(footprint)
        if left < 0.50 or top < 0.50 or right > width - 0.50 or bottom > height - 0.50:
            return False
    return True


def internal_courtyards_do_not_overlap(
    footprints: dict[str, pcbnew.FOOTPRINT],
    controlled: set[str],
) -> bool:
    references = sorted(footprints)
    boxes = {reference: bbox_mm(footprints[reference]) for reference in references}
    for index, reference in enumerate(references):
        footprint = footprints[reference]
        left, top, right, bottom = boxes[reference]
        for other_reference in references[index + 1 :]:
            if reference in controlled and other_reference in controlled:
                continue
            other = footprints[other_reference]
            if footprint.GetLayer() != other.GetLayer():
                continue
            other_left, other_top, other_right, other_bottom = boxes[other_reference]
            if (
                min(right, other_right) - max(left, other_left) > 0.001
                and min(bottom, other_bottom) - max(top, other_top) > 0.001
            ):
                return False
    return True


def side_contract(
    name: str,
    footprints: dict[str, pcbnew.FOOTPRINT],
    controlled: set[str],
) -> bool:
    internal = [item for reference, item in footprints.items() if reference not in controlled]
    if name == "AUDIO-8X8":
        return all(item.GetLayer() == pcbnew.B_Cu for item in internal)
    if name in {"CM5-CARRIER", "SIM-SERVICE"}:
        return all(item.GetLayer() == pcbnew.F_Cu for item in internal)
    sides = {item.GetLayer() for item in internal}
    return sides == {pcbnew.F_Cu, pcbnew.B_Cu}


def source_footprint(identifier: str) -> pcbnew.FOOTPRINT:
    library, name = identifier.split(":", 1)
    library_path = LOCAL_FP.get(library, GLOBAL_FP / f"{library}.pretty")
    footprint = pcbnew.FootprintLoad(str(library_path), name)
    if footprint is None:
        raise RuntimeError(f"Cannot load source footprint {identifier}")
    return footprint


def pad_signature(
    footprint: pcbnew.FOOTPRINT,
    *,
    mirror_y: bool = False,
    include_layers: bool = True,
) -> tuple:
    """Return all mating-relevant local pad and hole geometry."""
    records = []
    for pad in footprint.Pads():
        relative = pad.GetFPRelativePosition()
        size = pad.GetSize()
        drill = pad.GetDrillSize()
        records.append(
            (
                pad.GetNumber(),
                round(pcbnew.ToMM(relative.x), 6),
                round((-1.0 if mirror_y else 1.0) * pcbnew.ToMM(relative.y), 6),
                round(
                    ((-1.0 if mirror_y else 1.0) * pad.GetFPRelativeOrientation().AsDegrees())
                    % 360.0,
                    6,
                ),
                round(pcbnew.ToMM(size.x), 6),
                round(pcbnew.ToMM(size.y), 6),
                round(pcbnew.ToMM(drill.x), 6),
                round(pcbnew.ToMM(drill.y), 6),
                int(pad.GetShape()),
                int(pad.GetDrillShape()),
                int(pad.GetAttribute()),
                pad.GetLayerSet().FmtHex() if include_layers else "MIRRORED_SIDE",
            )
        )
    return tuple(sorted(records))


def validate_source_pad_geometry(
    footprints: dict[str, pcbnew.FOOTPRINT],
    expected: dict[str, tuple[float, float, float, str, str]],
    excluded: set[str] | None = None,
) -> bool:
    excluded = excluded or set()
    for reference, (_, _, _, _, identifier) in expected.items():
        if reference in excluded:
            continue
        actual = footprints[reference]
        source = source_footprint(identifier)
        if actual.GetLayer() == pcbnew.B_Cu and source.GetLayer() != pcbnew.B_Cu:
            if pad_signature(actual, include_layers=False) != pad_signature(
                source, mirror_y=True, include_layers=False
            ):
                return False
            continue
        if pad_signature(actual) != pad_signature(source):
            return False
    return True


def support_contract() -> dict[str, dict[str, tuple[float, float]]]:
    supports: dict[str, dict[str, tuple[float, float]]] = {
        "AUDIO-8X8": {},
        "CM5-CARRIER": {},
        "SIM-SERVICE": {},
    }
    with SUPPORT_CSV.open(newline="") as stream:
        for row in csv.DictReader(stream):
            supports[row["board"]][row["support_id"]] = (
                float(row["x_board_mm"]),
                float(row["y_board_mm"]),
            )
    # SIM-SERVICE is a horizontal daughterboard directly above the carrier.
    # These four holes align with CM5-CARRIER SD1-SD4 through 2.50 mm sleeves.
    supports["SIM-SERVICE"] = {
        "S1": (5.5, 5.5), "S2": (70.5, 5.5),
        "S3": (27.0, 34.5), "S4": (49.0, 34.5),
    }
    return supports


def schematic_footprint_count(schematic: Path) -> int:
    with tempfile.TemporaryDirectory(prefix="procomm-placement-netlist-") as temp:
        output = Path(temp) / "netlist.xml"
        subprocess.run(
            [
                str(KICAD_CLI),
                "sch",
                "export",
                "netlist",
                "--format",
                "kicadxml",
                "--output",
                str(output),
                str(schematic),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        root = ET.parse(output).getroot()
    return sum(
        1
        for component in root.findall("./components/comp")
        if component.find("property[@name='exclude_from_board']") is None
    )


def outline_is_exact(board: pcbnew.BOARD, width: float, height: float) -> bool:
    expected = {
        ((0.0, 0.0), (width, 0.0)),
        ((width, 0.0), (width, height)),
        ((0.0, height), (width, height)),
        ((0.0, 0.0), (0.0, height)),
    }
    actual = set()
    for drawing in board.GetDrawings():
        if drawing.GetLayer() != pcbnew.Edge_Cuts:
            continue
        if not isinstance(drawing, pcbnew.PCB_SHAPE):
            return False
        start = (round(pcbnew.ToMM(drawing.GetStart().x), 6), round(pcbnew.ToMM(drawing.GetStart().y), 6))
        end = (round(pcbnew.ToMM(drawing.GetEnd().x), 6), round(pcbnew.ToMM(drawing.GetEnd().y), 6))
        actual.add(tuple(sorted((start, end))))
        if not near(pcbnew.ToMM(drawing.GetWidth()), 0.1):
            return False
    return actual == {tuple(sorted(segment)) for segment in expected}


def fixed_audio_contract() -> dict[str, tuple[float, float, float, str, str]]:
    fixed = {}
    for channel in range(1, 9):
        row_y = 19.0 + 32.0 * (channel - 1)
        fixed[f"J{200 + channel}"] = (
            7.59,
            row_y,
            0.0,
            "F.Cu",
            "Connector_Audio:Jack_XLR_Neutrik_NC3MAV_Vertical",
        )
        fixed[f"J{300 + channel}"] = (
            58.59,
            row_y,
            0.0,
            "F.Cu",
            "Connector_Audio:Jack_XLR_Neutrik_NC3FAV_Vertical",
        )
    return fixed


def fixed_carrier_contract() -> dict[str, tuple[float, float, float, str, str]]:
    return {
        "J610": (34.000, 36.675, 0.0, "F.Cu", "CM5Carrier:Bel_V8BR_1AX1_GH"),
        "J611": (104.000, 36.675, 0.0, "F.Cu", "CM5Carrier:Bel_V8BR_1AX1_GH"),
        "J612": (34.000, 70.675, 0.0, "F.Cu", "CM5Carrier:Bel_V8BR_1AX1_GH"),
        "J613": (104.000, 70.675, 0.0, "F.Cu", "CM5Carrier:Bel_V8BR_1AX1_GH"),
        "J702": (
            89.500, 96.000, 0.0, "F.Cu",
            "CM5Carrier:Hirose_DF40C-20DP-0.4V_2x10-1MP_P0.4mm",
        ),
        "J501": (127.000, 245.000, 90.0, "B.Cu", "CM5Carrier:Radxa_CM5_U33A_DF40C_100DS_OFFICIAL"),
        "J502": (127.000, 245.000, 90.0, "B.Cu", "CM5Carrier:Radxa_CM5_U33B_DF40C_100DS_OFFICIAL"),
        "J503": (152.415, 233.595, 180.0, "B.Cu", "CM5Carrier:Radxa_CM5_J24_DF40C_100DS_OFFICIAL"),
    }


def fixed_sim_service_contract() -> dict[str, tuple[float, float, float, str, str]]:
    return {
        "J1": (
            38.000, 8.000, 0.0, "B.Cu",
            "CM5Carrier:Hirose_DF40HC(2.5)-20DS-0.4V_2x10_P0.4mm",
        ),
        "J2": (13.500, 32.000, 0.0, "F.Cu", "CM5Carrier:J_Wurth_WR-CRD_693043020611"),
        "J3": (62.500, 32.000, 0.0, "F.Cu", "CM5Carrier:J_Wurth_WR-CRD_693043020611"),
    }


def validate_fixed(
    footprints: dict[str, pcbnew.FOOTPRINT],
    expected: dict[str, tuple[float, float, float, str, str]],
) -> bool:
    for reference, (x, y, rotation, layer, identifier) in expected.items():
        footprint = footprints.get(reference)
        if footprint is None:
            return False
        actual_x, actual_y = position(footprint)
        if not (
            footprint.IsLocked()
            and near(actual_x, x)
            and near(actual_y, y)
            and near(footprint.GetOrientationDegrees() % 360.0, rotation % 360.0)
            and pcbnew.LayerName(footprint.GetLayer()) == layer
            and fpid(footprint) == identifier
        ):
            return False
    return True


def validate_supports(
    footprints: dict[str, pcbnew.FOOTPRINT],
    expected: dict[str, tuple[float, float]],
) -> bool:
    for reference, (x, y) in expected.items():
        footprint = footprints.get(reference)
        if footprint is None or not footprint.IsLocked():
            return False
        actual_x, actual_y = position(footprint)
        pads = list(footprint.Pads())
        if not (
            near(actual_x, x)
            and near(actual_y, y)
            and fpid(footprint) == "ProCommMechanical:ProComm_M3_Support_NPTH_3.4mm"
            and len(pads) == 1
            and near(pcbnew.ToMM(pads[0].GetDrillSize().x), 3.4)
            and near(pcbnew.ToMM(pads[0].GetSize().x), 3.4)
            and near(pcbnew.ToMM(pads[0].GetLocalClearance()), 2.3)
        ):
            return False
    return True


def validate_board(name: str, contract: dict, supports: dict[str, tuple[float, float]]) -> list[bool]:
    board = pcbnew.LoadBoard(str(contract["board"]))
    footprints = {item.GetReference(): item for item in board.GetFootprints()}
    fixed = (
        fixed_audio_contract()
        if name == "AUDIO-8X8"
        else fixed_carrier_contract() if name == "CM5-CARRIER"
        else fixed_sim_service_contract() if name == "SIM-SERVICE" else {}
    )
    expected_locked = set(fixed) | set(supports)
    actual_locked = {reference for reference, item in footprints.items() if item.IsLocked()}
    width, height = contract["size"]
    schematic_count = schematic_footprint_count(contract["schematic"])
    settings = board.GetDesignSettings()
    source_geometry_exclusions = {"J501", "J502", "J503"}
    checks = [
        check(f"{name} outline", outline_is_exact(board, width, height), f"{width:.1f} x {height:.1f} mm rectangle"),
        check(f"{name} revision", board.GetTitleBlock().GetRevision() == "PCB-A1", "PCB-A1 engineering placement"),
        check(f"{name} stack", board.GetCopperLayerCount() == contract["layers"] and near(pcbnew.ToMM(board.GetDesignSettings().GetBoardThickness()), 1.6), f"{contract['layers']} copper layers; 1.60 mm"),
        check(
            f"{name} PCBWay process rules",
            near(pcbnew.ToMM(settings.m_MinThroughDrill), 0.20)
            and near(pcbnew.ToMM(settings.m_HoleClearance), 0.20),
            "0.20 mm minimum drill and 0.20 mm NPTH-to-copper clearance",
        ),
        check(f"{name} netlist count", schematic_count == contract["schematic_footprints"] and len(footprints) == schematic_count + len(supports), f"{schematic_count} schematic footprints plus {len(supports)} supports"),
        check(f"{name} locked set", actual_locked == expected_locked, f"{len(expected_locked)} controlled footprints and no others"),
        check(f"{name} fixed connectors", validate_fixed(footprints, fixed), f"{len(fixed)} exact manufacturer/source placements"),
        check(
            f"{name} source pad identity",
            validate_source_pad_geometry(footprints, fixed, source_geometry_exclusions),
            f"{len(set(fixed) - source_geometry_exclusions)} locked connector pad/hole patterns match their source libraries",
        ),
        check(f"{name} supports", validate_supports(footprints, supports), f"{len(supports)} exact CSV positions and 3.40 mm NPTH geometry"),
        check(
            f"{name} in-board placement",
            internal_footprints_are_inside(footprints, expected_locked, width, height),
            "every schematic footprint courtyard is inside its own board",
        ),
        check(
            f"{name} assembly side",
            side_contract(name, footprints, expected_locked),
            "audio B.Cu; carrier/service F.Cu; selector split F.Cu/B.Cu",
        ),
        check(
            f"{name} same-side courtyards",
            internal_courtyards_do_not_overlap(footprints, expected_locked),
            "no internal same-side courtyard collisions",
        ),
        check(f"{name} routing state", len(board.GetTracks()) == 0 and board.GetAreaCount() == 0, "no tracks, vias, or zones in PCB-A1 placement baseline"),
    ]
    return checks


def main() -> int:
    support_map = support_contract()
    checks: list[bool] = []
    for name, contract in BOARD_CONTRACTS.items():
        checks.extend(validate_board(name, contract, support_map.get(name, {})))

    carrier = pcbnew.LoadBoard(str(BOARD_CONTRACTS["CM5-CARRIER"]["board"]))
    cm5 = {item.GetReference(): item for item in carrier.GetFootprints()}
    j501 = position(cm5["J501"])
    j502 = position(cm5["J502"])
    j503 = position(cm5["J503"])
    rigid_transform_ok = (
        j501 == j502
        and near(j503[0] - j501[0], 25.415)
        and near(j503[1] - j501[1], -11.405)
        and near((cm5["J503"].GetOrientationDegrees() - cm5["J501"].GetOrientationDegrees()) % 360.0, 90.0)
    )
    checks.append(
        check(
            "CM5 mirrored rigid-body transform",
            rigid_transform_ok,
            "J501/J502 share datum; J503 is T(x,y)=R90*mirror-X of the exact source transform",
        )
    )

    failures = len(checks) - sum(checks)
    print(f"\nRESULT: {len(checks)} checks, {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
