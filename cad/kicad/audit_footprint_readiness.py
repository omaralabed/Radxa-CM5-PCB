#!/usr/bin/env python3
"""Create a deterministic footprint and production-part readiness audit."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent.parent
KICAD_CLI = Path(
    os.environ.get(
        "KICAD_CLI",
        "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
    )
)
KICAD_GLOBAL_FOOTPRINTS = Path(
    "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
)
REPORT_DIR = ROOT / "reports"

SCHEMATICS = (
    ("PWR-SELECT", ROOT / "PWR-SELECT" / "PowerSelector.kicad_sch"),
    ("CM5-Carrier", ROOT / "CM5-CARRIER" / "CM5-Carrier.kicad_sch"),
    ("Audio-8x8", ROOT / "AUDIO-8X8" / "Audio-8x8.kicad_sch"),
)

# This typed port exists only to make cross-sheet ERC direction checks useful.
INTENTIONAL_NON_BOARD = {
    ("CM5-Carrier", "U900"): "Typed CM5 off-sheet audio interface",
    ("CM5-Carrier", "J711"): "ECT 818033349 off-board RF pigtail/bulkhead harness",
    ("CM5-Carrier", "J712"): "ECT 818033349 off-board RF pigtail/bulkhead harness",
    ("CM5-Carrier", "J713"): "ECT 818033349 off-board RF pigtail/bulkhead harness",
    ("CM5-Carrier", "J714"): "ECT 818033349 off-board RF pigtail/bulkhead harness",
}

# Copper probe lands are deliberate PCB features, not purchased components.
# They remain route-ready but are not production-BOM line items.
NO_BOM_BOARD_FEATURES = {
    ("Audio-8x8", "J901"): "Two-pad copper access feature for chassis-bond verification",
}

# Placement and routing must remain blocked until these drawing-derived lands
# pass the named first-article coupon. This is stricter than a production-only
# assembly check because escape routing and thermal-via geometry depend on it.
ROUTING_COUPON_REQUIRED = {
    (
        "Audio-8x8",
        "U201",
    ): "AK5558VN Coupon A1 artwork is ready; exposed-pad, thermal-via, stencil, X-ray, and assembly sign-off still required",
    (
        "Audio-8x8",
        "U301",
    ): "AK4458VN Coupon A1 artwork is ready; exposed-pad, thermal-via, stencil, X-ray, and assembly sign-off still required",
    **{
        (
            "Audio-8x8",
            f"K{reference}",
        ): "Panasonic TQ2 Coupon A1 artwork is ready; sample insertion, seating, and pin-map sign-off still required"
        for reference in range(501, 509)
    },
}

# These parts may be placed and routed for prototype capture, but production
# release remains blocked until the named physical verification is complete.
PRODUCTION_COUPON_REQUIRED = {
    (
        "CM5-Carrier",
        "J910",
    ): "Kycon Coupon A1 artwork is ready; exact sample insertion, seating, CTIA map, and plated-hole sign-off still required",
}


def field(comp: ET.Element, name: str) -> str:
    node = comp.find(f"./fields/field[@name='{name}']")
    return (node.text or "").strip() if node is not None else ""


def footprint_file(sheet: str, footprint: str) -> Path | None:
    if not footprint or ":" not in footprint:
        return None
    library, name = footprint.split(":", 1)
    if library == "CM5Carrier":
        return ROOT / "CM5-CARRIER" / "CM5Carrier.pretty" / f"{name}.kicad_mod"
    if library == "PowerSelector":
        return ROOT / "PWR-SELECT" / "PowerSelector.pretty" / f"{name}.kicad_mod"
    candidate = KICAD_GLOBAL_FOOTPRINTS / f"{library}.pretty" / f"{name}.kicad_mod"
    return candidate if candidate.exists() else None


def export_netlist(schematic: Path, output: Path) -> None:
    result = subprocess.run(
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
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(
            f"KiCad netlist export failed for {schematic}:\n{result.stderr.strip()}"
        )


def validate_molex_land_pattern() -> None:
    """Protect the drawing-derived Mini PCIe geometry against silent drift."""
    path = (
        ROOT
        / "CM5-CARRIER"
        / "CM5Carrier.pretty"
        / "Molex_0679101002_Mini_PCIe.kicad_mod"
    )
    text = path.read_text()
    observed: dict[int, tuple[float, float, float, float]] = {}
    pad_pattern = re.compile(
        r'\(pad "(?P<pin>\d+)" smd (?:rect|roundrect)\s+'
        r'\(at (?P<x>-?\d+(?:\.\d+)?) (?P<y>-?\d+(?:\.\d+)?)\) '
        r'\(size (?P<w>\d+(?:\.\d+)?) (?P<h>\d+(?:\.\d+)?)\)',
        re.MULTILINE,
    )
    for match in pad_pattern.finditer(text):
        observed[int(match.group("pin"))] = tuple(
            float(match.group(name)) for name in ("x", "y", "w", "h")
        )

    expected: dict[int, tuple[float, float, float, float]] = {}
    expected.update(
        {
            1 + 2 * index: (round(0.80 * index, 2), 4.10, 0.60, 2.00)
            for index in range(8)
        }
    )
    expected.update(
        {
            2 + 2 * index: (round(0.40 + 0.80 * index, 2), -4.10, 0.60, 2.00)
            for index in range(8)
        }
    )
    expected.update(
        {
            17 + 2 * index: (round(10.30 + 0.80 * index, 2), 4.10, 0.60, 2.00)
            for index in range(18)
        }
    )
    expected.update(
        {
            18 + 2 * index: (round(10.70 + 0.80 * index, 2), -4.10, 0.60, 2.00)
            for index in range(18)
        }
    )
    if observed != expected:
        raise RuntimeError("Molex 0679101002 signal-pad geometry has drifted from SD-67910-001 C2")

    required_geometry = (
        '(at 0 0) (size 1.60 1.60) (drill 1.60)',
        '(at 25.00 0) (size 1.10 1.10) (drill 1.10)',
        '(at -2.15 3.50) (size 1.60 3.20)',
        '(at 27.15 3.50) (size 1.60 3.20)',
    )
    for geometry in required_geometry:
        if geometry not in text:
            raise RuntimeError(f"Molex 0679101002 required geometry missing: {geometry}")


def audit_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="radxa-footprint-audit-") as temp:
        temp_root = Path(temp)
        for sheet, schematic in SCHEMATICS:
            netlist = temp_root / f"{sheet}.xml"
            export_netlist(schematic, netlist)
            components = ET.parse(netlist).findall("./components/comp")
            for comp in components:
                reference = comp.attrib["ref"]
                value = (comp.findtext("value") or "").strip()
                footprint = (comp.findtext("footprint") or "").strip()
                manufacturer = field(comp, "Manufacturer")
                mpn = field(comp, "MPN")
                exemption = INTENTIONAL_NON_BOARD.get((sheet, reference), "")
                no_bom_feature = NO_BOM_BOARD_FEATURES.get((sheet, reference), "")
                if reference.startswith("TP"):
                    no_bom_feature = "Copper-only electrical test point"
                routing_coupon_gate = ROUTING_COUPON_REQUIRED.get((sheet, reference), "")
                coupon_gate = PRODUCTION_COUPON_REQUIRED.get((sheet, reference), "")
                resolved = footprint_file(sheet, footprint)

                route_status = "READY"
                production_status = "READY"
                note = ""
                if exemption:
                    route_status = "NOT_BOARD_MOUNTED"
                    production_status = "NOT_BOARD_MOUNTED"
                    note = exemption
                elif no_bom_feature:
                    if not footprint or resolved is None or not resolved.exists():
                        route_status = "BLOCKED_UNRESOLVED_FOOTPRINT"
                        production_status = "BLOCKED_UNRESOLVED_FOOTPRINT"
                        note = "Copper-only board feature footprint does not resolve"
                    else:
                        production_status = "NOT_IN_BOM"
                        note = no_bom_feature
                elif not footprint:
                    route_status = "BLOCKED_NO_FOOTPRINT"
                    production_status = "BLOCKED_NO_FOOTPRINT"
                    note = "Assign a drawing-backed footprint before placement"
                elif resolved is None or not resolved.exists():
                    route_status = "BLOCKED_UNRESOLVED_FOOTPRINT"
                    production_status = "BLOCKED_UNRESOLVED_FOOTPRINT"
                    note = "Footprint identifier does not resolve in project or installed KiCad libraries"
                elif routing_coupon_gate:
                    route_status = "BLOCKED_MECHANICAL_COUPON"
                    production_status = "BLOCKED_MECHANICAL_COUPON"
                    note = routing_coupon_gate
                elif not manufacturer or not mpn:
                    production_status = "BLOCKED_NO_PRODUCTION_PART"
                    note = "Lock manufacturer and MPN before BOM release"
                elif coupon_gate:
                    production_status = "BLOCKED_MECHANICAL_COUPON"
                    note = coupon_gate

                rows.append(
                    {
                        "sheet": sheet,
                        "reference": reference,
                        "value": value,
                        "manufacturer": manufacturer,
                        "mpn": mpn,
                        "footprint": footprint,
                        "route_status": route_status,
                        "production_status": production_status,
                        "evidence_note": note,
                    }
                )
    return sorted(rows, key=lambda row: (row["sheet"], row["reference"]))


def write_reports(rows: list[dict[str, str]]) -> tuple[int, int]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = REPORT_DIR / "component-footprint-audit.csv"
    fieldnames = tuple(rows[0]) if rows else (
        "sheet",
        "reference",
        "value",
        "manufacturer",
        "mpn",
        "footprint",
        "route_status",
        "production_status",
        "evidence_note",
    )
    with csv_path.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    route_blockers = [row for row in rows if row["route_status"].startswith("BLOCKED")]
    production_blockers = [
        row for row in rows if row["production_status"].startswith("BLOCKED")
    ]
    ready = sum(row["route_status"] == "READY" for row in rows)
    non_board = sum(row["route_status"] == "NOT_BOARD_MOUNTED" for row in rows)
    by_sheet: dict[str, tuple[int, int, int]] = {}
    for sheet, _schematic in SCHEMATICS:
        sheet_rows = [row for row in rows if row["sheet"] == sheet]
        by_sheet[sheet] = (
            len(sheet_rows),
            sum(row["route_status"].startswith("BLOCKED") for row in sheet_rows),
            sum(row["production_status"].startswith("BLOCKED") for row in sheet_rows),
        )

    markdown = [
        "# Component and Footprint Audit",
        "",
        "Generated once from each physical board root so hierarchical child components are not double-counted. This report is deterministic and contains no audit timestamp.",
        "",
        "## Current gate",
        "",
        f"- Components audited: {len(rows)}",
        f"- Route-ready components: {ready}",
        f"- Intentional non-board symbols: {non_board}",
        f"- Routing blockers: {len(route_blockers)}",
        f"- Production/BOM blockers: {len(production_blockers)}",
        "",
        "A routing blocker has no footprint, references an unresolved footprint, or still requires a routing-critical mechanical coupon. A production blocker also includes any board-mounted component without a locked manufacturer and MPN.",
        "",
        "## By sheet",
        "",
        "| Sheet | Components | Routing blockers | Production blockers |",
        "|---|---:|---:|---:|",
    ]
    for sheet, counts in by_sheet.items():
        markdown.append(f"| {sheet} | {counts[0]} | {counts[1]} | {counts[2]} |")
    markdown.extend(
        [
            "",
            "## Gate commands",
            "",
            "```sh",
            "python3 cad/kicad/audit_footprint_readiness.py",
            "python3 cad/kicad/audit_footprint_readiness.py --routing",
            "python3 cad/kicad/audit_footprint_readiness.py --release",
            "```",
            "",
            "The default command refreshes this report. `--routing` fails while placement/routing blockers remain. `--release` also fails while production-part evidence is incomplete.",
            "",
            "See `component-footprint-audit.csv` for every reference designator and its exact blocking reason.",
            "",
        ]
    )
    (REPORT_DIR / "component-footprint-audit.md").write_text("\n".join(markdown))
    return len(route_blockers), len(production_blockers)


def main() -> int:
    parser = argparse.ArgumentParser()
    gate = parser.add_mutually_exclusive_group()
    gate.add_argument("--routing", action="store_true")
    gate.add_argument("--release", action="store_true")
    args = parser.parse_args()

    validate_molex_land_pattern()
    rows = audit_rows()
    route_blockers, production_blockers = write_reports(rows)
    print(
        f"Footprint audit: {len(rows)} components, "
        f"{route_blockers} routing blockers, "
        f"{production_blockers} production blockers."
    )
    if args.routing and route_blockers:
        print("ROUTING HOLD: assign and resolve every board-mounted footprint.")
        return 1
    if args.release and production_blockers:
        print("PRODUCTION HOLD: close every footprint and manufacturer/MPN record.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
