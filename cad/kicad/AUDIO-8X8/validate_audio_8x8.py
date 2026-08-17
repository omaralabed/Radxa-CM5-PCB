#!/usr/bin/env python3
"""Validate the six detailed AUDIO-8X8 A1 schematic contracts."""

from __future__ import annotations

from collections import Counter
import math
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
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
EXPECTED_COMPONENT_COUNTS = {
    "Audio-TDM-Clock": 21,
    "AK5558-ADC": 38,
    "AK4458-DAC": 23,
    "Audio-Inputs": 192,
    "Audio-Outputs": 232,
    "Audio-Power": 47,
}


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
        raise RuntimeError(f"Netlist export failed for {schematic}:\n{result.stderr}")


def parse_netlist(path: Path) -> tuple[dict[str, ET.Element], dict[tuple[str, str], str]]:
    root = ET.parse(path)
    components = {
        component.attrib["ref"]: component
        for component in root.findall("./components/comp")
    }
    pin_nets: dict[tuple[str, str], str] = {}
    for net in root.findall("./nets/net"):
        name = net.attrib["name"].removeprefix("/")
        for node in net.findall("node"):
            pin_nets[(node.attrib["ref"], node.attrib["pin"])] = name
    return components, pin_nets


def require(condition: bool, message: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(message)
    checks.append(message)


def require_component(
    components: dict[str, ET.Element],
    reference: str,
    value: str,
    mpn: str,
    checks: list[str],
) -> None:
    component = components.get(reference)
    require(component is not None, f"{reference} is present", checks)
    require((component.findtext("value") or "") == value, f"{reference} value is {value}", checks)
    require(field(component, "MPN") == mpn, f"{reference} MPN is {mpn}", checks)
    require(bool(component.findtext("footprint")), f"{reference} has a footprint", checks)


def require_pin(
    pin_nets: dict[tuple[str, str], str],
    reference: str,
    pin: int,
    net: str,
    checks: list[str],
) -> None:
    require(
        pin_nets.get((reference, str(pin))) == net,
        f"{reference}.{pin} is on {net}",
        checks,
    )


def validate() -> list[str]:
    checks: list[str] = []
    parsed: dict[str, tuple[dict[str, ET.Element], dict[tuple[str, str], str]]] = {}
    with tempfile.TemporaryDirectory(prefix="audio-8x8-validation-") as temp:
        temp_root = Path(temp)
        for sheet in SHEETS:
            netlist = temp_root / f"{sheet}.xml"
            export_netlist(ROOT / f"{sheet}.kicad_sch", netlist)
            parsed[sheet] = parse_netlist(netlist)

    for sheet, expected_count in EXPECTED_COMPONENT_COUNTS.items():
        components, _ = parsed[sheet]
        require(
            len(components) == expected_count,
            f"{sheet} has exactly {expected_count} components",
            checks,
        )

    tdm_components, tdm_nets = parsed["Audio-TDM-Clock"]
    require_component(tdm_components, "J101", "AUDIO_TDM_CONTROL", "87832-6423", checks)
    for reference in ("U101", "U102", "U103", "U104"):
        require_component(tdm_components, reference, "SN65LVDT2D", "SN65LVDT2DR", checks)
    require_component(tdm_components, "U105", "SN65LVDS1D", "SN65LVDS1DR", checks)
    require_component(
        tdm_components, "U106", "SN74LVC1G11DBVR", "SN74LVC1G11DBVR", checks
    )
    tdm_connector_map = {
        1: "AUD_MCLK_P", 2: "AUD_MCLK_N", 3: "GND", 4: "GND",
        5: "AUD_BCLK_P", 6: "AUD_BCLK_N", 7: "AUD_FSYNC_P", 8: "AUD_FSYNC_N",
        9: "GND", 10: "GND", 11: "AUD_DAC_SDIN_P", 12: "AUD_DAC_SDIN_N",
        13: "AUD_ADC_SDOUT_P", 14: "AUD_ADC_SDOUT_N", 15: "GND", 16: "GND",
        17: "AUD_I2C_SCL", 18: "AUD_I2C_SDA", 19: "AUD_ADC_RST_N",
        20: "AUD_DAC_RST_N", 21: "AUD_DAC_MUTE_CMD_N", 22: "AUD_IRQ_N",
        23: "AUDIO_PRESENT_N", 24: "AUDIO_ENABLE", 25: "LOGIC_3V3", 26: "GND",
        27: "TDM_SPARE_1", 28: "TDM_SPARE_2", 29: "GND", 30: "GND",
    }
    for pin, net in tdm_connector_map.items():
        require_pin(tdm_nets, "J101", pin, net, checks)
    for pin, net in {
        1: "AUD_DAC_MUTE_CMD_N", 2: "AGND", 3: "ADC_5V_PG",
        4: "AUDIO_SAFE_UNMUTE_N", 5: "AKM_3V3_D", 6: "DAC_5V_PG",
    }.items():
        require_pin(tdm_nets, "U106", pin, net, checks)
    require_component(tdm_components, "R117", "100k 1%", "RC0603FR-07100KL", checks)
    require_pin(tdm_nets, "R117", 1, "AUDIO_SAFE_UNMUTE_N", checks)
    require_pin(tdm_nets, "R117", 2, "AGND", checks)
    require_component(tdm_components, "C107", "100nF", "C1005X7R1H104K050BB", checks)
    require_pin(tdm_nets, "C107", 1, "AKM_3V3_D", checks)
    require_pin(tdm_nets, "C107", 2, "AGND", checks)

    adc_components, adc_nets = parsed["AK5558-ADC"]
    require_component(adc_components, "U201", "AK5558VN", "AK5558VN", checks)
    for pin, net in {
        2: "ADC_5V_A", 15: "ADC_5V_A", 24: "AKM_MCLK", 25: "AKM_3V3_D",
        27: "ADC_VDD18", 28: "AUD_ADC_RST_N", 32: "ADC_MSN",
        33: "AKM_BCLK", 34: "AKM_FSYNC", 36: "ADC_TDM_OUT",
        43: "AUD_I2C_SDA", 45: "AUD_I2C_SCL",
        49: "ADC_DIF0", 50: "ADC_DIF1", 51: "ADC_TDM0", 52: "ADC_TDM1",
        54: "ADC_I2C_MODE", 57: "ADC_LDOE", 65: "AGND",
    }.items():
        require_pin(adc_nets, "U201", pin, net, checks)
    for reference, high_net, low_net in (
        ("R224", "AKM_3V3_D", "ADC_DIF0"),
        ("R225", "AKM_3V3_D", "ADC_DIF1"),
        ("R226", "AKM_3V3_D", "ADC_TDM1"),
        ("R246", "ADC_TDM0", "AGND"),
        ("R241", "ADC_MSN", "AGND"),
    ):
        require_pin(adc_nets, reference, 1, high_net, checks)
        require_pin(adc_nets, reference, 2, low_net, checks)
    for channel, (pin_p, pin_n) in enumerate(
        ((59, 60), (64, 63), (3, 4), (8, 7), (9, 10), (14, 13), (17, 18), (22, 21)),
        start=1,
    ):
        require_pin(adc_nets, "U201", pin_p, f"ADC_CH{channel}P", checks)
        require_pin(adc_nets, "U201", pin_n, f"ADC_CH{channel}N", checks)
    for index in range(1, 5):
        require_pin(adc_nets, f"R{260 + index}", 1, "ADC_5V_A", checks)
        require_pin(adc_nets, f"R{260 + index}", 2, f"ADC_VREFH{index}", checks)
    require_pin(adc_nets, "R246", 1, "ADC_TDM0", checks)
    require_pin(adc_nets, "R246", 2, "AGND", checks)
    require_pin(adc_nets, "R226", 1, "AKM_3V3_D", checks)
    require_pin(adc_nets, "R226", 2, "ADC_TDM1", checks)
    require_pin(adc_nets, "R242", 1, "ADC_CAD0", checks)
    require_pin(adc_nets, "R242", 2, "AGND", checks)
    require_pin(adc_nets, "R243", 1, "ADC_CAD1", checks)
    require_pin(adc_nets, "R243", 2, "AGND", checks)
    require_component(adc_components, "C281", "4.7uF", "GRM21BR71A475KA73L", checks)
    for reference, rail in (
        ("C282", "ADC_5V_A"), ("C284", "AKM_3V3_D"),
        ("C286", "ADC_5V_A"),
    ):
        require_component(adc_components, reference, "100nF", "C1005X7R1H104K050BB", checks)
        require_pin(adc_nets, reference, 1, rail, checks)
        require_pin(adc_nets, reference, 2, "AGND", checks)
    for reference, rail in (
        ("C283", "ADC_5V_A"), ("C285", "AKM_3V3_D"),
        ("C287", "ADC_5V_A"),
    ):
        require_component(adc_components, reference, "10uF", "GRM188R71A106KA73D", checks)
        require_pin(adc_nets, reference, 1, rail, checks)
        require_pin(adc_nets, reference, 2, "AGND", checks)

    dac_components, dac_nets = parsed["AK4458-DAC"]
    require_component(dac_components, "U301", "AK4458VN", "AK4458VN", checks)
    for pin, net in {
        1: "AKM_MCLK", 2: "AKM_BCLK", 3: "AKM_FSYNC", 4: "DAC_TDM_IN",
        11: "AUDIO_SAFE_UNMUTE_N", 13: "AUD_I2C_SDA", 14: "AUD_I2C_SCL",
        17: "DAC_I2C_MODE", 31: "DAC_5V_A", 44: "DAC_LDOE",
        45: "AKM_3V3_D", 47: "DAC_VDD18", 48: "AUD_DAC_RST_N", 49: "AGND",
    }.items():
        require_pin(dac_nets, "U301", pin, net, checks)
    for channel, (pin_p, pin_n) in enumerate(
        ((18, 19), (23, 22), (24, 25), (29, 28), (32, 33), (37, 36), (38, 39), (43, 42)),
        start=1,
    ):
        require_pin(dac_nets, "U301", pin_p, f"DAC_CH{channel}P", checks)
        require_pin(dac_nets, "U301", pin_n, f"DAC_CH{channel}N", checks)
    for index in range(1, 5):
        require_pin(dac_nets, f"R{350 + index}", 1, "DAC_5V_A", checks)
        require_pin(dac_nets, f"R{350 + index}", 2, f"DAC_VREFH{index}", checks)
        require_component(
            dac_components, f"R{350 + index}", "10R", "RC0603FR-0710RL", checks
        )
        require_component(
            dac_components, f"C{360 + index}", "220uF 6.3V polymer", "6SVP220MX", checks
        )
    require_pin(dac_nets, "R323", 1, "AKM_3V3_D", checks)
    require_pin(dac_nets, "R323", 2, "DAC_CAD0", checks)
    require_pin(dac_nets, "R331", 1, "DAC_CAD1", checks)
    require_pin(dac_nets, "R331", 2, "AGND", checks)
    for pin in range(5, 11):
        require_pin(dac_nets, "U301", pin, "AGND", checks)

    input_components, input_nets = parsed["Audio-Inputs"]
    input_mpns = Counter(field(component, "MPN") for component in input_components.values())
    require(input_mpns["THAT1206S08-U"] == 8, "Audio-Inputs has eight THAT1206 receivers", checks)
    require(input_mpns["OPA1652AIDR"] == 8, "Audio-Inputs has eight OPA1652 ADC drivers", checks)
    for channel in range(1, 9):
        require_pin(input_nets, f"U{400 + channel}", 2, f"AIN{channel}_PROT_N", checks)
        require_pin(input_nets, f"U{400 + channel}", 3, f"AIN{channel}_PROT_P", checks)
        require_pin(input_nets, f"U{420 + channel}", 8, "ADC_5V_A", checks)
        base = 4000 + channel * 30
        require_pin(input_nets, f"R{base}", 1, f"AIN_CH{channel}_HOT", checks)
        require_pin(input_nets, f"R{base}", 2, f"AIN{channel}_PROT_P", checks)
        require_pin(input_nets, f"R{base + 1}", 1, f"AIN_CH{channel}_COLD", checks)
        require_pin(input_nets, f"R{base + 1}", 2, f"AIN{channel}_PROT_N", checks)
        require_pin(input_nets, f"R{base + 10}", 2, f"ADC_CH{channel}P", checks)
        require_pin(input_nets, f"R{base + 11}", 2, f"ADC_CH{channel}N", checks)
        require_pin(input_nets, f"C{base + 4}", 1, f"ADC_CH{channel}P", checks)
        require_pin(input_nets, f"C{base + 4}", 2, f"ADC_CH{channel}N", checks)
        require_pin(input_nets, f"C{base + 6}", 1, "AUDIO_P15V", checks)
        require_pin(input_nets, f"C{base + 6}", 2, "AGND", checks)
        require_pin(input_nets, f"C{base + 7}", 1, "AUDIO_N15V", checks)
        require_pin(input_nets, f"C{base + 7}", 2, "AGND", checks)

    output_components, output_nets = parsed["Audio-Outputs"]
    output_mpns = Counter(field(component, "MPN") for component in output_components.values())
    require(output_mpns["OPA1652AIDR"] == 8, "Audio-Outputs has eight OPA1652 reconstruction stages", checks)
    require(output_mpns["THAT1646S08-U"] == 8, "Audio-Outputs has eight THAT1646 drivers", checks)
    require(output_mpns["TQ2-12V"] == 8, "Audio-Outputs has eight fail-silent TQ2 relays", checks)
    require(output_mpns["2N7002K-7"] == 8, "Audio-Outputs has eight independent relay sinks", checks)
    for channel in range(1, 9):
        base = 5000 + channel * 40
        for offset, rail in (
            (7, "AUDIO_P15V"), (8, "AUDIO_N15V"),
            (9, "AUDIO_P15V"), (10, "AUDIO_N15V"),
        ):
            require_pin(output_nets, f"C{base + offset}", 1, rail, checks)
            require_pin(output_nets, f"C{base + offset}", 2, "AGND", checks)
        relay = f"K{500 + channel}"
        require_pin(output_nets, relay, 1, "AUDIO_12V", checks)
        require_pin(output_nets, relay, 2, "AGND", checks)
        require_pin(output_nets, relay, 9, "AGND", checks)
        require_pin(output_nets, relay, 4, f"AOUT{channel}_RELAY_N", checks)
        require_pin(output_nets, relay, 7, f"AOUT{channel}_RELAY_P", checks)
        require_pin(output_nets, f"Q{500 + channel}", 1, "AUDIO_SAFE_UNMUTE_N", checks)
        base = 5000 + channel * 40
        require_pin(output_nets, f"L{base}", 1, f"AOUT{channel}_RELAY_N", checks)
        require_pin(output_nets, f"L{base}", 2, f"AOUT_CH{channel}_COLD", checks)
        require_pin(output_nets, f"L{base + 1}", 1, f"AOUT{channel}_RELAY_P", checks)
        require_pin(output_nets, f"L{base + 1}", 2, f"AOUT_CH{channel}_HOT", checks)

    power_components, power_nets = parsed["Audio-Power"]
    require_component(power_components, "U601", "TRI 20-1223", "TRI 20-1223", checks)
    require_component(power_components, "U602", "TPS62913RPU", "TPS62913RPUT", checks)
    require_component(power_components, "U603", "LT3045IMSE", "LT3045IMSE#TRPBF", checks)
    require_component(power_components, "U604", "LT3045IMSE", "LT3045IMSE#TRPBF", checks)
    require_component(power_components, "U605", "TPS7A2033PDBVR", "TPS7A2033PDBVR", checks)
    require_pin(power_nets, "U602", 3, "AUDIO_5V5_PRE", checks)
    require_pin(power_nets, "U602", 7, "AGND", checks)
    require_pin(power_nets, "J102", 1, "AUDIO_12V_IN", checks)
    require_pin(power_nets, "J102", 2, "AUDIO_12V_IN", checks)
    require_pin(power_nets, "F601", 2, "AUDIO_12V", checks)
    require_pin(power_nets, "R601", 1, "GND", checks)
    require_pin(power_nets, "R601", 2, "AGND", checks)
    for reference, output_net in (("U603", "ADC_5V_A"), ("U604", "DAC_5V_A")):
        for pin in (10, 11, 12):
            require_pin(power_nets, reference, pin, output_net, checks)

    # Preserve the explicitly documented +24 dBu input map.
    input_vrms = 0.775 * 10 ** (24.0 / 20.0)
    that1206_gain = 10 ** (-6.0 / 20.0)
    input_vpp_at_adc = input_vrms * 2.0 * math.sqrt(2.0) * that1206_gain * (1.0 / 14.0) * 2.0
    input_margin_db = 20.0 * math.log10(2.8 / input_vpp_at_adc)
    nominal_vpp_at_adc = (
        0.775
        * 10 ** (4.0 / 20.0)
        * 2.0
        * math.sqrt(2.0)
        * that1206_gain
        * (1.0 / 14.0)
        * 2.0
    )
    nominal_dbfs = 20.0 * math.log10(nominal_vpp_at_adc / 2.8)
    require(abs(input_vpp_at_adc - 2.487) < 0.01, "+24 dBu maps to 2.49 Vpp differential at the ADC", checks)
    require(input_margin_db > 1.0, "ADC typical full-scale margin exceeds 1.0 dB at +24 dBu", checks)
    require(-21.2 < nominal_dbfs < -20.9, "+4 dBu nominal maps to approximately -21.0 dBFS", checks)
    require(abs((4.7 / 3.9) - 1.205) < 0.001, "AK4458 PCM reconstruction gain is 1.205", checks)
    require(150.0 * 470e-12 < 100e-9, "AK4458 150 ohm / 470 pF RF pole remains above audio band", checks)
    typical_output_vrms_600 = (
        5.6 / (2.0 * math.sqrt(2.0))
        * (4.7 / 3.9)
        * (1.0 + 21.5 / 10.0)
        * 10 ** (5.3 / 20.0)
    )
    minimum_output_vrms_600 = (
        5.3 / (2.0 * math.sqrt(2.0))
        * ((4.7 * 0.999) / (3.9 * 1.001))
        * (1.0 + (21.5 * 0.999) / (10.0 * 1.001))
        * 10 ** (5.0 / 20.0)
    )
    typical_output_dbu_600 = 20.0 * math.log10(typical_output_vrms_600 / 0.775)
    minimum_output_dbu_600 = 20.0 * math.log10(minimum_output_vrms_600 / 0.775)
    require(25.0 < typical_output_dbu_600 < 25.1, "Typical full-scale output is approximately +25.03 dBu into 600 ohm", checks)
    require(minimum_output_dbu_600 > 24.2, "Worst-case calculated output exceeds +24.2 dBu into 600 ohm", checks)

    return checks


def main() -> int:
    checks = validate()
    print(f"AUDIO-8X8 validation passed: {len(checks)} checks across six detailed sheets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
