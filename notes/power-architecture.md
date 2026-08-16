# Power Architecture

## Decision

Use the same ProComm power/source-selection architecture from
`/Users/viewvision/Desktop/ProComm enclosure and PCB boards` as the Radxa CM5
baseline, with a locked internal bottom-mounted MEAN WELL `RPS-400-24-C` 24 V
AC/DC PSU as the primary 24 V source.

The ProComm source-selection architecture is reused intentionally: protected
24 V first, D-Tap second, Gold Mount third, LTC4418 backup preselector, LTC4421
main selector, back-to-back MOSFET blocking, fusing/protection, telemetry, and
a protected raw-DC output feeding the carrier regulators.

Rev A telemetry is now captured with three `INA228AIDGSR` monitors: primary at
`0x40`, selected backup at `0x41`, and delivered `RAW_OUT_LOAD` at `0x44`.
PWR-SELECT `J402` mates with CM5-CARRIER `J103` on the 3.3 V control I2C bus.
The software and future-release requirements are controlled in
`../docs/power-telemetry-software-spec.md`.

Radxa changes are downstream of the protected raw-DC output. The final
regulator/load budget must be recalculated for the Radxa CM5, HDMI touchscreen,
8x8 AKM audio, Wi-Fi AP, cellular modem, Ethernet ports, headset codec, and
four fans.

Power reference files:

- `/Users/viewvision/Desktop/ProComm enclosure and PCB boards/POWER_ARCHITECTURE.md`
- `/Users/viewvision/Desktop/ProComm enclosure and PCB boards/ADVANCED_SCHEMATIC_WORK/POWER_ARCHITECTURE.md`
- `/Users/viewvision/Desktop/ProComm enclosure and PCB boards/ADVANCED_SCHEMATIC_WORK/POWER_SELECTOR_README.md`
- `/Users/viewvision/Desktop/ProComm enclosure and PCB boards/PCB_SOURCE/POWER_SELECTOR_24V_BATTERY`
- `/Users/viewvision/Desktop/ProComm enclosure and PCB boards/PCB_SOURCE/POWER_SELECTOR_24V_BATTERY/PowerSelector.kicad_sch`
- Controlled local baseline: `cad/kicad/PWR-SELECT/BASELINE_SOURCE.md`
- Current local A0 ERC: `cad/kicad/PWR-SELECT/REVIEW/PowerSelector-A0-ERC.rpt`
- Local Radxa budget note: `power-budget.md`

## Source Priority

Power-source priority:

1. Internal 24 V AC/DC PSU output
2. D-Tap / 2-pin LEMO alternate backup input
3. Gold Mount battery dock

The D-Tap and Gold Mount sources are never paralleled. A valid D-Tap source
takes priority over the Gold Mount battery. The internal 24 V PSU takes
priority over both backup sources.

## No-Blink Transfer Requirement

Power transfer between the primary 24 V PSU and a valid backup source must not
interrupt the product. The design target is no CM5 reset, no touchscreen blink,
no audio mute/click, no Ethernet/Wi-Fi/cellular reset, and no fan-controller
reset during source transfer.

This is a hard requirement only when a valid backup source is present before
the primary source is removed. If no backup source is valid, the unit may shut
down gracefully.

Implementation rule:

- Use the cascaded `LTC4418` and `LTC4421` source-selection architecture with
  correctly sized back-to-back MOSFETs, sense resistors, UV/OV thresholds,
  validation delays, and current-limit timers.
- Rate the low-voltage source path for at least 15 A and recalculate the old
  10 A-class sense setting for at least a 14 A operating threshold after
  tolerance analysis.
- Add a 22,000 uF nominal / 50 V protected raw-DC starting bank after the
  source selector, with controlled precharge and stuffing room up to 47,000 uF.
- Add local hold-up on critical downstream rails.
- Ensure every regulator remains in regulation across 24 V PSU operation,
  13.0-16.8 V D-Tap/LEMO operation, Gold Mount operation, wiring drop,
  MOSFET/fuse/eFuse drop, and transfer droop.
