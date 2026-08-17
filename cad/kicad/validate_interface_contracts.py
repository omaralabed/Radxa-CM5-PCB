#!/usr/bin/env python3
"""Validate the A0 inter-board pin contracts exported from KiCad."""

from __future__ import annotations

from pathlib import Path
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
NETLISTS = {
    "power": ROOT / "PWR-SELECT" / "REVIEW" / "PowerSelector-A0.xml",
    "carrier": ROOT / "CM5-CARRIER" / "REVIEW" / "CM5-Carrier-A1.xml",
    "thermal": ROOT / "CM5-CARRIER" / "REVIEW" / "Thermal-IO-A1.xml",
    "audio": ROOT / "AUDIO-8X8" / "REVIEW" / "Audio-8x8-A1.xml",
}

TDM_MAP = {
    "1": "AUD_MCLK_P",
    "2": "AUD_MCLK_N",
    "3": "GND",
    "4": "GND",
    "5": "AUD_BCLK_P",
    "6": "AUD_BCLK_N",
    "7": "AUD_FSYNC_P",
    "8": "AUD_FSYNC_N",
    "9": "GND",
    "10": "GND",
    "11": "AUD_DAC_SDIN_P",
    "12": "AUD_DAC_SDIN_N",
    "13": "AUD_ADC_SDOUT_P",
    "14": "AUD_ADC_SDOUT_N",
    "15": "GND",
    "16": "GND",
    "17": "AUD_I2C_SCL",
    "18": "AUD_I2C_SDA",
    "19": "AUD_ADC_RST_N",
    "20": "AUD_DAC_RST_N",
    "21": "AUD_DAC_MUTE_CMD_N",
    "22": "AUD_IRQ_N",
    "23": "AUDIO_PRESENT_N",
    "24": "AUDIO_ENABLE",
    "25": "LOGIC_3V3",
    "26": "GND",
    "27": "TDM_SPARE_1",
    "28": "TDM_SPARE_2",
    "29": "GND",
    "30": "GND",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def load_netlist(path: Path):
    if not path.exists():
        fail(f"missing exported netlist: {path}")
    root = ET.parse(path).getroot()
    components = {comp.get("ref"): comp for comp in root.findall("./components/comp")}
    pins: dict[tuple[str, str], str] = {}
    for net in root.findall("./nets/net"):
        net_name = net.get("name", "").lstrip("/")
        for node in net.findall("node"):
            pins[(node.get("ref", ""), node.get("pin", ""))] = net_name
    return components, pins


def assert_pin_map(label: str, pins: dict[tuple[str, str], str], ref: str, expected: dict[str, str]) -> None:
    mismatches = []
    for pin, wanted in expected.items():
        actual = pins.get((ref, pin))
        if actual != wanted:
            mismatches.append(f"{ref}.{pin}: wanted {wanted}, got {actual}")
    if mismatches:
        fail(f"{label} pin map mismatch:\n  " + "\n  ".join(mismatches))


power_components, power_pins = load_netlist(NETLISTS["power"])
carrier_components, carrier_pins = load_netlist(NETLISTS["carrier"])
thermal_components, thermal_pins = load_netlist(NETLISTS["thermal"])
audio_components, audio_pins = load_netlist(NETLISTS["audio"])

raw_power_map = {"1": "RAW_OUT_LOAD", "2": "RAW_OUT_LOAD", "3": "GND", "4": "GND"}
status_map = {
    "1": "GND",
    "2": "CH_24V_N",
    "3": "CH_BAT_N",
    "4": "VALID_24V_N",
    "5": "VALID_BAT_N",
    "6": "BAT_LOW_N",
    "7": "VALID_DTAP_N",
    "8": "VALID_GOLD_N",
}
carrier_audio_power_map = {"1": "AUDIO_12V", "2": "AUDIO_12V", "3": "GND", "4": "GND"}
audio_board_power_map = {"1": "AUDIO_12V_IN", "2": "AUDIO_12V_IN", "3": "GND", "4": "GND"}
power_telemetry_selector_map = {
    "1": "MON_3V3",
    "2": "GND",
    "3": "PWR_MON_SDA",
    "4": "PWR_MON_SCL",
    "5": "PWR_MON_ALERT_N",
    "6": "GND",
}
power_telemetry_carrier_map = {
    "1": "LOGIC_3V3",
    "2": "GND",
    "3": "CTRL_I2C_SDA",
    "4": "CTRL_I2C_SCL",
    "5": "PWR_MON_ALERT_N",
    "6": "GND",
}

assert_pin_map("PWR-SELECT raw power", power_pins, "J301", raw_power_map)
assert_pin_map("CM5-CARRIER raw power", carrier_pins, "J101", raw_power_map)
assert_pin_map("PWR-SELECT status", power_pins, "J401", status_map)
assert_pin_map("CM5-CARRIER status", carrier_pins, "J102", status_map)
assert_pin_map("PWR-SELECT telemetry", power_pins, "J402", power_telemetry_selector_map)
assert_pin_map("CM5-CARRIER telemetry", carrier_pins, "J103", power_telemetry_carrier_map)
assert_pin_map(
    "Thermal-IO alert allocation",
    thermal_pins,
    "U1001",
    {"9": "FAN_ALERT_N", "10": "TEMP_ALERT_N", "11": "PWR_MON_ALERT_N"},
)
for sensor_ref in ("U1050", "U1051", "U1052"):
    assert_pin_map(f"{sensor_ref} shared alert", thermal_pins, sensor_ref, {"3": "TEMP_ALERT_N"})
assert_pin_map("CM5-CARRIER TDM/control", carrier_pins, "J201", TDM_MAP)
assert_pin_map("AUDIO-8X8 TDM/control", audio_pins, "J101", TDM_MAP)
assert_pin_map("CM5-CARRIER audio power", carrier_pins, "J202", carrier_audio_power_map)
assert_pin_map("AUDIO-8X8 audio power", audio_pins, "J102", audio_board_power_map)

fan_maps = {
    "J401": {"1": "GND", "2": "CPU_FAN_12V", "3": "CPU_FAN_TACH", "4": "CPU_FAN_PWM"},
    "J402": {"1": "GND", "2": "MODEM_FAN_12V", "3": "MODEM_FAN_TACH", "4": "MODEM_FAN_PWM"},
    "J403": {"1": "GND", "2": "INTAKE_FAN_12V", "3": "INTAKE_FAN_TACH", "4": "INTAKE_FAN_PWM"},
    "J404": {"1": "GND", "2": "EXHAUST_FAN_12V", "3": "EXHAUST_FAN_TACH", "4": "EXHAUST_FAN_PWM"},
}
for ref, expected in fan_maps.items():
    assert_pin_map(f"CM5-CARRIER fan {ref}", carrier_pins, ref, expected)

expected_fan_values = {
    "J401": "CPU_FAN",
    "J402": "MODEM_FAN",
    "J403": "THA0412AD-TZW3_INTAKE",
    "J404": "THA0412AD-TZW3_EXHAUST",
}
for ref, wanted in expected_fan_values.items():
    component = carrier_components.get(ref)
    actual = component.findtext("value") if component is not None else None
    if actual != wanted:
        fail(f"{ref} fan identity: wanted {wanted}, got {actual}")

for channel in range(1, 9):
    output_ref = f"J{200 + channel}"
    input_ref = f"J{300 + channel}"
    assert_pin_map(
        f"channel {channel} output",
        audio_pins,
        output_ref,
        {"1": "XLR_CHASSIS", "2": f"AOUT_CH{channel}_HOT", "3": f"AOUT_CH{channel}_COLD"},
    )
    assert_pin_map(
        f"channel {channel} input",
        audio_pins,
        input_ref,
        {"1": "XLR_CHASSIS", "2": f"AIN_CH{channel}_HOT", "3": f"AIN_CH{channel}_COLD"},
    )
    for ref, part in ((output_ref, "NC3MAV"), (input_ref, "NC3FAV")):
        component = audio_components.get(ref)
        libsource = component.find("libsource") if component is not None else None
        actual = libsource.get("part") if libsource is not None else None
        if actual != part:
            fail(f"{ref} connector type: wanted {part}, got {actual}")

print("PASS: PWR-SELECT raw-power, status, and telemetry interfaces match CM5-CARRIER")
print("PASS: fan, temperature, and power-monitor alerts are allocated on TCA9535 U1001")
print("PASS: CM5-CARRIER 30-pin buffered TDM/control interface matches AUDIO-8X8")
print("PASS: separate audio-power harness maps carrier AUDIO_12V to fused AUDIO_12V_IN entry")
print("PASS: four independent fan headers include dedicated intake and exhaust channels")
print("PASS: eight NC3MAV outputs and eight NC3FAV inputs have correct channel pin maps")
print("PASS: 174 critical connector and control pin/net assignments checked")
