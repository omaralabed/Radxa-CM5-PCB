# iM2300 Mechanical Release Package

## Status

- Package revision: A2
- Release state: `HOLD_FOR_MEASUREMENT`
- Panel installation plane: 38.1 mm below the case parting line
- Controlled concept drawings:
  - `../../cad/im2300-top-panel-layout-rev-k.svg`
  - `../../cad/mechanical/im2300-underside-pcb-floorplan-rev-l.svg`
  - `../../cad/mechanical/im2300-sidewall-cooling-layout-rev-c.svg`
  - `../../cad/mechanical/im2300-closed-lid-stack-rev-f.svg`
  - `../../cad/mechanical/pcb-and-connector-support-detail-rev-a.svg`

This package controls the measurements that must be taken from the actual
Pelican iM2300, custom four-side frame, installed display assembly, battery
dock, and production connector samples. The monitor body uses the documented
396.24 x 203.20 x 20.32 mm nominal envelope; its mount, connector, cable, and
closed-lid geometry remain installation checks. Published case dimensions are
useful for planning but are not fabrication datums.

## Required Equipment

- Calibrated 0.01 mm digital caliper
- 300 mm depth gauge or height gauge
- Steel rule and machinist square
- Radius gauges or a printed radius template
- Feeler gauges or calibrated spacer blocks
- Actual iM2300 case, display, battery and dock, fans/guards, XLR connectors,
  C14 inlet, LEMO connector, switches, SIM holders, RJ45s, RF bulkheads, and
  four samples of each selected compact hinged antenna

## Datum System

- `A`: finished top-panel plane
- `B`: finished left panel edge at the operator-facing orientation
- `C`: finished hinge-side panel edge
- `D`: case parting-line plane
- `E`: custom frame inner support edge

All panel X/Y coordinates use the intersection of datums `B` and `C` as the
origin. Positive X runs toward the RF bank. Positive Y runs toward the
operator/handle side.

All vertical dimensions use the finished top face of the panel as datum `A`.
At the published 106.7 mm base depth, a 38.1 mm recess places `A` 68.6 mm
above the nominal deepest floor. A 3.175 mm panel leaves 65.425 mm below the panel
underside. These are planning values only; measure the actual floor ribs,
frame, tray, panel, and case.

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
5. Mount representative connectors, battery, display, sidewall fans, guards, CM5
   cooling stack, and harnesses. Close and latch the case for the closure and
   impact-clearance measurements.
   Fit 1000 +/- 25 mm H03A HDMI, H03B USB-touch, and H03C display-power
   prototype cables. Verify full lid travel, then release the panel-service
   clamps and raise the connected top panel at least 300 mm while tilting it
   at least 45 degrees. No connector may carry tension and no cable may enter
   a fan, airflow path, sharp-edge zone, or PCB keepout.
   Mount the Gold Mount dock with its supplied backplate against a supported
   flat panel/frame load path. The battery engages from left to right and
   removes from right to left. Measure the complete slide travel and verify at
   least 20 mm of clear insertion/hand space between the XLR hardware and dock.
   Carry the dock, battery, insertion, and vibration loads entirely through the
   top panel/custom frame. No dock fastener or load path may terminate in a PCB.
   Perform the transport-closure test with the battery removed and all eight
   released compact hinged antennas installed and folded inboard toward the
   panel center. Do not force or latch a closure that shows interference.
   Upright antennas, substitute antenna models, or battery-installed closure
   require a separate signed sweep record.
6. Enter measured minimum/maximum values in
   `mechanical-release-a2.json`, attach measurement photos or inspection
   records, and run `validate_mechanical_release.py --release`.
7. Only after the release validator passes may the exact panel outline, panel
   screw coordinates, and PCB mounting-hole coordinates be frozen for routing.

## Hard Constraints

