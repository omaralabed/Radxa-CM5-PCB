# No-Blink Power Transfer

## Requirement

Primary-to-backup power transfer must be invisible to the user and invisible to
the operating system when a valid backup source is present.

No-blink means:

- Radxa CM5 does not reset, brown out, reboot, or corrupt eMMC.
- HDMI touchscreen does not visibly blink or power-cycle.
- AK5558VN/AK4458VN program audio does not mute, click, lose clock, or drop
  channels.
- ES8316 headset audio does not pop, reset, or disappear.
- Ethernet, Wi-Fi AP, and cellular interfaces do not reset from power loss.
- Fan controllers and thermal sensors stay powered through the transfer.

This applies to:

- AC mains / `RPS-400-24-C` loss while D-Tap/LEMO or Gold Mount is valid.
- AC mains / `RPS-400-24-C` restoration while running from backup.
- D-Tap/LEMO to Gold Mount transfer when both are installed and the selected
  source changes.

If no valid backup source is installed, the unit can shut down. No-blink
transfer is required only when a valid backup source is present before the
primary source is removed.

## Design Direction

Use the implemented ProComm cascaded PowerPath architecture from
`/Users/viewvision/Desktop/ProComm enclosure and PCB boards/PCB_SOURCE/POWER_SELECTOR_24V_BATTERY`,
but resize it for the Radxa load and the locked `RPS-400-24-C` primary PSU.

The ProComm reference is useful because it already implements the intended
non-paralleled priority transfer:

- Fixed priority: rear/primary 24 V, then D-Tap/LEMO, then Gold Mount.
- `RAW_OUT` feeds the downstream carrier regulator instead of trying to
  generate all rails on the selector board.
- Source transfer is non-overlap/non-paralleled, with reverse and
  cross-conduction blocking.
- The system rocker switch only enables the controllers; high-current load does
  not cross the panel switch.
- Use the same E-Switch `RA812C1121` maintained DPST rocker and keyed four-wire
  harness as ProComm. One isolated pole controls LTC4421 `SHDN_MAIN`; the other
  controls LTC4418 `SHDN_PRE`, so OFF disables both the primary selector and the
  complete D-Tap/Gold Mount backup preselector.

Carry-forward circuit blocks:

- `LTC4418` preselects between D-Tap/LEMO and Gold Mount backup sources.
- `LTC4421` selects between 24 V PSU and `BAT_SELECTED`.
- Main selector uses external back-to-back N-channel MOSFETs per input. The
  ProComm Rev C schematic uses Nexperia `PSMN4R2-80YSE` as the reference device.
- Backup preselector uses back-to-back P-channel MOSFETs per backup source. The
  ProComm Rev C schematic uses Vishay `SiR5607DP-T1-RE3` as the reference
  device.
- Back-to-back MOSFETs block reverse and cross-conduction current.
- UV/OV thresholds define valid windows for every source.
- Validation delays are short enough for ride-through but long enough to avoid
  chatter on noisy source insertion.
- Source-valid and power-good signals are routed to CM5 GPIO or a supervisor
  so software can log transfers.

The controller alone is not enough. The carrier also needs energy storage and
regulators that tolerate the source voltage step.

## ProComm Reference Values

Use these as starting values, not blind-copy production values:

