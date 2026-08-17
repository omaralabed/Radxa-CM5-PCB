#!/usr/bin/env python3
"""Generate the navigation-only KiCad project for the complete system."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

import kicad_sch_api as ksa


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "cad/kicad/SYSTEM"
PROJECT_NAME = "Radxa-CM5-ProComm-System"
SCHEMATIC = HERE / f"{PROJECT_NAME}.kicad_sch"
PROJECT = HERE / f"{PROJECT_NAME}.kicad_pro"
NAMESPACE = uuid.UUID("470d65ea-a7a0-5de5-b5fb-8f154ae31baa")


SHEETS = [
    ("PWR-SELECT", "../PWR-SELECT/PowerSelector.kicad_sch", (30, 63), "2"),
    ("CM5 Interface Contract", "../CM5-CARRIER/CM5-Carrier.kicad_sch", (30, 143), "3"),
    ("CM5 Pin Allocation", "../CM5-CARRIER/CM5-Core-Allocated.kicad_sch", (165, 143), "4"),
    ("Network / PCIe / Wi-Fi", "../CM5-CARRIER/Network-PCIe.kicad_sch", (300, 143), "5"),
    ("WWAN / Dual SIM", "../CM5-CARRIER/WWAN-SIM.kicad_sch", (435, 143), "6"),
    ("Display Harness", "../CM5-CARRIER/Display-Harness.kicad_sch", (30, 198), "7"),
    ("Headset / Audio Control", "../CM5-CARRIER/Audio-Control.kicad_sch", (165, 198), "8"),
    ("Power Regulators", "../CM5-CARRIER/Power-Regulators-A1.kicad_sch", (300, 198), "9"),
    ("Thermal / Fans / IO", "../CM5-CARRIER/Thermal-IO.kicad_sch", (435, 198), "10"),
    ("AUDIO-8X8 Interface", "../AUDIO-8X8/Audio-8x8.kicad_sch", (30, 293), "11"),
    ("TDM / Clock / Control", "../AUDIO-8X8/Audio-TDM-Clock.kicad_sch", (165, 293), "12"),
    ("AK5558VN ADC", "../AUDIO-8X8/AK5558-ADC.kicad_sch", (300, 293), "13"),
    ("AK4458VN DAC", "../AUDIO-8X8/AK4458-DAC.kicad_sch", (435, 293), "14"),
    ("Balanced Inputs 1-8", "../AUDIO-8X8/Audio-Inputs.kicad_sch", (30, 348), "15"),
    ("Balanced Outputs 1-8", "../AUDIO-8X8/Audio-Outputs.kicad_sch", (165, 348), "16"),
    ("Audio Power", "../AUDIO-8X8/Audio-Power.kicad_sch", (300, 348), "17"),
]


def stable_uuid(name: str) -> str:
    return str(uuid.uuid5(NAMESPACE, name))


def add_index_text(
    schematic: ksa.Schematic,
    key: str,
    content: str,
    position: tuple[float, float],
    *,
    size: float,
    bold: bool = False,
) -> None:
    schematic._texts.add(
        content,
        position,
        size=size,
        bold=bold,
        text_uuid=stable_uuid(f"text:{key}"),
    )
    schematic._sync_texts_to_data()


def build_schematic() -> None:
    schematic = ksa.Schematic.create(
        name="Radxa CM5 ProComm - Complete System Schematic",
        version="20250114",
        generator="eeschema",
        generator_version="9.0",
        paper="A2",
        uuid=stable_uuid("root"),
    )
    schematic.set_title_block(
        title="Radxa CM5 ProComm - Complete System Schematic",
        date="2026-08-17",
        rev="A1",
        company="ProComm",
        comments={
            1: "Navigation index for all sixteen reviewed sheets",
            2: "Three physical PCB netlists remain separate",
            3: "Use board projects for ERC, BOM, netlist, and PCB update",
            4: "PCB ROUTING HELD FOR PHYSICAL RELEASE GATES",
        },
    )
    add_index_text(
        schematic,
        "title",
        "COMPLETE SYSTEM SCHEMATIC - 16 REVIEWED DESIGN SHEETS",
        (100, 25),
        size=3.0,
        bold=True,
    )
    add_index_text(
        schematic,
        "scope",
        "Open this project to navigate the entire design from one KiCad file. "
        "The source selector, carrier, and audio board remain separate physical "
        "PCBs with separate ERC, BOM, netlist, and layout release gates.",
        (150, 36),
        size=1.5,
    )
    add_index_text(
        schematic,
        "power-heading",
        "POWER SOURCE AND NO-BLINK SELECTOR",
        (65, 53),
        size=1.8,
        bold=True,
    )
    add_index_text(
        schematic,
        "carrier-heading",
        "CM5 CARRIER",
        (30, 128),
        size=1.8,
        bold=True,
    )
    add_index_text(
        schematic,
        "audio-heading",
        "BALANCED AUDIO 8X8",
        (30, 278),
        size=1.8,
        bold=True,
    )

    for name, filename, position, page in SHEETS:
        resolved = (HERE / filename).resolve()
        if not resolved.exists():
            raise FileNotFoundError(resolved)
        sheet_uuid = schematic.add_sheet(
            name=name,
            filename=filename,
            position=position,
            size=(120, 34),
            stroke_width=0.35,
            project_name=PROJECT_NAME,
            page_number=page,
            uuid=stable_uuid(f"sheet:{name}"),
        )
        sheet = next(item for item in schematic._data["sheets"] if item["uuid"] == sheet_uuid)
        sheet["exclude_from_sim"] = True
        sheet["in_bom"] = False
        sheet["on_board"] = False

    schematic.save(SCHEMATIC)


def build_project() -> None:
    source = ROOT / "cad/kicad/CM5-CARRIER/CM5-Carrier.kicad_pro"
    project = json.loads(source.read_text(encoding="utf-8"))
    project["meta"]["filename"] = PROJECT.name
    project["boards"] = []
    project["sheets"] = []
    project["text_variables"] = {
        "DESIGN_STATE": "ELECTRICAL_CAPTURE_COMPLETE",
        "PCB_STATE": "ROUTING_HELD_FOR_PHYSICAL_GATES",
    }
    PROJECT.write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    HERE.mkdir(parents=True, exist_ok=True)
    build_schematic()
    build_project()
    print(SCHEMATIC)
    print(PROJECT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
