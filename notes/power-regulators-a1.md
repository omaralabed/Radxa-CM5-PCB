# Power Regulators A1

## Status

`Power-Regulators-A1.kicad_sch` is the calculated engineering capture for the
CM5 carrier power tree. It fixes the rail architecture, controller families,
starting component values, branch protection, sequencing intent, and test
points. It is not a fabrication release. Final footprints, layout parasitics,
control-loop measurements, thermals, inrush, and source-transfer performance
remain release gates.

The source of truth is `cad/kicad/generate_interface_schematics.py`. Regenerate
the sheet from that script; do not hand-edit the generated KiCad file.

## Input And No-Blink Basis

- `RAW_OUT_LOAD` operating range after the source selector and delivered-load
  telemetry shunt: 10.5 V to 30 V.
- Nominal primary source: Mean Well `RPS-400-24-C`, 24 V / 10.5 A / 252 W
  convection-rated design basis.
- Source selector path: 15 A class.
- Continuous design load: 151.7 W after locking the high-flow enclosure fans.
- All-load transient budget: 184.2 W.
- Installed PWR-SELECT hold-up bank: four Nichicon `LGU1H682MELB`, 6800 uF /
  50 V each, 27.2 mF total, in 30 mm diameter x 35 mm snap-in cans.
- PWR-SELECT local hybrid storage: 660 uF, for 27.86 mF combined nominal.
- Worst-case capacitance basis: -20%, or 22.288 mF combined.
- The suspended carrier retains only local high-frequency input decoupling.

Ideal constant-power hold-up from 24.0 V to 12.5 V is:

```text
t = C x (Vstart^2 - Vend^2) / (2 x P)
```

| Capacitance | 151.7 W | 184.2 W |
| --- | ---: | ---: |
| 27.86 mF combined nominal | 38.5 ms | 31.7 ms |
| 22.288 mF combined at -20% | 30.8 ms | 25.4 ms |

These are ideal energy calculations. ESR, tolerance, aging, temperature,
converter dropout, wiring, and selector transfer behavior reduce real hold-up.
Hot-plug inrush, precharge, discharge time, source-MOSFET SOA, snap-in ripple
current, and the tray-supported retention clamp must be proven before release.

## Locked Rail Tree

