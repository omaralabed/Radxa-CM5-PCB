# Rev A Hardware Architecture Lock

## Status

This document is the schematic starting point for the first Radxa CM5 ProComm
prototype. Items marked `LOCKED` are design decisions. Parts marked
`STARTING PART` are approved for schematic work but still require calculation,
availability review, layout review, and prototype validation before release.

The three ProComm reference folders remain read-only references. No existing
converter, regulator, or XLR circuit is copied without recalculation for this
product.

## Locked Product Architecture

- Radxa CM5 with eMMC only; no microSD.
- 8 balanced inputs and 8 balanced outputs using `AK5558VN` and `AK4458VN`
  over CM5 `I2S0` TDM.
- Separate `ES8316` CTIA/AHJ headset codec on `I2S1`, with an external
  headphone amplifier and microphone conditioning.
- Two 1 GbE WAN ports and two 1 GbE shared LAN ports.
- Wi-Fi 6 AP for about 25 devices using a true 4T4R module and four antennas.
- Universal-style M.2 B-Key WWAN socket supporting 3042/3052 modules, with
  `SIM8260G-M2` as the first global validation modem.
- Four cellular/GNSS antenna paths.
- 15.6-inch JUNEBOX/DTM MALL `B0GK5X95D9` HDMI touchscreen in the lid.
- Four tachometer-equipped PWM fans: CM5, modem, enclosure 1, enclosure 2.
- Pelican Storm Case iM2300.
- MEAN WELL `RPS-400-24-C`, operated from its 24 V/10.5 A/252 W convection
  rating, as the primary AC/DC supply.
- ProComm-derived `LTC4418` backup preselector and `LTC4421` main source
  selector, with no-blink primary/backup transfer.

## Board Partition

`LOCKED`: use three low-voltage PCB assemblies plus the commercial AC/DC PSU.

1. `PWR-SELECT`: bottom-mounted source-selector board near the PSU and battery
   wiring. It contains source protection, `LTC4418`, `LTC4421`, back-to-back
   MOSFETs, current/voltage telemetry, protected-raw hold-up capacitance, and
   selector status/control. It contains no exposed AC mains.
2. `CM5-CARRIER`: CM5, PCIe switch, three added Ethernet controllers, M.2
   Wi-Fi, M.2 WWAN, HDMI/USB interfaces, headset subsystem, fan controller,
   temperature sensors, and the high-current low-voltage regulators.
3. `AUDIO-8X8`: the AKM converters, audio clocks/buffers, THAT1206 input
   receivers, OPA165x/THAT1646 output stages, clean audio regulators/filters,
   and the 16 panel-supported XLR connectors.

The AC/DC PSU is a separate covered commercial assembly mounted on the bottom
panel. The top panel carries the connector panel, XLR bank, fused C14 inlet,
service controls, and PCB assemblies underneath it.

The TDM/clock link between `CM5-CARRIER` and `AUDIO-8X8` must be short and
controlled. Prefer a keyed board-to-board or shielded cable interface with
interleaved grounds and separately routed audio power. Do not route audio
clocks beside fan, Ethernet, HDMI, USB 3, PCIe, modem, or switching nodes.

## Protected Raw Input

All downstream regulators are fed from `PROTECTED_RAW`, after source
selection, reverse-current blocking, telemetry, and hold-up capacitance.

Design input envelope:

- Normal primary source: 24 V nominal.
- Backup source: 13.0-16.8 V nominal operating range.
- Backup inlet: LEMO `EGG.1B.302.CLL`, 15 A rated starting part, with matching
  15 A cable, fuse, MOSFET, copper, and wiring path. The prior 10 A 0B inlet is
  not accepted at the estimated 14.17 A transient at 13.0 V.
- Include wiring, fuse, MOSFET, and eFuse drop in UVLO/dropout calculations.
- Every critical regulator must remain in regulation throughout a valid
  primary-to-backup and backup-to-primary transfer.
- Rate the selector, connector, fuse, MOSFET, shunt, copper, and harness path
  for at least 15 A. Set the selector operating threshold to at least 14 A
  after tolerance analysis; the old 10 A shunt setting is not accepted.
