# Top Panel Layout

## Source-Checked Panel Envelope

General published case interior:

- 17.00 in x 11.70 in x 6.20 in
- 431.8 mm x 297.2 mm x 157.5 mm

Official Pelican iM2300 base bezel drawing:

- 17.00 in nominal x 11.733 in nominal
- 431.8 mm nominal x 298.0 mm nominal

This means the published 11.70 in dimension is the general interior/cargo width,
while the base/top-panel bezel reference is about 11.733 in nominal. The
previous 11.90 in panel target is not source-verified yet; keep it only as a
measurement to check on the actual case/panel frame.

Pelican's official bezel drawing says the final plate size must be calculated
from the actual case: measure inside corner to inside corner, subtract 0.094 in
from length and width, then subtract another 0.018 in from each dimension for
every 0.25 in the plate is mounted below the parting line.

The current mechanical target places the panel 1.50 in (38.1 mm) below the
upper case edge/parting-line reference. This is six 0.25 in increments, so the
depth-dependent reduction is 0.108 in in addition to the initial 0.094 in.
Measure the real opening at that depth before replacing the nominal SVG panel
outline with the fabrication outline.

Working orientation:

- 17.00 in is left-to-right across the open case.
- 11.733 in nominal is front-to-back for the base/top-panel bezel reference.

This is the connector placement envelope for the custom top panel. Verify this
against the real Pelican iM2300 shell, panel lip, gasket, corner radius,
fastener pattern, and any inward case-wall taper before releasing CAD.

## Sources

- Pelican official iM2300 product page: https://www.pelican.com/us/en/product/cases/im2300
- Pelican official iM2300 base bezel drawing: https://pelicanweb-prod.s3.us-west-1.amazonaws.com/public/products/docs/products/cases/iM2300-P111-0095RevC.pdf
- DataPro iM2300 listing and panel accessories: https://www.datapro.net/products/pelican-im2300-storm-case.html
- Carry Cases Plus iM2300 listing: https://carrycasesplus.com/cases-by-brand/storm-cases/pelican-storm-im2300-case/
- XLR geometry source: `/Users/viewvision/Desktop/2026/ProComm PCB XLRs + Transformer`
- Local extracted XLR note: `notes/xlr-bank-reference.md`

## Required Panel Zones

Top-panel scope:

- Top panel carries the PCB/connector panel and the selected IEC C14 AC mains
  inlet.
- The MEAN WELL `RPS-400-24-C` AC/DC PSU is mounted on the bottom panel, not on
  the top panel.
- The selected C14 inlet style is a fused IEC inlet with no switch, like
  RS PRO `811-7204`.
- Mains wiring from the top-panel C14 inlet to the bottom-panel PSU/power area
  must be guarded and kept away from audio, RF, Ethernet, HDMI, USB, fan, and
  low-voltage harnesses.
- Protected low-voltage power harnessing from the bottom PSU/power area feeds
  the top-panel PCB assembly.

Left audio zone:

- 8 balanced XLR outputs
- 8 balanced XLR inputs
- Leave 15.0 mm (0.59 in) from the finished left panel edge to the outer left
  edge of the XLR bank. This is the minimum shift needed to preserve the
  four-side frame/screw keepout.
- XLR bank follows the provided photo reference:
  - Two vertical connector columns
  - Eight horizontal channel rows
  - Left column: `CH1 OUT` through `CH8 OUT`
  - Right column: `CH1 IN` through `CH8 IN`
  - Channel 1 at the top, channel 8 at the bottom
- XLR male connectors in the left/output column
- XLR female connectors in the right/input column
- XLR size/spacing basis comes from the legacy ProComm XLR KiCad folder:
  Neutrik `NC3MAV` outputs and `NC3FAV` inputs
- Starting geometry from the old board:
  - 28 mm row pitch
  - 43.38 mm circular-center spacing between output and input columns
  - 22.8 mm XLR courtyard/reference circle diameter
  - 66.18 mm circular XLR bank width, excluding labels and finger clearance
  - 218.80 mm circular XLR bank height for 8 rows at 28 mm pitch
- The current panel study uses 32 mm row pitch so each connector label
  fits below its XLR without colliding with the next connector. Retain the
  43.38 mm column-center spacing and validate the revised pitch against the
  final Neutrik cutouts and actual panel.
- No vertical label strips
- Each connector has its own printed/engraved label directly under it
- Labels read `CH1 OUT` through `CH8 OUT` under the output connectors and
  `CH1 IN` through `CH8 IN` under the input connectors
- Panel carries XLR insertion/removal force
- PCB and harnesses do not carry cable load

Network/radio/service zone:

- `WAN1`
- `WAN2`
- `LAN1`
- `LAN2`
- Cellular SIM/eSIM service access if panel-accessible
- Two top-facing Nano-SIM positions require a small vertical service
  daughterboard. The Wurth `693043020611` right-angle holder cannot sit flat on
  the horizontal main carrier and accept a card through the top panel.
