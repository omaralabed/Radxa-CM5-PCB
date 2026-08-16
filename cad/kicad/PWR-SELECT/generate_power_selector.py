#!/usr/bin/env python3
"""Generate the Radxa CM5 ProComm seamless selector and power telemetry."""

from pathlib import Path
import sys
import uuid as _uuid


_uuid_counter = 0


def _deterministic_uuid4() -> _uuid.UUID:
    """Return stable KiCad UUIDs for reproducible generated schematics."""
    global _uuid_counter
    _uuid_counter += 1
    return _uuid.uuid5(
        _uuid.NAMESPACE_URL,
        f"radxa-cm5-procomm:power-selector:{_uuid_counter}",
    )


_uuid.uuid4 = _deterministic_uuid4

sys.path.insert(0, "/tmp/radxa-cm5-kicad-deps")
from kicad_sch_api import create_schematic, get_symbol_cache


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "PowerSelector.kicad_sch"

cache = get_symbol_cache()
cache.add_library_path(ROOT / "PowerSelector.kicad_sym")

sch = create_schematic("PowerSelector")
sch.set_paper_size("A2")
sch.set_title_block(
    title="Radxa CM5 ProComm 24 V / Battery Seamless Power Selector",
    date="2026-08-16",
    rev="A1",
    company="ProComm",
    comments={
        1: "Fixed priority: internal PSU 24 V, then D-Tap, then Gold Mount dock",
        2: "RAW_OUT_LOAD feeds the protected CM5-CARRIER regulator input",
        3: "Battery inputs use LTC4418 plus back-to-back P-MOS reverse-polarity blocking",
        4: "INA228 telemetry reports primary, selected backup, and delivered load",
    },
)


def add(lib, ref, value, xy, footprint="", mpn="", manufacturer="", datasheet="", rotation=0):
    c = sch.components.add(lib, ref, value, position=xy, footprint=footprint or None, rotation=rotation)
    if mpn:
        c.add_property("MPN", mpn, hidden=True)
    if manufacturer:
        c.add_property("Manufacturer", manufacturer, hidden=True)
    if datasheet:
        c.set_property("Datasheet", datasheet)
    if lib.startswith("PowerSelector:"):
        c.add_property("Reference", ref, hidden=True)
        c.add_property("Value", value, hidden=True)
    return c


def pin_xy(c, pin):
    p = c.get_pin_position(str(pin))
    if p is None:
        raise RuntimeError(f"{c.reference} has no pin {pin}")
    # kicad-sch-api exposes library-pin Y in Cartesian coordinates while the
    # saved schematic uses KiCad's downward-positive page coordinates.
    # Reflect about the symbol anchor so labels and no-connect flags land on
    # the actual saved pin endpoints (including rotated symbols).
    return (p.x, 2.0 * c.position.y - p.y)


def net(c, pin, name, justify="left", rotation=0):
    sch.labels.add(name, pin_xy(c, pin), rotation=rotation, size=1.0, justify_h=justify)


def stub_net(c, pin, name, dx=0.0, dy=0.0, justify="left", rotation=0):
    """Move a net label away from a dense symbol using an orthogonal stub."""
    p = pin_xy(c, pin)
    end = (p[0] + dx, p[1] + dy)
    sch.wires.add(start=p, end=end)
    sch.labels.add(name, end, rotation=rotation, size=1.0, justify_h=justify)


def dogleg_net(c, pin, name, dx, dy, justify="left", size=0.8):
    """Fan a dense pin outward with two orthogonal segments."""
    start = pin_xy(c, pin)
    corner = (start[0] + dx, start[1])
    end = (corner[0], corner[1] + dy)
    sch.wires.add(start=start, end=corner)
    sch.wires.add(start=corner, end=end)
    sch.labels.add(name, end, size=size, justify_h=justify)


def nc(c, pin):
    sch.no_connects.add(pin_xy(c, pin))


def two_pin(c, n1, n2, p1="1", p2="2"):
    net(c, p1, n1, "right")
    net(c, p2, n2, "left")


def title(text, xy, size=2.0):
    x, y = xy
    sch.texts.add(text, (x + 25 if x < 50 else x, y), size=size, bold=True)


def note(text, xy, size=1.1):
    x, y = xy
    sch.texts.add(text, (x + 25 if x < 50 else x, y), size=size)


def tie_pins(c, pins, name, stub_dy, rotation=0):
    """Wire adjacent package pins to one logical node without a four-way junction."""
    pts = [pin_xy(c, p) for p in pins]
    for a, b in zip(pts, pts[1:]):
        sch.wires.add(start=a, end=b)
    # Branch the label from an end pin.  Branching from the middle pin creates
    # pin + left wire + right wire + stub, which KiCad correctly reports as a
    # four-item junction even though the node is electrically continuous.
    edge = pts[0]
    end = (edge[0], edge[1] + stub_dy)
    sch.wires.add(start=edge, end=end)
    sch.labels.add(name, end, rotation=rotation, size=1.0, justify_h="left")


def tie_right_pins(c, pins, name, stub_dx=5.08):
    """Tie adjacent right-side pins and place one uncluttered net label."""
    pts = [pin_xy(c, p) for p in pins]
    for a, b in zip(pts, pts[1:]):
        sch.wires.add(start=a, end=b)
    # Start the label stub on a real pin endpoint so KiCad cannot interpret
    # it as a free midpoint touching a separate vertical segment.
    edge = pts[0]
    end = (edge[0] + stub_dx, edge[1])
    sch.wires.add(start=edge, end=end)
    sch.labels.add(name, end, size=1.0, justify_h="left")


def kelvin_shunt(c, left_net, right_net):
    """Connect current and Kelvin pads to the same schematic nodes."""
    p1, p2, p3, p4 = (pin_xy(c, p) for p in (1, 2, 3, 4))
    corner_l = (p1[0], p2[1])
    corner_r = (p4[0], p3[1])
    sch.wires.add(start=p1, end=corner_l)
    sch.wires.add(start=corner_l, end=p2)
    sch.wires.add(start=p4, end=corner_r)
    sch.wires.add(start=corner_r, end=p3)
    sch.labels.add(left_net, p1, size=1.0, justify_h="right")
    sch.labels.add(right_net, p4, size=1.0, justify_h="left")


