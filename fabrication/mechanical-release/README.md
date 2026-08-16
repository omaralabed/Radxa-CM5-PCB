# iM2300 Mechanical Release Package

## Status

- Package revision: A1
- Release state: `HOLD_FOR_MEASUREMENT`
- Panel installation plane: 38.1 mm below the case parting line
- Controlled concept drawings:
  - `../../cad/im2300-top-panel-layout-rev-i.svg`
  - `../../cad/mechanical/im2300-underside-pcb-floorplan-rev-h.svg`

This package controls the measurements that must be taken from the actual
Pelican iM2300, custom four-side frame, display, battery dock, and production
connector samples. Published case dimensions are useful for planning but are
not fabrication datums.

## Required Equipment

- Calibrated 0.01 mm digital caliper
- 300 mm depth gauge or height gauge
- Steel rule and machinist square
- Radius gauges or a printed radius template
- Feeler gauges or calibrated spacer blocks
- Actual iM2300 case, display, battery and dock, fans/guards, XLR connectors,
  C14 inlet, LEMO connector, switches, SIM holders, RJ45s, and RF bulkheads

## Datum System

- `A`: finished top-panel plane
- `B`: finished left panel edge at the operator-facing orientation
- `C`: finished hinge-side panel edge
- `D`: case parting-line plane
- `E`: custom frame inner support edge

All panel X/Y coordinates use the intersection of datums `B` and `C` as the
origin. Positive X runs toward the RF bank. Positive Y runs toward the
operator/handle side.

## Procedure

1. Install temporary gauge rails at exactly 38.1 mm below datum `D`.
2. Measure the case opening at the four corners and centerlines without forcing
   the case walls outward. Record every value in
   `im2300-measurement-register.csv`.
3. Derive the preliminary plate size using the Pelican bezel rule: subtract
   2.3876 mm, then subtract 0.4572 mm per 6.35 mm of recess. At 38.1 mm recess,
   the total nominal subtraction is 5.1308 mm from each measured opening
   dimension. The actual frame geometry remains the controlling fit check.
4. Produce a cardboard, acrylic, or inexpensive aluminum gauge plate. Verify
   insertion, removal, frame seating, gasket clearance, and all screw access.
5. Mount representative connectors, battery, display, fans, guards, CM5
   cooling stack, and harnesses. Close and latch the case for the closure and
   impact-clearance measurements.
   Mount the Gold Mount dock so the battery engages from left to right and
   removes from right to left. Measure the complete slide travel and verify at
   least 20 mm of clear insertion/hand space between the XLR hardware and dock.
6. Enter measured minimum/maximum values in
   `mechanical-release-a1.json`, attach measurement photos or inspection
   records, and run `validate_mechanical_release.py --release`.
7. Only after the release validator passes may the exact panel outline, panel
   screw coordinates, and PCB mounting-hole coordinates be frozen for routing.

## Hard Constraints

- Continuous 15.0 mm no-PCB frame/screw band on all four sides.
- `AUDIO-8X8` PCB envelope no larger than 78 x 268 mm.
- `CM5-CARRIER` PCB envelope no larger than 166 x 268 mm.
- Panel screws and frame hardware are mechanically independent of PCB mounts.
- Minimum 8.0 mm closed-lid dynamic clearance after tolerance stack-up.
- Minimum 3.0 mm static clearance between unrelated metal hardware; use more
  where cables, latches, fingers, insulation, or vibration motion require it.
- XLR bank outside edge remains at least 15.0 mm from the finished panel edge.
- The CM5 panel fan must remain centered over the released CM5 heatsink inlet.
- Intake and exhaust openings require a divider/shroud that blocks direct
  short-circuit airflow.
- Gold Mount engagement is left to right. Keep the left insertion corridor and
  complete battery motion sweep free of panel hardware and connected cables.

## Files

- `im2300-measurement-register.csv`: inspection record for the actual hardware
- `mechanical-release-a1.json`: machine-readable release gate
- `validate_mechanical_release.py`: package/release validator
- `im2300-measurement-worksheet-a1.svg`: printable factory worksheet
