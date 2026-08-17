#!/usr/bin/env python3
"""Validate the controlled Thermal-IO production BOM and key interfaces."""

from __future__ import annotations

import csv
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent.parent.parent
BOM = WORKSPACE / "docs" / "thermal_io_bom_a1.csv"
SCHEMATIC = ROOT / "Thermal-IO.kicad_sch"
KICAD_CLI = Path(
    os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
)


def check(name: str, condition: bool, detail: str) -> bool:
    print(f"{'PASS' if condition else 'FAIL'}  {name}: {detail}")
    return condition


def export_net_map() -> dict[tuple[str, str], str]:
    with tempfile.TemporaryDirectory(prefix="radxa-thermal-validation-") as temp:
        output = Path(temp) / "Thermal-IO.xml"
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
    checks: list[bool] = []

    complete = bool(rows) and all(
        row["Manufacturer"] and row["MPN"] and row["Footprint"] for row in rows
    )
    checks.append(
        check(
            "Thermal-IO production BOM",
            len(rows) == 73 and complete,
            f"{len(rows)} rows; all manufacturer, MPN, and footprint fields complete",
        )
    )

    expected = {
        "U1000": ("PCA9306DP,118", "Package_SO:TSSOP-8_3x3mm_P0.65mm"),
        "U1001": ("TCA9535PWR", "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm"),
        "U1002": ("TCA9535PWR", "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm"),
        "U1003": ("TCA9535PWR", "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm"),
        "U1020": (
            "EMC2305-1-AP-TR",
            "Package_DFN_QFN:QFN-16-1EP_4x4mm_P0.65mm_EP2.1x2.1mm",
        ),
        "U1050": (
            "TMP117AIDRVR",
            "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm",
        ),
        "F1021": ("2920L300/15DR", "Fuse:Fuse_2920_7451Metric"),
        "F1022": ("1812L110/33DR", "Fuse:Fuse_1812_4532Metric"),
        "J1021": (
            "43045-0412",
            "Connector_Molex:Molex_Micro-Fit_3.0_43045-0412_2x02_P3.00mm_Vertical",
        ),
        "J1060": (
            "43045-0812",
            "Connector_Molex:Molex_Micro-Fit_3.0_43045-0812_2x04_P3.00mm_Vertical",
        ),
        "Q1060": ("2N7002K-7", "Package_TO_SOT_SMD:SOT-23"),
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

    for reference in ("U1050", "U1051", "U1052"):
        checks.append(
            check(
                f"{reference} industrial sensor grade",
                by_ref.get(reference, {}).get("MPN") == "TMP117AIDRVR",
                "-55 C to 150 C A-grade device required",
            )
        )

    net_map = export_net_map()
    checks.append(
        check(
            "PCA9306 enable/bias network",
            net_map.get(("U1000", "7")) == "CTRL_I2C_BIAS"
            and net_map.get(("U1000", "8")) == "CTRL_I2C_BIAS"
            and net_map.get(("R1006", "1")) == "LOGIC_3V3"
            and net_map.get(("R1006", "2")) == "CTRL_I2C_BIAS",
            "EN and VREF2 share the datasheet-required 200 k pull-up node",
        )
    )
    address_straps = {
        "U1001": {"2": "GND", "3": "GND", "21": "GND"},
        "U1002": {"2": "GND", "3": "GND", "21": "LOGIC_3V3"},
        "U1003": {"2": "LOGIC_3V3", "3": "GND", "21": "GND"},
    }
    checks.append(
        check(
            "TCA9535 unique address straps",
            all(
                net_map.get((reference, pin)) == net
                for reference, pins in address_straps.items()
                for pin, net in pins.items()
            ),
            "expanders resolve to 0x20, 0x21, and 0x22 with no address collision",
        )
    )
    control_map = {
        "4": "MODEM_POWER_EN", "5": "WIFI_POWER_EN", "6": "SYS_4V0_PG",
        "7": "MODEM_3V8_PRE_PG", "8": "MODEM_3V8_PG", "9": "WIFI_3V3_PRE_PG",
        "10": "WIFI_3V3_PG", "11": "NET_3V3_PG", "13": "PCIE_1V0_PG",
        "14": "LOGIC_1V8_PG", "15": "AUX_12V_PG", "16": "LOGIC_3V3_PG",
        "17": "IO_5V0_PG", "18": "VALID_DTAP_N", "19": "VALID_GOLD_N",
    }
    checks.append(
        check(
            "radio enable and power-state expander contract",
            all(net_map.get(("U1003", pin)) == net for pin, net in control_map.items()),
            f"U1003 maps {len(control_map)} enable/status signals to the locked firmware pin contract",
        )
    )
    checks.append(
        check(
            "expander reset-state radio safety",
            net_map.get(("R1019", "1")) == "MODEM_POWER_EN"
            and net_map.get(("R1019", "2")) == "GND"
            and net_map.get(("R1022", "1")) == "WIFI_POWER_EN"
            and net_map.get(("R1022", "2")) == "GND",
            "radio final rails remain off while TCA9535 ports power up as inputs",
        )
    )
    checks.append(
        check(
            "local expander decoupling",
            all(
                net_map.get((reference, "1")) == "LOGIC_3V3"
                and net_map.get((reference, "2")) == "GND"
                for reference in ("C1011", "C1012", "C1013")
            ),
            "each TCA9535 has a dedicated 100 nF bypass capacitor",
        )
    )

    cpu_fan_max_a = 21.0 / 12.0
    checks.append(
        check(
            "CPU fan room-temperature PPTC headroom",
            3.0 >= cpu_fan_max_a * 1.5,
            f"3.0 A hold vs {cpu_fan_max_a:.2f} A fan datasheet maximum; hot derating remains a chamber test",
        )
    )
    aux_fan_max_a = 0.52
    checks.append(
        check(
            "Enclosure fan 50 C PPTC headroom",
            0.83 >= aux_fan_max_a * 1.5,
            "1812L110/33 holds 0.83 A at 50 C vs 0.52 A THA maximum",
        )
    )

    failures = len(checks) - sum(checks)
    print(f"\nRESULT: {len(checks)} checks, {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