- Use the floor-mounted `PROTECTED_RAW` hold-up bank at 27,200 uF nominal /
  50 V plus 660 uF local storage, with controlled precharge/inrush limiting.
  Final raw and
  local capacitance follows measured transfer time, load, tolerance, ESR,
  temperature, and aging; capacitance is not accepted by nominal value alone.

## Regulator Tree

| Rail | Locked target | Starting implementation | Loads and rules |
| --- | ---: | --- | --- |
| `SYS_5V15` | 5.15 V, 12 A continuous | TI `LM5146RGYR`, onsemi `NVMFS6B25NLT1G` / `FDWS86068-F085`, TDK `SPM10065VC-3R3M-D` | CM5 and controlled 5 V system loads. Kelvin/remote sense at the CM5 connector. Recalculate the compensation with measured final-PCB response. |
| `AUX_12V` | Revised 12 V, 8 A minimum target | TI `LM5176` four-switch buck-boost | Backup-riding 12 V backbone. Recalculate and bench-qualify the A1 power stage before routing. |
| `DISPLAY_12V` | 12 V, 2.5 A branch | Simple fused harness branch from `AUX_12V`; no dedicated display eFuse/current limiter | Lid display only. Rated load is 25 W / 2.08 A; size the fuse and wiring after measuring full-brightness and startup current. |
| `FAN_CPU_12V` | 12 V, 3 A branch | Protected branch from `AUX_12V` | Locked Delta `FFB0412EN-00Y2E`; independent PWM/tach and fault containment. |
| `FAN_AUX_12V` | 12 V, 3 A branch | Protected branch from `AUX_12V` | Modem fan plus two Delta `THA0412AD-TZW3` enclosure fans; each load has local protection. |
| `MODEM_3V8` | 3.8 V, 6 A converter; 5 A minimum usable load | TI `LM61460` plus `TPS25982` eFuse/load disconnect | WWAN socket only. Software power cycle, current monitor, and at least 1000 uF initial low-ESR bulk near the socket plus ceramics. Tune from the final modem guide and scope measurements. |
| `WIFI_3V3` | 3.3 V, 4 A | TI `LM61440` plus `TPS22990` controlled load switch | Wi-Fi M.2 socket only. Local bulk, controlled rise time, reset, and power-good monitoring. |
| `NET_3V3` | 3.3 V, 4 A | Separate TI `LM61440` | PCIe switch I/O and three LAN7430 controllers. Do not share with Wi-Fi. |
| `PCIE_1V0` | 1.0 V, 2 A | 2 A point-of-load buck such as `TPS62850` family | PCIe switch core. Obey switch rail sequencing and reset timing. |
| `LOGIC_3V3` | 3.3 V, 3 A | Dedicated low-voltage buck | Carrier logic, sensors, LEDs, control, and low-power peripherals only. |
| `LOGIC_1V8` | 1.8 V, 1.5 A | Point-of-load buck or LDO after load calculation | Level references and control logic that require 1.8 V. |
| `AUDIO_BIPOLAR` | +/-15 V, 20 W class | TRACO Power `TRI 20-1223` starting module from `AUX_12V`, followed by common-mode/pi filtering | THAT1206/OPA165x/THAT1646 line stages. Confirm current and noise with all 16 channels driven. |
| `AKM_5V_A` | Clean 5.0 V, 500 mA class | Quiet 6 V pre-regulator followed by `LT3045` | AK5558/AK4458 analog supplies. Keep thermal dissipation within the LDO limit. |
| `AUDIO_3V3_D` | Clean 3.3 V, load TBD | `TPS7A20` or equivalent low-noise LDO | AKM digital/control and audio clock loads after exact current calculation. |
| `HEADSET_3V3` | Clean 3.3 V, load TBD | Separate `TPS7A20` or equivalent | ES8316, mic bias/preamp, jack detect, and `TPA6132A2` headphone amplifier. No radio, fan, USB, or LED loads. |

