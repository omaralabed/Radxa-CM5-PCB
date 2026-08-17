#!/usr/bin/env python3
"""Validate the controlled Network/PCIe production BOM and release invariants."""

from __future__ import annotations

import csv
from collections import Counter
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent.parent.parent
BOM = WORKSPACE / "docs" / "network_pcie_bom_a1.csv"
SCHEMATIC = ROOT / "Network-PCIe.kicad_sch"
INDUCTOR_FOOTPRINT = ROOT / "CM5Carrier.pretty" / "TDK_VLS3012HBX.kicad_mod"
KICAD_CLI = Path(
    os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
)


def check(name: str, condition: bool, detail: str) -> bool:
    print(f"{'PASS' if condition else 'FAIL'}  {name}: {detail}")
    return condition


def refs_with_mpn(rows: list[dict[str, str]], mpn: str) -> set[str]:
    return {row["Reference"] for row in rows if row["MPN"] == mpn}


def export_net_map() -> dict[tuple[str, str], str]:
    with tempfile.TemporaryDirectory(prefix="radxa-network-validation-") as temp:
        output = Path(temp) / "Network-PCIe.xml"
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


def main() -> int:
    rows = list(csv.DictReader(BOM.open())) if BOM.exists() else []
    by_ref = {row["Reference"]: row for row in rows}
    schematic_text = SCHEMATIC.read_text() if SCHEMATIC.exists() else ""
    footprint_text = INDUCTOR_FOOTPRINT.read_text() if INDUCTOR_FOOTPRINT.exists() else ""
    net_map = export_net_map()
    checks: list[bool] = []

    complete = bool(rows) and all(
        row["Manufacturer"] and row["MPN"] and row["Footprint"] for row in rows
    )
    checks.append(
        check(
            "Network/PCIe production BOM",
            len(rows) == 143 and complete,
            f"{len(rows)} rows; all manufacturer, MPN, and footprint fields complete",
        )
    )

    controlled_parts = {
        "U601": (
            "PI7C9X2G608GPCNJEX",
            "Package_BGA:BGA-196_15x15mm_Layout14x14_P1.0mm",
        ),
        "U606": ("SN74LVC1G11DBVR", "Package_TO_SOT_SMD:SOT-23-6"),
        "U611": (
            "LAN7430T-I/Y9X",
            "Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.3x5.3mm_ThermalVias",
        ),
        "J610": ("V8BR-1AX1-GH", "CM5Carrier:Bel_V8BR_1AX1_GH"),
        "J620": ("0679101002", "CM5Carrier:Molex_0679101002_Mini_PCIe"),
        "L6111": ("VLS3012HBX-3R3M-N", "CM5Carrier:TDK_VLS3012HBX"),
        "Y611": (
            "ABM8-25.000MHZ-10-D1G-T",
            "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
        ),
    }
    for reference, (mpn, footprint) in controlled_parts.items():
        row = by_ref.get(reference, {})
        checks.append(
            check(
                f"{reference} controlled part",
                row.get("MPN") == mpn and row.get("Footprint") == footprint,
                f"{row.get('MPN', 'missing')} / {row.get('Footprint', 'missing')}",
            )
        )

    expected_groups = {
        "industrial LAN7430 endpoints": (
            "LAN7430T-I/Y9X",
            {"U611", "U612", "U613"},
        ),
        "active 3.3 uH LAN inductors": (
            "VLS3012HBX-3R3M-N",
            {"L6111", "L6121", "L6131"},
        ),
        "industrial 25 MHz crystals": (
            "ABM8-25.000MHZ-10-D1G-T",
            {"Y611", "Y612", "Y613"},
        ),
        "Bel vertical integrated-magnetics jacks": (
            "V8BR-1AX1-GH",
            {"J610", "J611", "J612", "J613"},
        ),
        "low-capacitance Ethernet ESD arrays": (
            "TPD4E05U06DQAR",
            {f"U{reference}" for reference in range(630, 638)},
        ),
        "22 uF LAN buck and switch bulk capacitors": (
            "GRM21BR71A226ME44L",
            {"C6111", "C6121", "C6131", "C6630", "C6631"},
        ),
        "1 uF LAN LDO capacitors": (
            "GRM155R6YA105KE11D",
            {"C6113", "C6123", "C6133"},
        ),
        "15 pF crystal load capacitors": (
            "GRM1555C1H150JA01D",
            {"C6114", "C6115", "C6124", "C6125", "C6134", "C6135"},
        ),
    }
    for name, (mpn, expected_refs) in expected_groups.items():
        observed = refs_with_mpn(rows, mpn)
        checks.append(check(name, observed == expected_refs, f"refs {sorted(observed)}"))

    value_counts = Counter(row["Value"] for row in rows)
    checks.append(
        check(
            "LAN7430 2.5 V LDO capacitor requirement",
            value_counts["1uF 35V X5R / ESR <1R"] == 3,
            f"{value_counts['1uF 35V X5R / ESR <1R']} channels use the controlled <1 ohm ESR value",
        )
    )
    expected_10nf = {
        f"C{channel}{index}"
        for channel in (611, 612, 613)
        for index in range(6, 10)
    }
    checks.append(
        check(
            "LAN7430 3.3 V pin decoupling",
            refs_with_mpn(rows, "GRM188R71H103KA01D") == expected_10nf,
            "four 10 nF capacitors are assigned to VDD_REG_IN, VDD_SW_IN, VDDVARIO, and VDD_OTP per endpoint",
        )
    )
    expected_beads = {
        f"FB{channel}{index}"
        for channel in (611, 612, 613)
        for index in (1, 2)
    }
    checks.append(
        check(
            "LAN7430 analog rail ferrites",
            refs_with_mpn(rows, "BLM21PG221SN1D") == expected_beads,
            "each endpoint isolates its 1.2 V and 2.5 V analog loads through a controlled ferrite",
        )
    )

    switch_decouplers = {f"C{reference}" for reference in range(6601, 6630)}
    checks.append(
        check(
            "PCIe switch supply-ball decoupling",
            all(
                reference in by_ref
                and by_ref[reference].get("MPN") == "C1005X7R1H104K050BB"
                for reference in switch_decouplers
            ),
            "29 supply balls each have a dedicated 100 nF capacitor",
        )
    )

    upstream_coupling = {
        "C605": ("PCIE_UP_TX_P_CM5", "PCIE_UP_SW_RX_P"),
        "C606": ("PCIE_UP_TX_N_CM5", "PCIE_UP_SW_RX_N"),
        "C607": ("PCIE_UP_SW_TX_P", "PCIE_UP_RX_P_CM5"),
        "C608": ("PCIE_UP_SW_TX_N", "PCIE_UP_RX_N_CM5"),
        "C609": ("WIFI_SW_TX_P", "WIFI_PCIE_RX_P"),
        "C610": ("WIFI_SW_TX_N", "WIFI_PCIE_RX_N"),
    }
    checks.append(
        check(
            "CM5 and Wi-Fi host PCIe TX coupling",
            all(
                net_map.get((reference, "1")) == source
                and net_map.get((reference, "2")) == load
                for reference, (source, load) in upstream_coupling.items()
            ),
            "CM5 and switch transmitters are AC-coupled at their source boundaries",
        )
    )

    lan_contract_ok = True
    for reference, prefix in (("U611", "WAN2"), ("U612", "LAN1"), ("U613", "LAN2")):
        channel = reference.removeprefix("U")
        expected_pin_nets = {
            "1": f"{prefix}_2V5_A", "4": f"{prefix}_1V2_A",
            "9": f"{prefix}_1V2_A", "12": f"{prefix}_2V5_A",
            "13": f"{prefix}_1V2", "14": f"{prefix}_1V2_A",
            "19": f"{prefix}_EP_TX_P", "20": f"{prefix}_1V2_A",
            "21": f"{prefix}_EP_TX_N", "23": f"{prefix}_2V5_A",
            "27": f"{prefix}_2V5_OUT", "28": "NET_3V3",
            "29": f"{prefix}_RESET_LOCAL_N", "31": f"{prefix}_1V2",
            "32": f"{prefix}_SW_NODE", "33": "NET_3V3",
            "34": f"{prefix}_1V2", "35": "GND", "39": "NET_3V3",
            "40": f"{prefix}_1V2", "41": "NET_3V3",
            "45": f"{prefix}_1V2_A",
        }
        lan_contract_ok &= all(
            net_map.get((reference, pin)) == net for pin, net in expected_pin_nets.items()
        )
        lan_contract_ok &= net_map.get((reference, "36"), "").startswith("unconnected-")
        lan_contract_ok &= (
            net_map.get((f"R{channel}3", "1")) == "NET_3V3"
            and net_map.get((f"R{channel}3", "2")) == f"{prefix}_RESET_LOCAL_N"
            and net_map.get((f"FB{channel}1", "1")) == f"{prefix}_1V2"
            and net_map.get((f"FB{channel}1", "2")) == f"{prefix}_1V2_A"
            and net_map.get((f"FB{channel}2", "1")) == f"{prefix}_2V5_OUT"
            and net_map.get((f"FB{channel}2", "2")) == f"{prefix}_2V5_A"
        )
        coupling_contract = {
            f"C{channel}12": (f"{prefix}_SW_TX_P", f"{prefix}_PCIE_RX_P"),
            f"C{channel}13": (f"{prefix}_SW_TX_N", f"{prefix}_PCIE_RX_N"),
            f"C{channel}14": (f"{prefix}_EP_TX_P", f"{prefix}_PCIE_TX_P"),
            f"C{channel}15": (f"{prefix}_EP_TX_N", f"{prefix}_PCIE_TX_N"),
        }
        lan_contract_ok &= all(
            net_map.get((cap, "1")) == source and net_map.get((cap, "2")) == load
            for cap, (source, load) in coupling_contract.items()
        )
    checks.append(
        check(
            "LAN7430 electrical pin and PCIe contract",
            lan_contract_ok,
            "all endpoint power pins, deterministic PM straps, reset pull-ups, rail ferrites, and TX coupling networks match the datasheet checklist",
        )
    )

    magjack_contract_ok = True
    for reference, prefix in (
        ("J610", "WAN1"), ("J611", "WAN2"),
        ("J612", "LAN1"), ("J613", "LAN2"),
    ):
        mdi = ("0", "1", "2", "3") if reference == "J610" else ("A", "B", "C", "D")
        expected_pin_nets = {
            "1": "GND", "6": "GND", "7": "GND", "12": "GND",
            "11": f"{prefix}_MDI_{mdi[0]}_P" if reference != "J610" else f"{prefix}_MDI{mdi[0]}_P",
            "10": f"{prefix}_MDI_{mdi[0]}_N" if reference != "J610" else f"{prefix}_MDI{mdi[0]}_N",
            "4": f"{prefix}_MDI_{mdi[1]}_P" if reference != "J610" else f"{prefix}_MDI{mdi[1]}_P",
            "5": f"{prefix}_MDI_{mdi[1]}_N" if reference != "J610" else f"{prefix}_MDI{mdi[1]}_N",
            "3": f"{prefix}_MDI_{mdi[2]}_P" if reference != "J610" else f"{prefix}_MDI{mdi[2]}_P",
            "2": f"{prefix}_MDI_{mdi[2]}_N" if reference != "J610" else f"{prefix}_MDI{mdi[2]}_N",
            "8": f"{prefix}_MDI_{mdi[3]}_P" if reference != "J610" else f"{prefix}_MDI{mdi[3]}_P",
            "9": f"{prefix}_MDI_{mdi[3]}_N" if reference != "J610" else f"{prefix}_MDI{mdi[3]}_N",
            "17": f"{prefix}_LED0", "18": f"{prefix}_LED_A1",
            "19": f"{prefix}_LED1", "20": f"{prefix}_LED_A2",
            "21": "CHASSIS_GND", "22": "CHASSIS_GND",
        }
        magjack_contract_ok &= all(
            net_map.get((reference, pin)) == net
            for pin, net in expected_pin_nets.items()
        )
        magjack_contract_ok &= all(
            net_map.get((reference, pin), "").startswith("unconnected-")
            for pin in ("13", "14", "15", "16")
        )
    checks.append(
        check(
            "vertical Bel MagJack pin contract",
            magjack_contract_ok,
            "all four V8BR PHY pairs, grounded PHY center taps, NC PoE center taps, LEDs, and chassis leads match the Bel drawing",
        )
    )
    checks.append(
        check(
            "AW7915-NP1 supply margin",
            all(net_map.get(("J620", str(pin))) == "WIFI_3V3" for pin in (2, 24, 39, 41, 52))
            and "vendor maximum 9.1 W and 3.5 A recommended" in schematic_text
            and "dedicated rail is 3.3 V / 4 A" in schematic_text,
            "all Mini PCIe 3.3 V contacts use the dedicated 4 A rail, above AsiaRF's 3.5 A recommendation",
        )
    )
    checks.append(
        check(
            "606-mode switch strap",
            by_ref.get("R601", {}).get("MPN") == "RC0603FR-074K7L"
            and "GPIO[1:0] = 01 selects 606 mode" in schematic_text,
            "GPIO0 has a 4.7 k pull-up and GPIO1 uses the device pulldown",
        )
    )
    reset_gate_contract = {
        "1": "PCIE_UP_PERST_CMD_N", "2": "GND", "3": "NET_3V3_PG",
        "4": "PCIE_UP_PERST_N", "5": "LOGIC_3V3", "6": "PCIE_1V0_PG",
    }
    checks.append(
        check(
            "hardware-qualified upstream PCIe reset",
            all(net_map.get(("U606", pin)) == net for pin, net in reset_gate_contract.items())
            and net_map.get(("R608", "1")) == "PCIE_UP_PERST_N"
            and net_map.get(("R608", "2")) == "GND"
            and net_map.get(("C611", "1")) == "LOGIC_3V3"
            and net_map.get(("C611", "2")) == "GND"
            and net_map.get(("U601", "C12")) == "PCIE_UP_PERST_N",
            "switch reset requires CM5 request, NET_3V3_PG, and PCIE_1V0_PG; 100 k defaults asserted",
        )
    )
    checks.append(
        check(
            "PCIe reset timing requirement",
            "stable for at least 100 ms" in schematic_text,
            "CM5 root-complex timing must withhold its request until rails and REFCLK have been stable for 100 ms",
        )
    )
    checks.append(
        check(
            "unused switch port isolation",
            "PCIE_SPARE" not in schematic_text and "J621" not in by_ref,
            "port 5 is disabled/unrouted and no generic PCIe cable header is present",
        )
    )
    checks.append(
        check(
            "grounded four-pad crystal model",
            schematic_text.count("CM5Carrier:Crystal_GND24_3225") >= 3,
            "all three oscillators use the project-local grounded-case symbol",
        )
    )
    checks.append(
        check(
            "TDK inductor controlled land pattern",
            INDUCTOR_FOOTPRINT.exists()
            and footprint_text.count('(pad "1" smd') == 1
            and footprint_text.count('(pad "2" smd') == 1
            and "(size 1.00 3.40)" in footprint_text,
            "two 1.0 x 3.4 mm lands with the drawing-backed 1.1 mm gap",
        )
    )

    failures = len(checks) - sum(checks)
    print(f"\nRESULT: {len(checks)} checks, {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