| Rail | Rating | Controller / protection | Starting implementation |
| --- | ---: | --- | --- |
| `SYS_4V0` | 4.006 V nominal / 12 A | TI `LM5146RGYR` | Follows Radxa's 4 V RK806 recommendation; 300 kHz, 3.3 uH TDK `SPM10065VC-3R3M-D`, onsemi `NVMFS6B25NLT1G` high side and `FDWS86068-F085` low side, five 47 uF output ceramics, 9.58 V typical turn-on UVLO |
| `AUX_12V` | Revised A1 starting point: 12 V / 8 A | TI `LM5176PWP` | 6 mOhm output sense gives about 8.33 A nominal limit. Recalculate MOSFET loss, magnetics, shunts, compensation, copper, and thermal design before routing. |
| `MODEM_3V8_PRE` | 3.8 V / 6 A | TI `LM61460RJR` | 400 kHz, 4.7 uH Coilcraft `XAL7070-472MEC`, 100 k / 35.7 k feedback |
| `MODEM_3V8` | 3.8 V / 6 A limit | TI `TPS259827LNRGER` | 255 ohm 1% `ILIM`, 1320 uF local polymer bulk; weak-signal transmit validation mandatory |
| `WIFI_3V3_PRE` | 3.3 V / 4 A | TI `LM61440RJR` | 400 kHz, 4.7 uH `XAL7070-472MEC`, 100 k / 43.2 k feedback |
| `WIFI_3V3` | 3.3 V / 4 A design load | TI `TPS22990DMLR` | Controlled startup with 10 nF timing capacitor; not a current limiter |
| `NET_3V3` | 3.3 V / 4 A | TI `LM61440RJR` | 400 kHz, 4.7 uH `XAL7070-472MEC`; 10 W peak allocation |
| `LOGIC_3V3` | 3.3 V / 3 A | TI `LM61440RJR` | 400 kHz, 4.7 uH `XAL7070-472MEC` |
| `PCIE_1V0` | 1.0 V / 2 A | TI `TPS62913RPUT` | 2.2 MHz random spread spectrum, 2.2 uH `XGL4030-222MEC`, 1.24 k / 4.99 k feedback |
| `LOGIC_1V8` | 1.8 V / 1.5 A | TI `TPS62913RPUT` | 2.2 MHz random spread spectrum, 2.2 uH `XGL4030-222MEC`, 6.19 k / 4.99 k feedback |
| `IO_5V0` | 4.984 V nominal / 2 A | TI `TPS62913RPUT` on Display-Harness | Fed from separately fused `DISPLAY_IO_12V`; supplies CM5 U13-B pin 106 plus independent HDMI and USB-touch polyfuses |
| `HEADSET_3V3` | 3.3 V / 250 mA | TI `LP5907MFX-3.3/NOPB` | Dedicated low-noise LDO from `SYS_4V0`; actual headset peak current remains a bench gate |
| `AUDIO_PRE_5V5` | 5.5 V / 1 A | TI `TPS62913RPUT` | Fed from `AUDIO_12V`; 2.2 MHz random spread spectrum; 29.4 k / 4.99 k feedback |
| `AUDIO_P15V/N15V` | +/-15 V / 20 W class | Traco `TRI 20-1223` | Isolated converter mounted with the AUDIO-8X8 assembly |
| `ADC_5V_A` / `DAC_5V_A` | clean 5 V | TI `TPS7A2050PDBVR` | Separate converter LDOs from `AUDIO_PRE_5V5` |
| `AKM_3V3_D` | clean 3.3 V | TI `TPS7A2033PDBVR` | Dedicated AKM digital LDO |
| `HEADSET_1V8` | clean 1.8 V | TI `TPS7A2018PDBVR` | Dedicated headset codec LDO |

## Branches

| Branch | Locked requirement | Protection |
| --- | --- | --- |
| `DISPLAY_12V` | 12 V / 2.5 A, 25 W monitor | Littelfuse `0453003.MR` 3 A time-lag fuse; no dedicated display eFuse by requirement |
| `DISPLAY_IO_12V` | Input to the 2 A `IO_5V0` buck | Littelfuse `0453002.MR` 2 A time-lag fuse; separate from monitor power |
| `NIGHT_LIGHT_12V` | Two 12 V / 0.25 W YIS LS102W panel lights plus capacitive switch | Littelfuse `0453.250MR` 0.25 A fast fuse; hardware-only branch from `AUX_12V` |
| `FAN_CPU_12V` | Locked Delta CPU fan, 12 V / 3 A branch | Independent 3 A time-lag branch plus 2 A hold local protection. |
| `FAN_AUX_12V` | Modem plus two Delta `THA0412AD-TZW3` enclosure fans, 12 V / 3 A branch | Independent 3 A time-lag branch; 1 A hold local protection per load, subject to final modem-fan inrush measurement. |
| `AUDIO_12V` | Isolated bipolar and clean audio rails | Littelfuse `0453002.MR` 2 A time-lag fuse |

## Startup And Reset Order

1. A valid `RAW_OUT_LOAD` starts `SYS_4V0`, `AUX_12V`, `LOGIC_3V3`, and the radio
   pre-regulators through their local UVLO networks.
2. `SYS_4V0_PG` permits `LOGIC_1V8` and `PCIE_1V0` startup. `IO_5V0` starts from
   the separately fused `DISPLAY_IO_12V` branch and feeds CM5 pin 106.
3. PCIe reset remains asserted until `NET_3V3_PG` and `PCIE_1V0_PG` are valid.
4. Thermal-IO enables the final Wi-Fi and modem rails only after controller and
   temperature checks.
