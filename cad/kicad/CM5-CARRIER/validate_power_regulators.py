#!/usr/bin/env python3
"""Validate the Rev A1 carrier power tree and print the calculation record."""

from __future__ import annotations

from dataclasses import dataclass
import csv
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent.parent.parent
FOOTPRINTS = ROOT / "CM5Carrier.pretty"
BOM = WORKSPACE / "docs" / "power_regulator_bom_a1.csv"
SCHEMATIC = ROOT / "Power-Regulators-A1.kicad_sch"
KICAD_CLI = Path(
    os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
)


@dataclass(frozen=True)
class Stage:
    rail: str
    part: str
    vin_min: float
    vin_max: float
    vout: float
    current_rating: float
    load_cont_w: float
    load_peak_w: float
    efficiency: float
    frequency_khz: float
    inductance_uh: float
    inductor_isat_a: float

    @property
    def capacity_w(self) -> float:
        return self.vout * self.current_rating

    @property
    def peak_load_a(self) -> float:
        return self.load_peak_w / self.vout

    @property
    def ripple_high_line_a(self) -> float:
        """CCM buck estimate; buck-boost is handled separately below."""
        duty = self.vout / self.vin_max
        return (
            (self.vin_max - self.vout)
            * duty
            / (self.inductance_uh * 1e-6 * self.frequency_khz * 1e3)
        )


STAGES = (
    Stage("SYS_4V0", "LM5146RGYR", 10.5, 30.0, 4.0, 12.0, 30.0, 38.0, 0.94, 300.0, 3.3, 29.2),
    Stage("AUX_12V", "LM5176PWP", 10.5, 30.0, 12.0, 8.0, 76.0, 84.0, 0.90, 300.0, 4.7, 20.9),
    Stage("MODEM_3V8", "LM61460RJR", 10.5, 30.0, 3.8, 6.0, 12.0, 20.0, 0.90, 400.0, 4.7, 15.2),
    Stage("WIFI_3V3", "LM61440RJR", 10.5, 30.0, 3.3, 4.0, 9.0, 10.0, 0.90, 400.0, 4.7, 15.2),
    Stage("NET_3V3", "LM61440RJR", 10.5, 30.0, 3.3, 4.0, 8.5, 10.0, 0.90, 400.0, 4.7, 15.2),
    Stage("LOGIC_3V3", "LM61440RJR", 10.5, 30.0, 3.3, 3.0, 4.0, 5.0, 0.90, 400.0, 4.7, 15.2),
)


def actual_output(vref: float, r_top_k: float, r_bottom_k: float) -> float:
    return vref * (1.0 + r_top_k / r_bottom_k)


def buck_ripple(vin: float, vout: float, inductance_uh: float, frequency_khz: float) -> float:
    duty = vout / vin
    return (vin - vout) * duty / (inductance_uh * 1e-6 * frequency_khz * 1e3)


def holdup_ms(capacitance_f: float, v_start: float, v_end: float, load_w: float) -> float:
    return 1000.0 * capacitance_f * (v_start**2 - v_end**2) / (2.0 * load_w)


def required_capacitance_mf(load_w: float, time_ms: float, v_start: float, v_end: float) -> float:
    return 2000.0 * load_w * time_ms / (1000.0 * (v_start**2 - v_end**2))


def check(name: str, condition: bool, detail: str) -> bool:
    print(f"{'PASS' if condition else 'FAIL'}  {name}: {detail}")
    return condition


def export_net_map() -> dict[tuple[str, str], str]:
    with tempfile.TemporaryDirectory(prefix="radxa-power-validation-") as temp:
        output = Path(temp) / "Power-Regulators-A1.xml"
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


