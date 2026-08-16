# Radxa CM5 Carrier PCB

Project workspace for a custom carrier board for the Radxa CM5 compute module.

## Self-Contained Project Files

Only the current Rev J top-panel drawing and Rev K underside-floorplan drawing
are retained under `cad/`. They reserve a 15 mm four-side frame/screw keepout
and limit the suspended PCB envelopes before routing. The battery calculation
is under `docs/`. The obsolete 8.7 GB design-session recording was intentionally
removed before repository publication.

Mechanical fabrication remains on A2 `HOLD_FOR_MEASUREMENT`. The controlled
gate is `docs/fabrication-readiness-audit-a2.md`; it corrects the below-panel
stack, locks battery/antenna transport closure, and requires actual case,
monitor, dock, fan, tray, and connector samples before routing.

The ProComm field-unit photo PDF and rendered reference pages are preserved
under `references/procomm-field-unit/`.

## Current Status

- Workspace initialized.
- Official Radxa CM5 documentation and reference design identified.
- Audio architecture selected: photo-reference two-column XLR bank, left male outputs and right female inputs, with balanced 8x8 AK5558VN ADC and AK4458VN DAC over TDM.
- Capacitor/active-balanced XLR electrical reference selected from `/Users/viewvision/Desktop/ProComm enclosure and PCB boards`: THAT1206 input receivers, OPA165x/THAT1646 output drivers, coupling/filter/protection capacitors; AKM interface values must be recalculated.
- XLR bank geometry extracted from `/Users/viewvision/Desktop/2026/ProComm PCB XLRs + Transformer`: Neutrik `NC3MAV` / `NC3FAV`, 28 mm row pitch, 43.38 mm circular-center column spacing.
- Integrated headset architecture selected: ES8316 codec on a separate I2S bus,
  with headphone amplifier/driver and mic bias/preamp conditioning for a CTIA
  TRRS headset.
- Network architecture requirement added: 2x WAN, cellular WAN, 2x shared LAN, high-capacity Wi-Fi AP broadcast.
- Rev A Ethernet is locked to 1 GbE: native CM5 Ethernet for WAN1, three
  Microchip `LAN7430` controllers for WAN2/LAN1/LAN2, and an
  `PI7C9X2G608GP` PCIe switch shared with the 4T4R Wi-Fi AP module.
- Cellular modem direction locked to the ProComm native M.2 Key-B reference:
  SIM8260G-M2-class 3052 global target, 3042/3052 support, dual Nano-SIM, four
  cellular/GNSS antenna paths, and dedicated 3.8 V-class modem rail.
- Software runtime direction added: protect SIP/audio on reserved CPU resources,
  use the GPU for touchscreen UI, meters, waveform/spectrum display, and
  graphics, and reserve the NPU for future AI noise/classification and smart
  monitoring.
- Local touchscreen locked: JUNEBOX / DTM MALL `B0GK5X95D9` 15.6-inch HDMI
  touchscreen in the iM2300 lid, with USB touch and 12 V display power.
- Thermal architecture locked: four PWM/tach fans. The CM5 and modem are on the
  carrier underside with downward-facing heatsinks and attached, structurally
  supported dedicated fans. The enclosure uses a right-wall filtered intake
  and an operator-wall center-right exhaust; the top panel has no fan or mesh
  openings.
- The `RPS-400-24-C` remains bottom-mounted in a guarded hinge/display-side bay.
  Its footprint is rotated 90 degrees and shifted into the digital side, giving
  146 mm nominal separation from the audio quiet boundary to the grounded guard
  with a controlled 125 mm minimum. Enclosure-fan power/PWM harnesses stay out
  of the PSU corridor and the XLR analog quiet zone.
  The HDMI, USB-touch, and 12 V lid harness uses a separate protected corridor
  with at least 15 mm clearance to the PSU guard through service motion.
- Storage decision selected: CM5 eMMC only.
- Recovery/provisioning selected: USB recovery, debug UART, and network provisioning.
- Enclosure selected: Pelican Storm Case iM2300 with custom top panel and PCB mounted underneath.
- Top-panel connector envelope source-checked: 17.00 in x 11.733 in nominal base bezel reference.
- Power architecture selected: same ProComm source-selection baseline from
  `/Users/viewvision/Desktop/ProComm enclosure and PCB boards`, with
  bottom-panel MEAN WELL `RPS-400-24-C` 24 V AC/DC PSU as the locked
  production primary source,
  D-Tap / Gold Mount backup-source selection, telemetry, and Radxa-specific
  downstream regulators.
- Wi-Fi AP and cellular modem power are separate dedicated rails.
- No-blink primary/backup transfer is locked: with a valid backup source
  present, CM5, display, audio, headset, networking, and fan control must ride
  through source transfer without reset or mute.
- Preliminary system block diagram and power budget created; locked production
  PSU basis is `RPS-400-24-C` at 24 V / 10.5 A / 252 W convection-rated unless
  forced-air PSU cooling is intentionally designed and validated.
- AC mains entry direction selected: top-panel fused IEC C14 inlet with no
  built-in switch, using Qualtek `719W-00/03` as the production starting part;
  RS PRO `811-7204` remains the style reference.
- Main power control selected to match ProComm: E-Switch `RA812C1121`
  maintained DPST rocker. Its two isolated poles disable the LTC4421 primary
  selector and LTC4418 backup preselector; no high-current source wiring crosses
  the panel switch.
- Rev A schematic architecture, regulator starting parts, board partition,
  audio level, connector protection, antenna placement, service access, and
  AC safety/EMC direction are locked in `notes/rev-a-hardware-architecture.md`.
