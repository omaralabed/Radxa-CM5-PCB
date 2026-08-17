#!/usr/bin/env python3
"""Validate native PCB-A0 outlines and every source-controlled placement.

Run with KiCad's bundled Python interpreter. This validator intentionally fails
if an unverified schematic footprint enters a board outline.
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
        "schematic_footprints": 507,
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


def source_footprint(identifier: str) -> pcbnew.FOOTPRINT:
    library, name = identifier.split(":", 1)
    library_path = LOCAL_FP.get(library, GLOBAL_FP / f"{library}.pretty")
    footprint = pcbnew.FootprintLoad(str(library_path), name)
    if footprint is None:
        raise RuntimeError(f"Cannot load source footprint {identifier}")
    return footprint


def pad_signature(footprint: pcbnew.FOOTPRINT) -> tuple:
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
                round(pcbnew.ToMM(relative.y), 6),
                round(pad.GetFPRelativeOrientation().AsDegrees() % 360.0, 6),
                round(pcbnew.ToMM(size.x), 6),
                round(pcbnew.ToMM(size.y), 6),
                round(pcbnew.ToMM(drill.x), 6),
                round(pcbnew.ToMM(drill.y), 6),
                int(pad.GetShape()),
                int(pad.GetDrillShape()),
                int(pad.GetAttribute()),
                pad.GetLayerSet().FmtHex(),
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
        if pad_signature(footprints[reference]) != pad_signature(source_footprint(identifier)):
            return False
    return True


def support_contract() -> dict[str, dict[str, tuple[float, float]]]:
    supports: dict[str, dict[str, tuple[float, float]]] = {
        "AUDIO-8X8": {},
        "CM5-CARRIER": {},
    }
    with SUPPORT_CSV.open(newline="") as stream:
        for row in csv.DictReader(stream):
            supports[row["board"]][row["support_id"]] = (
                float(row["x_board_mm"]),
                float(row["y_board_mm"]),
            )
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
        "J610": (39.715, 32.700, 0.0, "F.Cu", "CM5Carrier:T_Wurth_WE-RJ45LAN_74991114412"),
        "J611": (109.715, 32.700, 0.0, "F.Cu", "CM5Carrier:T_Wurth_WE-RJ45LAN_74991114412"),
        "J612": (39.715, 66.700, 0.0, "F.Cu", "CM5Carrier:T_Wurth_WE-RJ45LAN_74991114412"),
        "J613": (109.715, 66.700, 0.0, "F.Cu", "CM5Carrier:T_Wurth_WE-RJ45LAN_74991114412"),
        "J702": (85.000, 120.000, 0.0, "F.Cu", "CM5Carrier:J_Wurth_WR-CRD_693043020611"),
        "J703": (134.000, 120.000, 0.0, "F.Cu", "CM5Carrier:J_Wurth_WR-CRD_693043020611"),
        "J501": (127.000, 245.000, 90.0, "B.Cu", "CM5Carrier:Radxa_CM5_U33A_DF40C_100DS_OFFICIAL"),
        "J502": (127.000, 245.000, 90.0, "B.Cu", "CM5Carrier:Radxa_CM5_U33B_DF40C_100DS_OFFICIAL"),
        "J503": (152.415, 233.595, 180.0, "B.Cu", "CM5Carrier:Radxa_CM5_J24_DF40C_100DS_OFFICIAL"),
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
        else fixed_carrier_contract() if name == "CM5-CARRIER" else {}
    )
    expected_locked = set(fixed) | set(supports)
    actual_locked = {reference for reference, item in footprints.items() if item.IsLocked()}
    width, height = contract["size"]
    staged_ok = all(
        position(item)[0] > width
        for reference, item in footprints.items()
        if reference not in expected_locked
    )
    schematic_count = schematic_footprint_count(contract["schematic"])
    settings = board.GetDesignSettings()
    source_geometry_exclusions = {"J501", "J502", "J503"}
    checks = [
        check(f"{name} outline", outline_is_exact(board, width, height), f"{width:.1f} x {height:.1f} mm rectangle"),
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
        check(f"{name} staging", staged_ok, "every unverified schematic footprint is outside the board outline"),
        check(f"{name} routing state", len(board.GetTracks()) == 0 and board.GetAreaCount() == 0, "no tracks, vias, or zones in PCB-A0 placement baseline"),
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
