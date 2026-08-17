#!/usr/bin/env python3
"""Validate the controlled PCB-A0 DRC state without hiding staged parts.

PCB-A0 is a source-verified mating-placement baseline, not a routed board.
Locked mating geometry must have no DRC errors. Known footprint errors are
allowed only on explicitly staged, unreleased parts outside the board outline.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "cad/kicad/PCB-REVIEW"

CONTRACTS = {
    "AUDIO-8X8": {
        "report": REPORTS / "Audio-8x8-PCB-A0-DRC.json",
        "violations": 8,
        "unconnected": 499,
        "parity": 229,
        "locked": {f"J{base + channel}" for base in (200, 300) for channel in range(1, 9)}
        | {f"A{index}" for index in range(1, 7)},
        "allowed_error_refs": set(),
        "allowed_warning_refs": {f"J{200 + channel}" for channel in range(1, 9)},
        "allowed_warning_types": {"lib_footprint_mismatch"},
    },
    "CM5-CARRIER": {
        "report": REPORTS / "CM5-Carrier-PCB-A0-DRC.json",
        "violations": 18,
        "unconnected": 499,
        "parity": 406,
        "locked": {
            "J501", "J502", "J503", "J610", "J611", "J612", "J613",
            "J702", "J703",
        }
        | {f"C{index}" for index in range(1, 7)},
        "allowed_error_refs": {"Q1110", "Q1111", "J910"},
        "allowed_warning_refs": set(),
        "allowed_warning_types": set(),
    },
    "PWR-SELECT": {
        "report": REPORTS / "PowerSelector-PCB-A0-DRC.json",
        "violations": 0,
        "unconnected": 278,
        "parity": 111,
        "locked": set(),
        "allowed_error_refs": set(),
        "allowed_warning_refs": set(),
        "allowed_warning_types": set(),
    },
}


def references(violation: dict) -> set[str]:
    text = " ".join(
        [violation.get("description", "")]
        + [item.get("description", "") for item in violation.get("items", [])]
    )
    return set(re.findall(r"\b(?:[AJCQRU]\d{1,4})\b", text))


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
                if locked_refs:
                    failures.append(
                        f"{board}: locked geometry in error {violation.get('type')}: "
                        f"{', '.join(sorted(locked_refs))}"
                    )
                if not found_refs or not found_refs <= contract["allowed_error_refs"]:
                    failures.append(
                        f"{board}: unapproved error refs {sorted(found_refs)} in "
                        f"{violation.get('type')}"
                    )
            elif severity == "warning":
                warnings += 1
                if (
                    violation.get("type") not in contract["allowed_warning_types"]
                    or not found_refs
                    or not found_refs <= contract["allowed_warning_refs"]
                ):
                    failures.append(
                        f"{board}: unapproved warning {violation.get('type')} on "
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
        print(f"\nRESULT: {len(failures)} PCB-A0 DRC baseline failures")
        return 1

    print("\nRESULT: locked mating geometry has zero DRC errors; staged exceptions match the exact allowlist")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
