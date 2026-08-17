#!/usr/bin/env python3
"""Validate the controlled PCBWay one-shot submission manifest."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MANIFEST = HERE / "release-manifest-a0.csv"
AUDIT = ROOT / "cad/kicad/reports/component-footprint-audit.md"
MECHANICAL = ROOT / "fabrication/mechanical-release/mechanical-release-a2.json"
PRODUCT_BOARDS = {
    "CM5-CARRIER": ROOT / "cad/kicad/CM5-CARRIER/CM5-Carrier.kicad_pcb",
    "AUDIO-8X8": ROOT / "cad/kicad/AUDIO-8X8/Audio-8x8.kicad_pcb",
    "PWR-SELECT": ROOT / "cad/kicad/PWR-SELECT/PowerSelector.kicad_pcb",
}
ALLOWED_STATES = {"READY", "OPEN", "MISSING", "BLOCKED", "N/A"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--release",
        action="store_true",
        help="fail unless every required manifest row and release gate is ready",
    )
    return parser.parse_args()


def load_rows() -> list[dict[str, str]]:
    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    required = {
        "item_id",
        "package",
        "required",
        "state",
        "path_or_pattern",
        "release_evidence",
        "notes",
    }
    if not rows or set(rows[0]) != required:
        raise ValueError("manifest header does not match the controlled schema")
    return rows


def audit_counts() -> tuple[int | None, int | None, int | None]:
    text = AUDIT.read_text(encoding="utf-8")
    component = re.search(r"Components audited: (\d+)", text)
    routing = re.search(r"Routing blockers: (\d+)", text)
    production = re.search(r"Production(?:/BOM)? blockers: (\d+)", text)
    return tuple(
        int(match.group(1)) if match else None
        for match in (component, routing, production)
    )


def main() -> int:
    args = parse_args()
    rows = load_rows()
    errors: list[str] = []
    blockers: list[str] = []
    ids: set[str] = set()

    for row in rows:
        item_id = row["item_id"]
        state = row["state"]
        if item_id in ids:
            errors.append(f"duplicate manifest item: {item_id}")
        ids.add(item_id)
        if state not in ALLOWED_STATES:
            errors.append(f"{item_id}: invalid state {state}")

        target = (HERE / row["path_or_pattern"]).resolve()
        if state == "READY" and not target.exists():
            errors.append(f"{item_id}: READY file does not exist: {target}")
        if row["required"] == "YES" and state != "READY":
            blockers.append(f"{item_id} [{row['package']}]: {state}")

    components, routing, production = audit_counts()
    if routing is None or production is None:
        errors.append("could not read footprint blocker counts")
    elif routing or production:
        blockers.append(
            f"footprint audit: {routing} routing / {production} production blockers"
        )

    mechanical = json.loads(MECHANICAL.read_text(encoding="utf-8"))
    if mechanical.get("release_state") != "RELEASED":
        blockers.append(
            "mechanical release: "
            + str(mechanical.get("release_state", "UNKNOWN"))
        )

    for board, path in PRODUCT_BOARDS.items():
        if not path.exists():
            blockers.append(f"{board}: routed PCB source missing")

    states = Counter(row["state"] for row in rows)
    print(f"Manifest rows: {len(rows)}")
    print("States: " + ", ".join(f"{key}={states[key]}" for key in sorted(states)))
    print(f"Footprint audit: components={components}, routing={routing}, production={production}")
    print(f"Release blockers: {len(blockers)}")
    for blocker in blockers:
        print(f"  - {blocker}")

    if errors:
        print(f"Manifest errors: {len(errors)}", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    if args.release and blockers:
        print("RELEASE BLOCKED", file=sys.stderr)
        return 2

    print("Manifest structure valid; release remains held." if blockers else "RELEASE READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
