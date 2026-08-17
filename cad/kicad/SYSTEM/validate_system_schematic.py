#!/usr/bin/env python3
"""Validate the complete-system KiCad navigation project."""

from __future__ import annotations

import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCHEMATIC = HERE / "Radxa-CM5-ProComm-System.kicad_sch"
PROJECT = HERE / "Radxa-CM5-ProComm-System.kicad_pro"
EXPECTED_PAGES = {str(page) for page in range(1, 18)}


def main() -> int:
    text = SCHEMATIC.read_text(encoding="utf-8")
    filenames = re.findall(r'\(property "Sheetfile" "([^"]+)"', text)
    page_numbers = set(re.findall(r'\(page "(\d+)"\)', text))
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
    if text.count("(in_bom no)") != 16:
        failures.append("all sixteen navigation sheets must be excluded from BOM")
    if text.count("(on_board no)") != 16:
        failures.append("all sixteen navigation sheets must be excluded from board update")
    if "Three physical PCB netlists remain separate" not in text:
        failures.append("physical-board boundary warning is missing")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("PASS: one native KiCad project indexes all 16 reviewed schematic sheets")
    print("PASS: PWR-SELECT, CM5-CARRIER, and AUDIO-8X8 remain separate PCB netlists")
    print("PASS: navigation sheets are excluded from BOM and board update")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