MF_2X2 = "Connector_Molex:Molex_Micro-Fit_3.0_43045-0412_2x02_P3.00mm_Vertical"
MEGAFIT_2_RA = "Connector_Molex:Molex_Mega-Fit_76825-0002_2x01_P5.70mm_Horizontal"
PICO_6 = "Connector_Molex:Molex_PicoBlade_53047-0610_1x06_P1.25mm_Vertical"
PICO_8 = "Connector_Molex:Molex_PicoBlade_53047-0810_1x08_P1.25mm_Vertical"
FUSE_FP = "Fuse:Fuse_Littelfuse-NANO2-451_453"
SMC_FP = "Diode_SMD:D_SMC"
R0603 = "Resistor_SMD:R_0603_1608Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C1210 = "Capacitor_SMD:C_1210_3225Metric"
WSK = "Resistor_SMD:R_Shunt_Vishay_WSK2512_6332Metric_T2.21mm"
LFPAK56E = "PowerSelector:LFPAK56E_SOT1023"
CAP10 = "Capacitor_SMD:CP_Elec_10x10"
CAP_G16 = "PowerSelector:CP_Panasonic_EEH-ZS_G16_10x16.8"


# ---------------------------------------------------------------------------
# Input connectors, fusing, clamping, and damping
# ---------------------------------------------------------------------------
title("A. MAIN INPUT, COMMON BACKUP FUSE, TVS CLAMPS", (80, 22), 0.9)
note("H01: RPS-400 CN3 +V to J101-1; CN2 -V to J101-2; 14 AWG.", (80, 26))

j101 = add(
    "Connector_Generic:Conn_01x02",
    "J101",
    "PSU_24V_HARNESS",
    (28, 43),
    MEGAFIT_2_RA,
    "76825-0002",
    "Molex",
    "https://www.molex.com/en-us/products/part-detail/768250002",
)
net(j101, 1, "V24_IN", "right")
net(j101, 2, "GND", "right")
j101.add_property("Reference", "J101", hidden=True)
j101.add_property("Value", "PSU_24V_HARNESS", hidden=True)
sch.texts.add("J101  BOTTOM-PSU 24 V HARNESS", (28, 34), size=0.85)
f101 = add("Device:Fuse", "F101", "15A", (52, 43), FUSE_FP, "0451015.MRL", "Littelfuse", rotation=90)
two_pin(f101, "V24_IN", "V24_FUSED")
f101.add_property("Reference", "F101", hidden=True); f101.add_property("Value", "15A", hidden=True)
note("F101  15A", (52, 34), 0.85)
d101 = add("Device:D_Zener", "D101", "SMCJ24A", (76, 43), SMC_FP, "SMCJ24A", "Littelfuse", rotation=90)
two_pin(d101, "V24_FUSED", "GND")
d101.add_property("Reference", "D101", hidden=True); d101.add_property("Value", "SMCJ24A", hidden=True)
note("D101  SMCJ24A", (76, 34), 0.85)
c101 = add("Device:C", "C101", "1uF 50V X7R", (91, 43), C1210, rotation=0)
two_pin(c101, "V24_FUSED", "GND")
c101.add_property("Reference", "C101", hidden=True); note("C101", (83, 43), 0.8)
r105 = add("Device:R", "R105", "2.40R 1%", (109, 39), R0603, rotation=90)
net(r105, 1, "V24_FUSED", "right")
r105.add_property("Reference", "R105", hidden=True); r105.add_property("Value", "2.40R 1%", hidden=True)
note("R105  2.40R", (109, 31), 0.85)
c105 = add("Device:C", "C105", "10uF 50V", (124, 43), C1210, rotation=0)
sch.wires.add(start=pin_xy(r105, 2), end=pin_xy(c105, 1))
net(c105, 2, "GND", "left")
c105.add_property("Reference", "C105", hidden=True); note("C105", (132, 43), 0.8)
note("24 V operating window: UV fall 18.0 V, UV rise 20.0 V, OV rise 30.0 V", (20, 57))

f201 = add("Device:Fuse", "F201", "15A", (52, 78), FUSE_FP, "0451015.MRL", "Littelfuse", rotation=90)
two_pin(f201, "BAT_SELECTED", "BAT_FUSED")
f201.add_property("Reference", "F201", hidden=True); f201.add_property("Value", "15A", hidden=True)
note("F201  15A", (52, 69), 0.85)
sch.texts.add("BAT_SELECTED FROM LTC4418 PRESELECTOR", (28, 69), size=0.75)
d201 = add("Device:D_Zener", "D201", "SMCJ18A", (76, 78), SMC_FP, "SMCJ18A", "Littelfuse", rotation=90)
two_pin(d201, "BAT_FUSED", "GND")
d201.add_property("Reference", "D201", hidden=True); d201.add_property("Value", "SMCJ18A", hidden=True)
note("D201  SMCJ18A", (76, 69), 0.85)
c201 = add("Device:C", "C201", "1uF 50V X7R", (91, 78), C1210, rotation=0)
two_pin(c201, "BAT_FUSED", "GND")
c201.add_property("Reference", "C201", hidden=True); note("C201", (83, 78), 0.8)
r205 = add("Device:R", "R205", "1.69R 1%", (109, 74), R0603, rotation=90)
net(r205, 1, "BAT_FUSED", "right")
r205.add_property("Reference", "R205", hidden=True); r205.add_property("Value", "1.69R 1%", hidden=True)
note("R205  1.69R", (109, 66), 0.85)
c205 = add("Device:C", "C205", "10uF 50V", (124, 78), C1210, rotation=0)
sch.wires.add(start=pin_xy(r205, 2), end=pin_xy(c205, 1))
net(c205, 2, "GND", "left")
c205.add_property("Reference", "C205", hidden=True); note("C205", (132, 78), 0.8)
note("Selected-backup outer window: UV fall 10.6 V, UV rise 11.6 V, OV rise 18.1 V", (20, 92))


