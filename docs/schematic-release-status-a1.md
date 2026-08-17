# Schematic Release Status A1

## Decision

**Electrical capture is complete. PCB placement and routing remain held.**

The native KiCad source consists of sixteen controlled sheets across
`PWR-SELECT`, `CM5-CARRIER`, and `AUDIO-8X8`. The complete deterministic review
gate passes without source drift. Open
`cad/kicad/SYSTEM/Radxa-CM5-ProComm-System.kicad_pro` for one native KiCad
entry point to the complete design. Page 1 is the real system electrical
interconnect and pages 2-17 contain the component-level circuits. Its system
representations cannot update a PCB.

## Passed Gates

- All three electrically authoritative board roots: `0 errors / 0 warnings`.
  Standalone child-sheet context findings match the review script's exact
  allowlist; any new or changed finding fails the gate.
- Complete-system project: page 1 contains 58 electrical symbols and 294 named
  pin interconnects; all sixteen source sheets are present, and its A2 PDF
  export contains exactly 17 pages.
- PWR-SELECT: zero ERC errors/warnings, 186 critical checks, 111 exact BOM
  components, reverse-polarity controls, source thresholds, telemetry ranges,
  current limit, and hold-up calculations pass.
- CM5-CARRIER/AUDIO-8X8 interface contract: 174 critical connector and control
  pin/net assignments pass.
- CM5 allocation: all 76 owned contacts reconcile across the generator,
  controlled workbook, official Radxa source, and exported netlist; 74 are
  connected and two are explicitly assigned no-connects.
- Power-Regulators-A1: 49 regulator, inductor, rail, source-current, and hold-up
  checks pass; the production BOM has 163 controlled rows.
- Thermal-IO: 22 part, sensor-grade, fan-protection, and hot-current checks pass.
- Network-PCIe: 29 controlled-part and architecture checks pass.
- WWAN-SIM: 23 modem, SIM, local supply-network, protection, and RF-harness
  checks pass.
- Display-Harness: 20 HDMI, USB touch, 12 V monitor, and IO-5 V checks pass.
- Audio-Control: 22 TDM, I2S1, ES8316, headset-amplifier, CTIA, and grounding
  checks pass.
- AUDIO-8X8: 581 checks across seven detailed sheets pass; the generated BOM
  has 553 rows.
- Cross-board XLR, fan, temperature, telemetry, source-control, TDM, and audio
  power assignments pass.

## Physical Gates Before PCB

The root-counted component audit covers 1203 unique schematic components. Ten routing blockers are
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