- Use a buck-boost or equivalent topology for `DISPLAY_12V` if the display must
  remain at 12 V during battery operation and source transfer.
- Do not shed noncritical loads until after the transfer is complete and the
  system has logged the new power source.

Detailed local note: `no-blink-power-transfer.md`.

The existing ProComm implementation already captures the intended behavior as a
Rev C schematic in
`/Users/viewvision/Desktop/ProComm enclosure and PCB boards/PCB_SOURCE/POWER_SELECTOR_24V_BATTERY`.
Use that schematic as the electrical starting point, not the older rejected
power board. Do not order or copy it unchanged for Radxa; the Radxa load,
primary PSU, display rail, connector partition, source-current telemetry, SOA,
hold-up capacitance, and thermal behavior must be recalculated.

## Power Path

```text
Top-panel fused C14 inlet, no switch -- EMI/PE -- bottom-mounted RPS-400-24-C PSU -- 24V_PSU -- protection --\
                                                                                                                > LTC4421 main selector -- protected raw DC -- carrier regulators -- system rails
LEMO EGG.1B.302.CLL backup inlet 13.0-16.8 V -- protection --\                       /
                                      > LTC4418 backup preselector -- BAT_SELECTED --/
Gold Mount battery ---- protection --/
```

Downstream rail split:

```text
protected raw DC
  -> main 5.15 V-class CM5/system rail
  -> separate 3.3 V Wi-Fi AP rail
  -> separate 3.8 V-class cellular modem rail
  -> clean audio analog/digital rails
  -> display/touch power rail, buck-boost if 12 V must ride through backup
  -> fan power rail, buck-boost if 12 V fans must ride through backup
  -> Ethernet controller/switch rails
```

The Wi-Fi AP rail and cellular modem rail are separate supplies. They must not
share one undersized 3.3 V peripheral rail, because radio transmit bursts can
pull down or inject noise into the rest of the system.

See `power-budget.md` for the current first-pass load table. The locked
production PSU basis is the `RPS-400-24-C` used at its 24 V / 10.5 A / 252 W
convection rating unless forced-air PSU cooling is intentionally designed and
validated.

## Primary 24 V AC/DC PSU

Locked production PSU:

- PSU: MEAN WELL `RPS-400-24-C`
- Type: covered/enclosed, chassis-mount AC/DC converter
- Mounting: bottom panel, not the top panel
- AC input: 80-264 Vac universal input
- DC output design basis: 24 V, 10.5 A, 252 W convection-rated
- Forced-air rating: about 400 W class; do not claim or depend on this unless
  validated PSU airflow and heat exit are designed into the enclosure
- Mechanical envelope: about 130 x 86 x 43 mm
- Useful support outputs/signals: 5 V standby, 12 V fan output, power-good/fail,
  remote sense
- Cooling: use the 252 W convection rating for the sealed iM2300 design basis;
  temperature rise must still be tested with the final bottom-panel mounting
  and internal airflow pattern
- Safety class: design as a Class I installation unless a full Class II
  integration is intentionally engineered; bond PSU metal case/chassis to PE

The top panel carries the PCB/connector panel plus the selected IEC C14 mains
inlet. Do not mount the AC/DC PSU on the top panel. The PSU remains on the
bottom panel and feeds the carrier/source-selector assembly through a protected
low-voltage `24V_PSU` harness.

## Top Panel AC Mains Inlet

Locked style and production starting part:

- Required style: IEC 60320 C14 male appliance inlet with integrated fuse
  holder and no built-in switch
- Production starting part: Qualtek `719W-00/03`
- Rating: 10 A, 250 Vac
- Fuse holder: one active 5 x 20 mm fuse position and one spare
- Termination: 4.8 mm quick-connect tabs
- Mounting: flanged panel mount
- Manufacturer-listed approvals: UL, CSA, TUV, and CCC; confirm the ordered
  suffix and current agency file at release
- Panel/style reference retained: RS PRO `811-7204`

Do not use the switched C14 module direction. The IEC inlet should not contain
a rocker switch. The user/system power switch remains the separate low-current
selector-enable switch described below.