# ---------------------------------------------------------------------------
# Back-to-back MOSFET paths and Kelvin current shunts
# ---------------------------------------------------------------------------
title("B. BREAK-BEFORE-MAKE IDEAL-DIODE POWER PATHS", (145, 22))
note("Common-source MOSFET pairs block reverse and cross current.", (145, 26))

q101 = add("PowerSelector:PSMN4R2-80YSE", "Q101", "PSMN4R2-80YSE", (155, 45),
           LFPAK56E, "PSMN4R2-80YSE", "Nexperia")
stub_net(q101, 1, "GATE_24", dx=-5.08, justify="right")
stub_net(q101, 5, "V24_FUSED", dy=-5.08, justify="left")
tie_pins(q101, (2, 3, 4), "SRC_24", 5.08)
note("Q101", (155, 45), 1.0)
q102 = add("PowerSelector:PSMN4R2-80YSE", "Q102", "PSMN4R2-80YSE", (180, 45),
           LFPAK56E, "PSMN4R2-80YSE", "Nexperia", rotation=180)
stub_net(q102, 1, "GATE_24", dx=5.08, justify="left")
stub_net(q102, 5, "V24_SENSE", dy=5.08, justify="left")
tie_pins(q102, (2, 3, 4), "SRC_24", -5.08)
note("Q102", (180, 45), 1.0)
c110 = add("Device:C", "C110", "47nF 50V", (168, 65), C0603, rotation=0)
two_pin(c110, "GATE_24", "SRC_24")
c110.add_property("Reference", "C110", hidden=True)
note("C110", (160, 65), 0.9)
r111 = add("Device:R_Shunt", "R111", "1.50mR 1% 1W", (230, 45), WSK,
           "WSK25121L500FEA", "Vishay", rotation=90)
r111.add_property("Reference", "R111", hidden=True)
r111.add_property("Value", "1.50mR 1% 1W", hidden=True)
kelvin_shunt(r111, "V24_SENSE", "RAW_OUT")
note("R111  1.50mR KELVIN", (230, 33), 0.9)

q201 = add("PowerSelector:PSMN4R2-80YSE", "Q201", "PSMN4R2-80YSE", (155, 82),
           LFPAK56E, "PSMN4R2-80YSE", "Nexperia")
stub_net(q201, 1, "GATE_BAT", dx=-5.08, justify="right")
stub_net(q201, 5, "BAT_FUSED", dy=-5.08, justify="left")
tie_pins(q201, (2, 3, 4), "SRC_BAT", 5.08)
note("Q201", (155, 82), 1.0)
q202 = add("PowerSelector:PSMN4R2-80YSE", "Q202", "PSMN4R2-80YSE", (180, 82),
           LFPAK56E, "PSMN4R2-80YSE", "Nexperia", rotation=180)
stub_net(q202, 1, "GATE_BAT", dx=5.08, justify="left")
stub_net(q202, 5, "BAT_SENSE", dy=5.08, justify="left")
tie_pins(q202, (2, 3, 4), "SRC_BAT", -5.08)
note("Q202", (180, 82), 1.0)
c210 = add("Device:C", "C210", "47nF 50V", (168, 102), C0603, rotation=0)
two_pin(c210, "GATE_BAT", "SRC_BAT")
c210.add_property("Reference", "C210", hidden=True)
note("C210", (160, 102), 0.9)
r211 = add("Device:R_Shunt", "R211", "1.50mR 1% 1W", (230, 82), WSK,
           "WSK25121L500FEA", "Vishay", rotation=90)
r211.add_property("Reference", "R211", hidden=True)
r211.add_property("Value", "1.50mR 1% 1W", hidden=True)
kelvin_shunt(r211, "BAT_SENSE", "RAW_OUT")
note("R211  1.50mR KELVIN", (230, 70), 0.9)
note("STARTING VALUE: ILIM = 25 mV / 1.50 mR = 16.7 A. Validate tolerance, SOA, and thermal margin before release.", (145, 107), 0.82)


# ---------------------------------------------------------------------------
# Selector controller
# ---------------------------------------------------------------------------
title("C. LTC4421 PRIORITY CONTROLLER", (238, 22))
u101 = add("PowerSelector:LTC4421IUHE", "U101", "LTC4421IUHE#PBF", (286, 68),
           "Package_DFN_QFN:QFN-36-1EP_5x6mm_P0.5mm_EP3.6x4.6mm_ThermalVias",
           "LTC4421IUHE#PBF", "Analog Devices")
note("U101  LTC4421IUHE#PBF", (335, 34), 1.1)

u1nets = {
    3: "V24_FUSED", 4: "UVF_24", 5: "UVR_24", 6: "OV_24", 7: "TMR_24",
    8: "FAULT_DISABLE_24", 9: "CH_24V_N", 10: "VALID_24V_N", 11: "FAULT_DISABLE_24",
    27: "BAT_FUSED", 26: "UVF_BAT", 25: "UVR_BAT", 24: "OV_BAT", 23: "TMR_BAT",
    22: "FAULT_DISABLE_BAT", 21: "CH_BAT_N", 20: "VALID_BAT_N", 19: "FAULT_DISABLE_BAT",
    1: "SRC_24", 2: "GATE_24", 36: "V24_SENSE", 35: "RAW_OUT",
    29: "SRC_BAT", 28: "GATE_BAT", 30: "BAT_SENSE", 31: "RAW_OUT",
    16: "GND", 18: "SHDN_MAIN",
}
for p, n in u1nets.items():
    net(u101, p, n, "right" if p in (3,4,5,6,7,8,9,10,11,27,26,25,24,23,22,21,20,19) else "left")
for p, n in ((32, "RAW_OUT"), (33, "CPO"), (34, "RAW_OUT")):
    stub_net(u101, p, n, dy=-5.08, rotation=90)
stub_net(u101, 15, "QUAL", dy=-10.16, rotation=90)
stub_net(u101, 13, "INTVCC", dy=5.08, rotation=90)
tie_pins(u101, (16, 37), "GND", 5.08, rotation=90)
stub_net(u101, 12, "INTVCC", dy=5.08, rotation=90)
stub_net(u101, 17, "GND", dx=5.08)
nc(u101, 14)
note("RETRY is grounded: a sustained overcurrent latches off until the selector is power-cycled.", (238, 112), 0.78)

