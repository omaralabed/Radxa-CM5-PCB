#!/usr/bin/env python3
"""Export one deterministic BOM covering the six detailed AUDIO-8X8 sheets."""

from __future__ import annotations

import csv
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent.parent.parent
OUTPUT = WORKSPACE / "docs" / "audio_8x8_bom_a1.csv"
KICAD_CLI = Path(
    os.environ.get(
        "KICAD_CLI",
        "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
    )
)
SHEETS = (
    "Audio-TDM-Clock",
    "AK5558-ADC",
    "AK4458-DAC",
    "Audio-Inputs",
    "Audio-Outputs",
    "Audio-Power",
)
FIELDS = (
    "Sheet",
    "Reference",
    "Value",
    "Footprint",
    "Manufacturer",
    "MPN",
    "Qty",
    "RoutingGate",
)


def field(component: ET.Element, name: str) -> str:
    node = component.find(f"./fields/field[@name='{name}']")
    return (node.text or "").strip() if node is not None else ""


def reference_key(reference: str) -> tuple[str, int, str]:
    prefix = "".join(character for character in reference if not character.isdigit())
    digits = "".join(character for character in reference if character.isdigit())
    return prefix, int(digits or 0), reference


def main() -> int:
    rows: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="audio-8x8-bom-") as temp:
        for sheet in SHEETS:
            netlist = Path(temp) / f"{sheet}.xml"
            result = subprocess.run(
                [
                    str(KICAD_CLI),
                    "sch",
                    "export",
                    "netlist",
                    "--format",
                    "kicadxml",
                    "--output",
                    str(netlist),
                    str(ROOT / f"{sheet}.kicad_sch"),
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode:
                raise RuntimeError(f"Netlist export failed for {sheet}:\n{result.stderr}")
            for component in ET.parse(netlist).findall("./components/comp"):
                reference = component.attrib["ref"]
                if reference.startswith("#"):
                    continue
                gate = ""
                if sheet in ("AK5558-ADC", "AK4458-DAC") and reference in ("U201", "U301"):
                    gate = "HOLD: exposed-pad/stencil/assembly coupon"
                if sheet == "Audio-Outputs" and reference in {f"K{number}" for number in range(501, 509)}:
                    gate = "HOLD: relay land-pattern/insertion coupon"
                rows.append(
                    {
                        "Sheet": sheet,
                        "Reference": reference,
                        "Value": (component.findtext("value") or "").strip(),
                        "Footprint": (component.findtext("footprint") or "").strip(),
                        "Manufacturer": field(component, "Manufacturer"),
                        "MPN": field(component, "MPN"),
                        "Qty": "1",
                        "RoutingGate": gate,
                    }
                )

    rows.sort(key=lambda row: (SHEETS.index(row["Sheet"]), reference_key(row["Reference"])))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Exported {len(rows)} detailed AUDIO-8X8 BOM rows to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
