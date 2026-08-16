# iM2300 Mechanical Studies

These drawings extend the current top-panel placement. Rev I preserves the XLR
and PCB datums, moves the bottom-mounted PSU into a guarded hinge-side bay, and
defines the sidewall airflow and downward-facing cooling cartridges.

- `im2300-closed-lid-stack-current.svg`: nominal side section using the 38.1 mm
  panel recess, published iM2300 lid/base depths, and the current monitor study
  dimensions.
- `im2300-underside-pcb-floorplan-rev-i.svg`: pre-routing revision that reserves
  a 15 mm four-side frame/screw keepout, reduces the audio and carrier board
  envelopes to 78 x 268 mm and 166 x 268 mm, moves the two Delta
  `THA0412AD-TZW3` enclosure fans to a right-wall intake and operator-wall
  exhaust, keeps all fan/PWM wiring out of the analog quiet zone and guarded
  PSU corridor, keeps the PCIe switch
  beside the CM5, fits the full-size AW7915-NP1 Mini PCIe card and eight coax
  paths, defines protected high-speed, lid-harness, TDM, RF, and power
  corridors, reserves the panel-mounted warm-white courtesy-light bodies and
  their independent fused AUX_12V harness, and keeps the Gold Mount insertion
  corridor clear on the left so the battery slides toward the network side.
- `cm5-5540a-delta-cooling-concept-rev-b.svg`: downward-facing cooling cartridge
  for
  the Radxa `5540A` heatsink and Delta `FFB0412EN-00Y2E` CPU fan, including
  a fan-to-heatsink adapter plus structural vibration-isolated support bracket,
  a 10 mm minimum bottom intake gap, and the protected 3 A fan power branch.
- `im2300-sidewall-cooling-layout-rev-a.svg`: preliminary right-wall intake and
  operator-wall exhaust centers, reinforcement/gasket rules, airflow path, and
  the hinge-side PSU/audio separation constraints.
- `im2300-cooling-clearance-rev-a.scad`: parametric 3D clearance concept for the
  panel, suspended boards, hinge-side PSU, sidewall fans, and downward-facing
  CM5/modem cooling stacks. Its assertions are planning checks, not release CAD.

These drawings are fit studies, not fabrication releases. Replace nominal case,
monitor, connector, PCB, heatsink, fan, PSU, battery-dock, and harness envelopes
with measured dimensions and manufacturer STEP/drawing data before release.
