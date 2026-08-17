#!/usr/bin/env python3
"""Validate the horizontal direct-socket dual-SIM daughterboard."""

from __future__ import annotations

import csv
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent.parent.parent
BOM = WORKSPACE / "docs" / "sim_service_bom_a1.csv"
SCHEMATIC = ROOT / "Sim-Service.kicad_sch"
KICAD_CLI = Path(
    os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
)


def check(name: str, condition: bool, detail: str) -> bool:
    print(f"{'PASS' if condition else 'FAIL'}  {name}: {detail}")
    return condition


def export_net_map() -> dict[tuple[str, str], str]:
    with tempfile.TemporaryDirectory(prefix="radxa-sim-service-validation-") as temp:
        output = Path(temp) / "Sim-Service.xml"
        result = subprocess.run(
            [
                str(KICAD_CLI), "sch", "export", "netlist", "--format", "kicadxml",
                "--output", str(output), str(SCHEMATIC),
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode:
            raise RuntimeError(f"KiCad netlist export failed:\n{result.stderr.strip()}")
        root = ET.parse(output)
        return {
            (node.attrib["ref"], node.attrib["pin"]): net.attrib["name"].lstrip("/")
            for net in root.findall("./nets/net")
            for node in net.findall("node")
        }


def main() -> int:
    rows = list(csv.DictReader(BOM.open())) if BOM.exists() else []
    by_ref = {row["Reference"]: row for row in rows}
    schematic_text = SCHEMATIC.read_text() if SCHEMATIC.exists() else ""
    net_map = export_net_map()
    checks: list[bool] = []

    checks.append(
        check(
            "SIM-SERVICE production BOM",
            len(rows) == 5
            and all(row["Manufacturer"] and row["MPN"] and row["Footprint"] for row in rows),
            f"{len(rows)} board parts with controlled manufacturer, MPN, and footprint",
        )
    )
    expected_parts = {
        "J1": (
            "DF40HC(2.5)-20DS-0.4V(51)",
            "CM5Carrier:Hirose_DF40HC(2.5)-20DS-0.4V_2x10_P0.4mm",
        ),
        "J2": ("693043020611", "CM5Carrier:J_Wurth_WR-CRD_693043020611"),
        "J3": ("693043020611", "CM5Carrier:J_Wurth_WR-CRD_693043020611"),
        "U1": (
            "TPD3F303DPVR",
            "Package_SON:Texas_R-PUSON-N8_USON-8-1EP_1.6x2.1mm_P0.5mm_EP0.4x1.7mm",
        ),
        "U2": (
            "TPD3F303DPVR",
            "Package_SON:Texas_R-PUSON-N8_USON-8-1EP_1.6x2.1mm_P0.5mm_EP0.4x1.7mm",
        ),
    }
    checks.append(
        check(
            "controlled service-board parts",
            all(
                by_ref.get(ref, {}).get("MPN") == mpn
                and by_ref.get(ref, {}).get("Footprint") == footprint
                for ref, (mpn, footprint) in expected_parts.items()
            ),
            "Hirose DF40 receptacle, two Wurth sockets, and two TPD3F303 filters",
        )
    )

    socket_expected = {
        "1": "GND", "2": "CHASSIS_GND",
        "3": "SIM1_VCC", "4": "SIM1_RESET_RAW", "5": "GND",
        "6": "SIM1_CLK_RAW", "7": "GND", "8": "SIM1_DATA_RAW",
        "9": "SIM2_VCC", "10": "SIM2_RESET_RAW", "11": "GND",
        "12": "SIM2_CLK_RAW", "13": "GND", "14": "SIM2_DATA_RAW",
        "15": "GND", "16": "CHASSIS_GND", "17": "GND",
        "18": "CHASSIS_GND", "19": "GND", "20": "CHASSIS_GND",
    }
    checks.append(
        check(
            "carrier socket pin-for-pin contract",
            all(net_map.get(("J1", pin)) == net for pin, net in socket_expected.items()),
            "directly matches CM5-CARRIER J702",
        )
    )

    for index in (1, 2):
        prefix = f"SIM{index}"
        holder = f"J{index + 1}"
        protection = f"U{index}"
        holder_expected = {
            "C1": f"{prefix}_VCC", "C2": f"{prefix}_RESET",
            "C3": f"{prefix}_CLK", "C5": "GND", "C7": f"{prefix}_DATA",
            **{f"S{shell}": "CHASSIS_GND" for shell in range(1, 7)},
        }
        filter_expected = {
            "1": f"{prefix}_DATA", "2": f"{prefix}_CLK", "3": f"{prefix}_RESET",
            "5": f"{prefix}_VCC", "6": f"{prefix}_RESET_RAW",
            "7": f"{prefix}_CLK_RAW", "8": f"{prefix}_DATA_RAW", "9": "GND",
        }
        checks.append(
            check(
                f"{prefix} protected socket contract",
                all(net_map.get((holder, pin)) == net for pin, net in holder_expected.items())
                and all(net_map.get((protection, pin)) == net for pin, net in filter_expected.items())
                and net_map.get((holder, "C6"), "").startswith("unconnected-")
                and net_map.get((protection, "4"), "").startswith("unconnected-"),
                "TPD3F303 is between the carrier socket and SIM holder; VPP and filter NC stay open",
            )
        )

    checks.append(
        check(
            "mechanical service declaration",
            "Socket mouths face the daughterboard service edge" in schematic_text
            and "Four supports and the service guide" in schematic_text,
            "horizontal board orientation and structural insertion load path are explicit",
        )
    )

    failures = len(checks) - sum(checks)
    print(f"\nRESULT: {len(checks)} checks, {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