c120 = add("Device:C", "C120", "1uF 16V", (242, 94), C0603)
two_pin(c120, "CPO", "RAW_OUT")
c120.add_property("Reference", "C120", hidden=True); note("C120", (234, 94), 0.85)
c121 = add("Device:C", "C121", "1uF 16V", (257, 116), C0603)
two_pin(c121, "INTVCC", "GND")
c121.add_property("Reference", "C121", hidden=True); note("C121", (249, 116), 0.85)
c122 = add("Device:C", "C122", "1nF C0G", (276, 116), C0603)
two_pin(c122, "QUAL", "GND")
c122.add_property("Reference", "C122", hidden=True); note("C122", (268, 116), 0.85)
c123 = add("Device:C", "C123", "100nF", (295, 116), C0603)
two_pin(c123, "TMR_24", "GND")
c123.add_property("Reference", "C123", hidden=True); note("C123", (287, 116), 0.85)
c223 = add("Device:C", "C223", "100nF", (314, 116), C0603)
two_pin(c223, "TMR_BAT", "GND")
c223.add_property("Reference", "C223", hidden=True); note("C223", (306, 116), 0.85)
r131 = add("Device:R", "R131", "100k", (333, 91), R0603, rotation=90)
two_pin(r131, "INTVCC", "FAULT_DISABLE_24")
r131.add_property("Reference", "R131", hidden=True); r131.add_property("Value", "100k", hidden=True)
note("R131  100k", (333, 84), 0.8)
r231 = add("Device:R", "R231", "100k", (333, 106), R0603, rotation=90)
two_pin(r231, "INTVCC", "FAULT_DISABLE_BAT")
r231.add_property("Reference", "R231", hidden=True); r231.add_property("Value", "100k", hidden=True)
note("R231  100k", (333, 99), 0.8)
note("C122 = 1 nF gives about 16 ms input qualification.", (238, 128))
note("C123/C223 = 100 nF gives about 8.3 ms current-limit timer.", (238, 132))


# ---------------------------------------------------------------------------
# User system power switch (off-board panel rocker through keyed harness)
# ---------------------------------------------------------------------------
title("H. USER SYSTEM POWER SWITCH", (400, 22))
note("SW201: E-Switch RA812C1121 maintained DPST OFF-ON panel rocker.", (400, 27), 0.9)
note("OFF opens both poles; 47k pull-downs disable LTC4421 and LTC4418 (fail-OFF).", (400, 31), 0.85)

j204 = add("Connector_Generic:Conn_02x02_Odd_Even", "J204", "PANEL_POWER_SWITCH_HARNESS", (420, 50), MF_2X2,
           "43045-0412", "Molex")
net(j204, 1, "INTVCC", "right")
net(j204, 2, "SHDN_MAIN", "left")
net(j204, 3, "PRE_INTVCC", "right")
net(j204, 4, "SHDN_PRE", "left")
j204.add_property("Reference", "J204", hidden=True)
j204.add_property("Value", "PANEL_POWER_SWITCH_HARNESS", hidden=True)
note("J204  KEYED 4-WIRE SWITCH HARNESS", (420, 39), 0.8)

r541 = add("Device:R", "R541", "47k", (468, 47), R0603, rotation=90)
two_pin(r541, "SHDN_MAIN", "GND")
r541.add_property("Reference", "R541", hidden=True)
r541.add_property("Value", "47k", hidden=True)
note("R541  47k", (468, 39), 0.75)

r542 = add("Device:R", "R542", "47k", (500, 47), R0603, rotation=90)
two_pin(r542, "SHDN_PRE", "GND")
r542.add_property("Reference", "R542", hidden=True)
r542.add_property("Value", "47k", hidden=True)
note("R542  47k", (500, 39), 0.75)

note("SW201 pole A: J204-1 INTVCC to J204-2 SHDN_MAIN.", (400, 66), 0.78)
note("SW201 pole B: J204-3 PRE_INTVCC to J204-4 SHDN_PRE.", (400, 70), 0.78)
note("Switch carries only controller-enable current; no 10 A load current crosses the panel.", (400, 74), 0.78)


# ---------------------------------------------------------------------------
# Output connector and hold-up bank
# ---------------------------------------------------------------------------
title("D. RAW OUTPUT AND TRANSFER HOLD-UP", (20, 120))
j301 = add("Connector_Generic:Conn_02x02_Odd_Even", "J301", "RAW_OUT_TO_LM5176", (28, 141), MF_2X2,
           "43045-0412", "Molex")
net(j301, 1, "RAW_OUT_LOAD", "right"); net(j301, 2, "RAW_OUT_LOAD", "left")
net(j301, 3, "GND", "right"); net(j301, 4, "GND", "left")
j301.add_property("Reference", "J301", hidden=True); j301.add_property("Value", "RAW_OUT_TO_LM5176", hidden=True)
sch.texts.add("J301  RAW OUT TO LM5176", (28, 132), size=0.85)
for idx, x in enumerate((56, 82, 108), 1):
    c = add("Device:C_Polarized", f"C30{idx}", "220uF 50V", (x, 141), CAP_G16,
            "EEH-ZS1H221V", "Panasonic")
    two_pin(c, "RAW_OUT", "GND")
    c.add_property("Reference", f"C30{idx}", hidden=True)
    note(f"C30{idx}", (x, 152), 0.8)
c304 = add("Device:C", "C304", "1uF 50V X7R", (134, 141), C1210)
two_pin(c304, "RAW_OUT", "GND")
c304.add_property("Reference", "C304", hidden=True); note("C304", (134, 152), 0.8)
c305 = add("Device:C", "C305", "100nF 50V", (158, 141), C0603)
two_pin(c305, "RAW_OUT", "GND")
c305.add_property("Reference", "C305", hidden=True); note("C305", (158, 152), 0.8)
r311 = add("Device:R_Shunt", "R311", "1.00mR 1% 1W", (190, 141), WSK,
           "WSK25121L000FEA", "Vishay", rotation=90)