5. `AUDIO_ENABLE` starts the audio converter rails. DAC mute remains asserted
   until power, clocks, and TDM framing are qualified.
6. Every power-good signal is pulled to `LOGIC_3V3` and is available to control
   logic or a test pad.

No rail is intentionally dropped during a valid primary-to-backup transfer.
Delayed load reduction may occur only after the transfer is complete.

## Source And Current Checks

| Case | Calculated current | Limit / interpretation |
| --- | ---: | --- |
| 24 V, 151.7 W | 6.32 A | Below 10.5 A PSU rating |
| 24 V, 184.2 W | 7.68 A | Below 10.5 A PSU rating |
| 13 V backup, 184.2 W | 14.17 A | Below 15 A path rating, with limited margin |
| 11.35 V Gold Mount, 151.7 W | 13.37 A | Above 12 A continuous rating; automatic load shedding required near cutoff |
| 11.35 V Gold Mount, 184.2 W | 16.23 A | Short transient only; depends on validated battery peak capability |

## Required Release Tests

- Validate every regulator at 10.5 V, 13 V, 16.8 V, 24 V, and 30 V input where
  applicable, including startup into maximum capacitance.
- Measure loop response/Bode margin for `SYS_4V0` and `AUX_12V` on the final
  PCB; update compensation from measured plant behavior.
- Verify `SYS_4V0` tolerance, connector drop, startup overshoot, and CM5
  stability against the official Radxa carrier guidance at full CPU/GPU/NPU load.
- Verify `IO_5V0` at CM5 U13-B pin 106 and at the monitor end of the USB cable.
- Measure efficiency and component temperature at continuous and transient
  loads with the enclosure closed.
- Test modem attach and sustained uplink at weak signal while monitoring
  `MODEM_3V8` droop and eFuse current limiting.
- Test Wi-Fi AP operation with 25 active devices while monitoring its dedicated
  rail and CM5/system rail.
- Test source removal/restoration with all loads active. Confirm no CM5 reset,
  display blink, TDM interruption, radio reset, or fan-controller reset.
- Verify fuse clearing, short-circuit behavior, capacitor ripple current,
  discharge time, hot-plug inrush, and source-selector MOSFET SOA.
- Inspect the drawing-derived RJR, DML, DNK and onsemi power-package lands in
  the first-article stencil/assembly review; their source dimensions and pad-net
  remapping are machine checked. The regulator-sheet BOM now has no missing
  manufacturer, MPN, or footprint fields.

## Controlled Outputs

- Schematic: `cad/kicad/CM5-CARRIER/Power-Regulators-A1.kicad_sch`
- BOM: `docs/power_regulator_bom_a1.csv`
- Calculation table: `docs/power_regulator_calculations_a1.csv`
- Machine validator: `cad/kicad/CM5-CARRIER/validate_power_regulators.py`
- ERC report: `cad/kicad/CM5-CARRIER/REVIEW/Power-Regulators-A1-ERC.rpt`

## Primary References

- TI LM5146: https://www.ti.com/lit/ds/symlink/lm5146.pdf
- TI LM5176: https://www.ti.com/lit/ds/symlink/lm5176.pdf
- TI LM5176 EVM: https://www.ti.com/lit/ug/snvu547/snvu547.pdf
- TI LM61460: https://www.ti.com/product/LM61460
- TI LM61440: https://www.ti.com/product/LM61440
- TI TPS62913: https://www.ti.com/product/TPS62913
- TI TPS25982: https://www.ti.com/lit/ds/symlink/tps25982.pdf
- TI TPS22990: https://www.ti.com/lit/ds/symlink/tps22990.pdf
- Radxa CM5 carrier design note: https://dl.radxa.com/cm5/radxa_cm5_carrier_board_design_note.pdf
- Traco TRI 20: https://www.tracopower.com/tri20-datasheet
- Wurth 74439370047: https://www.we-online.com/components/products/datasheet/74439370047.pdf