The selected 10 A/250 Vac inlet is sufficient for the `RPS-400-24-C` input
current. Do not print or advertise a separate 15 A/125 Vac inlet rating unless
the final ordered connector and agency file explicitly support that claim.

Use a gasketed cover or sealed external door around the inlet if the product
must retain its rugged sealing rating. The inlet alone is not the enclosure
seal.

The AC side needs its own mechanical/electrical integration:

- Top-panel fused C14 inlet, strain relief, optional interlock, and EMI filter
- Protective-earth/chassis bond near the inlet and PSU mounting
- Mains wiring from the top-panel inlet to the bottom-panel PSU kept short,
  guarded, strain-relieved, and physically separated from audio, RF, Ethernet,
  HDMI, USB, fan, and low-voltage harnesses
- Finger-safe guard/cover or service barrier around AC terminals and exposed
  mains wiring
- Creepage/clearance, wire gauge, connector current rating, pull test, and
  safety-label plan reviewed before any powered prototype

The previous Bel/CUI `VOF-120C-24-CNF` 120 W PSU is no longer the production
baseline. Keep it only as a prior candidate/prototype reference if needed.

The previous ProComm external MEAN WELL `GST120A24-R7B` / Kycon `KPJX-4S-S`
24 V inlet approach is now a fallback/reference only, not the selected primary
source for this Radxa CM5 build.

## Production PSU Direction

The MEAN WELL `RPS-400-24-C` is locked as the production PSU baseline. Treat
the 252 W convection rating as the design rating for the sealed iM2300 unless
forced-air PSU cooling is intentionally added and verified.

Recommended production target:

- Primary candidate: MEAN WELL `RPS-400-24-C`
- Output for our sealed/recirculating design basis: 24 V, 10.5 A, 252 W
  convection-rated
- Forced-air rating: about 400 W class, but do not claim or depend on this
  unless the enclosure design provides validated PSU airflow and thermal exit
- Input: 80-264 Vac universal
- Type: covered/enclosed medical AC/DC supply, chassis mount
- Size: about 130 x 86 x 43 mm
- Useful extras: 5 V standby, 12 V fan output, remote sense, power-good/fail
  signals
- Why: gives better margin than the 200 W candidates while staying close to
  the same bottom-panel footprint class.

Good alternate:

- TDK-Lambda `CUS200M-24/A`
- Output: 24 V, 8.4 A, 200 W convection / 250 W forced-air class
- Input: 85-265 Vac universal
- Type: enclosed / chassis mount
- Size: 139.7 x 90.0 x 43.0 mm
- Why: high-quality production alternate with useful headroom above the current
  151.7 W continuous estimate and 184.2 W transient estimate.

Compact open-frame variant:

- TDK-Lambda `CUS200M-24`
- Output: 24 V, 8.4 A, 200 W convection / 250 W forced-air class
- Input: 85-265 Vac universal
- Type: open frame / chassis mount
- Size: 127.0 x 76.2 x 31.0 mm
- Use only if the product design adds a proper finger-safe AC/service barrier,
  mounting standoffs, strain relief, and isolation from low-voltage wiring.

Smaller but lower-margin option:

- Bel Power / CUI `VOF-130-24-CNF`
- Output: 24 V, 5.4 A, 130 W
- Input: 80-264 Vac universal
- Type: enclosed / chassis mount
- Size: 91.4 x 64.0 x 34.5 mm
- This is the compact same-family upgrade, but it does not give enough margin
  for the current all-load transient estimate.

Low-cost/available mechanical backup:

- MEAN WELL `UHP-200-24`
- Output: 24 V, 8.4 A, about 202 W
- Input: 90-264 Vac universal
- Type: enclosed / chassis mount, slim fanless body
- Size: 194.0 x 55.0 x 26.0 mm
- Attractive for cost and availability, but its long, narrow shape and
  integration style need mechanical and EMC review before choosing it over the
  primary production candidate.