- USB recovery connector remains internal and is not exposed on the top panel
- Debug UART remains on an internal keyed 3.3 V service header
- Status LEDs
- Reset and recovery buttons are not exposed on the top panel. Mount them as
  recessed internal/underside service controls.

Power/control zone:

- Fused IEC C14 AC inlet on the top panel, no built-in switch
- Production starting part: Qualtek `719W-00/03`, C14, one active 5 x 20 mm
  fuse position plus one spare, 10 A / 250 Vac; RS PRO `811-7204` remains the
  visual/panel-style reference
- Main power switch as a separate panel control, represented in KiCad as
  `SW201` / `J204`
- No rocker switch inside the IEC inlet; main user power switch remains a
  separate low-current selector-enable/control switch
- AC EMI/service barrier plan; the inlet is fused but not filtered
- D-Tap / LEMO backup input
- Gold Mount battery/dock clearance
- Power-source and battery-low indicators
- Main power control: E-Switch `RA812C1121`, maintained DPST OFF-ON snap-in
  rocker. Pole A enables LTC4421 `SHDN_MAIN`; pole B independently enables
  LTC4418 `SHDN_PRE`. It carries low-current controller-enable signals only.
- RA812 panel opening is 13.0 mm high. Width is 19.2, 19.4, or 19.62 mm for
  panel thickness 0.75-1.25, 1.25-2.0, or 2.0-3.0 mm respectively. A 3.2 mm
  panel requires a local rear pocket to 3.0 mm maximum and a sample fit test.
- Status indicators: Bulgin `DX06` wire-lead 12 V family, 6 mm panel cutout

Night-lighting zone:

- Two YIS Marine `LS102W` 12 V courtesy lights illuminate the operator controls
  at night. Each uses a 22.0 mm round panel cutout, an approximately 38 mm
  matte diffused front face, warm-white output, and IP67 sealing. Require a
  nominal 3000 K sample and reject cool-white substitutions.
- One E-Switch `CS7L2FR` latching capacitive touch switch controls both lamps
  together without CM5 software. Use the manufacturer's recommended
  `22.20 +0.25/-0.00 mm` round panel cutout and retain the supplied O-ring and
  mounting nut.
- Place the three parts left-to-right as `WARM WHITE 1`, `TOUCH ON / OFF`, and
  `WARM WHITE 2` at panel centers `(108, 37)`, `(153, 37)`, and `(198, 37)` mm
  from the nominal upper-left datum.
- Feed the assembly from `NIGHT_LIGHT_12V`, a dedicated 0.25 A fused branch of
  `AUX_12V`. The CS switch's rated low-side output switches both internally
  12 V lamps in parallel; the control remains independent of the CM5.
- Validate full-panel coverage, connector-color recognition, reflected light
  on the lid display, and glare with a dark-room prototype before release.

Antenna zone:

- 4 Wi-Fi antennas for the locked AW7915-NP1 4T4R AP
- 4 cellular/GNSS paths for a 5G MIMO-capable modem; label the fourth
  `CELL 4 / GNSS` when supported by the selected modem
- All eight antenna bulkheads are arranged vertically along the right side of
  the top panel at a 38 mm starting center pitch, with the group centered
  vertically to give the first and last connectors about 45 mm center-to-edge
  clearance. Use a narrow 31 mm panel
  strip, an approximately 6.4 mm hole as the drawing placeholder for each SMA
  bulkhead, and place each antenna label directly below its connector. Replace
  the placeholder with the final bulkhead manufacturer's cutout.
- Keep antennas spaced from each other and away from XLR analog wiring,
  switching regulators, fan wiring, HDMI, USB3, and the cellular modem power
  converter.

Thermal/mechanical zone:

- CM5 heatsink/fan clearance below the panel
- Two 40 mm enclosure fans mounted through the top panel, each with its own
  grille, PWM control, and tach feedback
- Top-panel fan selection: two Delta `THA0412AD-TZW3`, 40 x 40 x 20 mm,
  independently controlled at 1 kHz PWM with tach monitoring. Use one Qualtek
  `09150-F/30` 30 PPI filter guard on the intake only and a low-restriction
  finger-safe guard/louver on the exhaust.
- Enclosure fan 1, the left fan in the operator-side view, is the filtered
  intake and blows air into the case.
- Enclosure fan 2, the right fan, is the exhaust and blows air out of the case.
- Point the intake and exhaust louvers in opposite external directions to
  reduce hot-air recirculation.
- Add an underside divider/shroud between the adjacent fans and extend it far
  enough toward the carrier to prevent immediate intake-to-exhaust recirculation.
  Final height and shape require the 3D component and harness fit check.
- Separate mesh opening above the dedicated CM5 heatsink fan
- The dedicated modem fan remains attached directly to the modem heatsink
  below the panel
- Internal spreader and gasketed upper-side-wall thermal bulkhead leading to
  protected external fins
- H03 lid-display bundle uses 1000 +/- 25 mm prototype HDMI, USB-touch, and
  12 V power cables, each with a retained hinge loop and releasable panel-lift
  loop. Final lengths follow the first-article motion test.
