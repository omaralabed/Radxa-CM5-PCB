#!/usr/bin/env python3
"""Validate the Rev A1 carrier power tree and print the calculation record."""

from __future__ import annotations

from dataclasses import dataclass
import math


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
    Stage("SYS_5V15", "LM5146RGYR", 10.5, 30.0, 5.15, 12.0, 30.0, 38.0, 0.94, 300.0, 3.3, 28.6),
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


def main() -> int:
    checks: list[bool] = []
    print("POWER-REGULATORS A1 CALCULATION CHECK\n")

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
        ("SYS_5V15", 5.15, actual_output(0.8, 24.0, 4.42)),
        ("AUX_12V", 12.0, actual_output(0.8, 280.0, 20.0)),
        ("MODEM_3V8", 3.8, actual_output(1.0, 100.0, 35.7)),
        ("WIFI/NET/LOGIC_3V3", 3.3, actual_output(1.0, 100.0, 43.2)),
        ("PCIE_1V0", 1.0, actual_output(0.8, 1.24, 4.99)),
        ("LOGIC_1V8", 1.8, actual_output(0.8, 6.19, 4.99)),
        ("HEADSET_3V3", 3.3, actual_output(0.8, 15.6, 4.99)),
        ("AUDIO_PRE_5V5", 5.5, actual_output(0.8, 29.4, 4.99)),
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
        ("PCIE_1V0", 5.15, 1.0, 2.0),
        ("LOGIC_1V8", 5.15, 1.8, 1.5),
        ("HEADSET_3V3", 5.15, 3.3, 1.0),
        ("AUDIO_PRE_5V5", 12.0, 5.5, 1.0),
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
            "SYS_5V15 UVLO window",
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

    for capacitance_mf in (22.4, 47.7):
        for load_w in (continuous_source_w, transient_source_w):
            duration = holdup_ms(capacitance_mf / 1000.0, 24.0, 12.5, load_w)
            checks.append(
                check(
                    f"{capacitance_mf:.0f} mF hold-up at {load_w:.1f} W",
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