| Function | ProComm Rev C value / part | Radxa action |
| --- | --- | --- |
| Main selector | ADI `LTC4421IUHE#PBF` | Reuse topology; recalc sense, timers, MOSFET SOA, thresholds, and layout copper. |
| Backup preselector | ADI `LTC4418IUF#PBF` | Reuse topology; keep D-Tap priority over Gold Mount. |
| Main-path MOSFETs | Nexperia `PSMN4R2-80YSE` | Candidate only; verify at Radxa current, thermal rise, and fault cases. |
| Backup blockers | Vishay `SiR5607DP-T1-RE3` | Candidate only; verify reverse-polarity and thermal behavior. |
| Source fuses | Littelfuse `0451015.MRL`, 15 A | Recalculate for RPS PSU, battery current, wire gauge, and fault energy. |
| Primary TVS | Littelfuse `SMCJ24A` | Recalculate for internal 24 V PSU harness and surge environment. |
| Backup TVS | Littelfuse `SMBJ18CA` | Reuse as reference for 13.0-16.8 V backup inputs; verify with final harness. |
| Main current sense | 2.50 mOhm, 2 W shunts | Rejected unchanged: its 10 A-class limit is below the 14.17 A D-Tap transient and the 16.23 A near-cutoff short transient. Recalculate for at least a 14 A operating threshold with tolerance, rate the normal path for 15 A, and shed load after transfer before sustained low-voltage battery operation. |
| Raw-output bulk | 3 x 220 uF / 50 V polymer electrolytic plus ceramics | Rejected unchanged: 660 uF is far below the 20 ms full-load hold-up calculation. |
| Switch pulldowns | `R541` / `R542`, 47 kOhm | Reuse fail-off behavior. |
| Panel switch | E-Switch `RA812C1121`, maintained DPST OFF-ON | Reuse exact two-pole controller-enable arrangement; do not route load current through it. |
| Preselector validation | `C532 = 1 nF`, about 16 ms | Recalculate against required no-blink transfer and source chatter behavior. |

Implemented ProComm thresholds:

- 24 V path: OV about 29.95 V, UV rising about 19.97 V, UV falling about
  17.99 V.
- Selected-backup path into LTC4421: OV about 18.09 V, UV rising about 11.58 V,
  UV falling about 10.57 V.
- D-Tap input: UV rise about 12.62 V, UV fall about 12.25 V, OV about 18.00 V.
- Gold Mount input: UV rise about 11.69 V, UV fall about 11.35 V, OV about
  17.74 V.

For Radxa, the D-Tap 13.0-16.8 V operating rule remains. Gold Mount lower UV
must be coordinated with the Dionic XT 90 behavior and with an orderly CM5
shutdown warning.

## Hold-Up Targets

First schematic target:

- Minimum critical-rail ride-through: 20 ms
- Preferred critical-rail ride-through: 50 ms
- Validation load: estimated continuous system load, then repeated at peak
  modem/display/Wi-Fi/fan cases

First-order raw-bus sizing uses:

```text
C = (2 x P x t) / (Vstart^2 - Vend^2)
```

Preliminary ideal capacitance from 24.0 V down to 12.5 V:

| Load | 20 ms | 50 ms |
| --- | ---: | ---: |
| 151.7 W continuous design case | 14,456 uF | 36,141 uF |
| 184.2 W peak design case | 17,553 uF | 43,883 uF |

`A1 CAPTURED STARTING POINT`: keep the bulk storage on the floor-mounted
PWR-SELECT assembly. Four Nichicon `LGU1H682MELB` snap-in capacitors provide
27,200 uF nominal / 50 V on `RAW_OUT`; the three local 220 uF hybrids raise the
nominal total to 27,860 uF. The selected snap-ins are 30 mm diameter x 35 mm
high. At the -20% capacitance limit the combined bank is 22,288 uF and provides
about 25.4 ms ideal hold-up at 184.2 W from 24.0 V to 12.5 V. Final capacitance
still depends on measured transfer waveforms.

The 50 V rating provides healthier margin above the 24 V source and its
protected transient envelope than a 35 V bank. The bank requires controlled
precharge/inrush limiting, discharge/bleeder
behavior, capacitor ripple-current and fault-current review, and confirmation
that the LTC4418/LTC4421 MOSFETs remain inside SOA. Do not connect a discharged
27.2 mF bank through an unverified hot-plug path. The cans require a rigid
tray-supported clamp; their mass must not be carried only by the snap-in leads.

At the low backup end, holding 184.2 W for only 1 ms while the raw bus falls from
13 V to 10 V already needs about 5,339 uF ideal. Therefore the D-Tap-to-Gold
Mount transition must use an already validated backup source and complete in a
few milliseconds; the 20 ms primary-loss target must not be misread as proof
that a long low-voltage backup-to-backup gap is acceptable.

Hold-up is placed at multiple levels:

- Protected raw-DC bus bulk capacitance after the source selector.
- Local bulk capacitance at `SYS_5V15`, `AUX_12V`, `DISPLAY_12V`,
  `FAN_CPU_12V`, `FAN_AUX_12V`, `MODEM_3V8`, `WIFI_3V3`,
  `NET_3V3`, and clean audio rails.