Production rule: design the bottom-panel PSU bay around the `RPS-400-24-C` /
`CUS200M-24/A` footprint class unless later measurements prove that a smaller
130 W or 150 W supply has safe thermal margin in the sealed enclosure.

## D-Tap / LEMO Backup Input

Reuse the previous ProComm alternate backup input concept:

- Function: backup power input only, not a charger
- Panel inlet: genuine LEMO `EGG.1B.302.CLL`, 15 A rated starting part
- Polarity: pin 1 return, pin 2 backup positive
- Intended operating range: 13.0-16.8 V DC
- Typical D-Tap valid threshold: 12.62 V rising, 12.25 V falling
- Overvoltage rejection around 18 V
- A 24 V supply must not be connected to this input
- Full reverse-polarity application must be non-destructive

The prior `EGG.0B.302.CLL` is rated 10 A and is rejected for Rev A because the
current budget reaches about 11.54 A at 13.0 V during the all-load transient.
Use the matching 1B cable connector, wire, fuse, MOSFETs, PCB copper, and source
path rated for at least 15 A. If an upstream D-Tap connector, cable, or source is
only rated 10 A, software must enforce a verified backup-load limit after the
no-blink transfer, or that cable cannot be approved for full-load operation.

The D-Tap/LEMO input feeds the LTC4418 backup preselector ahead of the Gold
Mount source.

## Gold Mount Battery

Reuse the previous ProComm Gold Mount direction:

- Battery basis: Anton/Bauer Dionic XT 90 Gold Mount, SKU `8675-0125`
- Nominal battery voltage: 14.1 V
- Capacity: 99 Wh
- Maximum continuous current: 12 A
- Battery envelope: 99 x 132 x 58 mm
- Dock basis: Anton/Bauer QRC-GOLD Universal Compact Gold Mount Bracket, SKU
  `8375-0094`; approximately 119.4 x 76.2 x 12.7 mm excluding the release latch
- Mechanical ownership: top panel/custom frame only; the dock is not mounted
  to or mechanically supported by any PCB
- Electrical interface: short, fused, strain-relieved positive/negative flying
  leads through a keyed removable high-current harness to power-selector `J203`
- Battery charging is external; no onboard charger unless a future battery
  protocol is explicitly selected and documented.

The exact QRC-GOLD polarity, mounting datum, latch travel, clearance, and main
power-path temperature rise at 12 A still need to be verified from manufacturer
documentation and a measured production sample.

## Selector Architecture

Use the cascaded selector concept:

- LTC4418 selects between D-Tap and Gold Mount.
- LTC4421 selects between `24V_PSU` and `BAT_SELECTED`.
- Back-to-back MOSFETs provide reverse/cross-current blocking.
- Each input has independent fusing/eFuse, surge/ESD protection, UV/OV windows,
  and current/thermal validation.
- Hold-up is required on the protected raw-DC output and critical downstream
  rails so source transfer does not reset, blink, or mute the system.
- Protected raw DC feeds the Radxa carrier regulator system.
- The ProComm Rev D telemetry concept is reused: monitor rear/primary source,
  selected backup source, and protected raw DC delivered to the carrier, with
  final shunt values and INA228 ranges recalculated if the Radxa load budget
  changes them.

Implemented ProComm Rev C reference points:

- Main selector: ADI `LTC4421IUHE#PBF`
- Backup preselector: ADI `LTC4418IUF#PBF`
- Main-path MOSFET candidate: Nexperia `PSMN4R2-80YSE`
- Backup reverse-protection MOSFET candidate: Vishay `SiR5607DP-T1-RE3`
- Input fuses: 15 A Littelfuse Nano2 class in the old schematic
- Raw output connector: `RAW_OUT_TO_LM5176`
- Raw-output bulk in old schematic: 3 x 220 uF / 50 V polymer plus ceramics
- Main current-sense value in old schematic: 2.50 mOhm, giving a 10 A-class
  selector current limit with the LTC4421 25 mV sense threshold
- Status outputs in old schematic include channel/valid status and battery-low
  telemetry to the carrier

