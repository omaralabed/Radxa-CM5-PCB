# Legacy ProComm Reference Review

## Source

Reference folder:

`/Users/viewvision/Desktop/ProComm enclosure and PCB boards`

Use this folder as engineering reference only. The Radxa CM5 carrier layout and
digital converter design will be different.

This folder contains the capacitor/active-balanced XLR electrical reference:

- Input: `NC3FAV2 -> THAT1206 -> coupling/filter capacitors -> PCM1861`
- Output: `PCM5102A -> OPA165x -> THAT1646 -> coupling/protection capacitors -> NC3MAV`

For Radxa, use this as the analog line-stage/protection reference, but replace
the PCM1861/PCM5102A converter portions with AK5558VN/AK4458VN. The extracted
electrical notes are captured in `notes/procomm-capacitor-xlr-audio-reference.md`.

Additional XLR geometry source:

`/Users/viewvision/Desktop/2026/ProComm PCB XLRs + Transformer`

Use the additional XLR folder for connector size, row/column pitch, and
footprint geometry. The extracted measurements are captured in
`notes/xlr-bank-reference.md`.

## Useful References To Reuse

- Pelican/iM2300-style rugged field-unit design language
- Lid-mounted operator display concept
- Top/base panel with electronics underneath
- Coordinate-controlled mechanical floorplan method
- Connector datums, keepouts, harness-register discipline, and release gates
- Panel-fastened XLR strategy so cable insertion force is carried by the enclosure
- Neutrik A-series XLR mechanical references
- Neutrik `NC3MAV` / `NC3FAV` XLR size and spacing from the old XLR KiCad
  board: 28 mm row pitch and 43.38 mm circular-center column spacing
- Balanced input/output analog front-end ideas:
  - THAT1206-class balanced input receivers
  - THAT1646-class balanced output drivers
  - Bipolar coupling capacitors, RFI capacitors, rail clamps, ferrites, and
    chassis-return protection networks from the capacitor XLR boards
  - RFI/ESD/protection networks at connector boundary
- Cellular M.2 Key-B/socket, dual-SIM, antenna, and modem-power planning ideas
- Implemented 24 V / D-Tap / Gold Mount source-selection schematic in
  `/Users/viewvision/Desktop/ProComm enclosure and PCB boards/PCB_SOURCE/POWER_SELECTOR_24V_BATTERY`;
  use this as the Radxa no-blink transfer starting point
- Fan/thermal release-gate thinking

## Power Selector Reference

The ProComm folder already implements the source-transfer concept as
`PowerSelector` Rev C.

What to reuse as the Radxa starting point:

- Fixed priority: primary 24 V, then D-Tap/LEMO, then Gold Mount
- D-Tap and Gold Mount are never paralleled
- `LTC4418` backup preselector feeding `BAT_SELECTED`
- `LTC4421` main prioritized selector feeding protected raw DC
- Back-to-back MOSFETs for reverse/cross-current blocking
- Separate low-current DPST power switch enable harness
- Fail-off pulldowns on both selector shutdown nets
- Status/telemetry outputs to the carrier
- Raw-output hold-up concept and oscilloscope transfer validation requirement

Radxa-specific items recalculated at A1 and still requiring bench/release
validation:

- Input thresholds for the locked internal `RPS-400-24-C` primary PSU and
  backup sources
- MOSFET SOA and copper temperature rise for the new current budget
- Fuse/eFuse ratings and connector/wire current ratings
- Hold-up capacitance needed for no-blink transfer with HDMI touchscreen,
  8x8 AKM audio, Wi-Fi AP, cellular, Ethernet, and four fans active
- Downstream regulator behavior, especially the 12 V display rail on battery
  backup
- Telemetry scaling and GPIO routing to the Radxa CM5 carrier

## Do Not Reuse Directly

- Do not submit old KiCad/Gerber/BOM files for the Radxa design.
- Do not copy the old 5-input/5-output PCM1861/PCM5102A converter architecture.
- Do not copy Raspberry Pi/old CM5 GPIO, DSI, or audio-lane assignments.
- Do not copy the old side-panel XLR layout; Radxa unit uses a left-side audio bank with 8 male XLRs and 8 female XLRs.
- Do not copy the old transformer board's analog circuit or routing directly;
  use it for XLR size/spacing only unless transformers are intentionally
  selected later.
- Do not copy old display electrical assumptions; Radxa unit uses HDMI plus USB touch unless changed later.
- Do not copy old Wi-Fi/cellular antenna assumptions without the exact Radxa module and modem choices.
- Do not copy the old power-load budget directly; Radxa has different display, audio, Wi-Fi, cellular, Ethernet, and fan loads.
- Do not order the old PowerSelector board unchanged; use it as a proven
  topology/reference and resize it for Radxa.

## Radxa-Specific Direction

The new Radxa CM5 board keeps the rugged ProComm field-unit style, but changes
the architecture:

- Radxa CM5 compute module
- AK5558VN + AK4458VN balanced 8x8 TDM program audio
- ES8316 headset codec on a separate I2S bus
- Two wired WAN ports, cellular WAN, two shared LAN ports
- Wi-Fi AP broadcast for about 25 devices
- HDMI + USB lid-mounted touchscreen
- CM5 eMMC-only boot with USB recovery, debug UART, and network provisioning
- CPU fan plus two enclosure fans
- ProComm-style rear 24 V > D-Tap > Gold Mount power source priority, with Radxa-specific regulator/load-budget redesign
- No-blink/no-mute source transfer using the implemented ProComm PowerSelector
  topology, with Radxa-specific hold-up and regulator validation

## Action Items

- Import only exact manufacturer footprints/STEP models that still match selected parts.
- Build a new Radxa bus/pin budget before schematic capture.
- Create a new Radxa mechanical floorplan based on the Pelican iM2300 and current 8x8 XLR/top-panel requirements.
- Treat the old XLR input/output schematics as analog topology examples, not as production circuitry.
