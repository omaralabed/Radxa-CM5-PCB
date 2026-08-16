# iM2300 Mechanical Studies

These drawings extend the current top-panel placement. Rev G shifts the XLR
bank 2.3 mm right solely to clear the new frame boundary.

- `im2300-closed-lid-stack-current.svg`: nominal side section using the 38.1 mm
  panel recess, published iM2300 lid/base depths, and the current monitor study
  dimensions.
- `im2300-underside-pcb-floorplan-rev-g.svg`: pre-routing revision that reserves
  a 15 mm four-side frame/screw keepout, reduces the audio and carrier board
  envelopes to 78 x 268 mm and 166 x 268 mm, preserves the current fan/mesh
  datums, and specifies two Delta
  `THA0412AD-TZW3` fans with independent 1 kHz PWM/tach control, locks
  left-fan intake and right-fan exhaust with an underside anti-short-circuit
  baffle, keeps the PCIe switch
  beside the CM5, fits the full-size AW7915-NP1 Mini PCIe card and eight coax
  paths, defines protected high-speed, lid-harness, TDM, RF, and power
  corridors, and reserves the panel-mounted warm-white courtesy-light bodies and their
  independent fused AUX_12V harness.
- `cm5-5540a-delta-cooling-concept-rev-a.svg`: locked airflow architecture for
  the Radxa `5540A` heatsink and Delta `FFB0412EN-00Y2E` CPU fan, including
  independent vibration-isolated fan mounting, downward airflow, the
  preliminary 5-10 mm plenum, and the protected 3 A fan power branch.

These drawings are fit studies, not fabrication releases. Replace nominal case,
monitor, connector, PCB, heatsink, fan, PSU, battery-dock, and harness envelopes
with measured dimensions and manufacturer STEP/drawing data before release.