For Radxa, preserve the topology and behavior. Recalculate part ratings,
thresholds, fuse values, sense values, timer values, connector current rating,
trace/copper width, inrush current, hold-up capacitance, and thermal rise for
the locked `RPS-400-24-C` PSU and the new 8x8/audio/network/display load.

## User Power Switch

Reuse the previous switch concept:

- Maintained DPST rocker: E-Switch `RA812C1121`
- Capture this in KiCad as `SW201` through keyed four-circuit harness `J204`,
  matching the ProComm low-voltage control circuit and not the IEC C14 inlet.
- One pole enables the LTC4421 main selector.
- One pole enables the LTC4418 backup preselector.
- No high-current system load crosses the panel switch.
- No AC mains should cross the user power switch unless a future safety review
  intentionally changes the AC entry architecture.
- OFF or disconnected switch harness must fail safely to source-selector
  shutdown.
- Retain separate 47 kOhm pull-downs on `SHDN_MAIN` and `SHDN_PRE`; do not tie
  the two controller INTVCC rails together.

The PCB uses Molex Micro-Fit 3.0 header `43045-0412` at `J204`. The panel harness
uses housing `0430250400`, four contacts `0430300007`, four 22 AWG conductors,
and four insulated TE `2-520182-2` FASTON receptacles. The rocker is not mounted
directly to the PCB.

## Radxa System Rails

The Rev A regulator tree is locked for schematic capture. Exact passives,
compensation, copper, and thermal design still require calculation.

| Rail | Target | Starting part/topology |
| --- | ---: | --- |
| `SYS_5V15` | 5.15 V / 12 A | `LM5146` synchronous buck controller with external MOSFETs |
| `AUX_12V` | Revised 12 V / 8 A minimum target | `LM5176` four-switch buck-boost; recalculate and bench-qualify A1 stage |
| `DISPLAY_12V` | 12 V / 2.5 A | Simple fused harness branch from `AUX_12V`; no dedicated display eFuse/current limiter; 25 W / 2.08 A rated monitor load |
| `NIGHT_LIGHT_12V` | 12 V / 0.25 A protected branch | Two YIS Marine LS102W warm-white courtesy lights and one E-Switch CS7L2FR latching touch control; independent of CM5 software |
| `FAN_CPU_12V` | 12 V / 3 A | Protected Delta CPU-fan branch from `AUX_12V` |
| `FAN_AUX_12V` | 12 V / 3 A | Protected modem/enclosure-fan branch with local protection per fan |
| `MODEM_3V8` | 3.8 V / 6 A converter | `LM61460` plus `TPS25982` eFuse; 5 A minimum usable load |
| `WIFI_3V3` | 3.3 V / 4 A | Dedicated `LM61440` plus controlled load switch |
| `NET_3V3` | 3.3 V / 4 A | Separate `LM61440` |
| `PCIE_1V0` | 1.0 V / 2 A | Point-of-load buck for PCIe-switch core |
| `LOGIC_3V3` | 3.3 V / 3 A | Dedicated carrier-logic buck |
| `LOGIC_1V8` | 1.8 V / 1.5 A | Point-of-load regulator |
| `AUDIO_BIPOLAR` | +/-15 V, 20 W class | `TRI 20-1223` starting module plus pi/common-mode filtering |
| `AKM_5V_A` | Clean 5.0 V | Quiet pre-regulator plus `LT3045` |
| `HEADSET_3V3` | Clean 3.3 V | Separate `TPS7A20`-class LDO |

Selected separation rule:

- CM5/system 5.15 V rail is separate from radio rails.
- Wi-Fi AP gets its own switched/local 3.3 V rail sized for AP transmit duty.
- Cellular modem gets its own switched/protected 3.8 V-class rail sized for 5G
  registration and transmit bursts.
- Audio analog rails stay clean and filtered away from Wi-Fi/cellular current
  pulses.
- Headset codec/amplifier power gets its own local low-noise regulator/filter
  path and should not be fed directly from noisy system, radio, fan, USB, or
  Ethernet rails.
