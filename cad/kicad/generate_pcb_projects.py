#!/usr/bin/env python3
"""Generate controlled native KiCad PCB engineering-placement baselines.

Run this script with KiCad's bundled Python interpreter. Verified mating parts
remain locked to controlled datums. Every other footprint receives a deterministic,
collision-checked functional placement inside its board outline so the PCB and 3D
views always describe one physical assembly.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
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


@dataclass(frozen=True)
class PlacementRegion:
    name: str
    x_mm: float
    y_mm: float
    width_mm: float
    height_mm: float


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
            ("SD1", 57.0, 93.5),
            ("SD2", 122.0, 93.5),
            ("SD3", 78.5, 122.5),
            ("SD4", 100.5, 122.5),
            ("C3", 6.0, 134.0),
            ("C4", 112.0, 134.0),
            ("C5", 6.0, 262.0),
            ("C6", 160.0, 190.0),
        ),
    ),
    BoardSpec(
        "SIM-SERVICE",
        ROOT / "cad/kicad/SIM-SERVICE/Sim-Service.kicad_sch",
        ROOT / "cad/kicad/SIM-SERVICE/Sim-Service.kicad_pcb",
        76.0,
        40.0,
        4,
        "S",
        (
            ("S1", 5.5, 5.5),
            ("S2", 70.5, 5.5),
            ("S3", 27.0, 34.5),
            ("S4", 49.0, 34.5),
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


def create_board(
    spec: BoardSpec,
    netlist: ET.Element,
) -> tuple[pcbnew.BOARD, dict[str, pcbnew.FOOTPRINT], dict[str, str]]:
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
    title.SetRevision("PCB-A1")
    title.SetComment(0, "LOCKED MATING GEOMETRY + DETERMINISTIC FUNCTIONAL ENGINEERING PLACEMENT")

    add_board_outline(board, spec.width_mm, spec.height_mm)
    add_text(board, f"{spec.name} PCB-A1", 4.0, spec.height_mm - 8.0, pcbnew.Cmts_User, 1.1, True)

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
    sheet_names: dict[str, str] = {}
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
        sheet_names[ref] = sheet.get("names", "/") if sheet is not None else "/"
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
    return board, footprints, sheet_names


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
    # and (104,73). The official Bel housing center is (0,+2.325) from
    # the exact V8BR-1AX1-GH land-pattern origin.
    rj45_centers = {
        "J610": (34.0, 39.0),
        "J611": (104.0, 39.0),
        "J612": (34.0, 73.0),
        "J613": (104.0, 73.0),
    }
    for ref, (cx, cy) in rj45_centers.items():
        place(footprints[ref], cx, cy - 2.325, 0.0, True)
        placed.add(ref)

    # The SIM-SERVICE receptacle is on the daughterboard B.Cu and mates at
    # this exact top-side carrier datum. Four nearby SD supports carry every
    # card and vibration load; the 2.5 mm DF40 pair is not structural.
    place(footprints["J702"], 89.5, 96.0, 0.0, True)
    placed.add("J702")

    add_rect(board, 13.0, 19.0, 135.0, 74.0)
    add_rect(board, 99.5, 225.0, 55.0, 40.0)
    add_text(board, "LOCKED VERTICAL BEL RJ45 BODY CENTERS", 14.0, 18.0, size_mm=0.75)
    add_text(board, "LOCKED OFFICIAL RADXA CM5 B.Cu MATE", 100.0, 224.0, size_mm=0.75)
    return placed


def place_sim_service_verified(
    board: pcbnew.BOARD,
    footprints: dict[str, pcbnew.FOOTPRINT],
) -> set[str]:
    # The horizontal SIM daughterboard sits 2.5 mm above the carrier. J1 is on
    # B.Cu and mates directly to carrier J702; the Wurth holders remain on F.Cu
    # with both card mouths at +Y and the locked 49 mm panel-center pitch.
    place(footprints["J1"], 38.0, 8.0, 0.0, False)
    footprints["J1"].Flip(footprints["J1"].GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    place(footprints["J1"], 38.0, 8.0, 0.0, True)
    place(footprints["J2"], 13.5, 32.0, 0.0, True)
    place(footprints["J3"], 62.5, 32.0, 0.0, True)
    add_text(board, "PANEL / CARD SERVICE EDGE", 38.0, 38.5, size_mm=0.75, bold=True)
    add_text(board, "SIM 1", 13.5, 37.0, size_mm=0.70, bold=True)
    add_text(board, "SIM 2", 62.5, 37.0, size_mm=0.70, bold=True)
    return {"J1", "J2", "J3"}


def footprint_side(footprint: pcbnew.FOOTPRINT) -> int:
    return pcbnew.B_Cu if footprint.GetLayer() == pcbnew.B_Cu else pcbnew.F_Cu


def courtyard_bbox(footprint: pcbnew.FOOTPRINT) -> pcbnew.BOX2I:
    footprint.BuildCourtyardCaches()
    courtyard_layer = pcbnew.B_CrtYd if footprint_side(footprint) == pcbnew.B_Cu else pcbnew.F_CrtYd
    courtyard = footprint.GetCourtyard(courtyard_layer)
    return courtyard.BBox() if not courtyard.IsEmpty() else footprint.GetBoundingBox(False, False)


def set_footprint_side(footprint: pcbnew.FOOTPRINT, side: int) -> None:
    if footprint_side(footprint) != side:
        footprint.Flip(footprint.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)


def move_internal_fields_to_fab(footprint: pcbnew.FOOTPRINT) -> None:
    """Keep dense assembly markings on Fab without creating false silk errors."""
    fab_layer = pcbnew.B_Fab if footprint_side(footprint) == pcbnew.B_Cu else pcbnew.F_Fab
    footprint.Reference().SetLayer(fab_layer)
    footprint.Value().SetLayer(fab_layer)


def through_hole_pads(footprint: pcbnew.FOOTPRINT) -> list[pcbnew.PAD]:
    return [
        pad
        for pad in footprint.Pads()
        if pad.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
    ]


class GridPacker:
    """Deterministic 0.5 mm bit-grid courtyard packer for one board side."""

    RESOLUTION_MM = 0.5

    def __init__(self, region: PlacementRegion, side: int, gap_mm: float = 0.50) -> None:
        self.region = region
        self.side = side
        self.gap_mm = gap_mm
        self.columns = int(math.floor(region.width_mm / self.RESOLUTION_MM))
        self.rows_count = int(math.floor(region.height_mm / self.RESOLUTION_MM))
        self.rows = [0] * self.rows_count

    def _cell_range(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
    ) -> tuple[int, int, int, int] | None:
        left = max(0, int(math.floor((x1 - self.region.x_mm) / self.RESOLUTION_MM)))
        top = max(0, int(math.floor((y1 - self.region.y_mm) / self.RESOLUTION_MM)))
        right = min(self.columns, int(math.ceil((x2 - self.region.x_mm) / self.RESOLUTION_MM)))
        bottom = min(self.rows_count, int(math.ceil((y2 - self.region.y_mm) / self.RESOLUTION_MM)))
        if left >= right or top >= bottom:
            return None
        return left, top, right, bottom

    def block(self, x1: float, y1: float, x2: float, y2: float) -> None:
        cells = self._cell_range(x1, y1, x2, y2)
        if cells is None:
            return
        left, top, right, bottom = cells
        mask = ((1 << (right - left)) - 1) << left
        for row in range(top, bottom):
            self.rows[row] |= mask

    def block_board_obstacles(self, board: pcbnew.BOARD) -> None:
        for footprint in board.GetFootprints():
            if not footprint.IsLocked():
                continue
            if footprint_side(footprint) == self.side:
                bbox = courtyard_bbox(footprint)
                self.block(
                    pcbnew.ToMM(bbox.GetLeft()) - self.gap_mm,
                    pcbnew.ToMM(bbox.GetTop()) - self.gap_mm,
                    pcbnew.ToMM(bbox.GetRight()) + self.gap_mm,
                    pcbnew.ToMM(bbox.GetBottom()) + self.gap_mm,
                )
            for pad in through_hole_pads(footprint):
                bbox = pad.GetBoundingBox()
                local_clearance = pad.GetLocalClearance()
                clearance_mm = pcbnew.ToMM(local_clearance) if local_clearance is not None else 0.0
                required_clearance = max(0.50, clearance_mm + 0.20)
                self.block(
                    pcbnew.ToMM(bbox.GetLeft()) - required_clearance,
                    pcbnew.ToMM(bbox.GetTop()) - required_clearance,
                    pcbnew.ToMM(bbox.GetRight()) + required_clearance,
                    pcbnew.ToMM(bbox.GetBottom()) + required_clearance,
                )

    def _first_slot(self, width_cells: int, height_cells: int) -> tuple[int, int] | None:
        if width_cells > self.columns or height_cells > self.rows_count:
            return None
        mask_base = (1 << width_cells) - 1
        for top in range(self.rows_count - height_cells + 1):
            occupied = 0
            for row in self.rows[top : top + height_cells]:
                occupied |= row
            for left in range(self.columns - width_cells + 1):
                if occupied & (mask_base << left) == 0:
                    return left, top
        return None

    def place_footprint(self, footprint: pcbnew.FOOTPRINT) -> None:
        set_footprint_side(footprint, self.side)
        footprint.SetPosition(mm(0.0, 0.0))

        candidates: list[tuple[tuple[int, int], float, pcbnew.BOX2I, int, int]] = []
        for rotation in (0.0, 90.0):
            footprint.SetOrientationDegrees(rotation)
            bbox = courtyard_bbox(footprint)
            width_mm = pcbnew.ToMM(bbox.GetWidth()) + 2.0 * self.gap_mm
            height_mm = pcbnew.ToMM(bbox.GetHeight()) + 2.0 * self.gap_mm
            width_cells = max(1, int(math.ceil(width_mm / self.RESOLUTION_MM)))
            height_cells = max(1, int(math.ceil(height_mm / self.RESOLUTION_MM)))
            slot = self._first_slot(width_cells, height_cells)
            if slot is not None:
                candidates.append((slot, rotation, bbox, width_cells, height_cells))

        if not candidates:
            raise RuntimeError(
                f"{footprint.GetReference()} ({footprint.GetValue()}) does not fit "
                f"in {self.region.name} on {'B.Cu' if self.side == pcbnew.B_Cu else 'F.Cu'}"
            )

        slot, rotation, bbox, width_cells, height_cells = min(
            candidates,
            key=lambda item: (item[0][1], item[0][0], item[3] * item[4], item[1]),
        )
        left_cell, top_cell = slot
        footprint.SetOrientationDegrees(rotation)
        target_left = self.region.x_mm + left_cell * self.RESOLUTION_MM + self.gap_mm
        target_top = self.region.y_mm + top_cell * self.RESOLUTION_MM + self.gap_mm
        place(
            footprint,
            target_left - pcbnew.ToMM(bbox.GetLeft()),
            target_top - pcbnew.ToMM(bbox.GetTop()),
            rotation,
        )
        move_internal_fields_to_fab(footprint)
        mask = ((1 << width_cells) - 1) << left_cell
        for row in range(top_cell, top_cell + height_cells):
            self.rows[row] |= mask

    def place_many(self, footprints: list[pcbnew.FOOTPRINT]) -> None:
        def footprint_area(item: pcbnew.FOOTPRINT) -> tuple[float, str]:
            set_footprint_side(item, self.side)
            item.SetPosition(mm(0.0, 0.0))
            item.SetOrientationDegrees(0.0)
            bbox = courtyard_bbox(item)
            return -(pcbnew.ToMM(bbox.GetWidth()) * pcbnew.ToMM(bbox.GetHeight())), item.GetReference()

        for footprint in sorted(footprints, key=footprint_area):
            self.place_footprint(footprint)


def packer(
    board: pcbnew.BOARD,
    region: PlacementRegion,
    side: int,
    gap_mm: float = 0.50,
) -> GridPacker:
    result = GridPacker(region, side, gap_mm)
    result.block_board_obstacles(board)
    return result


def place_audio_engineered(
    board: pcbnew.BOARD,
    footprints: dict[str, pcbnew.FOOTPRINT],
    sheets: dict[str, str],
    locked: set[str],
) -> set[str]:
    regions = {
        "digital": PlacementRegion("audio digital / converters", 1.5, 1.5, 75.0, 48.0),
        "channels": PlacementRegion("eight balanced channel stages", 1.5, 51.0, 75.0, 153.0),
        "power": PlacementRegion("isolated audio power", 1.5, 205.5, 75.0, 61.0),
    }
    packers = {name: packer(board, region, pcbnew.B_Cu, 0.25) for name, region in regions.items()}
    assignments: dict[str, list[pcbnew.FOOTPRINT]] = {name: [] for name in regions}
    for reference, footprint in footprints.items():
        if reference in locked:
            continue
        sheet = sheets[reference]
        if sheet in ("/Balanced Inputs 1-8/", "/Balanced Outputs 1-8/"):
            zone = "channels"
        elif sheet == "/Audio Power/" or reference in {"C901", "J901", "R901"}:
            zone = "power"
        else:
            zone = "digital"
        assignments[zone].append(footprint)
    for name in ("digital", "channels", "power"):
        packers[name].place_many(assignments[name])
    return locked | {item.GetReference() for items in assignments.values() for item in items}


def place_carrier_engineered(
    board: pcbnew.BOARD,
    footprints: dict[str, pcbnew.FOOTPRINT],
    sheets: dict[str, str],
    locked: set[str],
) -> set[str]:
    regions = {
        "network": PlacementRegion("PCIe / Ethernet / Wi-Fi", 1.5, 1.5, 163.0, 92.0),
        "service": PlacementRegion("WWAN / display / headset / control", 1.5, 95.0, 163.0, 69.0),
        "power": PlacementRegion("high-current regulator stages", 1.5, 166.0, 163.0, 58.0),
        "core": PlacementRegion("CM5 support interfaces", 1.5, 226.0, 163.0, 40.5),
    }
    packers = {name: packer(board, region, pcbnew.F_Cu) for name, region in regions.items()}
    assignments: dict[str, list[pcbnew.FOOTPRINT]] = {name: [] for name in regions}
    for reference, footprint in footprints.items():
        if reference in locked:
            continue
        sheet = sheets[reference]
        if sheet == "/Network / PCIe / Wi-Fi/":
            zone = "network"
        elif sheet == "/Power Regulators/":
            zone = "power"
        elif sheet == "/CM5 Core / Allocated Pins/":
            zone = "core"
        else:
            zone = "service"
        assignments[zone].append(footprint)
    for name in ("network", "service", "power", "core"):
        packers[name].place_many(assignments[name])
    return locked | {item.GetReference() for items in assignments.values() for item in items}


def place_sim_service_engineered(
    board: pcbnew.BOARD,
    footprints: dict[str, pcbnew.FOOTPRINT],
    locked: set[str],
) -> set[str]:
    # Keep the two protection/filter ICs directly behind their own sockets.
    # This is a deliberate short protected segment, not a general auto-pack.
    place(footprints["U1"], 13.5, 20.0, 0.0)
    place(footprints["U2"], 62.5, 20.0, 0.0)
    move_internal_fields_to_fab(footprints["U1"])
    move_internal_fields_to_fab(footprints["U2"])
    return locked | {"U1", "U2"}


def place_power_selector_engineered(
    board: pcbnew.BOARD,
    footprints: dict[str, pcbnew.FOOTPRINT],
) -> set[str]:
    region = PlacementRegion("power selector assembly", 1.5, 1.5, 113.0, 77.0)
    top: list[pcbnew.FOOTPRINT] = []
    bottom: list[pcbnew.FOOTPRINT] = []
    for footprint in footprints.values():
        footprint.SetPosition(mm(0.0, 0.0))
        footprint.SetOrientationDegrees(0.0)
        bbox = courtyard_bbox(footprint)
        area = pcbnew.ToMM(bbox.GetWidth()) * pcbnew.ToMM(bbox.GetHeight())
        if through_hole_pads(footprint) or footprint.GetReference().startswith("J") or area >= 100.0:
            top.append(footprint)
        else:
            bottom.append(footprint)

    top_packer = packer(board, region, pcbnew.F_Cu)
    top_packer.place_many(top)
    bottom_packer = packer(board, region, pcbnew.B_Cu)
    for footprint in top:
        for pad in through_hole_pads(footprint):
            bbox = pad.GetBoundingBox()
            local_clearance = pad.GetLocalClearance()
            clearance_mm = pcbnew.ToMM(local_clearance) if local_clearance is not None else 0.0
            required_clearance = max(0.50, clearance_mm + 0.20)
            bottom_packer.block(
                pcbnew.ToMM(bbox.GetLeft()) - required_clearance,
                pcbnew.ToMM(bbox.GetTop()) - required_clearance,
                pcbnew.ToMM(bbox.GetRight()) + required_clearance,
                pcbnew.ToMM(bbox.GetBottom()) + required_clearance,
            )
    bottom_packer.place_many(bottom)
    return set(footprints)


def add_engineering_zones(spec: BoardSpec, board: pcbnew.BOARD) -> None:
    if spec.name == "AUDIO-8X8":
        add_rect(board, 1.5, 1.5, 75.0, 48.0)
        add_rect(board, 1.5, 51.0, 75.0, 153.0)
        add_rect(board, 1.5, 205.5, 75.0, 61.0)
        add_text(board, "B.Cu DIGITAL / AKM", 3.0, 4.0, size_mm=0.7, bold=True)
        add_text(board, "B.Cu BALANCED CHANNEL STAGES", 3.0, 53.5, size_mm=0.7, bold=True)
        add_text(board, "B.Cu ISOLATED AUDIO POWER", 3.0, 208.0, size_mm=0.7, bold=True)
    elif spec.name == "CM5-CARRIER":
        add_rect(board, 1.5, 1.5, 163.0, 92.0)
        add_rect(board, 1.5, 95.0, 163.0, 69.0)
        add_rect(board, 1.5, 166.0, 163.0, 58.0)
        add_rect(board, 1.5, 226.0, 163.0, 40.5)
        add_text(board, "F.Cu NETWORK", 3.0, 4.0, size_mm=0.7, bold=True)
        add_text(board, "F.Cu SERVICE / WWAN / DISPLAY / AUDIO / THERMAL", 3.0, 97.5, size_mm=0.7, bold=True)
        add_text(board, "F.Cu POWER CONVERSION", 3.0, 168.5, size_mm=0.7, bold=True)
        add_text(board, "F.Cu CM5 SUPPORT; CM5 MATE LOCKED ON B.Cu", 3.0, 228.5, size_mm=0.7, bold=True)
    elif spec.name == "SIM-SERVICE":
        add_rect(board, 5.0, 13.0, 66.0, 25.0)
        add_text(board, "HORIZONTAL DIRECT-SOCKET DAUGHTERBOARD; SIM MOUTHS +Y", 38.0, 1.5, size_mm=0.65, bold=True)
    else:
        add_text(board, "F.Cu POWER HARDWARE / B.Cu CONTROL; MOUNT DATUM PENDING", 4.0, 8.0, size_mm=0.8, bold=True)


def generate(spec: BoardSpec, netlist_path: Path) -> None:
    export_xml_netlist(spec.schematic, netlist_path)
    netlist = ET.parse(netlist_path).getroot()
    board, footprints, sheets = create_board(spec, netlist)
    locked: set[str] = set()
    if spec.name == "AUDIO-8X8":
        locked = place_audio_verified(board, footprints)
    elif spec.name == "CM5-CARRIER":
        locked = place_carrier_verified(board, footprints)
    elif spec.name == "SIM-SERVICE":
        locked = place_sim_service_verified(board, footprints)
    add_engineering_zones(spec, board)
    if spec.name == "AUDIO-8X8":
        placed = place_audio_engineered(board, footprints, sheets, locked)
    elif spec.name == "CM5-CARRIER":
        placed = place_carrier_engineered(board, footprints, sheets, locked)
    elif spec.name == "SIM-SERVICE":
        placed = place_sim_service_engineered(board, footprints, locked)
    else:
        placed = place_power_selector_engineered(board, footprints)
    if placed != set(footprints):
        missing = sorted(set(footprints) - placed)
        raise RuntimeError(f"{spec.name} has unplaced footprints: {', '.join(missing)}")
    spec.output.parent.mkdir(parents=True, exist_ok=True)
    pcbnew.SaveBoard(str(spec.output), board)
    print(
        f"{spec.name}: wrote {spec.output.relative_to(ROOT)} with "
        f"{len(footprints)} in-board schematic footprints, {len(locked)} locked mating footprints, "
        f"{len(spec.supports)} controlled supports, and {spec.copper_layers} copper layers"
    )


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="procomm-pcb-") as temp:
        temp_dir = Path(temp)
        for spec in SPECS:
            generate(spec, temp_dir / f"{spec.name}.xml")


if __name__ == "__main__":
    main()
