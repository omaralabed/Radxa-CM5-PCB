#!/usr/bin/env python3
"""Validate the locked lid-display connectors, protection, and harness contract."""

from __future__ import annotations

import csv
import math
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
            len(rows) == 22 and complete,
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
        "U805": (
            "TPS62913RPUT",
            "Package_DFN_QFN:Texas_RPU0010A_VQFN-HR-10_2x2mm_P0.5mm",
        ),
        "L805": ("XGL4030-222MEC", "Inductor_SMD:L_Coilcraft_XxL4040"),
        "R805": ("TNPW060326K1BEEA", "Resistor_SMD:R_0603_1608Metric"),
        "R806": ("TNPW06034K99BEEA", "Resistor_SMD:R_0603_1608Metric"),
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
        "16": "HDMI_DDC_SDA", "17": "GND", "18": "HDMI_5V_OUT",
        "19": "HDMI_HPD", "SH": "CHASSIS_GND",
    }
    checks.append(
        check(
            "HDMI Type-A pin contract",
            all(net_map.get(("J801", pin)) == net for pin, net in hdmi_expected.items()),
            "TMDS, DDC, CEC, HPD, 5 V, ground, and shell nets match the Type-A allocation",
        )
    )
    checks.append(
        check(
            "Radxa-reference direct HDMI DDC",
            "R801" not in by_ref
            and "R802" not in by_ref
            and net_map.get(("J801", "15")) == "HDMI_DDC_SCL"
            and net_map.get(("J801", "16")) == "HDMI_DDC_SDA"
            and "do not add duplicate carrier pull-ups" in schematic_text,
            "DDC reaches the CM5 5 V DDC nets without duplicate carrier pull-ups",
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

    io5_expected = {
        "1": "DISPLAY_IO_12V", "2": "IO5V0_SW", "3": "IO_5V0",
        "4": "GND", "5": "IO_5V0_PG", "6": "DISPLAY_IO_12V",
        "7": "GND", "8": "IO5V0_NRSS", "9": "IO5V0_FB",
        "10": "IO5V0_SCONF",
    }
    io5_actual = 0.8 * (1.0 + 26.1 / 4.99)
    checks.append(
        check(
            "dedicated IO_5V0 regulator contract",
            all(net_map.get(("U805", pin)) == net for pin, net in io5_expected.items())
            and math.isclose(io5_actual, 5.0, rel_tol=0.005),
            f"TPS62913 is wired from DISPLAY_IO_12V and set to {io5_actual:.3f} V",
        )
    )
    checks.append(
        check(
            "separate HDMI and touch 5 V protection",
            net_map.get(("F801", "1")) == "IO_5V0"
            and net_map.get(("F801", "2")) == "HDMI_5V_OUT"
            and net_map.get(("F802", "1")) == "IO_5V0"
            and net_map.get(("F802", "2")) == "TOUCH_USB_5V",
            "IO_5V0 independently feeds the 0.10 A HDMI and 1.10 A touch polyfuses",
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
            and "DISPLAY_IO_12V" in schematic_text
            and not any("EFUSE" in row["Value"].upper() for row in rows),
            "separate fused 12 V monitor and IO buck branches; no dedicated display eFuse",
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
