#!/usr/bin/env python3
"""Validate the controlled Network/PCIe production BOM and release invariants."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent.parent.parent
BOM = WORKSPACE / "docs" / "network_pcie_bom_a1.csv"
SCHEMATIC = ROOT / "Network-PCIe.kicad_sch"
INDUCTOR_FOOTPRINT = ROOT / "CM5Carrier.pretty" / "TDK_VLS3012HBX.kicad_mod"


def check(name: str, condition: bool, detail: str) -> bool:
    print(f"{'PASS' if condition else 'FAIL'}  {name}: {detail}")
    return condition


def refs_with_mpn(rows: list[dict[str, str]], mpn: str) -> set[str]:
    return {row["Reference"] for row in rows if row["MPN"] == mpn}


def main() -> int:
    rows = list(csv.DictReader(BOM.open())) if BOM.exists() else []
    by_ref = {row["Reference"]: row for row in rows}
    schematic_text = SCHEMATIC.read_text() if SCHEMATIC.exists() else ""
    footprint_text = INDUCTOR_FOOTPRINT.read_text() if INDUCTOR_FOOTPRINT.exists() else ""
    checks: list[bool] = []

    complete = bool(rows) and all(
        row["Manufacturer"] and row["MPN"] and row["Footprint"] for row in rows
    )
    checks.append(
        check(
            "Network/PCIe production BOM",
            len(rows) == 64 and complete,
            f"{len(rows)} rows; all manufacturer, MPN, and footprint fields complete",
        )
    )

    controlled_parts = {
        "U601": (
            "PI7C9X2G608GPCNJEX",
            "Package_BGA:BGA-196_15x15mm_Layout14x14_P1.0mm",
        ),
        "U611": (
            "LAN7430T-I/Y9X",
            "Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.3x5.3mm_ThermalVias",
        ),
        "J610": ("74991114412", "CM5Carrier:T_Wurth_WE-RJ45LAN_74991114412"),
        "J620": ("0679101002", "CM5Carrier:Molex_0679101002_Mini_PCIe"),
        "L6111": ("VLS3012HBX-3R3M-N", "CM5Carrier:TDK_VLS3012HBX"),
        "Y611": (
            "ABM8-25.000MHZ-10-D1G-T",
            "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
        ),
    }
    for reference, (mpn, footprint) in controlled_parts.items():
        row = by_ref.get(reference, {})
        checks.append(
            check(
                f"{reference} controlled part",
                row.get("MPN") == mpn and row.get("Footprint") == footprint,
                f"{row.get('MPN', 'missing')} / {row.get('Footprint', 'missing')}",
            )
        )

    expected_groups = {
        "industrial LAN7430 endpoints": (
            "LAN7430T-I/Y9X",
            {"U611", "U612", "U613"},
        ),
        "active 3.3 uH LAN inductors": (
            "VLS3012HBX-3R3M-N",
            {"L6111", "L6121", "L6131"},
        ),
        "industrial 25 MHz crystals": (
            "ABM8-25.000MHZ-10-D1G-T",
            {"Y611", "Y612", "Y613"},
        ),
        "Wurth integrated-magnetics jacks": (
            "74991114412",
            {"J610", "J611", "J612", "J613"},
        ),
        "low-capacitance Ethernet ESD arrays": (
            "TPD4E05U06DQAR",
            {f"U{reference}" for reference in range(630, 638)},
        ),
        "10 uF LAN buck capacitors": (
            "GRM188R61E106MA73D",
            {"C6111", "C6121", "C6131"},
        ),
        "1 uF LAN LDO capacitors": (
            "GRM155R6YA105KE11D",
            {"C6113", "C6123", "C6133"},
        ),
        "15 pF crystal load capacitors": (
            "GRM1555C1H150JA01D",
            {"C6114", "C6115", "C6124", "C6125", "C6134", "C6135"},
        ),
    }
    for name, (mpn, expected_refs) in expected_groups.items():
        observed = refs_with_mpn(rows, mpn)
        checks.append(check(name, observed == expected_refs, f"refs {sorted(observed)}"))

    value_counts = Counter(row["Value"] for row in rows)
    checks.append(
        check(
            "LAN7430 2.5 V LDO capacitor requirement",
            value_counts["1uF 35V X5R / ESR <1R"] == 3,
            f"{value_counts['1uF 35V X5R / ESR <1R']} channels use the controlled <1 ohm ESR value",
        )
    )
    checks.append(
        check(
            "606-mode switch strap",
            by_ref.get("R601", {}).get("MPN") == "RC0603FR-074K7L"
            and "GPIO[1:0] = 01 selects 606 mode" in schematic_text,
            "GPIO0 has a 4.7 k pull-up and GPIO1 uses the device pulldown",
        )
    )
    checks.append(
        check(
            "PCIe reset timing requirement",
            "stable for at least 100 ms" in schematic_text,
            "PERST# remains asserted until rails and REFCLK are stable for 100 ms",
        )
    )
    checks.append(
        check(
            "unused switch port isolation",
            "PCIE_SPARE" not in schematic_text and "J621" not in by_ref,
            "port 5 is disabled/unrouted and no generic PCIe cable header is present",
        )
    )
    checks.append(
        check(
            "grounded four-pad crystal model",
            schematic_text.count("CM5Carrier:Crystal_GND24_3225") >= 3,
            "all three oscillators use the project-local grounded-case symbol",
        )
    )
    checks.append(
        check(
            "TDK inductor controlled land pattern",
            INDUCTOR_FOOTPRINT.exists()
            and footprint_text.count('(pad "1" smd') == 1
            and footprint_text.count('(pad "2" smd') == 1
            and "(size 1.00 3.40)" in footprint_text,
            "two 1.0 x 3.4 mm lands with the drawing-backed 1.1 mm gap",
        )
    )

    failures = len(checks) - sum(checks)
    print(f"\nRESULT: {len(checks)} checks, {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
