#!/usr/bin/env python3
"""Independent netlist, telemetry, and threshold checks for the Radxa selector."""

from pathlib import Path
import csv
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
NETLIST = ROOT / "REVIEW" / "PowerSelector-A0.xml"
ERC = ROOT / "REVIEW" / "PowerSelector-A0-ERC.rpt"
POWER_SWITCH_BOM = ROOT / "POWER_SWITCH_BOM.csv"
PSU_HARNESS_BOM = ROOT.parent.parent.parent / "fabrication" / "harnesses" / "H01-PSU-24V-BOM.csv"


def fail(message):
    print(f"FAIL: {message}")
    raise SystemExit(1)


if not NETLIST.exists():
    fail(f"missing netlist: {NETLIST}")
if not ERC.exists():
    fail(f"missing ERC report: {ERC}")

erc_text = ERC.read_text(errors="replace")
if not re.search(r"ERC messages:\s*0\s+Errors\s+0\s+Warnings\s+0", erc_text):
    fail("ERC report is not 0 errors / 0 warnings")

root = ET.parse(NETLIST).getroot()
components = root.findall("./components/comp")
component_by_ref = {component.get("ref"): component for component in components}
pin_net = {}
pins_by_ref = {}
for net in root.findall("./nets/net"):
    net_name = net.get("name", "").lstrip("/")
    for node in net.findall("node"):
        pin_net[(node.get("ref"), node.get("pin"))] = net_name
        pins_by_ref.setdefault(node.get("ref"), set()).add(node.get("pin"))

expected = {
    # Bottom-mounted RPS-400-24-C low-voltage output harness. One 14 AWG
    # conductor per polarity terminates in a keyed two-circuit Mega-Fit.
    ("J101", "1"): "V24_IN",
    ("J101", "2"): "GND",
    # Panel power-switch harness. A maintained external DPST switch closes
    # pins 1-2 and 3-4; pull-downs make an open/unplugged harness fail OFF.
    ("J204", "1"): "INTVCC",
    ("J204", "2"): "SHDN_MAIN",
    ("J204", "3"): "PRE_INTVCC",
    ("J204", "4"): "SHDN_PRE",
    ("R541", "1"): "SHDN_MAIN",
    ("R541", "2"): "GND",
    ("R542", "1"): "SHDN_PRE",
    ("R542", "2"): "GND",
    # Keyed LEMO harness and reverse-polarity-tolerant front end.
    ("J202", "1"): "DTAP_IN",
    ("J202", "2"): "DTAP_IN",
    ("J202", "3"): "GND",
    ("J202", "4"): "GND",
    ("F202", "1"): "DTAP_IN",
    ("F202", "2"): "DTAP_FUSED",
    ("D202", "1"): "DTAP_FUSED",
    ("D202", "2"): "GND",
    ("C202", "1"): "DTAP_FUSED",
    ("C202", "2"): "GND",
    # LTC4418 backup preselector.
    ("U201", "17"): "DTAP_FUSED",
    ("U201", "2"): "UV_DTAP",
    ("U201", "3"): "OV_DTAP",
    ("U201", "6"): "VALID_DTAP_N",
    ("U201", "16"): "GOLD_FUSED",
    ("U201", "4"): "UV_GOLD",
    ("U201", "5"): "OV_GOLD",
    ("U201", "7"): "VALID_GOLD_N",
    ("U201", "14"): "SRC_DTAP",
    ("U201", "13"): "G1_CTRL",
    ("U201", "12"): "SRC_GOLD",
    ("U201", "11"): "G2_CTRL",
    ("U201", "15"): "BAT_SELECTED",
    ("U201", "18"): "PRE_INTVCC",
    ("U201", "19"): "SHDN_PRE",
    ("U201", "10"): "PRE_INTVCC",
    ("U201", "1"): "TMR_PRE",
    ("U201", "8"): "GND",
    ("U201", "20"): "GND",
    ("U201", "21"): "GND",
    # Fast-turn-off Schottky polarity: pin 1 is cathode, pin 2 is anode.
    ("D511", "1"): "GATE_DTAP",
    ("D511", "2"): "G1_CTRL",
    ("D521", "1"): "GATE_GOLD",
    ("D521", "2"): "G2_CTRL",
    # Main LTC4421 selector.
    ("U101", "3"): "V24_FUSED",
    ("U101", "27"): "BAT_FUSED",
    ("U101", "1"): "SRC_24",
    ("U101", "2"): "GATE_24",
    ("U101", "36"): "V24_SENSE",
    ("U101", "35"): "RAW_OUT",
    ("U101", "29"): "SRC_BAT",
    ("U101", "28"): "GATE_BAT",
    ("U101", "30"): "BAT_SENSE",
    ("U101", "31"): "RAW_OUT",
    ("U101", "18"): "SHDN_MAIN",
    ("U101", "17"): "GND",
    # Delivered-load shunt and high-current carrier output.
    ("R111", "1"): "V24_SENSE",
    ("R111", "2"): "V24_SENSE",
    ("R111", "3"): "RAW_OUT",
    ("R111", "4"): "RAW_OUT",
    ("R211", "1"): "BAT_SENSE",
    ("R211", "2"): "BAT_SENSE",
    ("R211", "3"): "RAW_OUT",
    ("R211", "4"): "RAW_OUT",
    ("R311", "1"): "RAW_OUT",
    ("R311", "2"): "RAW_OUT",
    ("R311", "3"): "RAW_OUT_LOAD",
    ("R311", "4"): "RAW_OUT_LOAD",
    ("J301", "1"): "RAW_OUT_LOAD",
    ("J301", "2"): "RAW_OUT_LOAD",
    ("J301", "3"): "GND",
    ("J301", "4"): "GND",
    # Carrier status connector.
    ("J401", "1"): "GND",
    ("J401", "2"): "CH_24V_N",
    ("J401", "3"): "CH_BAT_N",
    ("J401", "4"): "VALID_24V_N",
    ("J401", "5"): "VALID_BAT_N",
    ("J401", "6"): "BAT_LOW_N",
    ("J401", "7"): "VALID_DTAP_N",
    ("J401", "8"): "VALID_GOLD_N",
    # Digital power telemetry harness. The carrier supplies MON_3V3 and owns
    # the I2C/alert pull-ups.
    ("J402", "1"): "MON_3V3",
    ("J402", "2"): "GND",
    ("J402", "3"): "PWR_MON_SDA",
    ("J402", "4"): "PWR_MON_SCL",
    ("J402", "5"): "PWR_MON_ALERT_N",
    ("J402", "6"): "GND",
}

