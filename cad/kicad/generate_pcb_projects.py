#!/usr/bin/env python3
"""Generate controlled native KiCad PCB placement baselines.

Run this script with KiCad's bundled Python interpreter. Verified mating parts are
locked to controlled datums; every other schematic footprint is staged outside
the board so an engineering drawing can never be mistaken for guessed placement.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import pcbnew


ROOT = Path(__file__).resolve().parents[2]
KICAD_CLI = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
GLOBAL_FP = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")
MECHANICAL_FP = ROOT / "cad/kicad/ProCommMechanical.pretty"
LOCAL_FP = {
    "CM5Carrier": ROOT / "cad/kicad/CM5-CARRIER/CM5Carrier.pretty",
    "PowerSelector": ROOT / "cad/kicad/PWR-SELECT/PowerSelector.pretty",
    "ProCommMechanical": MECHANICAL_FP,
}


@dataclass(frozen=True)
class BoardSpec:
    name: str
    schematic: Path
    output: Path
    width_mm: float
    height_mm: float
    copper_layers: int
    support_prefix: str
    supports: tuple[tuple[str, float, float], ...]


SPECS = (
    BoardSpec(
        "AUDIO-8X8",
        ROOT / "cad/kicad/AUDIO-8X8/Audio-8x8.kicad_sch",
        ROOT / "cad/kicad/AUDIO-8X8/Audio-8x8.kicad_pcb",
        78.0,
        268.0,
        6,
        "A",
        (
            ("A1", 32.0, 6.0),
            ("A2", 73.0, 6.0),
            ("A3", 32.0, 134.0),
            ("A4", 73.0, 134.0),
            ("A5", 32.0, 262.0),
            ("A6", 73.0, 262.0),
        ),
    ),
    BoardSpec(
        "CM5-CARRIER",
        ROOT / "cad/kicad/CM5-CARRIER/CM5-Carrier.kicad_sch",
        ROOT / "cad/kicad/CM5-CARRIER/CM5-Carrier.kicad_pcb",
        166.0,
        268.0,
        10,
        "C",
        (
            ("C1", 6.0, 6.0),
            ("C2", 160.0, 6.0),
            ("C3", 6.0, 134.0),
            ("C4", 112.0, 134.0),
            ("C5", 6.0, 262.0),
            ("C6", 160.0, 190.0),
        ),
    ),
    BoardSpec(
        "PWR-SELECT",
        ROOT / "cad/kicad/PWR-SELECT/PowerSelector.kicad_sch",
        ROOT / "cad/kicad/PWR-SELECT/PowerSelector.kicad_pcb",
        116.0,
        80.0,
        6,
        "P",
        (),
    ),
)


def mm(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I_MM(x, y)


def export_xml_netlist(schematic: Path, output: Path) -> None:
    subprocess.run(
        [
            str(KICAD_CLI),
            "sch",
            "export",
            "netlist",
            "--format",
            "kicadxml",
            "-o",
            str(output),
            str(schematic),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def component_is_on_board(comp: ET.Element) -> bool:
    return comp.find("property[@name='exclude_from_board']") is None


def footprint_path(identifier: str) -> tuple[Path, str, str]:
    library, name = identifier.split(":", 1)
    library_path = LOCAL_FP.get(library, GLOBAL_FP / f"{library}.pretty")
    return library_path, library, name


def add_segment(
    board: pcbnew.BOARD,
    start: tuple[float, float],
    end: tuple[float, float],
    layer: int,
    width_mm: float = 0.25,
) -> None:
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
    shape.SetStart(mm(*start))
    shape.SetEnd(mm(*end))
    shape.SetLayer(layer)
    shape.SetWidth(pcbnew.FromMM(width_mm))
    board.Add(shape)


def add_rect(
    board: pcbnew.BOARD,
    x: float,
    y: float,
    width: float,
    height: float,
    layer: int = pcbnew.Dwgs_User,
    line_width: float = 0.25,
) -> None:
    add_segment(board, (x, y), (x + width, y), layer, line_width)
    add_segment(board, (x + width, y), (x + width, y + height), layer, line_width)
    add_segment(board, (x + width, y + height), (x, y + height), layer, line_width)
    add_segment(board, (x, y + height), (x, y), layer, line_width)


def add_text(
    board: pcbnew.BOARD,
    text: str,
    x: float,
    y: float,
    layer: int = pcbnew.Cmts_User,
    size_mm: float = 1.2,
    bold: bool = False,
) -> None:
    item = pcbnew.PCB_TEXT(board)
    item.SetText(text)
    item.SetPosition(mm(x, y))
    item.SetLayer(layer)
    item.SetTextSize(mm(size_mm, size_mm))
    item.SetTextThickness(pcbnew.FromMM(max(0.15, size_mm * 0.14)))
    item.SetBold(bold)
    board.Add(item)


def add_board_outline(board: pcbnew.BOARD, width: float, height: float) -> None:
    # Rev L controls the maximum rectangular envelope. Corner radii remain a
    # fabrication detail, so this baseline uses the exact limiting rectangle.
    add_segment(board, (0, 0), (width, 0), pcbnew.Edge_Cuts, 0.1)
    add_segment(board, (width, 0), (width, height), pcbnew.Edge_Cuts, 0.1)
    add_segment(board, (width, height), (0, height), pcbnew.Edge_Cuts, 0.1)
    add_segment(board, (0, height), (0, 0), pcbnew.Edge_Cuts, 0.1)


def create_board(spec: BoardSpec, netlist: ET.Element) -> tuple[pcbnew.BOARD, dict[str, pcbnew.FOOTPRINT]]:
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(spec.copper_layers)
    settings = board.GetDesignSettings()
    settings.SetBoardThickness(pcbnew.FromMM(1.6))
    # PCBWay's published process supports 0.20 mm mechanical drills on a
    # 1.60 mm board and 0.20 mm clearance from an NPTH to adjacent copper.
    # The latter is required by the unmodified Wurth 74991114412 land pattern.
    # These are fabrication requirements, not geometry adjustments.
    settings.m_MinThroughDrill = pcbnew.FromMM(0.20)
    settings.m_HoleClearance = pcbnew.FromMM(0.20)
    title = board.GetTitleBlock()
    title.SetTitle(f"Radxa CM5 ProComm {spec.name}")
    title.SetCompany("ProComm")
    title.SetRevision("PCB-A0")
    title.SetComment(0, "VERIFIED MATING GEOMETRY ONLY; UNPLACED FOOTPRINTS ARE STAGED OUTSIDE BOARD")

    add_board_outline(board, spec.width_mm, spec.height_mm)
    add_text(board, f"{spec.name} PCB-A0", 4.0, spec.height_mm - 8.0, pcbnew.Cmts_User, 1.1, True)

    nets: dict[str, pcbnew.NETINFO_ITEM] = {}
    for net_node in netlist.find("nets") or ():
        name = net_node.get("name", "")
        if not name:
            continue
        code = int(net_node.get("code", "-1"))
        net = pcbnew.NETINFO_ITEM(board, name, code)
        board.Add(net)
        nets[name] = net

    footprints: dict[str, pcbnew.FOOTPRINT] = {}
    components = netlist.find("components")
    if components is None:
        raise RuntimeError(f"No components in {spec.name} netlist")

    for comp in components:
        if not component_is_on_board(comp):
            continue
        identifier = (comp.findtext("footprint") or "").strip()
        if not identifier:
            raise RuntimeError(f"{spec.name} {comp.get('ref')} has no PCB footprint")
        library_path, library, footprint_name = footprint_path(identifier)
        footprint = pcbnew.FootprintLoad(str(library_path), footprint_name)
        if footprint is None:
            raise RuntimeError(f"Cannot load {identifier} for {comp.get('ref')}")
        ref = comp.get("ref", "")
        footprint.SetReference(ref)
        footprint.SetValue(comp.findtext("value") or "")
        footprint.SetFPID(pcbnew.LIB_ID(library, footprint_name))
        sheet = comp.find("sheetpath")
        sheet_path = sheet.get("tstamps", "/") if sheet is not None else "/"
        component_uuid = (comp.findtext("tstamps") or "").strip()
        footprint.SetPath(pcbnew.KIID_PATH(f"{sheet_path}{component_uuid}"))
        board.Add(footprint)
        footprints[ref] = footprint

    for net_node in netlist.find("nets") or ():
        net = nets.get(net_node.get("name", ""))
        if net is None:
            continue
        for node in net_node.findall("node"):
            footprint = footprints.get(node.get("ref", ""))
            if footprint is None:
                continue
            pin = node.get("pin", "")
            matched = False
            for pad in footprint.Pads():
                if pad.GetNumber() == pin:
                    pad.SetNet(net)
                    matched = True
            if not matched:
                raise RuntimeError(f"{spec.name} {node.get('ref')} pin {pin} is absent from its footprint")

    for support_id, x, y in spec.supports:
        support = pcbnew.FootprintLoad(str(MECHANICAL_FP), "ProComm_M3_Support_NPTH_3.4mm")
        if support is None:
            raise RuntimeError("Cannot load controlled M3 support footprint")
        support.SetReference(support_id)
        support.SetValue("M3_CAPTIVE_SUPPORT_3.4")
        support.SetFPID(pcbnew.LIB_ID("ProCommMechanical", "ProComm_M3_Support_NPTH_3.4mm"))
        support.SetAttributes(pcbnew.FP_BOARD_ONLY | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
        board.Add(support)
        support.SetPosition(mm(x, y))
        support.SetLocked(True)

    board.BuildListOfNets()
    return board, footprints


def place(
    footprint: pcbnew.FOOTPRINT,
    x: float,
    y: float,
    rotation: float = 0.0,
    locked: bool = False,
) -> None:
    footprint.SetPosition(mm(x, y))
    footprint.SetOrientationDegrees(rotation)
    footprint.SetLocked(locked)


def move_front_silkscreen_graphics_to_fab(footprint: pcbnew.FOOTPRINT) -> None:
    """Keep an overhanging connector outline as assembly data, not panel ink."""
    for item in footprint.GraphicalItems():
        if item.GetLayer() == pcbnew.F_SilkS:
            item.SetLayer(pcbnew.F_Fab)


def place_audio_verified(board: pcbnew.BOARD, footprints: dict[str, pcbnew.FOOTPRINT]) -> set[str]:
    placed: set[str] = set()
    for channel in range(1, 9):
        row_y = 19.0 + 32.0 * (channel - 1)
        output_ref = f"J{200 + channel}"
        input_ref = f"J{300 + channel}"
        # Neutrik manufacturer geometry puts the male face center at +3.81 mm
        # and the female face center at -3.81 mm from the footprint origins.
        place(footprints[output_ref], 11.40 - 3.81, row_y, 0.0, True)
        place(footprints[input_ref], 54.78 + 3.81, row_y, 0.0, True)
        # The male connector body intentionally overhangs the PCB edge. Preserve
        # that exact outline on F.Fab without asking a fabricator to print it.
        move_front_silkscreen_graphics_to_fab(footprints[output_ref])
        placed.update((output_ref, input_ref))
    add_rect(board, 0.5, 0.5, 77.0, 267.0)
    add_text(board, "LOCKED: NC3MAV / NC3FAV FACE CENTERS FROM REV L + NEUTRIK FOOTPRINT", 2.0, 266.0, size_mm=0.75)
    return placed


def place_cm5_assembly_bottom(
    board: pcbnew.BOARD,
    footprints: dict[str, pcbnew.FOOTPRINT],
    origin_x: float,
    origin_y: float,
) -> set[str]:
    # The CM5 faces the case floor, so every source anchor receives the same
    # bottom-side transform T(x,y) = R(90 deg) * mirror-X(x,y) = (-y,-x).
    # J24's source anchor is (+11.405,-25.415) at -90 deg relative to U33.
    # Therefore its carrier anchor is (+25.415,-11.405) at 180 deg. Flip each
    # footprint in place to B.Cu, then set these fully derived final transforms;
    # never use a board-space flip that can reflect anchors about a wrong axis.
    final = {
        "J501": (origin_x, origin_y, 90.0),
        "J502": (origin_x, origin_y, 90.0),
        "J503": (origin_x + 25.415, origin_y - 11.405, 180.0),
    }
    for ref, (x, y, rotation) in final.items():
        footprint = footprints[ref]
        footprint.SetPosition(mm(x, y))
        footprint.Flip(footprint.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        place(footprint, x, y, rotation, True)
    return {"J501", "J502", "J503"}


def place_carrier_verified(board: pcbnew.BOARD, footprints: dict[str, pcbnew.FOOTPRINT]) -> set[str]:
    placed = place_cm5_assembly_bottom(board, footprints, 127.0, 245.0)

    # Rev L opening centers are board-local (34,39), (104,39), (34,73),
    # and (104,73). Wurth 74991114412 body center is (-5.715,+6.300)
    # from its official land-pattern origin.
    rj45_centers = {
        "J610": (34.0, 39.0),
        "J611": (104.0, 39.0),
        "J612": (34.0, 73.0),
        "J613": (104.0, 73.0),
    }
    for ref, (cx, cy) in rj45_centers.items():
        place(footprints[ref], cx + 5.715, cy - 6.300, 0.0, True)
        placed.add(ref)

    # The Wurth nano-SIM footprint origin is the exact holder center; the Rev L
    # service apertures are centered at these same controlled board datums.
    for ref, center in {"J702": (85.0, 120.0), "J703": (134.0, 120.0)}.items():
        place(footprints[ref], *center, 0.0, True)
        placed.add(ref)

    add_rect(board, 13.0, 19.0, 135.0, 74.0)
    add_rect(board, 99.5, 225.0, 55.0, 40.0)
    add_text(board, "LOCKED RJ45 BODY CENTERS", 14.0, 18.0, size_mm=0.75)
    add_text(board, "LOCKED OFFICIAL RADXA CM5 B.Cu MATE", 100.0, 224.0, size_mm=0.75)
    return placed


def stage_unplaced(
    board: pcbnew.BOARD,
    footprints: dict[str, pcbnew.FOOTPRINT],
    placed: set[str],
    board_width: float,
) -> None:
    x0 = board_width + 25.0
    x = x0
    y = 8.0
    row_height = 0.0
    max_width = 300.0
    add_text(board, "UNPLACED / UNVERIFIED PCB FOOTPRINT STAGING - NOT BOARD GEOMETRY", x0, 2.0, size_mm=1.2, bold=True)
    for ref in sorted(footprints):
        if ref in placed:
            continue
        footprint = footprints[ref]
        footprint.BuildCourtyardCaches()
        courtyard = footprint.GetCourtyard(pcbnew.F_CrtYd)
        bbox = courtyard.BBox() if not courtyard.IsEmpty() else footprint.GetFpPadsLocalBbox()
        width = max(4.0, pcbnew.ToMM(bbox.GetWidth())) + 2.0
        height = max(4.0, pcbnew.ToMM(bbox.GetHeight())) + 2.0
        if x + width > x0 + max_width:
            x = x0
            y += row_height + 2.0
            row_height = 0.0
        offset_x = -pcbnew.ToMM(bbox.GetX()) + 1.0
        offset_y = -pcbnew.ToMM(bbox.GetY()) + 1.0
        place(footprint, x + offset_x, y + offset_y)
        x += width + 1.0
        row_height = max(row_height, height)


def add_engineering_zones(spec: BoardSpec, board: pcbnew.BOARD) -> None:
    if spec.name == "AUDIO-8X8":
        add_text(board, "AUDIO QUIET ZONE: NO PWM / SWITCH NODES", 39.0, 132.0, size_mm=0.8, bold=True)
    elif spec.name == "CM5-CARRIER":
        add_rect(board, 13.0, 101.0, 55.0, 40.0)
        add_text(board, "HEADSET / FAN / SENSOR CANDIDATE ZONE", 14.0, 100.0, size_mm=0.7)
        add_rect(board, 16.0, 176.0, 56.0, 48.0)
        add_rect(board, 96.0, 176.0, 56.0, 48.0)
        add_text(board, "POWER ZONES - PLACEMENT NOT LOCKED", 17.0, 175.0, size_mm=0.7)
    else:
        add_text(board, "BOTTOM-TRAY MOUNT HOLES NOT RELEASED - NONE GUESSED", 4.0, 8.0, size_mm=0.9, bold=True)


def generate(spec: BoardSpec, netlist_path: Path) -> None:
    export_xml_netlist(spec.schematic, netlist_path)
    netlist = ET.parse(netlist_path).getroot()
    board, footprints = create_board(spec, netlist)
    placed: set[str] = set()
    if spec.name == "AUDIO-8X8":
        placed = place_audio_verified(board, footprints)
    elif spec.name == "CM5-CARRIER":
        placed = place_carrier_verified(board, footprints)
    add_engineering_zones(spec, board)
    stage_unplaced(board, footprints, placed, spec.width_mm)
    spec.output.parent.mkdir(parents=True, exist_ok=True)
    pcbnew.SaveBoard(str(spec.output), board)
    print(
        f"{spec.name}: wrote {spec.output.relative_to(ROOT)} with "
        f"{len(footprints)} schematic footprints, {len(placed)} locked mating footprints, "
        f"{len(spec.supports)} controlled supports, and {spec.copper_layers} copper layers"
    )


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="procomm-pcb-") as temp:
        temp_dir = Path(temp)
        for spec in SPECS:
            generate(spec, temp_dir / f"{spec.name}.xml")


if __name__ == "__main__":
    main()