- Continuous 15.0 mm no-PCB frame/screw band on all four sides.
- `AUDIO-8X8` PCB envelope no larger than 78 x 268 mm.
- `CM5-CARRIER` PCB envelope no larger than 166 x 268 mm.
- Panel screws and frame hardware are mechanically independent of PCB mounts.
- Top panel is 3.175 mm nominal 5052-H32 aluminum with a matte black finish;
  validate a 3.0-3.3 mm coupon. Rear-pocket the RA812 rocker area to no more
  than 3.0 mm without weakening its local support.
- Bottom equipment tray is 2.0 mm nominal 5052-H32 aluminum. Its released top
  surface may be no more than 3.0 mm above the deepest local case-floor datum.
  Do not put a compressible foam stack under the PSU.
- The QRC-GOLD dock is top-panel/custom-frame hardware, not a PCB-mounted part;
  only its strain-relieved removable power harness reaches the selector PCB.
- Minimum 8.0 mm closed-lid dynamic clearance after tolerance stack-up.
- Transport closure requires the Gold-mount battery removed and all four
  Taoglas `GW.05.0153` Wi-Fi antennas plus all four Taoglas `TG.66.A113`
  cellular antennas installed and folded inboard. Upright or substitute
  antennas are not an approved closure configuration.
- Minimum 3.0 mm static clearance between unrelated metal hardware; use more
  where cables, latches, fingers, insulation, or vibration motion require it.
- XLR bank outside edge remains at least 15.0 mm from the finished panel edge.
- The CM5/modem dedicated fan inlets face the bottom and retain at least 10 mm
  unobstructed clearance through the full tolerance and vibration stack.
- The right-wall filtered intake and operator-wall center-right exhaust require
  separate reinforcement plates, gaskets, guards, and splash-directed louvers.
- Maintain at least 100 mm practical separation between enclosure fan/PWM
  hardware and the AUDIO-8X8 quiet boundary; route fan power with a filtered
  star return and outside the guarded hinge-side PSU harness corridor.
- Rotate the `RPS-400-24-C` footprint 90 degrees in plan and maintain at least
  125 mm from the AUDIO-8X8 quiet boundary to the nearest grounded PSU guard
  edge after tolerance stack-up. The Rev L nominal study provides 146 mm.
  Keep the complete tray-mounted PSU/terminal-guard envelope no more than
  48.0 mm above the deepest interior floor. Maintain at least 10 mm vertically
  from that guard to the nearest carrier
  component or panel underside and keep the overlying carrier B.Cu area clear.
- Keep the actual HDMI, USB-touch, and 12 V lid-harness cable envelope at least
  15 mm from the grounded PSU guard through full lid travel and the complete
  panel-lift service motion. No mains conductor, fan harness, or shared clamp
  may enter that protected corridor.
- Gold Mount engagement is left to right. Keep the left insertion corridor and
  complete battery motion sweep free of panel hardware and connected cables.
- Use the six controlled supports `A1-A6` on AUDIO-8X8 and `C1-C6` on
  CM5-CARRIER from `pcb-support-pattern-a2.csv`. Each support uses a 3.4 mm
  finished NPTH, 8.0 mm all-layer copper keepout, 10.0 mm component keepout,
  and a rigid captive metal M3 standoff. Maximum longitudinal support-row span
  is 128 mm. Do not soft-float either PCB.
- Every user-operated connector shall transfer plug, unplug, downward push,
  cable-side, and vibration loads to the panel or frame. Follow
  `connector-load-path-a2.csv`; solder-only retention is prohibited. Release
  the RJ45 capture bracket and headset/SIM service-board coupons before routing.
- Qualify the complete unit at 45 C ambient and 151.7 W continuous load.
  Measure at least 15 CFM through-case with a clean filter, at least 12 CFM at
  the released filter-maintenance limit, and keep PSU inlet air at or below
  50 C. The RPS-400-24-C derates with temperature.

## Files

- `im2300-measurement-register.csv`: inspection record for the actual hardware
- `mechanical-release-a2.json`: machine-readable release gate
- `validate_mechanical_release.py`: package/release validator
- `pcb-support-pattern-a2.csv`: controlled board and panel support coordinates
- `connector-load-path-a2.csv`: controlled load path for each interface group
- `im2300-measurement-worksheet-a2.svg`: printable factory worksheet
