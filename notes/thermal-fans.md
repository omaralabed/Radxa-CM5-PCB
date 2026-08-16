# Thermal And Fan Control

## Goal

Provide active cooling for the CM5, cellular modem, and internal enclosure
airflow.

Target enclosure: Pelican Storm Case iM2300.

Required fans:

- Fan 1: selected CPU cooling assembly: Radxa `5540A` passive heatsink plus
  Delta `FFB0412EN-00Y2E` fan
- Fan 2: dedicated cellular modem fan aimed at the modem heatsink/thermal
  spreader
- Fan 3 / enclosure fan 1: right-sidewall filtered intake, controlled by board
  temperature sensors
- Fan 4 / enclosure fan 2: operator-sidewall center-right exhaust, controlled
  by board temperature sensors

## Preferred Hardware

Use four 12 V, 4-wire PWM/tach fans. The CPU fan is locked as follows:

- Heatsink: Radxa `5540A`, 55 x 40 x 10 mm, attached to the Radxa CM5 with
  the supplied thermal pad and four CM2 x 4 mm screws.
- Fan: Delta `FFB0412EN-00Y2E`, 40 x 40 x 28 mm, 12 V, 1.45 A nominal,
  17.4 W, 25,000 RPM, 32.9 CFM, PWM, and tachometer.
- Mount the CM5 on the carrier B.Cu so the 5540A and fan face the case bottom.
  Attach the Delta fan to a short heatsink adapter/shroud, but use a structural
  bracket and vibration isolators to carry the 51 g fan mass into carrier/frame
  standoffs. Do not load only the heatsink screws or board-to-board connectors.
- Drive air upward through the heatsink and maintain at least 10 mm of clear
  inlet space between the fan and the case floor or bottom-mounted hardware.
- Use a protected `FAN_CPU_12V` branch sized for 3 A. The CPU fan alone is too
  large for the previous 2 A shared fan-rail assumption.
- Use 25 kHz PWM and tach feedback. Hardware failure states command full speed.

The remaining fan system uses:

- `FAN_CPU_12V`: separately protected 3 A branch from `AUX_12V`
- `FAN_AUX_12V`: separately protected 3 A branch for the modem and two
  enclosure fans; retain local branch protection per fan
- PWM control line per fan
- Tach feedback line per fan
- Power switching or current limiting per fan group
- Flyback/ESD protection as required by the fan driver topology

Use a Microchip `EMC2305` five-channel PWM/tach controller. Four channels
control the installed fans and one remains spare. The board controls each fan
independently from temperature and fault state. Hardware pull states must
command all four fans to full speed if firmware, I2C, or the fan controller
fails.

The two sidewall enclosure fans are selected as Delta
`THA0412AD-TZW3`: 40 x 40 x 20 mm, 12 V, four wire, PWM and tach, IP55,
0.43 A nominal / 0.52 A maximum each, 15,600 RPM, 20.56 CFM free-air flow,
and 1.385 inch H2O maximum static pressure. The label current is 0.60 A, so
wire, connector, and branch protection calculations use at least that value.
Use one Qualtek `09150-F/30` 30 PPI filter guard on enclosure fan 1, the
intake. Use a low-restriction finger-safe guard/louver on enclosure fan 2, the
exhaust. The two external louvers point in opposing directions so discharged
hot air cannot be pulled directly back into the intake.

The airflow direction is locked: the right-wall fan is intake and the
operator-wall center-right fan is exhaust. Add internal baffles so intake air
travels through the CM5, modem, and regulator zones before reaching the
exhaust. Prototype testing must confirm filter pressure drop, wall vibration,
external and internal recirculation, and the actual swept airflow path. The
20.56 CFM rating is a free-air value; the intake/exhaust pair forms one series
air path and must not be budgeted as 41.12 CFM.

The `THA0412AD-TZW3` specifies a preferred 1 kHz PWM input. Configure each
enclosure-fan EMC2305 channel for a 26.00 kHz base divided by 26 (`0x1A`) to
produce 1.000 kHz. Use direct-duty control from the board thermal policy, with
tach feedback for speed/fault monitoring. Configure four-pole tach sampling.
The fan controller's guaranteed closed-loop range ends at 16,000 RPM while the
fan tolerance can exceed that value, so do not depend on closed-loop RPM
regulation near full speed.

## Enclosure Constraint

The Pelican iM2300 starts as a sealed rugged case, but the two sidewall fan
openings make this product intentionally vented and no longer watertight. The
top panel has no cooling openings. Filters, gaskets, and splash-directed
louvers reduce contamination but do not restore the original Pelican rating.

Size and test this path at the 151.7 W continuous system design case and the
184.2 W transient case. If the prototype cannot meet limits, use a sealed
air-to-air heat exchanger or reduce the load. Use replaceable intake media and
external splash-resistant guards, and state the reduced sealing in the product
specification.

## Cellular Modem Cooling

The cellular modem gets its own thermal hardware:

- Selected approach: both heatsink/thermal spreader and dedicated fan.
- Fan-only is not enough for a sealed field unit because it only moves hot air
  around the modem.
- Heatsink-only is not enough unless a tested conductive path carries heat to
  the case wall or an external heatsink.
