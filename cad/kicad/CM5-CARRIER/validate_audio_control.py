#!/usr/bin/env python3
"""Validate the locked TDM transport and translated ES8316 headset capture."""

from __future__ import annotations

import csv
import os
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent.parent.parent
BOM = WORKSPACE / "docs" / "audio_control_bom_a1.csv"
SCHEMATIC = ROOT / "Audio-Control.kicad_sch"
JACK_FOOTPRINT = (
    ROOT / "CM5Carrier.pretty" /
    "Kycon_STX-353K7A-6N-KTTR_PRELIMINARY.kicad_mod"
)
KICAD_CLI = Path(
    os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
)


def check(name: str, condition: bool, detail: str) -> bool:
    print(f"{'PASS' if condition else 'FAIL'}  {name}: {detail}")
    return condition


def export_net_map() -> dict[tuple[str, str], str]:
    with tempfile.TemporaryDirectory(prefix="radxa-audio-control-validation-") as temp:
        output = Path(temp) / "Audio-Control.xml"
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


def pins_match(
    net_map: dict[tuple[str, str], str],
    reference: str,
    expected: dict[str, str],
) -> bool:
    return all(net_map.get((reference, pin)) == net for pin, net in expected.items())


def main() -> int:
    rows = list(csv.DictReader(BOM.open())) if BOM.exists() else []
    by_ref = {row["Reference"]: row for row in rows}
    net_map = export_net_map()
    schematic_text = SCHEMATIC.read_text() if SCHEMATIC.exists() else ""
    checks: list[bool] = []

    complete = bool(rows) and all(
        row["Manufacturer"] and row["MPN"] and row["Footprint"] for row in rows
    )
    checks.append(
        check(
            "audio-control controlled BOM",
            len(rows) == 57 and complete and "U900" not in by_ref,
            f"{len(rows)} board parts; off-sheet U900 excluded; all production fields complete",
        )
    )

    expected_parts = {
        "J901": (
            "87832-6423",
            "Connector_Molex_Milligrid:Molex_8783230xx_2x15_P2.0mm_Header_Vertical_Polarized_MountingPegs",
        ),
        "J910": (
            "STX-353K7A-6N-KTTR",
            "CM5Carrier:Kycon_STX-353K7A-6N-KTTR_PRELIMINARY",
        ),
        "U903": ("PCA9517ADP,118", "Package_SO:TSSOP-8_3x3mm_P0.65mm"),
        "U904": ("PCA9306DP,118", "Package_SO:TSSOP-8_3x3mm_P0.65mm"),
        "U905": ("SN74AVC4T245PWR", "Package_SO:TSSOP-16_4.4x5mm_P0.65mm"),
        "U906": ("SN74LVC1T45DCKR", "Package_TO_SOT_SMD:SOT-363_SC-70-6"),
        "U910": ("LP5907MFX-3.3/NOPB", "Package_TO_SOT_SMD:SOT-23-5"),
        "U911": ("LP5907MFX-1.8/NOPB", "Package_TO_SOT_SMD:SOT-23-5"),
        "U912": (
            "ES8316",
            "Package_DFN_QFN:QFN-32-1EP_4x4mm_P0.4mm_EP2.9x2.9mm_ThermalVias",
        ),
        "U913": (
            "TPA6132A2RTER",
            "Package_DFN_QFN:WQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm_ThermalVias",
        ),
        "U914": ("TPD4E05U06DQAR", "Package_SON:USON-10_2.5x1.0mm_P0.5mm"),
    }
    for reference, (mpn, footprint) in expected_parts.items():
        row = by_ref.get(reference, {})
        checks.append(
            check(
                f"{reference} controlled part",
                row.get("MPN") == mpn and row.get("Footprint") == footprint,
                f"{row.get('MPN', 'missing')} / {row.get('Footprint', 'missing')}",
            )
        )

    checks.append(
        check(
            "program-audio I2C isolation",
            pins_match(
                net_map,
                "U903",
                {
                    "1": "LOGIC_3V3", "2": "SYS_I2C7_SCL", "3": "SYS_I2C7_SDA",
                    "4": "GND", "5": "AUDIO_ENABLE", "6": "AUD_I2C_SDA",
                    "7": "AUD_I2C_SCL", "8": "LOGIC_3V3",
                },
            ),
            "PCA9517A isolates the 3.3 V off-board branch without a false 1.8 V domain",
        )
    )

    checks.append(
        check(
            "headset I2C translation",
            pins_match(
                net_map,
                "U904",
                {
                    "1": "HEADSET_AGND", "2": "HEADSET_1V8",
                    "3": "HS_CODEC_I2C_SCL", "4": "HS_CODEC_I2C_SDA",
                    "5": "HS_I2C_SDA", "6": "HS_I2C_SCL",
                    "7": "HS_I2C_BIAS", "8": "HS_I2C_BIAS",
                },
            )
            and pins_match(
                net_map, "R909", {"1": "LOGIC_3V3", "2": "HS_I2C_BIAS"}
            )
            and by_ref.get("R909", {}).get("MPN") == "RC0603FR-07200KL",
            "PCA9306 VREF2/EN bias follows the NXP 200k always-enabled circuit",
        )
    )

    checks.append(
        check(
            "four-channel I2S translation",
            pins_match(
                net_map,
                "U905",
                {
                    "1": "LOGIC_3V3", "2": "LOGIC_3V3", "3": "LOGIC_3V3",
                    "4": "HS_MCLK", "5": "HS_BCLK", "6": "HS_LRCK",
                    "7": "HS_SDOUT_TO_CODEC", "8": "HEADSET_AGND",
                    "9": "HEADSET_AGND", "10": "HS_CODEC_SDOUT",
                    "11": "HS_CODEC_LRCK", "12": "HS_CODEC_BCLK",
                    "13": "HS_CODEC_MCLK", "14": "HEADSET_AGND",
                    "15": "HEADSET_AGND", "16": "HEADSET_1V8",
                },
            ),
            "MCLK, BCLK, LRCK and playback data translate 3.3 V A-side to 1.8 V B-side",
        )
    )
    checks.append(
        check(
            "capture-data translation",
            pins_match(
                net_map,
                "U906",
                {
                    "1": "LOGIC_3V3", "2": "HEADSET_AGND",
                    "3": "HS_SDIN_FROM_CODEC", "4": "HS_CODEC_SDIN",
                    "5": "HEADSET_AGND", "6": "HEADSET_1V8",
                },
            ),
            "DIR low selects ES8316 B-to-CM5 A flow for capture data",
        )
    )

    checks.append(
        check(
            "ES8316 translated digital contract",
            pins_match(
                net_map,
                "U912",
                {
                    "1": "HS_CODEC_I2C_SCL", "2": "HS_CODEC_MCLK",
                    "5": "HEADSET_AGND", "6": "HS_CODEC_BCLK",
                    "7": "HS_CODEC_SDOUT", "8": "HS_CODEC_LRCK",
                    "9": "HS_CODEC_SDIN", "31": "ES8316_CE",
                    "32": "HS_CODEC_I2C_SDA", "33": "HEADSET_AGND",
                },
            )
            and pins_match(
                net_map, "R914", {"1": "HEADSET_1V8", "2": "ES8316_CE"}
            ),
            "codec-enable is pulled high to 1.8 V and no CM5 3.3 V net reaches the codec directly",
        )
    )

    checks.append(
        check(
            "TPA6132A2 0 dB and supply straps",
            pins_match(
                net_map,
                "U913",
                {
                    "2": "HEADSET_AGND", "3": "HEADSET_AGND",
                    "6": "HEADSET_3V3", "7": "HEADSET_AGND",
                    "8": "HPAMP_HPVSS", "10": "HEADSET_AGND",
                    "12": "HEADSET_3V3", "14": "HEADSET_3V3",
                    "15": "HEADSET_AGND", "17": "HEADSET_AGND",
                },
            )
            and "G0=1 and G1=0 select 0 dB gain" in schematic_text,
            "G0 high/G1 low selects 0 dB; HPVDD and VDD use the clean 3.3 V rail",
        )
    )

    checks.append(
        check(
            "Kycon CTIA contact contract",
            pins_match(
                net_map,
                "J910",
                {
                    "1": "HS_MIC_JACK", "2": "HEADSET_AGND",
                    "3": "HEADSET_HP_R", "4": "HEADSET_HP_L",
                    "5": "HEADSET_AGND", "6": "HS_JACK_DET_N",
                },
            )
            and pins_match(
                net_map, "R911", {"1": "LOGIC_3V3", "2": "HS_JACK_DET_N"}
            ),
            "tip L, ring1 R, ring2 ground, sleeve mic; isolated switch is active-low candidate",
        )
    )

    checks.append(
        check(
            "single headset analog-ground bond",
            pins_match(net_map, "R900", {"1": "GND", "2": "HEADSET_AGND"})
            and by_ref.get("R900", {}).get("MPN") == "RC0603JR-070RL",
            "one explicit 0 ohm bond owns the GND-to-HEADSET_AGND connection",
        )
    )

    codec_decoupling = {"C926", "C927", "C928", "C929"}
    checks.append(
        check(
            "codec local high-frequency decoupling",
            all(
                by_ref.get(reference, {}).get("MPN") == "C1005X7R1H104K050BB"
                for reference in codec_decoupling
            )
            and all(
                net_map.get((reference, "2")) == "HEADSET_AGND"
                for reference in codec_decoupling
            ),
            "three 1.8 V and one 3.3 V 100 nF capacitors return locally to HEADSET_AGND",
        )
    )

    footprint_text = JACK_FOOTPRINT.read_text() if JACK_FOOTPRINT.exists() else ""
    pad_pattern = re.compile(
        r'\(pad "(?P<pin>[1-6])" thru_hole (?:circle|roundrect)\s+'
        r'\(at (?P<x>-?\d+(?:\.\d+)?) (?P<y>-?\d+(?:\.\d+)?)\) '
        r'\(size 1\.80 1\.80\) \(drill 1\.00\)',
        re.MULTILINE,
    )
    observed = {
        int(match.group("pin")): (float(match.group("x")), float(match.group("y")))
        for match in pad_pattern.finditer(footprint_text)
    }
    expected_pads = {
        1: (0.0, 0.0), 2: (-1.725, -5.1), 3: (1.725, -5.1),
        4: (3.07, 0.0), 5: (-1.3, 0.0), 6: (-3.35, 0.0),
    }
    checks.append(
        check(
            "Kycon coupon-gated footprint geometry",
            observed == expected_pads
            and "PRELIMINARY - COUPON REQUIRED" in footprint_text,
            "six drawing-center pads are stable; sample and plated-hole coupon remain mandatory",
        )
    )

    failures = len(checks) - sum(checks)
    print(f"\nRESULT: {len(checks)} checks, {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