- HDMI, USB-touch, and 12 V display sockets mount on the PCB underside facing
  down. The harness exits through one centered notch that opens directly
  through the hinge edge; there is no enclosed cable hole farther inside the
  panel.
- With the lid open, releasing the service-loop clamps must allow at least
  300 mm top-panel lift and 45 degrees of tilt without loading any connector.

## Placement Rules

- Reserve a continuous 15 mm minimum mechanical mounting band along all four
  panel sides for the custom support frame, screw hardware, tolerance, and PCB
  clearance. Increase this to 18 mm wherever nuts, washers, or brackets extend
  underneath the panel.
- Panel screw holes are independent of every PCB outline and PCB mounting hole.
  Do not use panel fasteners as PCB datums or shared PCB standoffs.
- Keep PCB copper, components, cables, and board standoffs clear of the panel
  screw heads, washers, nuts/inserts, driver access, and sealing hardware.
- Before routing, enforce an `AUDIO-8X8` maximum outline of 78 x 268 mm at the
  current panel datum and a `CM5-CARRIER` maximum outline of 166 x 268 mm.
  Neither board may extend into the 15 mm perimeter keepout.
- Lock panel-hole count, diameter, spacing, edge offset, countersink/counterbore,
  and gasket treatment only after the custom four-side frame drawing and actual
  recessed panel opening are measured.
- Keep the XLR bank on the left side of the panel.
- Place the XLR bank with 15.0 mm clearance from the finished left panel edge
  before the first XLR cutout/reference envelope.
- With the extracted 22.8 mm circular XLR reference diameter, the first output
  center is 26.4 mm from the finished left panel edge. The input center remains
  43.38 mm to its right at 69.78 mm.
- Keep heavier connectors panel-supported.
- Use manufacturer panel cutouts, drill patterns, connector keepouts, and STEP
  models for final placement.
- Reserve finger clearance around RJ45 latch tabs, XLR release tabs, SIM trays,
  USB service ports, and power connectors.
- Reserve cable bend radius above the panel and harness bend radius below the
  panel.
- Keep antenna bulkheads clear of lid closing path and display assembly.
- Keep per-connector labels readable with the case open and the screen in the
  lid.
- Keep the top-panel C14 inlet and its AC wiring in a guarded mains zone with
  clear separation from the XLR bank, radio antennas, HDMI/USB, Ethernet, and
  low-voltage controls.

## Open Layout Decisions

- Final XLR panel cutouts, latch-tab orientation, and confirmation of the current
  32 mm row pitch used for per-connector label clearance.
- Final per-connector label size, material, engraving/printing method, and
  clearance under every XLR.
- Actual measured base/top-panel opening and finished panel plate size.
- Final custom four-side support-frame profile and its independent panel screw
  pattern.
- Whether RJ45 ports are top-facing or on a side/rear interface area.
- Exact C14 inlet location, fuse/switch/EMI/service barrier layout, and whether
  any AC control/status is exposed on the top panel.
- Final C14 cutout, gasketed cover/service door, fuse coordination, and agency
  file verification for the Qualtek `719W-00/03` starting part.
- Whether SIM access is external, under a service door, or internal-only.
- Exact internal debug-UART header location.
- Final antenna connector type, cable assemblies, and spacing after RF test.

## Mechanical Part Package

The preliminary exact-part freeze and cutout release gates are in:

- `panel-mounted-parts-selection.md`
- `../docs/panel_mechanical_bom_preliminary.csv`
- `../docs/mechanical-parts/`

Do not trace the concept artwork into a production DXF. PCB-mounted RJ45 and
headset openings, the SIM service openings, the Gold Mount pattern, the RF
bulkheads, and the lid harness notch all remain dependent on final stack height
or physical sample measurements.

## Rev I SVG

The current dimensioned connector-placement study is:

- `../cad/im2300-top-panel-layout-rev-i.svg`

It uses the nominal 431.8 x 298.0 mm bezel envelope and shows the Gold Mount
battery envelope, all required user connectors, RF spacing, the guarded AC
zone, and the two hardware-controlled diffused warm-white panel lights. Rev I
adds the 15 mm four-side frame/screw keepout, moves the XLR bank 2.3 mm right,
retains the centered 90 x 8 mm hinge-edge lid-harness notch and selected DPST
rocker, and labels the left enclosure fan as intake and the right enclosure fan
as exhaust. It also locks the Gold Mount dock orientation so the battery
engages from left to right, toward the network side, and removes toward the XLR
side. The left insertion corridor and complete slide/release sweep must remain
clear with representative XLR and RJ45 cables attached.
The notch dimensions must be replaced by the selected HDMI, USB-touch, and
12 V harness bundle, grommet/edge protection, and minimum bend radius before
fabrication. It is not a CNC/fabrication cut file until actual case
measurements and manufacturer cutout drawings replace the nominal geometry.

Rev I is the sole retained top-panel drawing. Older panel revisions and locked
duplicate exports have been removed.