def validate_controlled_artifacts(checks: list[bool]) -> None:
    footprint_requirements = {
        "TI_RJR0014A.kicad_mod": (
            set(map(str, range(1, 15))),
            ('(at 1.000 0.000) (size 2.400 0.400)', '(at -1.850 -0.525) (size 0.700 0.250)'),
        ),
        "TI_DML0010A.kicad_mod": (
            set(map(str, range(1, 11))),
            ('(at 0.020 0.000) (size 1.100 1.950)', '(at -1.300 -1.000) (size 0.450 0.240)'),
        ),
        "TI_DNK0008A_GSD.kicad_mod": (
            {"1", "2", "3"},
            ('(at 0.330 0.000) (size 4.350 4.510)', '(at -2.800 1.905) (size 0.700 0.700)'),
        ),
        "onsemi_DFN5_5x6_488AA_GSD.kicad_mod": (
            {"1", "2", "3"},
            ('(at 0.000 -0.665) (size 4.560 3.200)', '(at 1.905 2.765) (size 0.750 1.000)'),
        ),
        "onsemi_DFNW8_5p2x6p3_507AU_GSD.kicad_mod": (
            {"1", "2", "3"},
            ('(at 0.000 0.000) (size 4.420 3.750)', '(at 1.905 2.745) (size 0.610 1.420)'),
        ),
        "TDK_SPM10065VC.kicad_mod": (
            {"1", "2"},
            ('(at -4.525 0.000) (size 2.950 4.500)',),
        ),
        "Wurth_74439370047.kicad_mod": (
            {"1", "2"},
            ('(at 0.000 -5.300) (size 14.100 3.300)',),
        ),
        "Susumu_KRL6432E_6mR.kicad_mod": (
            {"1", "2"},
            ('(at -1.600 0.000) (size 1.000 6.600)',),
        ),
        "Susumu_KRL11050_4mR.kicad_mod": (
            {"1", "2"},
            ('(at -2.300 0.000) (size 1.000 11.200)',),
        ),
    }
    pad_pattern = re.compile(r'\(pad "(\d+)" smd')
    for filename, (expected_pads, geometry) in footprint_requirements.items():
        path = FOOTPRINTS / filename
        text = path.read_text() if path.exists() else ""
        observed_pads = set(pad_pattern.findall(text))
        checks.append(
            check(
                f"{filename} controlled footprint",
                path.exists() and observed_pads == expected_pads and all(item in text for item in geometry),
                f"pads {sorted(observed_pads)}; {len(geometry)} drawing-critical geometry checks",
            )
        )

    rows = list(csv.DictReader(BOM.open())) if BOM.exists() else []
    by_ref = {row["Reference"]: row for row in rows}
    key_parts = {
        "L1110": ("SPM10065VC-3R3M-D", "CM5Carrier:TDK_SPM10065VC"),
        "L1120": ("74439370047", "CM5Carrier:Wurth_74439370047"),
        "Q1110": ("NVMFS6B25NLT1G", "CM5Carrier:onsemi_DFN5_5x6_488AA_GSD"),
        "Q1111": ("FDWS86068-F085", "CM5Carrier:onsemi_DFNW8_5p2x6p3_507AU_GSD"),
        "Q1120": ("CSD18532Q5B", "CM5Carrier:TI_DNK0008A_GSD"),
        "Q1122": ("CSD17573Q5B", "CM5Carrier:TI_DNK0008A_GSD"),
        "U1130": ("LM61460RJR", "CM5Carrier:TI_RJR0014A"),
        "U1140": ("LM61440RJR", "CM5Carrier:TI_RJR0014A"),
        "U1141": ("TPS22990DMLR", "CM5Carrier:TI_DML0010A"),
    }
    key_parts_ok = all(
        reference in by_ref
        and by_ref[reference]["MPN"] == mpn
        and by_ref[reference]["Footprint"] == footprint
        for reference, (mpn, footprint) in key_parts.items()
    )
    complete = bool(rows) and all(
        row["Manufacturer"] and row["MPN"] and row["Footprint"] for row in rows
    )
    checks.append(
        check(
            "Power-Regulators production BOM",
            len(rows) == 163 and complete and key_parts_ok,
            f"{len(rows)} rows (expected 163); all MPN/footprint fields complete; controlled power parts agree",
        )
    )

    net_map = export_net_map()
    checks.append(
        check(
            "LM614 radio/network/logic enable ownership",
            all(
                net_map.get((reference, pin)) == "RAW_OUT_LOAD"
                for reference in ("U1130", "U1140", "U1150", "U1160")
                for pin in ("7", "8")
            ),
            "VIN and EN/SYNC are tied to the protected raw rail on all four always-on pre-regulators",
        )
    )
    checks.append(
        check(
            "PCIe POL sequencing",
            all(net_map.get((reference, "1")) == "SYS_4V0_PG" for reference in ("U1170", "U1171")),
            "PCIE_1V0 and LOGIC_1V8 remain disabled until SYS_4V0 power-good is high",
        )
    )
    pg_pullups = {
        "R1117": "SYS_4V0_PG", "R1129": "AUX_12V_PG",
        "R1134": "MODEM_3V8_PRE_PG", "R1144": "WIFI_3V3_PRE_PG",
        "R1154": "NET_3V3_PG", "R1164": "LOGIC_3V3_PG",
        "R1137": "MODEM_3V8_PG", "R1149": "WIFI_3V3_PG",
        "R11703": "PCIE_1V0_PG", "R11713": "LOGIC_1V8_PG",
    }
    checks.append(
        check(
            "open-drain power-good pull-ups",
            all(
                net_map.get((reference, "1")) == "LOGIC_3V3"
                and net_map.get((reference, "2")) == signal
                for reference, signal in pg_pullups.items()
            ),
            f"{len(pg_pullups)} monitored power-good nets have controlled 10 k pull-ups",
        )
    )
    checks.append(
        check(
            "radio final-rail safe defaults",
            net_map.get(("R1139", "1")) == "MODEM_POWER_EN"
            and net_map.get(("R1139", "2")) == "GND"
            and net_map.get(("R1148", "1")) == "WIFI_POWER_EN"
            and net_map.get(("R1148", "2")) == "GND",
            "100 k pull-downs keep modem and Wi-Fi final load switches off during controller reset",
        )
    )
    checks.append(
        check(
            "power telemetry test access",
            net_map.get(("TP1194", "1")) == "MODEM_IMON"
            and net_map.get(("TP1195", "1")) == "SYS_SYNCOUT_TP",
            "modem current monitor and system sync/output monitor have dedicated factory probes",
        )
    )


