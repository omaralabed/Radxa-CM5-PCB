# Schematic Release Status A1

## Decision

**Electrical capture is complete. PCB placement and routing remain held.**

The native KiCad source consists of sixteen controlled sheets across
`PWR-SELECT`, `CM5-CARRIER`, and `AUDIO-8X8`. The complete deterministic review
gate passes without source drift.

## Passed Gates

- All sixteen sheets: zero ERC errors after controlled classification of
  intentional off-sheet labels and unused package pins.
- PWR-SELECT: zero ERC errors/warnings, 186 critical checks, 111 exact BOM
  components, reverse-polarity controls, source thresholds, telemetry ranges,
  current limit, and hold-up calculations pass.
- CM5-CARRIER/AUDIO-8X8 interface contract: 174 critical connector and control
  pin/net assignments pass.
- Power-Regulators-A1: 44 regulator, inductor, rail, source-current, and hold-up
  checks pass; the production BOM has 151 controlled rows.
- Thermal-IO: 15 part, sensor-grade, fan-protection, and hot-current checks pass.
- Network-PCIe: 21 controlled-part and architecture checks pass.
- WWAN-SIM: 14 modem, SIM, protection, and RF-harness checks pass.
- Display-Harness: 20 HDMI, USB touch, 12 V monitor, and IO-5 V checks pass.
- Audio-Control: 22 TDM, I2S1, ES8316, headset-amplifier, CTIA, and grounding
  checks pass.
- AUDIO-8X8: 381 checks across seven detailed sheets pass; the generated BOM
  has 500 rows.
- Cross-board XLR, fan, temperature, telemetry, source-control, TDM, and audio
  power assignments pass.

## Physical Gates Before PCB

The component audit covers 1038 schematic components. Ten routing blockers are
deliberately retained for physical evidence:

- AK5558VN exposed-pad/via/stencil coupon and X-ray signoff;
- AK4458VN exposed-pad/via/stencil coupon and X-ray signoff;
- eight Panasonic TQ2-12V relay insertion, seating, and pin-map signoffs.

The Kycon STX-353K7A-6N-KTTR headset jack is route-ready at the schematic level
but remains blocked from production until its sample, plated-hole, bezel,
switch-polarity, and CTIA coupon pass. Total production blockers: 11.

Mechanical A2 remains `HOLD_FOR_MEASUREMENT`. Board outlines, connector Z
datums, support coordinates, sidewall machining, and panel cut files cannot be
released until M001-M080 is completed on the actual hardware and the mechanical
release validator passes.

## Controlled Commands

```sh
cad/kicad/review_detailed_capture.sh
python3 cad/kicad/audit_footprint_readiness.py
python3 cad/kicad/audit_footprint_readiness.py --routing
python3 fabrication/mechanical-release/validate_mechanical_release.py --release
python3 fabrication/pcbway-release/validate_release.py --release
```

The last three release-mode commands are expected to fail until their physical
evidence is attached. Do not replace those failures with assumptions.

