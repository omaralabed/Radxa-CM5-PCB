#!/usr/bin/env python3
"""Validate the WWAN, dual-SIM, and RF harness capture."""

from __future__ import annotations

import csv
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent.parent.parent
BOM = WORKSPACE / "docs" / "wwan_sim_bom_a1.csv"
SCHEMATIC = ROOT / "WWAN-SIM.kicad_sch"
KICAD_CLI = Path(
    os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
)


def check(name: str, condition: bool, detail: str) -> bool:
    print(f"{'PASS' if condition else 'FAIL'}  {name}: {detail}")
    return condition


def export_net_map() -> dict[tuple[str, str], str]:
    with tempfile.TemporaryDirectory(prefix="radxa-wwan-validation-") as temp:
        output = Path(temp) / "WWAN-SIM.xml"
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

    board_rows = [row for row in rows if row["Reference"] not in {"J711", "J712", "J713", "J714"}]
    complete = bool(rows) and all(
        row["Manufacturer"] and row["MPN"] and (row["Footprint"] or row["Reference"].startswith("J71"))
        for row in rows
    )
    checks.append(
        check(
            "WWAN/SIM controlled BOM",
            len(rows) == 26 and len(board_rows) == 22 and complete,
            f"{len(board_rows)} board parts plus four off-board RF pigtail assemblies",
        )
    )

    expected = {
        "J701": ("2199230-3", "CM5Carrier:TE_2199230-3_M2_Key_B_4.2mm"),
        "J702": ("693043020611", "CM5Carrier:J_Wurth_WR-CRD_693043020611"),
        "U702": ("TPD4E05U06DQAR", "Package_SON:USON-10_2.5x1.0mm_P0.5mm"),
        "U704": (
            "FSA2567MPX",
            "Package_DFN_QFN:WQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm",
        ),
        "U705": (
            "TPD3F303DPVR",
            "Package_SON:Texas_R-PUSON-N8_USON-8-1EP_1.6x2.1mm_P0.5mm_EP0.4x1.7mm",
        ),
        "C701": ("6SVP220MX", "Capacitor_SMD:CP_Elec_8x6.9"),
        "C702": ("6SVP220MX", "Capacitor_SMD:CP_Elec_8x6.9"),
        "C703": ("C1005X7R1H104K050BB", "Capacitor_SMD:C_0402_1005Metric"),
        "C704": ("GRM1885C1H682JA01D", "Capacitor_SMD:C_0603_1608Metric"),
        "C705": ("GRM1555C1H221JA01D", "Capacitor_SMD:C_0402_1005Metric"),
        "C706": ("GRM1555C1H680JA01D", "Capacitor_SMD:C_0402_1005Metric"),
        "C710": ("GRM1555C1H150JA01D", "Capacitor_SMD:C_0402_1005Metric"),
        "C711": ("GRM1555C1H9R1BA01D", "Capacitor_SMD:C_0402_1005Metric"),
        "C712": ("GRM1555C1H4R7BA01D", "Capacitor_SMD:C_0402_1005Metric"),
        "D701": ("SMF4L5.0AT1G", "Diode_SMD:D_SOD-123F"),
        "R701": ("RC0603FR-07100KL", "Resistor_SMD:R_0603_1608Metric"),
    }
    for reference, (mpn, footprint) in expected.items():
        row = by_ref.get(reference, {})
        checks.append(
            check(
                f"{reference} controlled part",
                row.get("MPN") == mpn and row.get("Footprint") == footprint,
                f"{row.get('MPN', 'missing')} / {row.get('Footprint', 'missing')}",
            )
        )

    rf_refs = {"J711", "J712", "J713", "J714"}
    checks.append(
        check(
            "cellular RF harness contract",
            all(
                by_ref.get(reference, {}).get("Manufacturer") == "ECT"
                and by_ref.get(reference, {}).get("MPN") == "818033349"
                and not by_ref.get(reference, {}).get("Footprint")
                for reference in rf_refs
            ),
            "four off-board USS RF IV-to-SMA pigtail/bulkhead assemblies",
        )
    )

    mux_expected = {
        "1": "SIM2_VCC", "3": "SIM1_RESET_RAW", "5": "SIM2_RESET_RAW",
        "7": "SIM1_CLK_RAW", "9": "SIM2_CLK_RAW", "11": "SIM1_DATA_RAW",
        "13": "SIM2_DATA_RAW", "15": "SIM1_VCC",
    }
    checks.append(
        check(
            "FSA2567 physical-slot cross-map",
            all(net_map.get(("U704", pin)) == net for pin, net in mux_expected.items()),
            "SEL high selects mux channel 2, which is deliberately physical SIM 1",
        )
    )

    for reference, prefix in (("U705", "SIM1"), ("U706", "SIM2")):
        expected_nets = {
            "1": f"{prefix}_DATA", "2": f"{prefix}_CLK", "3": f"{prefix}_RESET",
            "5": f"{prefix}_VCC", "6": f"{prefix}_RESET_RAW",
            "7": f"{prefix}_CLK_RAW", "8": f"{prefix}_DATA_RAW", "9": "GND",
        }
        checks.append(
            check(
                f"{prefix} protected interface",
                all(net_map.get((reference, pin)) == net for pin, net in expected_nets.items()),
                "TPD3F303 filters RESET/CLK/DATA and clamps SIM VCC",
            )
        )

    test_refs = {f"TP72{index:02d}" for index in range(1, 9)}
    test_nets = {net_map.get((reference, "1"), "") for reference in test_refs}
    checks.append(
        check(
            "stub-free factory probing",
            "J720" not in by_ref
            and test_refs.issubset({reference for reference, _pin in net_map})
            and not any(net.startswith("WWAN_USB") for net in test_nets),
            "eight copper control/power probes; no USB 2/3 test-header branch",
        )
    )
    checks.append(
        check(
            "RM520N-GL socket-local VCC reference network",
            {f"C{reference}" for reference in range(701, 713)}.issubset(by_ref)
            and net_map.get(("D701", "1")) == "MODEM_3V8"
            and net_map.get(("D701", "2")) == "GND"
            and all(
                net_map.get((f"C{reference}", "1")) == "MODEM_3V8"
                and net_map.get((f"C{reference}", "2")) == "GND"
                for reference in range(701, 713)
            )
            and "C1189-C1192 retain 1320 uF upstream bulk" in schematic_text,
            "two local 220 uF banks, the full HF ladder, and a 5 V TVS supplement the upstream regulator bulk",
        )
    )

    failures = len(checks) - sum(checks)
    print(f"\nRESULT: {len(checks)} checks, {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