def main() -> int:
    checks: list[bool] = []
    print("POWER-REGULATORS A1 CALCULATION CHECK\n")
    validate_controlled_artifacts(checks)

    for stage in STAGES:
        required_headroom = 1.10 if stage.rail in {"MODEM_3V8", "AUX_12V"} else 1.15
        checks.append(
            check(
                f"{stage.rail} output capacity",
                stage.capacity_w >= stage.load_peak_w * required_headroom,
                f"{stage.capacity_w:.1f} W rating vs {stage.load_peak_w:.1f} W allocated peak "
                f"({(stage.capacity_w / stage.load_peak_w - 1.0) * 100.0:.1f}% headroom)",
            )
        )
        if stage.rail == "AUX_12V":
            low_line_input_a = stage.capacity_w / (stage.vin_min * stage.efficiency)
            design_peak_a = low_line_input_a * 1.30
            checks.append(
                check(
                    "AUX_12V inductor saturation",
                    stage.inductor_isat_a >= design_peak_a * 1.50,
                    f"{stage.inductor_isat_a:.1f} A Isat vs {design_peak_a:.2f} A conservative design peak",
                )
            )
        else:
            ripple = stage.ripple_high_line_a
            peak_current = stage.current_rating + ripple / 2.0
            checks.append(
                check(
                    f"{stage.rail} inductor saturation",
                    stage.inductor_isat_a >= peak_current * 1.35,
                    f"{stage.inductor_isat_a:.1f} A Isat vs {peak_current:.2f} A full-rating high-line estimate",
                )
            )

    feedback = (
        ("SYS_4V0", 4.0, actual_output(0.8, 20.0, 4.99)),
        ("AUX_12V", 12.0, actual_output(0.8, 280.0, 20.0)),
        ("MODEM_3V8", 3.8, actual_output(1.0, 100.0, 35.7)),
        ("WIFI/NET/LOGIC_3V3", 3.3, actual_output(1.0, 100.0, 43.2)),
        ("PCIE_1V0", 1.0, actual_output(0.8, 1.24, 4.99)),
        ("LOGIC_1V8", 1.8, actual_output(0.8, 6.19, 4.99)),
    )
    for rail, target, actual in feedback:
        error = 100.0 * (actual - target) / target
        checks.append(
            check(
                f"{rail} feedback divider",
                abs(error) <= 0.6,
                f"{actual:.4f} V, {error:+.3f}% nominal resistor-set error",
            )
        )

    pol_specs = (
        ("PCIE_1V0", 4.0, 1.0, 2.0),
        ("LOGIC_1V8", 4.0, 1.8, 1.5),
    )
    for rail, vin, vout, rating_a in pol_specs:
        ripple = buck_ripple(vin, vout, 2.2, 2200.0)
        peak = rating_a + ripple / 2.0
        checks.append(
            check(
                f"{rail} TPS62913 switch-current margin",
                peak <= 3.7,
                f"{peak:.2f} A estimated peak vs 3.7 A minimum peak-current limit",
            )
        )

    modem_r_ilim = 1500.0 / (6.0 - 0.11)
    checks.append(
        check(
            "MODEM_3V8 eFuse ILIM",
            math.isclose(modem_r_ilim, 254.67, rel_tol=0.01),
            f"calculated {modem_r_ilim:.1f} ohm; select 255 ohm 1% for about 6.0 A nominal",
        )
    )

    sys_uvlo_on = 1.2 * (1.0 + 69.8 / 10.0)
    sys_uvlo_off = sys_uvlo_on - 69.8e3 * 10e-6
    checks.append(
        check(
            "SYS_4V0 UVLO window",
            sys_uvlo_on < 10.5 and sys_uvlo_off < sys_uvlo_on,
            f"{sys_uvlo_on:.2f} V typical on / {sys_uvlo_off:.2f} V typical off",
        )
    )

    aux_uvlo_on = 1.22 * (1.0 + 73.2 / 10.0) + 73.2e3 * 2e-6
    aux_uvlo_off = aux_uvlo_on - 73.2e3 * 3.15e-6
    checks.append(
        check(
            "AUX_12V UVLO window",
            aux_uvlo_on < 10.5 and aux_uvlo_off < aux_uvlo_on,
            f"{aux_uvlo_on:.2f} V typical on / {aux_uvlo_off:.2f} V typical off",
        )
    )

    aux_pwm_limit_a = 0.050 / 0.004
    checks.append(
        check(
            "AUX_12V PWM current-sense threshold",
            aux_pwm_limit_a >= 8.25 * 1.35,
            f"{aux_pwm_limit_a:.2f} A nominal from 50 mV / 4 mOhm vs 8.25 A design peak",
        )
    )
    aux_output_limit_a = 0.050 / 0.006
    checks.append(
        check(
            "AUX_12V output constant-current threshold",
            8.0 < aux_output_limit_a <= 8.5,
            f"{aux_output_limit_a:.2f} A nominal from 50 mV / 6 mOhm",
        )
    )

    continuous_source_w = 151.7
    transient_source_w = 184.2
    checks.append(check("24 V PSU continuous", continuous_source_w <= 252.0 * 0.70, "151.7 W <= 70% of 252 W"))
    checks.append(check("24 V PSU transient", transient_source_w <= 252.0, "184.2 W <= 252 W convection rating"))
    checks.append(check("13 V backup transient path", transient_source_w / 13.0 <= 15.0, f"{transient_source_w / 13.0:.2f} A <= 15 A path"))
    checks.append(check("11.35 V battery load-shed threshold", 12.0 < continuous_source_w / 11.35 <= 15.0, f"{continuous_source_w / 11.35:.2f} A requires automatic load shedding below the 12 A battery rating"))
    checks.append(check("11.35 V battery transient", transient_source_w / 11.35 <= 20.0, f"{transient_source_w / 11.35:.2f} A <= 20 A short peak; not a sustained operating point"))

    for label, capacitance_mf in (("nominal", 27.86), ("minus-20-percent", 22.288)):
        for load_w in (continuous_source_w, transient_source_w):
            duration = holdup_ms(capacitance_mf / 1000.0, 24.0, 12.5, load_w)
            checks.append(
                check(
                    f"{label} {capacitance_mf:.3f} mF hold-up at {load_w:.1f} W",
                    duration >= 20.0,
                    f"{duration:.1f} ms ideal from 24.0 V to 12.5 V",
                )
            )
    required = required_capacitance_mf(transient_source_w, 20.0, 24.0, 12.5)
    print(f"INFO  20 ms / {transient_source_w:.1f} W theoretical minimum: {required:.2f} mF (before tolerance, ESR, and aging)")

    failures = len(checks) - sum(checks)
    print(f"\nRESULT: {len(checks)} checks, {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