r311.add_property("Reference", "R311", hidden=True)
r311.add_property("Value", "1.00mR 1% 1W", hidden=True)
kelvin_shunt(r311, "RAW_OUT", "RAW_OUT_LOAD")
note("R311  1.00mR LOAD KELVIN", (190, 129), 0.9)
note("C301-C303 are low-ESR Panasonic hybrid capacitors.", (20, 162), 0.95)
note("660 uF nominal (528 uF at -20%): approximately 0.33 V worst-case transfer droop at 10 A / 15 us.", (20, 166))
note("RAW_OUT remains within the downstream LM5176 input range during 24 V to battery transfer.", (20, 170))


# ---------------------------------------------------------------------------
# Input validity divider networks
# ---------------------------------------------------------------------------
title("E. VALID-VOLTAGE WINDOWS (0.5 V COMPARATOR TAPS)", (95, 177))
note("Physical order is VIN - R4 - UVF - R3 - UVR - R2 - OV - R1 - GND.", (95, 181))

divider24 = [
    ("R104", "1.06M 0.1%", "V24_FUSED", "UVF_24", 28),
    ("R103", "3.01k 0.1%", "UVF_24", "UVR_24", 58),
    ("R102", "9.10k 0.1%", "UVR_24", "OV_24", 88),
    ("R101", "18.2k 0.1%", "OV_24", "GND", 118),
]
for ref, val, a, b, x in divider24:
    r = add("Device:R", ref, val, (x, 200), R0603, rotation=90)
    two_pin(r, a, b)
    r.add_property("Reference", ref, hidden=True); r.add_property("Value", val, hidden=True)
    sch.texts.add(f"{ref}  {val}", (x, 207), size=0.75)
note("24 V: OV=29.95 V, UV rising=19.97 V, UV falling=17.99 V", (20, 213))

dividerbat = [
    ("R204", "965k 0.1%", "BAT_FUSED", "UVF_BAT", 158),
    ("R203", "4.22k 0.1%", "UVF_BAT", "UVR_BAT", 188),
    ("R202", "15.8k 0.1%", "UVR_BAT", "OV_BAT", 218),
    ("R201", "28.0k 0.1%", "OV_BAT", "GND", 248),
]
for ref, val, a, b, x in dividerbat:
    r = add("Device:R", ref, val, (x, 200), R0603, rotation=90)
    two_pin(r, a, b)
    r.add_property("Reference", ref, hidden=True); r.add_property("Value", val, hidden=True)
    note(f"{ref}  {val}", (x, 207), 0.75)
note("Battery: OV=18.09 V, UV rising=11.58 V, UV falling=10.57 V", (150, 213))


# ---------------------------------------------------------------------------
# Battery low indication and status connector
# ---------------------------------------------------------------------------
title("F. BATTERY WARNING AND CARRIER STATUS", (284, 177))
u301 = add("PowerSelector:TPS3842A015", "U301", "TPS3842A015DRLRQ1", (317, 204),
           "PowerSelector:Texas_DRL0006A_SOT-5X3-6_1.6x1.6mm_P0.5mm",
           "TPS3842A015DRLRQ1", "Texas Instruments")
note("U301  TPS3842A015DRLRQ1", (317, 190), 1.0)
net(u301, 6, "MON_3V3", "right")
net(u301, 5, "BAT_MON", "right")
net(u301, 4, "BAT_LOW_N", "left")
net(u301, 2, "GND", "left")
nc(u301, 1); nc(u301, 3)
r301 = add("Device:R", "R301", "176k 0.1%", (290, 228), R0603, rotation=90)
two_pin(r301, "BAT_FUSED", "BAT_MON")
r301.add_property("Reference", "R301", hidden=True); r301.add_property("Value", "176k 0.1%", hidden=True)
note("R301  176k 0.1%", (290, 235), 0.75)
r302 = add("Device:R", "R302", "10.0k 0.1%", (315, 228), R0603, rotation=90)
two_pin(r302, "BAT_MON", "GND")
r302.add_property("Reference", "R302", hidden=True); r302.add_property("Value", "10.0k 0.1%", hidden=True)
note("R302  10.0k 0.1%", (315, 235), 0.75)
c310 = add("Device:C", "C310", "100nF 10V X7R", (339, 228), C0603)
two_pin(c310, "MON_3V3", "GND")
c310.add_property("Reference", "C310", hidden=True); c310.add_property("Value", "100nF 10V X7R", hidden=True)
note("C310  100nF 10V", (339, 235), 0.75)
c311 = add("Device:C", "C311", "1nF 50V C0G", (361, 228), C0603)
two_pin(c311, "BAT_MON", "GND")
c311.add_property("Reference", "C311", hidden=True); c311.add_property("Value", "1nF 50V C0G", hidden=True)
note("C311  1nF C0G", (361, 235), 0.75)
note("Hardware backup-low policy: assert about 13.02 V; 5% hysteresis releases near 13.67 V.", (282, 241))

j401 = add("Connector_Generic:Conn_01x08", "J401", "STATUS_TO_CARRIER_3V3_PULLUPS", (373, 204), PICO_8,
           "53047-0810", "Molex")
for pin, name in enumerate(("GND", "CH_24V_N", "CH_BAT_N", "VALID_24V_N", "VALID_BAT_N", "BAT_LOW_N", "VALID_DTAP_N", "VALID_GOLD_N"), 1):
    net(j401, pin, name, "right")
j401.add_property("Reference", "J401", hidden=True); j401.add_property("Value", "STATUS_TO_CARRIER_3V3_PULLUPS", hidden=True)
note("J401  STATUS TO CARRIER", (373, 190), 0.85)
note("J401 pins 1-8: GND, /CH24, /CHBAT, /VALID24, /VALIDBAT, /BATLOW, /VDTAP, /VGOLD", (282, 246), 0.85)
note("Open-drain outputs require 3.3 V pull-ups on the carrier.", (282, 250), 0.85)


# ---------------------------------------------------------------------------
# Three-channel digital power telemetry
# ---------------------------------------------------------------------------
title("I. PRIMARY / BACKUP / LOAD DIGITAL POWER TELEMETRY", (405, 177), 1.45)
note("INA228: 85 V, 20-bit shunt/bus monitor; common I2C with wired-OR active-low alert.", (405, 182), 0.78)