for ref, address_pins, prefix in (
    ("U601", {"1": "GND", "2": "GND"}, "MON24"),
    ("U602", {"1": "GND", "2": "MON_3V3"}, "MONBAT"),
    ("U603", {"1": "MON_3V3", "2": "GND"}, "MONLOAD"),
):
    for pin, net_name in {
        **address_pins,
        "3": "PWR_MON_ALERT_N",
        "4": "PWR_MON_SDA",
        "5": "PWR_MON_SCL",
        "6": "MON_3V3",
        "7": "GND",
        "8": f"{prefix}_VBUS",
        "9": f"{prefix}_INN",
        "10": f"{prefix}_INP",
    }.items():
        expected[(ref, pin)] = net_name

for ref, pin_1, pin_2 in (
    ("R601", "V24_SENSE", "MON24_INP"),
    ("R602", "RAW_OUT", "MON24_INN"),
    ("R603", "V24_FUSED", "MON24_VBUS"),
    ("R611", "BAT_SENSE", "MONBAT_INP"),
    ("R612", "RAW_OUT", "MONBAT_INN"),
    ("R613", "BAT_FUSED", "MONBAT_VBUS"),
    ("R621", "RAW_OUT", "MONLOAD_INP"),
    ("R622", "RAW_OUT_LOAD", "MONLOAD_INN"),
    ("R623", "RAW_OUT_LOAD", "MONLOAD_VBUS"),
):
    expected[(ref, "1")] = pin_1
    expected[(ref, "2")] = pin_2

for ref, source, drain, gate in (
    ("Q501", "SRC_DTAP", "DTAP_FUSED", "GATE_DTAP"),
    ("Q502", "SRC_DTAP", "BAT_SELECTED", "GATE_DTAP"),
    ("Q503", "SRC_GOLD", "GOLD_FUSED", "GATE_GOLD"),
    ("Q504", "SRC_GOLD", "BAT_SELECTED", "GATE_GOLD"),
):
    for pin in ("1", "2", "3"):
        expected[(ref, pin)] = source
    expected[(ref, "5")] = drain
    expected[(ref, "4")] = gate

for ref, source, drain, gate in (
    ("Q101", "SRC_24", "V24_FUSED", "GATE_24"),
    ("Q102", "SRC_24", "V24_SENSE", "GATE_24"),
    ("Q201", "SRC_BAT", "BAT_FUSED", "GATE_BAT"),
    ("Q202", "SRC_BAT", "BAT_SENSE", "GATE_BAT"),
):
    expected[(ref, "1")] = gate
    for pin in ("2", "3", "4"):
        expected[(ref, pin)] = source
    expected[(ref, "5")] = drain

mismatches = []
for key, wanted in sorted(expected.items()):
    actual = pin_net.get(key)
    if actual != wanted:
        mismatches.append((key, wanted, actual))
