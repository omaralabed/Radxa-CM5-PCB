# iM2300 Mechanical Studies

These drawings extend the current Rev K top-panel placement. Rev K preserves
the XLR and panel datums while adding the A2 vertical-stack gate, low-profile
bottom tray, six supports per long PCB, selected modem fan, transport-closure
rules, PSU airflow wash, and corrected panel-thickness logic.

- `im2300-closed-lid-stack-rev-d.svg`: corrected side section using datum A at
  the finished panel top face, 3.175 mm panel thickness, sample-controlled
  monitor geometry, 65.425 mm nominal space below the panel underside, and
  battery-removed transport closure with all eight released compact hinged
  antennas installed and folded inboard. Their approximately 32 mm preliminary
  folded envelope remains sample-controlled and requires 8 mm dynamic clearance.
- `im2300-underside-pcb-floorplan-rev-k.svg`: pre-routing revision that reserves
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
  The PSU guard is nominally 146 mm from the audio quiet boundary and may not
  fall below 125 mm after the physical tolerance stack is released.
  The lid-display harness has a separate protected corridor with 15 mm minimum
  clearance to the PSU guard. The complete installed PSU guard stays no more
  than 48 mm above the deepest floor and retains 10 mm minimum to carrier B.Cu.
- `cm5-5540a-delta-cooling-concept-rev-b.svg`: downward-facing cooling cartridge
  for
  the Radxa `5540A` heatsink and Delta `FFB0412EN-00Y2E` CPU fan, including
  a fan-to-heatsink adapter plus structural vibration-isolated support bracket,
  a 10 mm minimum bottom intake gap, and the protected 3 A fan power branch.
- `im2300-sidewall-cooling-layout-rev-c.svg`: preliminary right-wall intake and
  operator-wall exhaust centers, selected Qualtek guards, custom splash-hood
  rules, clean-air PSU wash, reinforcement/gasket rules, and thermal acceptance.
- `im2300-cooling-clearance-rev-c.scad`: parametric 3D clearance concept for the
  panel, suspended boards, hinge-side PSU, sidewall fans, and downward-facing
  CM5/modem cooling stacks, corrected panel underside, tray, and guarded PSU
  Z stack. Its assertions are planning checks, not release CAD.

These drawings are fit studies, not fabrication releases. Replace nominal case,
monitor, connector, PCB, heatsink, fan, PSU, battery-dock, and harness envelopes
with measured dimensions and manufacturer STEP/drawing data before release.