def ina228_monitor(ref, xy, sense_p, sense_n, vbus_src, prefix, address, refs):
    """Add one Kelvin-connected INA228 channel and its symmetric input filter."""
    u = add(
        "Sensor_Energy:INA228", ref, "INA228AIDGSR", xy,
        "Package_SO:TSSOP-10_3x3mm_P0.5mm",
        "INA228AIDGSR", "Texas Instruments",
        "https://www.ti.com/lit/ds/symlink/ina228.pdf",
    )
    hide_ref = ref
    u.add_property("Reference", hide_ref, hidden=True)
    u.add_property("Value", "INA228AIDGSR", hidden=True)
    net(u, 10, f"{prefix}_INP", "right")
    net(u, 9, f"{prefix}_INN", "right")
    net(u, 8, f"{prefix}_VBUS", "right")
    net(u, 7, "GND", "right")
    net(u, 6, "MON_3V3", "left")
    net(u, 5, "PWR_MON_SCL", "left")
    net(u, 4, "PWR_MON_SDA", "left")
    net(u, 3, "PWR_MON_ALERT_N", "left")
    a1, a0, _ = address
    dogleg_net(u, 1, a1, 7.62, -10.16, "left", 0.62)
    dogleg_net(u, 2, a0, 17.78, -7.62, "left", 0.62)

    rp, rn, rv, cd, cb, cs = refs
    x, y = xy
    r_p = add("Device:R", rp, "10R 1%", (x - 8, y + 21), R0603, rotation=90)
    two_pin(r_p, sense_p, f"{prefix}_INP")
    r_p.add_property("Reference", rp, hidden=True); r_p.add_property("Value", "10R 1%", hidden=True)
    r_n = add("Device:R", rn, "10R 1%", (x - 8, y + 31), R0603, rotation=90)
    two_pin(r_n, sense_n, f"{prefix}_INN")
    r_n.add_property("Reference", rn, hidden=True); r_n.add_property("Value", "10R 1%", hidden=True)
    c_d = add("Device:C", cd, "100nF", (x - 8, y + 41), C0603)
    two_pin(c_d, f"{prefix}_INP", f"{prefix}_INN")
    c_d.add_property("Reference", cd, hidden=True); c_d.add_property("Value", "100nF", hidden=True)
    r_v = add("Device:R", rv, "100R 1%", (x - 8, y + 52), R0603, rotation=90)
    two_pin(r_v, vbus_src, f"{prefix}_VBUS")
    r_v.add_property("Reference", rv, hidden=True); r_v.add_property("Value", "100R 1%", hidden=True)
    c_b = add("Device:C", cb, "10nF 100V", (x + 13, y + 47), C0603)
    two_pin(c_b, f"{prefix}_VBUS", "GND")
    c_b.add_property("Reference", cb, hidden=True); c_b.add_property("Value", "10nF 100V", hidden=True)
    c_s = add("Device:C", cs, "100nF", (x + 13, y + 57), C0603)
    two_pin(c_s, "MON_3V3", "GND")
    c_s.add_property("Reference", cs, hidden=True); c_s.add_property("Value", "100nF", hidden=True)
    note(f"{ref}  {address[2]}", (x - 6, y - 18), 0.75)


ina228_monitor(
    "U601", (425, 210), "V24_SENSE", "RAW_OUT", "V24_FUSED", "MON24",
    ("GND", "GND", "0x40"), ("R601", "R602", "R603", "C601", "C602", "C603"),
)
ina228_monitor(
    "U602", (480, 210), "BAT_SENSE", "RAW_OUT", "BAT_FUSED", "MONBAT",
    ("GND", "MON_3V3", "0x41"), ("R611", "R612", "R613", "C611", "C612", "C613"),
)
ina228_monitor(
    "U603", (535, 210), "RAW_OUT", "RAW_OUT_LOAD", "RAW_OUT_LOAD", "MONLOAD",
    ("MON_3V3", "GND", "0x44"), ("R621", "R622", "R623", "C621", "C622", "C623"),
)

j402 = add("Connector_Generic:Conn_01x06", "J402", "POWER_TELEMETRY_TO_CARRIER", (405, 270), PICO_6,
           "53047-0610", "Molex")
for pin, name in enumerate(("MON_3V3", "GND", "PWR_MON_SDA", "PWR_MON_SCL", "PWR_MON_ALERT_N", "GND"), 1):
    net(j402, pin, name, "right")
j402.add_property("Reference", "J402", hidden=True)
j402.add_property("Value", "POWER_TELEMETRY_TO_CARRIER", hidden=True)
note("J402 TELEMETRY: 1 3V3, 2 GND, 3 SDA, 4 SCL, 5 /ALERT, 6 GND", (425, 276), 0.72)

c630 = add("Device:C", "C630", "1uF", (535, 270), C0603)
two_pin(c630, "MON_3V3", "GND")
c630.add_property("Reference", "C630", hidden=True); c630.add_property("Value", "1uF", hidden=True)
f601 = add("power:PWR_FLAG", "#FLG0601", "PWR_FLAG", (515, 270))
net(f601, 1, "MON_3V3", "left")
note("Source shunts: 1.5mR -> 27.307 A at +/-40.96 mV. Load shunt: 1mR -> 40.96 A.", (405, 281), 0.72)
note("R311 is after the hold-up bank, so U603 includes capacitor-supplied load current during transfer.", (405, 286), 0.72)


# ---------------------------------------------------------------------------
# D-Tap / Gold Mount backup preselector
# ---------------------------------------------------------------------------
title("G. D-TAP / GOLD MOUNT NON-PARALLELING PRESELECTOR", (110, 290))
note("LTC4418 V1 gives valid D-Tap priority over V2 Gold Mount. Both paths are break-before-make.", (110, 294), 0.95)
note("External interface: LEMO EGG.0B.302.CLL female panel inlet; pin 1 return, pin 2 positive.", (110, 299), 0.85)

j202 = add("Connector_Generic:Conn_02x02_Odd_Even", "J202", "LEMO_EGG.0B.302.CLL_13V_TO_16V8", (28, 314), MF_2X2,
           "43045-0412", "Molex")