- Extra low-ESR bulk near the cellular modem M.2 socket for transmit bursts.
- Converter-specific input/output capacitance per regulator datasheets.

Final capacitance must be calculated from measured transfer time, load current,
minimum regulator input voltage, ESR, inrush current, and thermal limits. Do not
guess the production capacitor bank from nominal wattage alone.

The original 660 uF selector bank remains additive local storage. The large
bank is no longer installed on the suspended CM5 carrier because the previously
selected 22 x 50 mm cans violate the available carrier Z envelope.

## Regulator Rule

Every downstream regulator fed from protected raw DC must remain in regulation
across the full source range and through transfer transients:

- 24 V PSU nominal and trim range
- D-Tap/LEMO 13.0-16.8 V operating range
- Gold Mount battery operating range
- Source-selector droop, MOSFET drop, fuse/eFuse drop, and wiring drop

Rail-specific rule:

- `SYS_5V15`: wide-input high-current buck is acceptable because every valid
  source is above the 5.15 V output.
- `WIFI_3V3`: wide-input buck with local hold-up and load switch.
- `MODEM_3V8`: wide-input high-current buck with large local bulk.
- `AUX_12V`: use the locked `LM5176` buck-boost topology so the 12 V backbone
  remains regulated during battery operation and source transfer.
- `DISPLAY_12V`: simple fused harness branch from `AUX_12V`, with no dedicated
  display eFuse/current limiter. `FAN_CPU_12V` and `FAN_AUX_12V` remain
  separately protected branches. All three remain powered during source transfer.
- `AUDIO_MAIN` and `HEADSET`: clean regulators must stay alive through transfer
  and must not assert mute/reset unless software intentionally requests it.

## Load-Shedding Rule

Backup operation may reduce noncritical loads, but not during the instant of
transfer.

Allowed after transfer is complete:

- Dim touchscreen after a delay.
- Reduce CPU performance limit after a delay.
- Reduce Wi-Fi transmit power or client service policy after a delay.
- Reduce fan acoustic profile only if temperatures are safe.

Not allowed during transfer:

- Turning off display power.
- Resetting CM5.
- Resetting audio converters or headset codec.
- Power-cycling Wi-Fi or cellular modem.
- Dropping the main audio TDM clock.

## Validation Test

Acceptance test with oscilloscope and system logging:

- Scope `24V_PSU`, `BAT_SELECTED`, `PROTECTED_RAW_DC`, `SYS_5V15`,
  `AUX_12V`, `DISPLAY_12V`, `FAN_CPU_12V`, `FAN_AUX_12V`, `MODEM_3V8`, `WIFI_3V3`,
  `NET_3V3`, audio rails, and reset/mute GPIOs.
- Run CM5, HDMI touchscreen, 8x8 audio, Wi-Fi AP, cellular modem, Ethernet, and
  all fans.
- Remove AC input while backup is valid.
- Restore AC input while backup is powering the system.
- Repeat D-Tap/LEMO and Gold Mount transfers.
- Confirm no CM5 reset, no display blink, no audible mute/click, no ALSA xrun,
  no modem reset, no Wi-Fi AP reset, and no fan-controller reset.

The old ProComm reference explicitly says physical source-transfer and fault
testing remains required even after schematic ERC and automated net checks pass.
Keep that same discipline for Radxa.

## Source Notes

- Analog Devices `LTC4421` is a high-power prioritized PowerPath controller
  with fast switchover intended to minimize output droop.
- Analog Devices `LTC4418` is a dual-channel prioritized PowerPath controller
  with fast switchover, reverse/cross-conduction blocking, and cascadable
  behavior for multiple inputs.
- ProComm source implementation:
  `/Users/viewvision/Desktop/ProComm enclosure and PCB boards/PCB_SOURCE/POWER_SELECTOR_24V_BATTERY/PowerSelector.kicad_sch`
- Controlled Radxa baseline and current review:
  `cad/kicad/PWR-SELECT/BASELINE_SOURCE.md` and
  `cad/kicad/PWR-SELECT/REVIEW/PowerSelector-A0-ERC.rpt`