if mismatches:
    for key, wanted, actual in mismatches:
        print(f"MISMATCH {key[0]}.{key[1]}: wanted {wanted}, got {actual}")
    fail(f"{len(mismatches)} critical pin/net mismatches")

# Reverse-polarity protection is a controlled architecture, not an ERC side
# effect. Lock the exact controller, P-channel blockers, bidirectional TVS and
# non-polarized input capacitor so an innocent BOM edit cannot defeat it.
required_values = {
    "U601": "INA228AIDGSR",
    "U602": "INA228AIDGSR",
    "U603": "INA228AIDGSR",
    "R111": "1.50mR 1% 1W",
    "R211": "1.50mR 1% 1W",
    "R311": "1.00mR 1% 1W",
    "R301": "176k 0.1%",
    "U201": "LTC4418IUF#PBF",
    "Q501": "SiR5607DP-T1-RE3",
    "Q502": "SiR5607DP-T1-RE3",
    "Q503": "SiR5607DP-T1-RE3",
    "Q504": "SiR5607DP-T1-RE3",
    "D202": "SMBJ18CA",
    "D203": "SMBJ18CA",
    "C202": "10uF 50V X7R",
    "C203": "10uF 50V X7R",
}
for ref, wanted in required_values.items():
    component = component_by_ref.get(ref)
    actual = component.findtext("value") if component is not None else None
    if actual != wanted:
        fail(f"reverse-protection part {ref}: wanted {wanted}, got {actual}")

# The panel switch is an off-board system item, so it is controlled by a
# separate exact-MPN BOM rather than being assigned a misleading PCB footprint.
if not POWER_SWITCH_BOM.exists():
    fail(f"missing power-switch BOM: {POWER_SWITCH_BOM}")
with POWER_SWITCH_BOM.open(newline="") as handle:
    switch_bom = {row["Reference"]: row for row in csv.DictReader(handle)}
required_switch_parts = {
    "SW201": ("E-Switch", "RA812C1121", "1"),
    "T201-T204": ("TE Connectivity", "2-520182-2", "4"),
    "P204": ("Molex", "0430250400", "1"),
    "C204A-C204D": ("Molex", "0430300007", "4"),
}
for ref, (manufacturer, mpn, qty) in required_switch_parts.items():
    row = switch_bom.get(ref)
    if row is None:
        fail(f"power-switch BOM missing {ref}")
    actual = (row.get("Manufacturer"), row.get("MPN"), row.get("Qty"))
    if actual != (manufacturer, mpn, qty):
        fail(f"power-switch BOM {ref}: wanted {(manufacturer, mpn, qty)}, got {actual}")

# The removable PSU harness is a controlled system assembly. Lock its mating
# connector, TPA, contacts, ring terminals and conductor specification here.
if not PSU_HARNESS_BOM.exists():
    fail(f"missing PSU harness BOM: {PSU_HARNESS_BOM}")
with PSU_HARNESS_BOM.open(newline="") as handle:
    psu_harness_bom = {row["Reference"]: row for row in csv.DictReader(handle)}
required_psu_harness_parts = {
    "J101": ("Molex", "76825-0002", "1"),
    "P101": ("Molex", "171692-0202", "1"),
    "TPA101": ("Molex", "105415-0002", "1"),
    "C101A-C101B": ("Molex", "76823-0344", "2"),
    "RT101-RT102": ("TE Connectivity", "320619", "2"),
    "W101-W102": ("Harness supplier", "UL1015-14AWG", "2"),
}
for ref, (manufacturer, mpn, qty) in required_psu_harness_parts.items():
    row = psu_harness_bom.get(ref)
    if row is None:
        fail(f"PSU harness BOM missing {ref}")
    actual = (row.get("Manufacturer"), row.get("MPN"), row.get("Qty"))
    if actual != (manufacturer, mpn, qty):
        fail(f"PSU harness BOM {ref}: wanted {(manufacturer, mpn, qty)}, got {actual}")

# Confirm every BOM item has a footprint and every connected schematic pin
# exists in that footprint. This catches pad-number mismatches that ERC cannot.
refs = [component.get("ref") for component in components]
if len(refs) != len(set(refs)):
    fail("duplicate component references in netlist")

footprint_by_ref = {}
for component in components:
    ref = component.get("ref")
    footprint = (component.findtext("footprint") or "").strip()
    libsource = component.find("libsource")
    library = libsource.get("lib") if libsource is not None else ""
    if not footprint and not (ref.startswith("#") or library == "power"):
        fail(f"{ref} has no assigned footprint")
    footprint_by_ref[ref] = footprint