net(j202, 1, "DTAP_IN", "right"); net(j202, 2, "DTAP_IN", "left")
net(j202, 3, "GND", "right"); net(j202, 4, "GND", "left")
j202.add_property("Reference", "J202", hidden=True); j202.add_property("Value", "LEMO_EGG.0B.302.CLL_13V_TO_16V8", hidden=True)
sch.texts.add("J202  FROM 2-PIN LEMO PANEL INLET 13.0-16.8 V", (28, 304), size=0.85)
f202 = add("Device:Fuse", "F202", "15A", (52, 314), FUSE_FP, "0451015.MRL", "Littelfuse", rotation=90)
two_pin(f202, "DTAP_IN", "DTAP_FUSED")
f202.add_property("Reference", "F202", hidden=True); f202.add_property("Value", "15A", hidden=True)
note("F202  15A", (52, 304), 0.8)
d202 = add("Device:D_TVS", "D202", "SMBJ18CA", (76, 314), "Diode_SMD:D_SMB", "SMBJ18CA", "Littelfuse", rotation=90)
two_pin(d202, "DTAP_FUSED", "GND")
d202.add_property("Reference", "D202", hidden=True); d202.add_property("Value", "SMBJ18CA", hidden=True)
note("D202  SMBJ18CA", (76, 304), 0.8)
c202 = add("Device:C", "C202", "10uF 50V X7R", (96, 314), C1210)
two_pin(c202, "DTAP_FUSED", "GND")
c202.add_property("Reference", "C202", hidden=True); note("C202", (96, 325), 0.8)

j203 = add("Connector_Generic:Conn_02x02_Odd_Even", "J203", "GOLD_MOUNT_10V_TO_16V8", (28, 359), MF_2X2,
           "43045-0412", "Molex")
net(j203, 1, "GOLD_IN", "right"); net(j203, 2, "GOLD_IN", "left")
net(j203, 3, "GND", "right"); net(j203, 4, "GND", "left")
j203.add_property("Reference", "J203", hidden=True); j203.add_property("Value", "GOLD_MOUNT_10V_TO_16V8", hidden=True)
sch.texts.add("J203  FROM PANEL QRC-GOLD 8375-0094 HARNESS 10.0-16.8 V", (28, 349), size=0.85)
f203 = add("Device:Fuse", "F203", "15A", (52, 359), FUSE_FP, "0451015.MRL", "Littelfuse", rotation=90)
two_pin(f203, "GOLD_IN", "GOLD_FUSED")
f203.add_property("Reference", "F203", hidden=True); f203.add_property("Value", "15A", hidden=True)
note("F203  15A", (52, 349), 0.8)
d203 = add("Device:D_TVS", "D203", "SMBJ18CA", (76, 359), "Diode_SMD:D_SMB", "SMBJ18CA", "Littelfuse", rotation=90)
two_pin(d203, "GOLD_FUSED", "GND")
d203.add_property("Reference", "D203", hidden=True); d203.add_property("Value", "SMBJ18CA", hidden=True)
note("D203  SMBJ18CA", (76, 349), 0.8)
c203 = add("Device:C", "C203", "10uF 50V X7R", (96, 359), C1210)
two_pin(c203, "GOLD_FUSED", "GND")
c203.add_property("Reference", "C203", hidden=True); note("C203", (96, 370), 0.8)

for ref, x, y, source, drain, gate in (
    ("Q501", 135, 314, "SRC_DTAP", "DTAP_FUSED", "GATE_DTAP"),
    ("Q502", 170, 314, "SRC_DTAP", "BAT_SELECTED", "GATE_DTAP"),
    ("Q503", 135, 359, "SRC_GOLD", "GOLD_FUSED", "GATE_GOLD"),
    ("Q504", 170, 359, "SRC_GOLD", "BAT_SELECTED", "GATE_GOLD"),
):
    q = add("PowerSelector:SiR5607DP", ref, "SiR5607DP-T1-RE3", (x, y),
            "Package_SO:PowerPAK_SO-8_Single", "SiR5607DP-T1-RE3", "Vishay",
            "https://www.vishay.com/docs/62247/sir5607dp.pdf")
    stub_net(q, 4, gate, dx=-5.08, justify="right")
    tie_pins(q, (1, 2, 3), source, 5.08)
    # KiCad's PowerPAK_SO-8_Single footprint repeats physical drain lands
    # 5-8 as one logical pad number 5, matching the standard 5-pin MOSFET map.
    stub_net(q, 5, drain, dy=-5.08)
    note(ref, (x, y), 0.8)

r511 = add("Device:R", "R511", "6.81k 1%", (205, 306), R0603, rotation=90)
two_pin(r511, "G1_CTRL", "GATE_DTAP")
r511.add_property("Reference", "R511", hidden=True); r511.add_property("Value", "6.81k 1%", hidden=True)
d511 = add("Device:D_Schottky", "D511", "BAT46WJ", (220, 306), "Diode_SMD:D_SOD-323", "BAT46WJ,115", "Nexperia", rotation=90)
# Anode at the LTC4418 G1 pin, cathode at the MOSFET gate. This bypasses
# R511 only while G1 rises toward VS1, giving the datasheet's fast turn-off.
two_pin(d511, "GATE_DTAP", "G1_CTRL")
d511.add_property("Reference", "D511", hidden=True); d511.add_property("Value", "BAT46WJ", hidden=True)
c511 = add("Device:C", "C511", "47nF 50V", (235, 314), C0603)
two_pin(c511, "GATE_DTAP", "BAT_SELECTED")
c511.add_property("Reference", "C511", hidden=True)
c512 = add("Device:C", "C512", "470nF 50V", (250, 314), C0603)
two_pin(c512, "SRC_DTAP", "BAT_SELECTED")
c512.add_property("Reference", "C512", hidden=True)