The listed ICs are schematic starting parts, not a substitute for the vendor
design worksheets. Inductor saturation, MOSFET SOA, current sense, compensation,
transient response, thermal vias, copper area, EMI filters, and derating must be
calculated at 24 V and at the lowest valid backup voltage.

## Ethernet And Radio

`LOCKED`: Rev A uses 1 GbE, not 2.5 GbE.

```text
CM5 native Gigabit Ethernet MDI -------------------------> WAN1
CM5 PCIE20_0 x1 -> PI7C9X2G608GP PCIe switch
                       |-> LAN7430 -> magnetics/RJ45 ----> WAN2
                       |-> LAN7430 -> magnetics/RJ45 ----> LAN1
                       |-> LAN7430 -> magnetics/RJ45 ----> LAN2
                       |-> Mini PCIe AW7915-NP1 --------> 4T4R Wi-Fi AP
                       `-> one downstream port reserved/tested if available

CM5 USB30_2 + USB2 -> M.2 B-Key 3042/3052 -------------> WWAN
```

- Use Microchip `LAN7430` for the three added 1 GbE ports. It has an integrated
  PHY, uses a single external 3.3 V supply, and has mainline Linux support.
- Use Diodes `PI7C9X2G608GP` in an x1-upstream configuration. Hold reset until
  the required 3.3 V/1.0 V rails and PCIe reference clock are stable.
- Use AsiaRF `AW7915-NP1` as the first Wi-Fi AP validation module.
- The PCIe Gen2 x1 upstream link is a shared bandwidth limit. Validate
  simultaneous WAN2/LAN1/LAN2/Wi-Fi traffic; do not advertise four-port
  line-rate aggregate throughput without test evidence.
- Do not add PoE in Rev A.

## Audio Level And Loading

`LOCKED` for the first analog design:

- Nominal input and output level: `+4 dBu`.
- Maximum input and output level: `+24 dBu`, providing 20 dB nominal headroom.
- Normal output load: 10 kohm or higher.
- Compatibility/test load: 600 ohm. The output must remain stable and meet the
  specified maximum level into 600 ohm, but 600 ohm is not the expected load.
- Main inputs are balanced line level only.
- Main outputs are actively balanced.
- No phantom power in Rev A.

The `THAT1206` input receiver and `THAT1646` output driver are retained from the
ProComm active-balanced reference. The A1 gain, attenuation, common-mode,
coupling, anti-alias, reconstruction, DC-blocking, protection, and AKM
interface starting values are captured in the detailed AUDIO-8X8 sheets and
`../docs/audio_8x8_level_budget_a1.csv`. They require first-article level,
noise, THD+N, crosstalk, stability, and fault validation. XLR pin 1 bonds to
chassis at the connector boundary.

## Thermal Exit Path

`LOCKED`: use a filtered right-wall intake and operator-wall center-right
exhaust to reject heat through the iM2300 sidewalls. The top panel has no fan
or mesh openings. Each sidewall fan uses a reinforcement plate, closed-cell
gasket, finger guard, and splash-directed louver.

- Mount the CM5 and universal M.2 WWAN card on carrier B.Cu. Their heatsinks and
  dedicated attached fans face the bottom with at least 10 mm clear inlet gap.
- Use structural brackets so fan mass and vibration load the carrier/frame
  standoffs rather than the CM5 screws, B2B connectors, or M.2 edge connector.
- Keep fan motors and PWM/power harnesses outside the XLR quiet zone. Filter the
  fan rail and use a star return at the power board, independent of audio return.
- Keep the bottom-mounted `RPS-400-24-C` in a guarded hinge/display-side bay;
  rotate it 90 degrees in plan and maintain at least 125 mm from the audio
  quiet boundary to its grounded guard. Do not route fan harnesses through the
  PSU or guarded AC corridor. Keep the actual H03 HDMI/USB-touch/12 V cable
  envelope at least 15 mm from the guard and use independent clamps.
- Size the thermal solution from the 151.7 W continuous system design case and
  verify the 184.2 W transient case. The display dissipates in the lid, so record
  base and lid temperatures separately.
- Thermal acceptance testing is at 45 C / 113 F ambient, enclosure closed, display at
  maximum brightness, all network links active, Wi-Fi AP and cellular traffic
  active, all 8 audio channels running, and CPU/GPU/NPU load applied.
- The sidewall openings make reduced sealing an explicit product decision. If
  that is unacceptable or thermal limits are missed, redesign around a sealed
  air-to-air heat exchanger before production.

Use a Microchip `EMC2305` five-channel fan controller for four independent PWM
and tach channels, leaving one spare. Use three `TMP117` starting sensors near
the modem, network/Wi-Fi zone, and power/audio hot zone, plus the CM5 thermal
zone and modem internal temperature. All four fans must default to full speed
through hardware pulls if control firmware or I2C fails. Configure each Delta
`THA0412AD-TZW3` channel for 1 kHz direct-duty control with tach monitoring.

## Antenna Placement

Provide eight RF bulkheads in the right-side RF bank:

- `WIFI 1`, `WIFI 2`, `WIFI 3`, `WIFI 4`
- `CELL 1`, `CELL 2`, `CELL 3`, `CELL 4 / GNSS`

Starting mechanical rules, to be replaced by antenna-vendor and enclosure RF
test results:

- Place the four Wi-Fi bulkheads at one end of the panel and the cellular cluster at the
  opposite end. Put `CELL 4 / GNSS` farthest from Wi-Fi and switching power.
- The current mechanical panel study uses a compact 34 mm vertical pitch for
  all eight right-side bulkheads. This overrides the earlier 50 mm starting
  pitch and must be accepted only after antenna isolation/coexistence testing.
- The controlled validation set is four Taoglas `GW.05.0153` hinged RP-SMA(M)
  Wi-Fi antennas and four Taoglas `TG.66.A113` hinged SMA(M) cellular antennas.
  They remain installed and fold inboard for transport. Samples must prove the
  full hinge sweep and 8 mm closed-lid dynamic clearance; deploy them for use.
- Keep RF bulkheads/coax at least 100 mm from the C14, AC filter, PSU, and major
  switching inductors, and at least 50 mm from Ethernet magnetics and fan motors.
- Do not place antennas beneath the metal display/backplate in the lid or close
  to the XLR analog bank.
- Keep coax short, avoid tight bends, bond bulkheads to chassis, and do not run
  coax over switch nodes or parallel to HDMI, USB 3, or PCIe.
- Validate S11, isolation, throughput, TRP/TIS, GNSS acquisition, and all-radios-
  active operation in the final closed enclosure.

## Service And Debug

- Keep dual Nano-SIM access available through sealed panel features. USB
  recovery, reset, and recovery-button access are internal/underside service
  features and do not appear on the top panel.
- Keep the 3.3 V debug UART on an internal keyed header; do not expose raw TTL
  directly on the exterior.
- Make the internal USB recovery connector usable without removing the main
  carrier from the enclosure.
- Add labeled test points for `24V_PSU`, `BAT_SELECTED`, `PROTECTED_RAW`, every
  regulator output, selector status, power-good, fan PWM/tach, I2C, reset, and
  TDM clocks/data.
- Add a ground spring/loop and a test connector suitable for oscilloscope
  capture of source-transfer events.
- Add programming/test access for the fan controller, EEPROM, and any board
  management MCU.
- LEDs: primary source, backup source, battery low, system, audio clock/fault,
  Wi-Fi, cellular, and thermal/fan fault. Use integrated RJ45 link/activity LEDs
  for the four Ethernet ports.
- Make the mains fuse accessible from outside the safety barrier.

## AC Safety And EMC

- Production inlet starting part: Qualtek `719W-00/03`, C14, no switch,
  10 A/250 Vac, one active 5x20 mm fuse position plus one spare, with agency
  approvals listed by the manufacturer. RS PRO `811-7204` remains the panel
  style reference, not the production approval basis.
- Preliminary external fuse: `T6.3A H 250V` ceramic, selected finally by PSU
  inrush and protection-coordination tests. Never substitute a higher rating
  merely to stop nuisance opening.
- Use a 10 A/250 Vac agency-approved mains EMI filter, with low-leakage variant
  selected if the final product leakage-current requirement demands it.
- Put a thermally protected 275 Vac MOV after the fuse and before the PSU;
  select exact surge parts from conducted-immunity testing.
- C14 PE goes first to a dedicated chassis stud beside the inlet using a short
  green/yellow conductor, toothed washer, locking hardware, and a marked PE
  connection. Bond PSU FG and the exposed metal top panel to this point; bond
  metal sidewall reinforcement/guard parts only as required by the final EMC
  and safety construction.
- Use one deliberate low-voltage 0 V-to-chassis bond near power entry, with
  stuffing options for direct, RC, or capacitor coupling after EMC/audio test.
- Bond XLR pin 1 and connector shells to chassis at entry; do not carry pin 1
  through long digital-ground traces.
- Route the top-to-bottom mains harness in a dedicated guarded corner, using
  18 AWG, 600 V, 105 C wire, insulated terminals, strain relief, and tie-downs.
- Cover all mains terminals with a UL94 V-0 finger-safe service barrier. Keep
  mains routing and hardware away from low-voltage PCB, XLR, RF, HDMI, USB,
  fan, and Ethernet wiring.
- Begin layout with an 8 mm mains-to-SELV keepout and no copper beneath the
  safety barrier; final creepage, clearance, insulation, flammability, and
  accessibility values must be derived from the selected safety standard,
  material group, pollution degree, altitude, and agency review.
- Use a normally closed thermal cutout in the PSU enable path and a one-shot
  thermal fuse as a fire backstop near the PSU/AC bay. Final trip temperatures
  follow enclosure thermal testing; 85 C resettable and 105 C one-shot are
  preliminary starting values only.
- Design toward IEC/UL 62368-1 and applicable FCC/ICES/CE EMC requirements;
  obtain a qualified safety/EMC review before production release.

## External Connector Protection

Every external conductor receives protection at the connector boundary. The
detailed starting implementation is in `connector-protection-matrix.md`.

General rules:

- Protection devices are placed before long PCB routes.
- Chassis-return surge current does not flow through the audio/digital ground
  plane.
- High-speed arrays are selected and laid out by insertion loss and
  capacitance, not only by ESD voltage.
- Every powered port has current limiting and fault isolation.
- RF protection footprints may be `DNI` if measured RF loss is unacceptable,
  but the panel bond and layout provision remain.

## Remaining Engineering Gates

The architecture is locked, but these items still require engineering proof:

- Exact CM5 hardware revision and maximum input tolerance.
- Regulator calculations, simulation, layout, and measured load transients.
- Display, fan, modem, Wi-Fi, and full-system current measurements.
- Actual source-selector transfer time and hold-up capacitor calculation.
- PCB stackup and controlled-impedance rules.
- Final XLR level/filter/protection calculations and audio performance tests.
- Antenna models, cable assemblies, coexistence, and certified RF performance.
- Final sidewall fan centers, guards/louvers, internal baffles, dedicated
  cooling cartridges, ingress checks, and closed-case chamber test.
- Final safety standard, fuse coordination, leakage current, hi-pot, ground
  bond, surge, ESD, EFT, conducted emissions, and radiated emissions.
- OS/kernel driver validation and full-load TDM xrun/dropout testing.

## Primary Vendor References

- TI `LM5146`: https://www.ti.com/product/LM5146
- TI `LM5176`: https://www.ti.com/product/LM5176
- TI `LM61460`: https://www.ti.com/product/LM61460
- TI `LM61440`: https://www.ti.com/product/LM61440
- TI `TPS25982`: https://www.ti.com/product/TPS25982
- TI `TPS7A20`: https://www.ti.com/product/TPS7A20
- TI `TPA6132A2`: https://www.ti.com/product/TPA6132A2
- Diodes `PI7C9X2G608GP`: https://www.diodes.com/part/view/PI7C9X2G608GP
- Microchip `LAN7430`: https://www.microchip.com/en-us/product/lan7430
- Microchip `EMC2305`: https://www.microchip.com/en-us/product/emc2305
- LEMO `EGG.1B.302` family: https://www.lemo.com/en/2-pin-circular-connector
