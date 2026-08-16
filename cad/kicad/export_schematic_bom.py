#!/usr/bin/env python3
"""Export a deterministic, reference-level CSV BOM from a KiCad schematic."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET


KICAD_CLI = Path(
    os.environ.get(
        "KICAD_CLI",
        "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
    )
)
FIELDS = (
    "Reference",
    "Value",
    "Footprint",
    "Manufacturer",
    "MPN",
    "Assembly",
    "Qty",
    "DNP",
)


def field(component: ET.Element, name: str) -> str:
    node = component.find(f"./fields/field[@name='{name}']")
    return (node.text or "").strip() if node is not None else ""


def export_netlist(schematic: Path, output: Path) -> None:
    result = subprocess.run(
        [
            str(KICAD_CLI),
            "sch",
            "export",
            "netlist",
            "--format",
            "kicadxml",
            "--output",
            str(output),
            str(schematic),
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(
            f"KiCad netlist export failed for {schematic}:\n{result.stderr.strip()}"
        )


def reference_key(reference: str) -> tuple[str, int, str]:
    prefix = "".join(character for character in reference if not character.isdigit())
    digits = "".join(character for character in reference if character.isdigit())
    return prefix, int(digits or 0), reference


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schematic", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--exclude", action="append", default=[])
    args = parser.parse_args()

    excluded = set(args.exclude)
    with tempfile.TemporaryDirectory(prefix="radxa-bom-") as temp:
        netlist = Path(temp) / "schematic.xml"
        export_netlist(args.schematic, netlist)
        components = ET.parse(netlist).findall("./components/comp")

    rows = []
    for component in components:
        reference = component.attrib["ref"]
        if reference in excluded or reference.startswith("#"):
            continue
        value = (component.findtext("value") or "").strip()
        dnp = "YES" if "DNP" in value.upper() else ""
        rows.append(
            {
                "Reference": reference,
                "Value": value,
                "Footprint": (component.findtext("footprint") or "").strip(),
                "Manufacturer": field(component, "Manufacturer"),
                "MPN": field(component, "MPN"),
                "Assembly": field(component, "Assembly"),
                "Qty": "1",
                "DNP": dnp,
            }
        )

    rows.sort(key=lambda row: reference_key(row["Reference"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Exported {len(rows)} BOM rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