r521 = add("Device:R", "R521", "6.81k 1%", (205, 351), R0603, rotation=90)
two_pin(r521, "G2_CTRL", "GATE_GOLD")
r521.add_property("Reference", "R521", hidden=True); r521.add_property("Value", "6.81k 1%", hidden=True)
d521 = add("Device:D_Schottky", "D521", "BAT46WJ", (220, 351), "Diode_SMD:D_SOD-323", "BAT46WJ,115", "Nexperia", rotation=90)
# Same fast-turn-off polarity as D511: anode at G2, cathode at MOSFET gate.
two_pin(d521, "GATE_GOLD", "G2_CTRL")
d521.add_property("Reference", "D521", hidden=True); d521.add_property("Value", "BAT46WJ", hidden=True)
c521 = add("Device:C", "C521", "47nF 50V", (235, 359), C0603)
two_pin(c521, "GATE_GOLD", "BAT_SELECTED")
c521.add_property("Reference", "C521", hidden=True)
c522 = add("Device:C", "C522", "470nF 50V", (250, 359), C0603)
two_pin(c522, "SRC_GOLD", "BAT_SELECTED")
c522.add_property("Reference", "C522", hidden=True)

u201 = add("PowerSelector:LTC4418IUF", "U201", "LTC4418IUF#PBF", (315, 337),
           "Package_DFN_QFN:QFN-20-1EP_4x4mm_P0.5mm_EP2.6x2.6mm_ThermalVias",
           "LTC4418IUF#PBF", "Analog Devices")
note("U201  LTC4418IUF#PBF", (315, 304), 0.95)
for p, n in {
    17: "DTAP_FUSED", 2: "UV_DTAP", 3: "OV_DTAP", 6: "VALID_DTAP_N",
    16: "GOLD_FUSED", 4: "UV_GOLD", 5: "OV_GOLD", 7: "VALID_GOLD_N",
    20: "GND", 14: "SRC_DTAP", 13: "G1_CTRL", 12: "SRC_GOLD", 11: "G2_CTRL",
    15: "BAT_SELECTED", 1: "TMR_PRE",
}.items():
    net(u201, p, n, "right" if p in (17, 2, 3, 6, 16, 4, 5, 7, 20) else "left")
stub_net(u201, 10, "PRE_INTVCC", dy=7.62, rotation=90)
stub_net(u201, 18, "PRE_INTVCC", dx=10.16)
stub_net(u201, 19, "SHDN_PRE", dx=5.08)
tie_pins(u201, (8, 21), "GND", 5.08, rotation=90)
nc(u201, 9)

c531 = add("Device:C", "C531", "100nF 16V", (350, 348), C0603)
two_pin(c531, "PRE_INTVCC", "GND")
c531.add_property("Reference", "C531", hidden=True)
c532 = add("Device:C", "C532", "1nF C0G", (370, 348), C0603)
two_pin(c532, "TMR_PRE", "GND")
c532.add_property("Reference", "C532", hidden=True)
c533 = add("Device:C_Polarized", "C533", "100uF 35V", (390, 348), CAP10)
two_pin(c533, "BAT_SELECTED", "GND")
c533.add_property("Reference", "C533", hidden=True)
note("C532 = 1 nF: about 16 ms source validation", (292, 375), 0.8)
note("R511/R521 + C511/C521 limit higher-voltage-source inrush; verify SOA on prototype", (292, 379), 0.8)
note("D511/D521: anode at controller G pin, cathode at MOSFET gate for fast turn-off", (292, 383), 0.8)

dtap_div = [
    ("R503", "919k 0.1%", "DTAP_FUSED", "UV_DTAP", 415),
    ("R502", "26.1k 0.1%", "UV_DTAP", "OV_DTAP", 465),
    ("R501", "55.6k 0.1%", "OV_DTAP", "GND", 515),
]
for ref, val, a, b, x in dtap_div:
    r = add("Device:R", ref, val, (x, 320), R0603, rotation=90)
    two_pin(r, a, b)
    r.add_property("Reference", ref, hidden=True); r.add_property("Value", val, hidden=True)
    note(f"{ref} {val}", (x, 330), 0.65)
note("D-Tap actual: UV rise 12.62 V, UV fall 12.25 V, OV rise 18.00 V", (415, 340), 0.82)

gold_div = [
    ("R506", "909k 0.1%", "GOLD_FUSED", "UV_GOLD", 415),
    ("R505", "31.6k 0.1%", "UV_GOLD", "OV_GOLD", 465),
    ("R504", "56.2k 0.1%", "OV_GOLD", "GND", 515),
]
for ref, val, a, b, x in gold_div:
    r = add("Device:R", ref, val, (x, 365), R0603, rotation=90)
    two_pin(r, a, b)
    r.add_property("Reference", ref, hidden=True); r.add_property("Value", val, hidden=True)
    note(f"{ref} {val}", (x, 375), 0.65)
note("Gold actual: UV rise 11.69 V, UV fall 11.35 V, OV rise 17.74 V", (415, 385), 0.82)

note("SiR5607DP: -60 V P-MOS, 12 mOhm max at VGS=-4.5 V. Use large copper heat-spreading areas.", (80, 381), 0.82)
note("D-Tap and Gold Mount are alternate backup inputs only. Never parallel and never charge through this board.", (80, 384), 0.82)
note("REVERSE MISWIRE SAFE: fuse + bidirectional TVS + ceramic C precede LTC4418/back-to-back P-MOS blockers.", (80, 387), 0.82)


# ---------------------------------------------------------------------------
# Explicit power drivers for ERC
# ---------------------------------------------------------------------------
for i, (name, x) in enumerate((("V24_FUSED", 30), ("BAT_FUSED", 55), ("RAW_OUT", 80),
                               ("DTAP_FUSED", 105), ("GOLD_FUSED", 130), ("BAT_SELECTED", 155),
                               ("RAW_OUT_LOAD", 180)), 1):
    f = add("power:PWR_FLAG", f"#FLG010{i}", "PWR_FLAG", (x, 399))
    net(f, 1, name, "left")
fg = add("power:PWR_FLAG", "#FLG0108", "PWR_FLAG", (205, 399))
net(fg, 1, "GND", "left")

title("DESIGN INTENT", (330, 388), 1.6)
note("Priority: internal PSU 24 V, then D-Tap, then Gold Mount. No source paralleling.", (330, 392), 1.0)
note("Both selectors are break-before-make; C301-C303 provide continuous energy to the LM5176 input.", (330, 396), 1.0)
note("SW201 OFF disables both selectors; no valid source can energize RAW_OUT. Charge batteries externally.", (330, 400), 1.0)

sch.save(OUT)
print(OUT)