- Native KiCad 10 A0 projects are created under `cad/kicad/` for `PWR-SELECT`,
  `CM5-CARRIER`, and `AUDIO-8X8`. The source/status/telemetry, carrier/audio,
  fan, temperature-alert, and XLR interfaces now have 174 critical connector
  and control pin/net assignments machine-validated. The A1 carrier
  regulator tree, starting component calculations, sequencing, and hold-up
  bank are captured; all production PCB layouts remain to be completed.
- The Radxa CM5 V2.21 A0 pin allocation is controlled in
  `notes/cm5-pin-allocation-a0.md` and
  `outputs/cm5-pin-allocation-a0/radxa_cm5_pin_allocation_a0.xlsx`. The audit
  contains 76 unique physical pins with no duplicate claims or source/mux
  mismatches. The monitor USB2 touch test and final `VCC_SYSIN` tolerance check
  remain release actions.

## Official References

- Radxa CM5 download page: https://docs.radxa.com/en/som/cm/cm5/download
- Radxa CM5 hardware interface page: https://docs.radxa.com/en/som/cm/cm5/hardware/hw-interface
- Radxa CM5 IO reference design: https://github.com/radxa/radxa-cm-projects/tree/main/cm5/radxa-cm5-io-board
- ProComm field unit photo documentation:
  `references/procomm-field-unit/procomm-field-unit-photo-documentation.pdf`

## Local Folders

- `cad/` - schematic and PCB design files
- `cad/kicad/` - native three-project KiCad A0 capture and interface validator
- `docs/` - datasheets, PDFs, pinout exports, design notes
- `fabrication/` - Gerbers, drill files, assembly files, BOM exports
- `notes/` - requirements and review notes
- `outputs/` - controlled engineering workbooks and review deliverables
- `references/` - vendor reference designs and imported examples

## Active Notes

- `notes/rev-a-hardware-architecture.md` - locked Rev A schematic architecture and release gates
- `notes/cm5-pin-allocation-a0.md` - controlled CM5 V2.21 pin ownership,
  mux exclusions, and schematic-integration actions
- `notes/connector-protection-matrix.md` - external-connector ESD, surge, and current-limit plan
- `notes/audio-tdm-architecture.md` - AK5558VN/AK4458VN TDM plan and CM5 pin candidates
- `notes/enclosure-mechanical.md` - Pelican iM2300 enclosure constraints
- `notes/headset-audio.md` - integrated 3.5 mm headset jack plan
- `notes/legacy-procomm-reference.md` - reference review of previous ProComm enclosure/PCB folder
- `notes/network-architecture.md` - WAN/LAN/Wi-Fi architecture options
- `notes/network-module-selection.md` - selected network, Wi-Fi AP, and cellular modem-slot direction
- `notes/power-architecture.md` - bottom-mounted 24 V AC/DC PSU plus D-Tap and Gold Mount power plan
- `notes/pre-schematic-open-decisions.md` - remaining decisions before schematic capture
- `notes/procomm-capacitor-xlr-audio-reference.md` - active capacitor-coupled XLR electrical reference from prior ProComm board
- `notes/software-runtime-architecture.md` - CPU partitioning and GPU/VPU/NPU offload plan for SIP/audio reliability
- `notes/system-block-diagram.md` - top-level power, data, audio, network, modem, display, and thermal block diagram
- `notes/power-budget.md` - first-pass power budget and locked production PSU margin check
- `notes/no-blink-power-transfer.md` - seamless primary/backup transfer requirements and validation plan
- `notes/power-regulators-a1.md` - calculated A1 regulator tree, selected parts,
  sequencing, hold-up, source-current checks, and release tests
- `notes/thermal-fans.md` - CPU and enclosure fan control plan
- `docs/thermal-control-firmware-spec.md` - Linux device-tree, driver,
  thermal-service, watchdog, fail-safe, and qualification specification for
  board-controlled fan speed
- `docs/power-telemetry-software-spec.md` - three-channel INA228 hardware map,
  carrier harness, Linux hwmon integration, touchscreen fields, calibration,
  backup-runtime method, and future firmware release checklist
- `notes/top-panel-layout.md` - source-checked iM2300 connector-panel layout envelope
- `notes/main-power-switch.md` - exact ProComm-matching DPST switch, cutout,
  harness, wiring, and acceptance tests
- `notes/xlr-bank-reference.md` - extracted Neutrik XLR bank geometry from the legacy ProComm XLR KiCad folder
- `notes/requirements.md` - product requirements draft
- `notes/bringup-checklist.md` - board bring-up checklist
- `notes/cellular-modem-reference.md` - native M.2 B-Key cellular modem reference adapted from ProComm
- `docs/power_budget_preliminary.csv` - CSV version of the preliminary power budget
- `docs/source_current_check_preliminary.csv` - CSV source-current check for 24 V, D-Tap, and Gold Mount operation

## Remaining Detailed-Capture Work

The architecture and native CAD tool are selected. Complete these engineering
inputs before layout:

- Final CM5 `VCC_SYSIN` tolerance/setpoint release and monitor USB2 touch test
- Six-layer-or-greater controlled-impedance PCB stackup from the fabricator
- Controlled power footprints, final passive land patterns, placement/thermal
  review, safety review, and final mechanical CAD
- Bench measurements for display, modem, Wi-Fi, fans, audio, transfer, and thermal load
- Manufacturing target: prototype only or assembly-ready production files

## Version Control Policy

- Canonical repository: https://github.com/omaralabed/Radxa-CM5-PCB
- `main` holds the latest reviewed project state.
- After each completed controlled design update, run the applicable validation,
  create a focused commit, and push it to `origin/main`.
- Do not commit temporary renders, editor state, KiCad session files, or local
  scratch data covered by `.gitignore`.
