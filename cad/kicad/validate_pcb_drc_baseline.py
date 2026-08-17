#!/usr/bin/env python3
"""Validate the controlled PCB-A1 placement DRC state.

PCB-A1 is a fully in-board engineering placement, not a routed board. The gate
permits only explicit preliminary-footprint defects, opposite-side THT/courtyard
notices on the audio assembly, and silkscreen warnings that routing placement
must resolve. No copper-placement error is silently accepted.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "cad/kicad/PCB-REVIEW"

CONTRACTS = {
    "AUDIO-8X8": {
        "report": REPORTS / "Audio-8x8-PCB-A1-DRC.json",
        "violations": 145,
        "unconnected": 499,
        "parity": 229,
        "locked": {f"J{base + channel}" for base in (200, 300) for channel in range(1, 9)}
        | {f"A{index}" for index in range(1, 7)},
        "allowed_error_refs": set(),
        "allowed_error_types": {"pth_inside_courtyard", "npth_inside_courtyard"},
        "allowed_warning_refs": {f"J{200 + channel}" for channel in range(1, 9)},
        "allowed_warning_types": {"lib_footprint_mismatch", "silk_over_copper"},
    },
    "CM5-CARRIER": {
        "report": REPORTS / "CM5-Carrier-PCB-A1-DRC.json",
        "violations": 92,
        "unconnected": 499,
        "parity": 406,
        "locked": {
            "J501", "J502", "J503", "J610", "J611", "J612", "J613",
            "J702", "J703",
        }
        | {f"C{index}" for index in range(1, 7)},
        "allowed_error_refs": {"Q1110", "Q1111", "J910"},
        "allowed_error_types": {"shorting_items", "clearance", "solder_mask_bridge"},
        "allowed_warning_refs": set(),
        "allowed_warning_types": {"silk_over_copper"},
    },
    "PWR-SELECT": {
        "report": REPORTS / "PowerSelector-PCB-A1-DRC.json",
        "violations": 12,
        "unconnected": 278,
        "parity": 111,
        "locked": set(),
        "allowed_error_refs": set(),
        "allowed_error_types": set(),
        "allowed_warning_refs": set(),
        "allowed_warning_types": {"silk_over_copper"},
    },
}


def references(violation: dict) -> set[str]:
    text = " ".join(
        [violation.get("description", "")]
        + [item.get("description", "") for item in violation.get("items", [])]
    )
    return set(re.findall(r"\b(?:TP|FB|[AJCDFKLQRUY])\d{1,6}\b", text))


def count_items(data: dict, key: str) -> int:
    value = data.get(key, [])
    return len(value) if isinstance(value, list) else int(value)


def main() -> int:
    failures: list[str] = []
    for board, contract in CONTRACTS.items():
        report = contract["report"]
        if not report.exists():
            failures.append(f"{board}: missing {report.relative_to(ROOT)}")
            continue
        data = json.loads(report.read_text())
        violations = data.get("violations", [])
        unconnected = count_items(data, "unconnected_items")
        parity = count_items(data, "schematic_parity")

        if len(violations) != contract["violations"]:
            failures.append(
                f"{board}: {len(violations)} violations, expected {contract['violations']}"
            )
        if unconnected != contract["unconnected"]:
            failures.append(
                f"{board}: {unconnected} unconnected, expected {contract['unconnected']}"
            )
        if parity != contract["parity"]:
            failures.append(f"{board}: {parity} parity findings, expected {contract['parity']}")

        errors = 0
        warnings = 0
        for violation in violations:
            severity = violation.get("severity")
            found_refs = references(violation)
            locked_refs = found_refs & contract["locked"]
            if severity == "error":
                errors += 1
                violation_type = violation.get("type")
                if violation_type not in contract["allowed_error_types"]:
                    failures.append(f"{board}: unapproved error type {violation_type}")
                elif board == "AUDIO-8X8":
                    # KiCad checks THT pins against courtyards on both assembly
                    # sides. These notices are allowed only where an unlocked
                    # B.Cu part crosses a locked F.Cu XLR body projection; pad
                    # and support-hole clearances remain ordinary hard errors.
                    if not locked_refs or not (found_refs - contract["locked"]):
                        failures.append(
                            f"{board}: courtyard error is not a locked-XLR/unlocked-B.Cu pair: "
                            f"{sorted(found_refs)}"
                        )
                elif not found_refs or not found_refs <= contract["allowed_error_refs"]:
                    failures.append(
                        f"{board}: unapproved error refs {sorted(found_refs)} in "
                        f"{violation_type}"
                    )
            elif severity == "warning":
                warnings += 1
                violation_type = violation.get("type")
                warning_ok = violation_type in contract["allowed_warning_types"] and bool(found_refs)
                if violation_type == "lib_footprint_mismatch":
                    warning_ok = warning_ok and found_refs <= contract["allowed_warning_refs"]
                elif violation_type == "silk_over_copper":
                    warning_ok = warning_ok and bool(found_refs - contract["locked"])
                if not warning_ok:
                    failures.append(
                        f"{board}: unapproved warning {violation_type} on "
                        f"{sorted(found_refs)}"
                    )
            else:
                failures.append(f"{board}: unexpected severity {severity!r}")

        print(
            f"PASS  {board}: {errors} errors, {warnings} warnings, "
            f"{unconnected} unconnected, {parity} schematic-parity findings"
        )

    if failures:
        for failure in failures:
            print(f"FAIL  {failure}")
        print(f"\nRESULT: {len(failures)} PCB-A1 DRC baseline failures")
        return 1

    print("\nRESULT: PCB-A1 placement findings match the exact preliminary/cross-side allowlist")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