- Dedicated fan aimed at the M.2 modem heatsink or heat spreader.
- Removable heatsink/thermal pad sized for the exact installed modem.
- No mechanical load on the modem's miniature RF connectors.
- Airflow path that does not bend or stress the four cellular RF pigtails.
- Temperature sensor near the modem hot zone.
- Software should also read the modem's internal temperature if the module
  exposes it through QMI/MBIM/AT commands.

## Control Strategy

- The CPU fan follows CM5 CPU temperature from Linux thermal zones.
- The cellular modem fan follows the modem-zone temperature sensor and modem
  internal temperature if available.
- The two board/enclosure fans follow board-mounted temperature sensors.
- The EMC2305 controls the two enclosure fans independently at the fan-required
  1 kHz PWM frequency. Start at 100% duty, then permit reduction no lower than
  30% after valid tach feedback is present.
- Enclosure fan 1 and enclosure fan 2 must never be assembled with the same
  airflow direction. Key or label both fan harnesses and add permanent
  `INTAKE` / `EXHAUST` markings beside the sidewall mounts.
- Control the two enclosure fans independently. Start with slightly higher
  intake command for modest positive pressure, then tune from measured CFM,
  filter loading, temperatures, and measured case leakage.
- On every stopped-to-running transition, command 100 percent duty for the
  spin-up interval, then reduce to the requested duty. Do not command a running
  duty below 30 percent; the Delta datasheet guarantees dead-stop starting at
  30 percent duty at 12 V and 1 kHz.
- Use temperature-based direct PWM duty under normal operation. Command both
  enclosure fans to 100 percent for overtemperature, missing/invalid thermal
  sensors, stalled tach, I2C/watchdog failure, or software shutdown caused by a
  thermal event.
- The board fans can also ramp when Wi-Fi/cellular traffic is high or when the
  modem/Wi-Fi temperature sensor reports elevated temperature.
- The two enclosure fans remain independently controllable; do not combine
  their PWM or tach nets.
- Treat loss of either tach signal as a fan fault and command all thermal fans
  to full speed while raising the panel thermal/fan alarm.

Preliminary enclosure-fan policy, to be tuned in chamber testing:

| Hottest board/modem sensor | Intake duty | Exhaust duty |
| --- | ---: | ---: |
| Startup for 3 seconds | 100% | 100% |
| Below 45 C | 40% | 35% |
| 45-55 C | 60% | 55% |
| 55-65 C | 80% | 75% |
| 65 C or above, invalid sensor, stalled fan, or control fault | 100% | 100% |

The small intake bias is a starting point for positive pressure. Filter loading
and case leakage may reverse that balance, so release values come
from measured pressure, CFM, and component temperatures rather than the table
alone.

## Temperature Sensing

Use multiple temperature sources:

- CM5 CPU temperature from Linux thermal zones
- `TMP117` starting sensor near the cellular modem heatsink/hot zone
  for dedicated modem fan control
- `TMP117` starting sensor near the Wi-Fi/network hot zone for
  enclosure fan control
- `TMP117` starting sensor near the carrier/audio/power hot zone for
  enclosure fan control
- Optional sensor near audio analog area if fan noise/heat coupling becomes a concern

## Software Notes

The controlled Linux/device-tree implementation specification is
`docs/thermal-control-firmware-spec.md`. It defines the channel map, startup
sequence, EMC2305 watchdog, service behavior, fault handling, and production
release tests. The runtime software is not yet implemented.

Linux direction:

- Use PWM fan bindings for the CPU fan where practical.
- Expose PWM controls and tach inputs for all four fans through
  GPIO/interrupt/counter support if available.
- Add a small ProComm health/status view for fan speed and thermal state.

## Open Decisions

- Exact modem 12 V fan model, all fan connector types, and pinouts.
- Final downward CM5 cooling-cartridge bracket, adapter/shroud, 10 mm minimum
  inlet gap, and vibration-isolator geometry after importing exact 3D models.
- Exact TMP117 placement and trip curves.
- Optional internal heat-spreader/heat-pipe geometry if chamber testing shows
  the sidewall airflow alone does not provide adequate local heat transport.
- Final intake/exhaust centers, PWM balance, baffle geometry, reinforcement
  plates, splash guards, and clogged-filter alarm threshold after measuring
  the actual wall ribs, taper, handle, hinges, and latches.
- Final board-temperature ramp thresholds after 45 C chamber characterization.

## Airflow Acceptance

- Use smoke or tracer testing to prove right-wall intake air crosses the CM5,
  modem, and regulator zones before leaving the operator-wall exhaust.
- Measure intake and exhaust flow with clean and dust-loaded filters.
- Qualify at 45 C / 113 F ambient, including the maximum CPU/GPU/NPU load,
  Wi-Fi AP traffic, cellular uplink, all audio channels, and maximum display
  brightness. Log every temperature sensor, PWM command, and fan tachometer
  until steady state; no component may exceed its manufacturer limit or enter
  unintended thermal throttling.
- Demonstrate at least 15 CFM measured through-case flow with a clean intake
  filter and document the dust-loaded maintenance threshold. The exact
  acceptance value may be raised after the first 45 C thermal run.
- Block the intake filter to the maintenance limit and verify safe throttling or
  shutdown without damaging the CM5, modem, regulators, PSU, or audio stages.
