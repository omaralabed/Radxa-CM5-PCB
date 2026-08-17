#!/usr/bin/env python3
"""Generate the complete-system electrical interconnect and detailed hierarchy."""

from __future__ import annotations

import json
import uuid
from pathlib import Path


UUID_COUNTER = 0


def deterministic_uuid4() -> uuid.UUID:
    """Return stable UUIDs so repeated generation produces no source drift."""
    global UUID_COUNTER
    UUID_COUNTER += 1
    return uuid.uuid5(
        uuid.NAMESPACE_URL,
        f"radxa-cm5-procomm:complete-electrical:{UUID_COUNTER}",
    )


uuid.uuid4 = deterministic_uuid4

import kicad_sch_api as ksa


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "cad/kicad/SYSTEM"
PROJECT_NAME = "Radxa-CM5-ProComm-System"
SCHEMATIC = HERE / f"{PROJECT_NAME}.kicad_sch"
PROJECT = HERE / f"{PROJECT_NAME}.kicad_pro"
NAMESPACE = uuid.UUID("470d65ea-a7a0-5de5-b5fb-8f154ae31baa")


TDM_MAP = {
    1: "AUD_MCLK_P", 2: "AUD_MCLK_N", 3: "GND", 4: "GND",
    5: "AUD_BCLK_P", 6: "AUD_BCLK_N", 7: "AUD_FSYNC_P", 8: "AUD_FSYNC_N",
    9: "GND", 10: "GND", 11: "AUD_DAC_SDIN_P", 12: "AUD_DAC_SDIN_N",
    13: "AUD_ADC_SDOUT_P", 14: "AUD_ADC_SDOUT_N", 15: "GND", 16: "GND",
    17: "AUD_I2C_SCL", 18: "AUD_I2C_SDA", 19: "AUD_ADC_RST_N",
    20: "AUD_DAC_RST_N", 21: "AUD_DAC_MUTE_CMD_N", 22: "AUD_IRQ_N",
    23: "AUDIO_PRESENT_N", 24: "AUDIO_ENABLE", 25: "LOGIC_3V3", 26: "GND",
    27: "TDM_SPARE_1", 28: "TDM_SPARE_2", 29: "GND", 30: "GND",
}

HDMI_MAP = {
    1: "HDMI_D2_P", 2: "GND", 3: "HDMI_D2_N", 4: "HDMI_D1_P",
    5: "GND", 6: "HDMI_D1_N", 7: "HDMI_D0_P", 8: "GND",
    9: "HDMI_D0_N", 10: "HDMI_CLK_P", 11: "GND", 12: "HDMI_CLK_N",
    13: "HDMI_CEC", 14: "HDMI_HEAC_P", 15: "HDMI_DDC_SCL",
    16: "HDMI_DDC_SDA", 17: "GND", 18: "HDMI_5V_OUT", 19: "HDMI_HPD",
}

RAW_POWER_MAP = {1: "RAW_OUT_LOAD", 2: "RAW_OUT_LOAD", 3: "GND", 4: "GND"}
STATUS_MAP = {
    1: "GND", 2: "CH_24V_N", 3: "CH_BAT_N", 4: "VALID_24V_N",
    5: "VALID_BAT_N", 6: "BAT_LOW_N", 7: "VALID_DTAP_N", 8: "VALID_GOLD_N",
}
TELEMETRY_MAP = {
    1: "PWR_TELEM_3V3", 2: "GND", 3: "CTRL_I2C_SDA",
    4: "CTRL_I2C_SCL", 5: "PWR_MON_ALERT_N", 6: "GND",
}
AUDIO_POWER_MAP = {1: "AUDIO_12V", 2: "AUDIO_12V", 3: "GND", 4: "GND"}
DISPLAY_POWER_MAP = {1: "DISPLAY_12V", 2: "DISPLAY_12V", 3: "GND", 4: "GND"}
USB_TOUCH_MAP = {1: "TOUCH_USB_5V", 2: "TOUCH_USB_DM", 3: "TOUCH_USB_DP", 4: "GND"}