system_footprints = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")
for ref, used_pins in sorted(pins_by_ref.items()):
    footprint = footprint_by_ref.get(ref, "")
    if not footprint:
        continue
    library, name = footprint.split(":", 1)
    if library == "PowerSelector":
        footprint_path = ROOT / "PowerSelector.pretty" / f"{name}.kicad_mod"
    else:
        footprint_path = system_footprints / f"{library}.pretty" / f"{name}.kicad_mod"
    if not footprint_path.exists():
        fail(f"{ref} footprint file not found: {footprint_path}")
    pad_numbers = set(re.findall(r'\(pad\s+"([^"]*)"', footprint_path.read_text(errors="ignore"))) - {""}
    missing_pads = used_pins - pad_numbers
    if missing_pads:
        fail(f"{ref} pins absent from {footprint}: {sorted(missing_pads)}")


def thresholds(r_top, r_mid, r_bottom):
    total = r_top + r_mid + r_bottom
    uv_falling = total / (r_bottom + r_mid)
    uv_rising = 1.03 * uv_falling
    ov_rising = total / r_bottom
    return uv_rising, uv_falling, ov_rising


dtap = thresholds(919_000, 26_100, 55_600)
gold = thresholds(909_000, 31_600, 56_200)
targets = (
    ("D-Tap UV rising", dtap[0], 12.60, 12.64),
    ("D-Tap UV falling", dtap[1], 12.23, 12.27),
    ("D-Tap OV rising", dtap[2], 17.98, 18.02),
    ("Gold UV rising", gold[0], 11.67, 11.72),
    ("Gold UV falling", gold[1], 11.33, 11.38),
    ("Gold OV rising", gold[2], 17.71, 17.76),
)
for label, actual, low, high in targets:
    if not low <= actual <= high:
        fail(f"{label} {actual:.3f} V is outside {low:.3f}..{high:.3f} V")

# LTC4418 UV/OV pins are clamped near ground during a reversed input. The
# datasheet absolute maximum allows 3 mA negative input current; these high
# value divider tops limit a -16.8 V cable miswire to about 18 uA.
reverse_dtap_uA = (16.8 - 0.3) / 919_000 * 1_000_000
reverse_gold_uA = (16.8 - 0.3) / 909_000 * 1_000_000
for label, actual in (("D-Tap", reverse_dtap_uA), ("Gold", reverse_gold_uA)):
    if actual > 25.0:
        fail(f"{label} reverse UV/OV clamp current {actual:.2f} uA exceeds 25 uA design limit")

# INA228 is configured for its +/-40.96 mV shunt range. These checks lock the
# electrical starting point while leaving final tolerance/thermal sign-off as
# an explicit release task.
source_shunt_ohms = 0.0015
load_shunt_ohms = 0.0010
source_full_scale_a = 0.04096 / source_shunt_ohms
load_full_scale_a = 0.04096 / load_shunt_ohms
nominal_ltc4421_limit_a = 0.025 / source_shunt_ohms
source_shunt_w_at_15a = 15.0 ** 2 * source_shunt_ohms
if source_full_scale_a < 25.0 or load_full_scale_a < 35.0:
    fail("INA228 telemetry full-scale current is too low")
if not 16.5 <= nominal_ltc4421_limit_a <= 16.9:
    fail(f"nominal LTC4421 current limit {nominal_ltc4421_limit_a:.3f} A is unexpected")
if source_shunt_w_at_15a > 0.40:
    fail(f"source shunt dissipation at 15 A is {source_shunt_w_at_15a:.3f} W")

print(f"PASS: ERC 0 errors / 0 warnings")
print(f"PASS: {len(expected)} critical pin/net checks")
print(f"PASS: reverse-polarity architecture and parts locked")
print(f"PASS: exact power-switch and harness BOM locked")
print(f"PASS: exact bottom-PSU 24 V harness BOM locked")
print(f"PASS: {len(components)} unique BOM components; footprint pad maps agree")
print(f"PASS: D-Tap thresholds {dtap[0]:.3f} / {dtap[1]:.3f} / {dtap[2]:.3f} V")
print(f"PASS: Gold thresholds {gold[0]:.3f} / {gold[1]:.3f} / {gold[2]:.3f} V")
print(f"PASS: -16.8 V UV/OV clamp currents {reverse_dtap_uA:.2f} / {reverse_gold_uA:.2f} uA (<25 uA design, <<3 mA abs max)")
print(f"PASS: INA228 source/load ranges {source_full_scale_a:.3f} A / {load_full_scale_a:.2f} A")
print(f"PASS: nominal LTC4421 limit {nominal_ltc4421_limit_a:.3f} A; source shunt {source_shunt_w_at_15a:.4f} W at 15 A")