- Ethernet controller/switch rails follow their own regulator and sequencing
  requirements.
- Critical rails must ride through source transfer. `SYS_5V15`, modem, Wi-Fi,
  audio, headset, `AUX_12V`, and display rails must not brown out when the
  selected source steps from 24 V PSU to backup voltage.
- `AUX_12V` is buck-boost so both display and fan branches remain at 12 V on
  the 13.0-16.8 V backup source and during transfer droop.

The prior 5.15 V / 9 A target is not accepted as final. The Radxa design should
start with at least a 5.15 V / 12 A-class continuous engineering target until a
full worst-case load budget proves otherwise.

## Network And Radio Rail Rules

The WAN, LAN, Wi-Fi, and cellular power rails must be designed from the exact
selected controller/module datasheets. Do not infer supply voltage only from the
connector type.

- Do not route raw 24 V or battery voltage to WAN/LAN RJ45 ports unless a future
  PoE feature is explicitly selected. PoE is not part of the current design.
- RJ45 ports need magnetics, ESD/protection, shield/chassis treatment, and LED
  power as required by the Ethernet PHY/controller.
- Native CM5 Ethernet can follow the Radxa reference power/interface treatment
  for the CM5 MDI pairs and external magnetics.
- The three added Ethernet ports use `LAN7430` controllers from `NET_3V3`.
  Follow the Microchip reference for each controller's external 1.2 V switcher
  and 2.5 V LDO parts. The `PI7C9X2G608GP` PCIe switch uses `NET_3V3` and a
  separate `PCIE_1V0` core rail with datasheet sequencing/reset timing.
- Wi-Fi AP hardware, likely PCIe/M.2 or a dedicated AP module, should receive a
  strong local rail, commonly 3.3 V for M.2-style modules, with load switching,
  inrush control, bulk capacitance, and thermal margin sized for AP transmit
  duty. This rail is separate from the cellular modem rail and should be kept
  away from clean audio rails. Final voltage/current come from the exact module.
- Cellular modem power must be a dedicated high-peak-current rail for the M.2
  B-Key WWAN socket. The ProComm reference uses a 3.8 V-class 5 A buck concept
  for SIM8260G-M2. Start with at least 1000 uF low-ESR bulk near the M.2 socket
  plus ceramics, then tune from the selected modem guide and scope results.
  Include modem enable, reset, power-cycle control,
  current measurement/protection, and bulk capacitance close to the modem power
  pins. This rail is separate from the Wi-Fi AP rail and the CM5/system 5.15 V
  rail.
- SIM/eSIM power is not a boardwide fixed rail. SIM voltage, commonly 1.8 V or
  3.0 V, should come from or be controlled by the selected modem with the proper
  ESD protection and routing.

## Do Not Reuse Directly

- Do not use the old `/Users/viewvision/Desktop/2026/PCB Power Circuit` board.
- Do not order the old selector board as-is for the Radxa product until the
  Radxa current budget, connector pinout, telemetry, thermal behavior, and board
  partition are reviewed; use it as the electrical baseline.
- Do not assume the old DSI-display load budget applies to the HDMI touchscreen.
- Do not assume the old 5-channel audio power budget applies to the new 8x8
  AKM balanced audio system.

## Release Gates

The Radxa power design is not ready for fabrication until:

- Final display sample, Wi-Fi module, cellular modem, fan, and audio analog
  parts are received and measured.
- Bottom-mounted PSU, AC inlet, fuse/EMI/PE wiring, service barrier, and
  low-voltage harness routing are mechanically released.
- Worst-case load budget and transient budget are closed.
- Source selector schematic and PCB pass ERC/DRC and manual power-path review.
- Regulator thermals, MOSFET SOA, fuse/eFuse sizing, hold-up capacitance, and
  connector temperature rise are calculated and tested.
- Source transfer is verified on a prototype: AC PSU arrival/loss, D-Tap
  insertion/removal, Gold Mount operation, low-battery shutdown, reverse
  polarity, overvoltage rejection, no-blink/no-mute transfer, and load-step
  stability.