SHEETS = [
    ("PWR-SELECT", "../PWR-SELECT/PowerSelector.kicad_sch", "2"),
    ("CM5-CARRIER Connected Root", "../CM5-CARRIER/CM5-Carrier.kicad_sch", "3"),
    ("AUDIO-8X8 Connected Root", "../AUDIO-8X8/Audio-8x8.kicad_sch", "11"),
]


def stable_uuid(name: str) -> str:
    return str(uuid.uuid5(NAMESPACE, name))


def add_text(
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


def pin_xy(component, pin: int | str) -> tuple[float, float]:
    point = component.get_pin_position(str(pin))
    if point is None:
        raise RuntimeError(f"{component.reference} has no pin {pin}")
    return (point.x, 2.0 * component.position.y - point.y)


def add_connector(
    schematic: ksa.Schematic,
    lib_id: str,
    reference: str,
    value: str,
    position: tuple[float, float],
    pin_map: dict[int, str],
    *,
    rotation: int = 0,
    label_size: float = 0.58,
):
    component = schematic.components.add(
        lib_id,
        reference,
        value,
        position=position,
        rotation=rotation,
    )
    component.in_bom = False
    component.on_board = False
    component.add_property("Purpose", "SYSTEM_INTERCONNECT_REPRESENTATION", hidden=True)
    pin_positions = [pin_xy(component, pin) for pin in pin_map]
    value_y = min(point[1] for point in pin_positions) - 3.2
    component.set_property_effects(
        "Reference",
        {"font_size": (0.5, 0.5), "position": (position[0], value_y - 1.8)},
    )
    component.set_property_effects(
        "Value",
        {
            "font_size": (0.72, 0.72),
            "position": (position[0], value_y),
        },
    )
    for pin, net_name in pin_map.items():
        start = pin_xy(component, pin)
        direction = -1 if start[0] < component.position.x else 1
        end = (start[0] + direction * 6.35, start[1])
        schematic.wires.add(start=start, end=end)
        schematic.labels.add(
            net_name,
            end,
            size=label_size,
            justify_h="right" if direction < 0 else "left",
        )
    return component


def add_harness_pair(
    schematic: ksa.Schematic,
    key: str,
    heading: str,
    left_ref: str,
    left_value: str,
    right_ref: str,
    right_value: str,
    lib_id: str,
    pin_map: dict[int, str],
    left_position: tuple[float, float],
    right_position: tuple[float, float],
    *,
    label_size: float = 0.58,
) -> None:
    center_x = (left_position[0] + right_position[0]) / 2
    add_text(
        schematic,
        f"{key}-heading",
        heading,
        (center_x, left_position[1] - 28),
        size=1.35,
        bold=True,
    )
    add_connector(
        schematic,
        lib_id,
        left_ref,
        left_value,
        left_position,
        pin_map,
        label_size=label_size,
    )
    add_connector(
        schematic,
        lib_id,
        right_ref,
        right_value,
        right_position,
        pin_map,
        rotation=180,
        label_size=label_size,
    )


def add_power_sources(schematic: ksa.Schematic) -> None:
    add_text(schematic, "power-title", "1. AC, PSU, AND BACKUP SOURCES", (190, 58), size=1.7, bold=True)
    add_connector(
        schematic,
        "Connector_Generic:Conn_01x03",
        "J9001",
        "FUSED C14 AC INLET",
        (70, 105),
        {1: "AC_L_IN", 2: "AC_N", 3: "CHASSIS_PE"},
    )
    fuse = schematic.components.add("Device:Fuse", "F9001", "C14 INLET FUSE", position=(150, 95))
    fuse.in_bom = False
    fuse.on_board = False
    fuse.add_property("Purpose", "SYSTEM_INTERCONNECT_REPRESENTATION", hidden=True)
    fuse.set_property_effects(
        "Reference", {"font_size": (0.5, 0.5), "position": (150, 84.2)}
    )
    fuse.set_property_effects(
        "Value",
        {"font_size": (0.72, 0.72), "position": (150, 86)},
    )
    for pin, net_name in ((1, "AC_L_IN"), (2, "AC_L_FUSED")):
        start = pin_xy(fuse, pin)
        direction = -1 if start[0] < fuse.position.x else 1
        end = (start[0] + direction * 8, start[1])
        schematic.wires.add(start=start, end=end)
        schematic.labels.add(
            net_name,
            end,
            size=0.62,
            justify_h="right" if direction < 0 else "left",
        )
    add_connector(
        schematic,
        "Connector_Generic:Conn_01x03",
        "J9002",
        "RPS-400-24-C AC CN1",
        (245, 105),
        {1: "AC_L_FUSED", 2: "AC_N", 3: "CHASSIS_PE"},
        rotation=180,
    )
    add_connector(
        schematic,
        "Connector_Generic:Conn_01x02",
        "J9003",
        "RPS-400-24-C DC CN2/CN3",
        (245, 170),
        {1: "V24_IN", 2: "GND"},
    )
    add_connector(
        schematic,
        "Connector_Generic:Conn_01x02",
        "J9004",
        "PWR-SELECT J101 PSU INPUT",
        (350, 170),
        {1: "V24_IN", 2: "GND"},
        rotation=180,
    )
    add_connector(
        schematic,
        "Connector_Generic:Conn_01x02",
        "J9005",
        "ANTON/BAUER QRC-GOLD",
        (90, 225),
        {1: "GOLD_IN", 2: "GND"},
    )
    add_connector(
        schematic,
        "Connector_Generic:Conn_01x02",
        "J9006",
        "D-TAP BACKUP INPUT",
        (245, 225),
        {1: "DTAP_IN", 2: "GND"},
    )
    add_text(
        schematic,
        "power-note",
        "RPS-400-24-C is primary. PWR-SELECT performs break-before-make source priority and no-blink hold-up.",
        (205, 275),
        size=0.9,
    )


def add_power_carrier_harnesses(schematic: ksa.Schematic) -> None:
    add_text(schematic, "carrier-power-title", "2. PWR-SELECT TO CM5-CARRIER", (600, 58), size=1.7, bold=True)
    add_harness_pair(
        schematic,
        "raw-power",
        "H01 - FOUR-CONDUCTOR RAW POWER HARNESS",
        "J9301",
        "PWR-SELECT J301",
        "J9101",
        "CM5-CARRIER J101",
        "Connector_Generic:Conn_02x02_Odd_Even",
        RAW_POWER_MAP,
        (470, 115),
        (700, 115),
    )
    add_harness_pair(
        schematic,
        "status",
        "H02A - SOURCE STATUS HARNESS",
        "J9401",
        "PWR-SELECT J401",
        "J9102",
        "CM5-CARRIER J102",
        "Connector_Generic:Conn_01x08",
        STATUS_MAP,
        (470, 205),
        (700, 205),
    )
    add_harness_pair(
        schematic,
        "telemetry",
        "H02B - VOLTAGE / CURRENT TELEMETRY I2C",
        "J9402",
        "PWR-SELECT J402",
        "J9103",
        "CM5-CARRIER J103",
        "Connector_Generic:Conn_01x06",
        TELEMETRY_MAP,
        (470, 290),
        (700, 290),
    )
    add_text(
        schematic,
        "telemetry-alias-note",
        "PWR_TELEM_3V3 is MON_3V3 on PWR-SELECT and LOGIC_3V3 on CM5-CARRIER.",
        (590, 330),
        size=0.75,
    )


def add_audio_harnesses(schematic: ksa.Schematic) -> None:
    add_text(schematic, "audio-link-title", "3. CM5-CARRIER TO AUDIO-8X8", (980, 58), size=1.7, bold=True)
    add_harness_pair(
        schematic,
        "tdm",
        "H04 - 30-PIN BUFFERED DIFFERENTIAL TDM / CONTROL",
        "J9201",
        "CM5-CARRIER J201",
        "J9501",
        "AUDIO-8X8 J101",
        "Connector_Generic:Conn_02x15_Odd_Even",
        TDM_MAP,
        (860, 165),
        (1090, 165),
        label_size=0.44,
    )
    add_harness_pair(
        schematic,
        "audio-power",
        "H05 - DEDICATED AUDIO 12 V POWER",
        "J9202",
        "CM5-CARRIER J202",
        "J9502",
        "AUDIO-8X8 J102",
        "Connector_Generic:Conn_02x02_Odd_Even",
        AUDIO_POWER_MAP,
        (860, 300),
        (1090, 300),
    )


def add_display_harnesses(schematic: ksa.Schematic) -> None:
    add_text(schematic, "display-title", "4. LID DISPLAY ELECTRICAL HARNESS", (200, 350), size=1.7, bold=True)
    add_harness_pair(
        schematic,
        "hdmi",
        "H03A - HDMI VIDEO",
        "J9801",
        "CM5-CARRIER J801 HDMI-A",
        "J9851",
        "15.6-IN MONITOR HDMI IN",
        "Connector_Generic:Conn_01x19",
        HDMI_MAP,
        (80, 445),
        (315, 445),
        label_size=0.43,
    )
    add_harness_pair(
        schematic,
        "usb-touch",
        "H03B - USB 2 TOUCH DATA",
        "J9802",
        "CM5-CARRIER J802 USB-A",
        "J9852",
        "MONITOR USB-B TOUCH",
        "Connector_Generic:Conn_01x04",
        USB_TOUCH_MAP,
        (80, 555),
        (315, 555),
    )
    add_harness_pair(
        schematic,
        "display-power",
        "H03C - 12 V / 2.5 A MONITOR POWER",
        "J9803",
        "CM5-CARRIER J803",
        "J9853",
        "MONITOR DC 12 V",
        "Connector_Generic:Conn_02x02_Odd_Even",
        DISPLAY_POWER_MAP,
        (80, 615),
        (315, 615),
    )


def add_compute_external_io(schematic: ksa.Schematic) -> None:
    add_text(schematic, "compute-io-title", "5. COOLING, NETWORK, SERVICE, AND RF", (600, 350), size=1.7, bold=True)
    fan_maps = (
        ("J9411", "CPU HEATSINK FAN", {1: "GND", 2: "CPU_FAN_12V", 3: "CPU_FAN_TACH", 4: "CPU_FAN_PWM"}),
        ("J9412", "MODEM HEATSINK FAN", {1: "GND", 2: "MODEM_FAN_12V", 3: "MODEM_FAN_TACH", 4: "MODEM_FAN_PWM"}),
        ("J9413", "THA0412AD INTAKE", {1: "GND", 2: "INTAKE_FAN_12V", 3: "INTAKE_FAN_TACH", 4: "INTAKE_FAN_PWM"}),
        ("J9414", "THA0412AD EXHAUST", {1: "GND", 2: "EXHAUST_FAN_12V", 3: "EXHAUST_FAN_TACH", 4: "EXHAUST_FAN_PWM"}),
    )
    for index, (reference, value, pin_map) in enumerate(fan_maps):
        x = 455 + (index % 2) * 145
        y = 405 + (index // 2) * 65
        add_connector(
            schematic,
            "Connector_Generic:Conn_01x04",
            reference,
            value,
            (x, y),
            pin_map,
            label_size=0.5,
        )

    for index, port in enumerate(("WAN1", "WAN2", "LAN1", "LAN2")):
        x = 735 + (index % 2) * 105
        y = 405 + (index // 2) * 65
        add_connector(
            schematic,
            "Connector_Generic:Conn_01x08",
            f"J94{21 + index}",
            f"{port} RJ45",
            (x, y),
            {pin: f"{port}_RJ45_{pin}" for pin in range(1, 9)},
            label_size=0.42,
        )

    add_connector(
        schematic,
        "Connector_Generic:Conn_01x04",
        "J9430",
        "CTIA HEADSET JACK",
        (455, 550),
        {1: "HEADSET_L", 2: "HEADSET_R", 3: "HEADSET_GND", 4: "HEADSET_MIC"},
        label_size=0.5,
    )
    for index in range(2):
        add_connector(
            schematic,
            "Connector_Generic:Conn_01x06",
            f"J943{1 + index}",
            f"NANO-SIM {index + 1}",
            (590 + index * 120, 550),
            {
                1: f"SIM{index + 1}_VCC", 2: f"SIM{index + 1}_RST",
                3: f"SIM{index + 1}_CLK", 4: f"SIM{index + 1}_IO",
                5: "GND", 6: f"SIM{index + 1}_DET",
            },
            label_size=0.46,
        )

    rf_names = ("WIFI_1_RF", "WIFI_2_RF", "WIFI_3_RF", "WIFI_4_RF", "CELL_1_RF", "CELL_2_RF", "CELL_3_RF", "CELL_4_GNSS_RF")
    for index, net_name in enumerate(rf_names):
        x = 455 + index * 52
        add_connector(
            schematic,
            "Connector_Generic:Conn_01x01",
            f"J94{40 + index}",
            net_name.replace("_RF", ""),
            (x, 625),
            {1: net_name},
            label_size=0.42,
        )


def add_balanced_audio_panel(schematic: ksa.Schematic) -> None:
    add_text(schematic, "xlr-title", "6. BALANCED AUDIO PANEL - 8 OUTPUTS / 8 INPUTS", (985, 350), size=1.7, bold=True)
    for channel in range(1, 9):
        y = 385 + (channel - 1) * 32
        add_connector(
            schematic,
            "Connector_Generic:Conn_01x03",
            f"J96{channel:02d}",
            f"NC3MAV CH{channel} OUT",
            (895, y),
            {1: "XLR_CHASSIS", 2: f"AOUT_CH{channel}_HOT", 3: f"AOUT_CH{channel}_COLD"},
            label_size=0.42,
        )
        add_connector(
            schematic,
            "Connector_Generic:Conn_01x03",
            f"J97{channel:02d}",
            f"NC3FAV CH{channel} IN",
            (1080, y),
            {1: "XLR_CHASSIS", 2: f"AIN_CH{channel}_HOT", 3: f"AIN_CH{channel}_COLD"},
            rotation=180,
            label_size=0.42,
        )


def add_detailed_sheets(schematic: ksa.Schematic) -> None:
    add_text(
        schematic,
        "detail-title",
        "PHYSICAL BOARD ROOTS - EACH ROOT CONTAINS ITS CONNECTED DETAILED PAGES",
        (390, 674),
        size=1.7,
        bold=True,
    )
    positions = [
        (40 + column * 285, 700 + row * 34)
        for row in range(4)
        for column in range(4)
    ]
    for (name, filename, page), position in zip(SHEETS, positions):
        resolved = (HERE / filename).resolve()
        if not resolved.exists():
            raise FileNotFoundError(resolved)
        sheet_uuid = schematic.add_sheet(
            name=name,
            filename=filename,
            position=position,
            size=(245, 20),
            stroke_width=0.3,
            project_name=PROJECT_NAME,
            page_number=page,
            uuid=stable_uuid(f"sheet:{name}"),
        )
        sheet = next(item for item in schematic._data["sheets"] if item["uuid"] == sheet_uuid)
        sheet["exclude_from_sim"] = True
        sheet["in_bom"] = False
        sheet["on_board"] = False


def build_schematic() -> None:
    schematic = ksa.Schematic.create(
        name="Radxa CM5 ProComm - Complete Electrical Schematic",
        version="20250114",
        generator="eeschema",
        generator_version="9.0",
        paper="A0",
        uuid=stable_uuid("root"),
    )
    schematic.set_title_block(
        title="Radxa CM5 ProComm - Complete Electrical Schematic",
        date="2026-08-17",
        rev="A2",
        company="ProComm",
        comments={
            1: "Top sheet is the electrical system interconnect; nested roots expose all detailed circuits",
            2: "PWR-SELECT, CM5-CARRIER, and AUDIO-8X8 are authoritative physical PCB netlists",
            3: "System connector representations are excluded from BOM and board update",
            4: "PCB ROUTING HELD FOR PHYSICAL RELEASE GATES",
        },
    )
    add_text(
        schematic,
        "title",
        "RADXA CM5 PROCOMM - COMPLETE ELECTRICAL SCHEMATIC",
        (300, 24),
        size=3.0,
        bold=True,
    )
    add_text(
        schematic,
        "scope",
        "Page 1 shows system harness interconnects. The three physical board roots contain the complete connected component-level circuits.",
        (400, 38),
        size=1.15,
    )

    add_power_sources(schematic)
    add_power_carrier_harnesses(schematic)
    add_audio_harnesses(schematic)
    add_display_harnesses(schematic)
    add_compute_external_io(schematic)
    add_balanced_audio_panel(schematic)
    add_detailed_sheets(schematic)
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
