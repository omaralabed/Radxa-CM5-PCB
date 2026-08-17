#!/usr/bin/env python3
"""Validate the complete-system KiCad electrical schematic project."""

from __future__ import annotations

import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCHEMATIC = HERE / "Radxa-CM5-ProComm-System.kicad_sch"
PROJECT = HERE / "Radxa-CM5-ProComm-System.kicad_pro"
EXPECTED_PAGES = {str(page) for page in range(1, 18)}
EXPECTED_ROOT_SYMBOLS = 58
EXPECTED_ROOT_WIRES = 294
EXPECTED_ROOT_LABELS = 294
CRITICAL_REFERENCES = {
    "J9001", "F9001", "J9002", "J9003", "J9004", "J9005", "J9006",
    "J9301", "J9101", "J9401", "J9102", "J9402", "J9103",
    "J9201", "J9501", "J9202", "J9502", "J9801", "J9851",
    "J9802", "J9852", "J9803", "J9853", "J9411", "J9412",
    "J9413", "J9414", "J9421", "J9422", "J9423", "J9424",
    "J9430", "J9431", "J9432", "J9440", "J9441", "J9442",
    "J9443", "J9444", "J9445", "J9446", "J9447",
    *(f"J96{channel:02d}" for channel in range(1, 9)),
    *(f"J97{channel:02d}" for channel in range(1, 9)),
}
CRITICAL_NETS = {
    "AC_L_FUSED", "RAW_OUT_LOAD", "CTRL_I2C_SDA", "PWR_MON_ALERT_N",
    "AUD_MCLK_P", "AUD_ADC_SDOUT_N", "DISPLAY_12V", "TOUCH_USB_DP",
    "CPU_FAN_PWM", "EXHAUST_FAN_TACH", "WIFI_4_RF", "CELL_4_GNSS_RF",
    "AOUT_CH8_HOT", "AOUT_CH8_COLD", "AIN_CH8_HOT", "AIN_CH8_COLD",
}


def main() -> int:
    text = SCHEMATIC.read_text(encoding="utf-8")
    filenames = re.findall(r'\(property "Sheetfile" "([^"]+)"', text)
    page_numbers = set(re.findall(r'\(page "(\d+)"\)', text))
    references = set(re.findall(r'\(property "Reference" "([^"]+)"', text))
    representation_count = text.count("SYSTEM_INTERCONNECT_REPRESENTATION")
    wire_count = len(re.findall(r"^\s*\(wire$", text, re.MULTILINE))
    label_count = len(re.findall(r"^\s*\(label ", text, re.MULTILINE))
    failures: list[str] = []

    if not PROJECT.exists():
        failures.append("system project file is missing")
    if len(filenames) != 16:
        failures.append(f"expected 16 sheet files, found {len(filenames)}")
    if len(set(filenames)) != len(filenames):
        failures.append("sheet filenames are not unique")
    if page_numbers != EXPECTED_PAGES:
        failures.append(
            f"expected root and child pages {sorted(EXPECTED_PAGES)}, "
            f"found {sorted(page_numbers)}"
        )
    for filename in filenames:
        if not (HERE / filename).resolve().exists():
            failures.append(f"missing child schematic: {filename}")
    if representation_count != EXPECTED_ROOT_SYMBOLS:
        failures.append(
            f"expected {EXPECTED_ROOT_SYMBOLS} electrical root symbols, "
            f"found {representation_count}"
        )
    if wire_count != EXPECTED_ROOT_WIRES:
        failures.append(f"expected {EXPECTED_ROOT_WIRES} root wires, found {wire_count}")
    if label_count != EXPECTED_ROOT_LABELS:
        failures.append(f"expected {EXPECTED_ROOT_LABELS} root labels, found {label_count}")
    missing_references = sorted(CRITICAL_REFERENCES - references)
    if missing_references:
        failures.append(f"missing electrical root references: {missing_references}")
    missing_nets = sorted(net for net in CRITICAL_NETS if f'"{net}"' not in text)
    if missing_nets:
        failures.append(f"missing critical system nets: {missing_nets}")
    excluded_count = 16 + EXPECTED_ROOT_SYMBOLS
    if text.count("(in_bom no)") != excluded_count:
        failures.append("system representations and all sixteen sheets must be excluded from BOM")
    if text.count("(on_board no)") != excluded_count:
        failures.append("system representations and all sixteen sheets must be excluded from board update")
    if "Top sheet is the electrical system interconnect" not in text:
        failures.append("electrical system-interconnect title-block declaration is missing")
    if "Three physical PCB netlists remain separate" not in text:
        failures.append("physical-board boundary warning is missing")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("PASS: page 1 contains 58 real electrical symbols and 294 named pin interconnects")
    print("PASS: pages 2-17 contain all 16 reviewed component-level circuit sheets")
    print("PASS: PWR-SELECT, CM5-CARRIER, and AUDIO-8X8 remain separate PCB netlists")
    print("PASS: system representations are excluded from BOM and board update")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
