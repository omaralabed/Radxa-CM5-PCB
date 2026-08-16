#!/usr/bin/env python3
"""Validate the controlled Thermal-IO production BOM and key interfaces."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent.parent.parent
BOM = WORKSPACE / "docs" / "thermal_io_bom_a1.csv"


def check(name: str, condition: bool, detail: str) -> bool:
    print(f"{'PASS' if condition else 'FAIL'}  {name}: {detail}")
    return condition


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
            len(rows) == 66 and complete,
            f"{len(rows)} rows; all manufacturer, MPN, and footprint fields complete",
        )
    )

    expected = {
        "U1000": ("PCA9306DP,118", "Package_SO:TSSOP-8_3x3mm_P0.65mm"),
        "U1001": ("TCA9535PWR", "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm"),
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
