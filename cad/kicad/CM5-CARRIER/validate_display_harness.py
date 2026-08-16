#!/usr/bin/env python3
"""Validate the locked lid-display connectors, protection, and harness contract."""

from __future__ import annotations

import csv
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent.parent.parent
BOM = WORKSPACE / "docs" / "display_harness_bom_a1.csv"
SCHEMATIC = ROOT / "Display-Harness.kicad_sch"
KICAD_CLI = Path(
    os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
)


def check(name: str, condition: bool, detail: str) -> bool:
    print(f"{'PASS' if condition else 'FAIL'}  {name}: {detail}")
    return condition


def export_net_map() -> dict[tuple[str, str], str]:
    with tempfile.TemporaryDirectory(prefix="radxa-display-validation-") as temp:
        output = Path(temp) / "Display-Harness.xml"
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

    complete = bool(rows) and all(
        row["Manufacturer"] and row["MPN"] and row["Footprint"] for row in rows
    )
    checks.append(
        check(
            "display-harness controlled BOM",
            len(rows) == 13 and complete,
            f"{len(rows)} rows; every manufacturer, MPN, and footprint field is complete",
        )
    )

    expected_parts = {
        "J801": (
            "208658-1001",
            "Connector_Video:HDMI_A_Molex_208658-1001_Horizontal",
        ),
        "J802": (
            "692122030100",
            "Connector_USB:USB3_A_Receptacle_Wuerth_692122030100",
        ),
        "J803": (
            "43045-0412",
            "Connector_Molex:Molex_Micro-Fit_3.0_43045-0412_2x02_P3.00mm_Vertical",
        ),
        "F801": ("0603L010YR", "Fuse:Fuse_0603_1608Metric"),
        "F802": ("1206L110/16WR", "Fuse:Fuse_1206_3216Metric"),
        "C801": ("GRM188R61E106MA73D", "Capacitor_SMD:C_0603_1608Metric"),
        "R801": ("RC0603FR-072K2L", "Resistor_SMD:R_0603_1608Metric"),
    }
    for reference, (mpn, footprint) in expected_parts.items():
        row = by_ref.get(reference, {})
        checks.append(
            check(
                f"{reference} controlled part",
                row.get("MPN") == mpn and row.get("Footprint") == footprint,
                f"{row.get('MPN', 'missing')} / {row.get('Footprint', 'missing')}",
            )
        )

    esd_refs = {"U801", "U802", "U803", "U804"}
    checks.append(
        check(
            "low-capacitance display ESD arrays",
            {
                reference
                for reference, row in by_ref.items()
                if row.get("MPN") == "TPD4E05U06DQAR"
            } == esd_refs,
            "three HDMI arrays and one USB-touch array use TPD4E05U06DQAR",
        )
    )

    hdmi_expected = {
        "1": "HDMI_D2_P", "2": "GND", "3": "HDMI_D2_N",
        "4": "HDMI_D1_P", "5": "GND", "6": "HDMI_D1_N",
        "7": "HDMI_D0_P", "8": "GND", "9": "HDMI_D0_N",
        "10": "HDMI_CLK_P", "11": "GND", "12": "HDMI_CLK_N",
        "13": "HDMI_CEC", "14": "HDMI_HEAC_P", "15": "HDMI_DDC_SCL",
        "16": "HDMI_DDC_SDA", "17": "GND", "18": "HDMI_5V_OPTION",
        "19": "HDMI_HPD", "SH": "CHASSIS_GND",
    }
    checks.append(
        check(
            "HDMI Type-A pin contract",
            all(net_map.get(("J801", pin)) == net for pin, net in hdmi_expected.items()),
            "TMDS, DDC, CEC, HPD, 5 V, ground, and shell nets match the Type-A allocation",
        )
    )

    usb_expected = {
        "1": "TOUCH_USB_5V", "2": "TOUCH_USB_DM", "3": "TOUCH_USB_DP",
        "4": "GND", "SH": "CHASSIS_GND",
    }
    usb2_only = all(
        net_map.get(("J802", pin), "").startswith("unconnected-")
        for pin in ("5", "6", "7", "8", "9")
    )
    checks.append(
        check(
            "USB 2 touch-only contract",
            all(net_map.get(("J802", pin)) == net for pin, net in usb_expected.items())
            and usb2_only,
            "USB-A host carries VBUS, D-/D+ and ground; SuperSpeed contacts remain NC",
        )
    )

    display_power_expected = {
        "1": "DISPLAY_12V", "2": "DISPLAY_12V", "3": "GND", "4": "GND",
    }
    checks.append(
        check(
            "duplicated 12 V monitor-power contacts",
            all(net_map.get(("J803", pin)) == net for pin, net in display_power_expected.items()),
            "two Micro-Fit contacts carry 12 V and two carry return for the 2.5 A branch",
        )
    )

    checks.append(
        check(
            "display power architecture",
            "No local display eFuse" in schematic_text
            and "2.5 A continuous / 30 W branch" in schematic_text
            and not any("EFUSE" in row["Value"].upper() for row in rows),
            "simple upstream-fused 12 V branch; no dedicated display eFuse",
        )
    )
    checks.append(
        check(
            "service-loop acceptance contract",
            "1000 +/- 25 mm each" in schematic_text
            and "300 mm panel lift / 45 degree tilt" in schematic_text,
            "all three lid cables retain full travel plus panel-lift service slack",
        )
    )

    failures = len(checks) - sum(checks)
    print(f"\nRESULT: {len(checks)} checks, {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
