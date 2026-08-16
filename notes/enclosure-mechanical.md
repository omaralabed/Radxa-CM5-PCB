# Enclosure And Mechanical

## Selected Enclosure

Pelican Storm Case iM2300.

Decision update: the smaller-than-iM2300 exploration is canceled. The active
enclosure remains the Pelican Storm iM2300.

Official Pelican dimensions:

- Exterior: 18.2 x 13.9 x 6.7 in (46.23 x 35.31 x 17.02 cm)
- Interior: 17.00 x 11.70 x 6.20 in (43.18 x 29.72 x 15.75 cm)
- Lid depth: 2.00 in (5.08 cm)
- Bottom depth: 4.20 in (10.67 cm)
- Weight without foam: 5.90 lb (2.68 kg)
- Weight with foam: 7.10 lb (3.22 kg)

## Mechanical Direction

Design the electronics as a top-panel-mounted assembly inside the iM2300:

- Top panel is the main operator/service panel for the box
- Target the top-panel mounting plane 1.50 in (38.1 mm) below the upper case
  edge/parting-line reference, subject to measurement of the actual case and
  final support-frame geometry.
- Mount the top panel to dedicated custom support edges on all four sides using
  a panel-only screw pattern.
- Keep those panel fasteners mechanically independent from the suspended PCB
  assemblies. The PCB uses separate standoffs and separate mounting holes.
- Finalize panel screw count, diameter, pitch, edge distance, inserts/nuts,
  tool clearance, and sealing treatment from the measured custom frame.
- Source-checked base/top-panel bezel reference is 17.00 in x 11.733 in nominal (431.8 mm x 298.0 mm nominal)
- Main carrier PCB mounted underneath the top panel on standoffs
- Top panel material: 3.175 mm nominal 5052-H32 aluminum, matte black powder
  coat, with masked PE/chassis bond points and a local RA812 rocker pocket no
  thicker than 3.0 mm
- Low-profile bottom equipment tray: 2.0 mm nominal 5052-H32 aluminum, with
  its top surface no more than 3.0 mm above the deepest measured floor datum
- MEAN WELL `RPS-400-24-C` 24 V AC/DC PSU mounted to the bottom panel, not to
  the top panel
- Touchscreen mounted in the Pelican lid
- HDMI, USB touch, and display power cable routed from the PCB under the top panel to the lid display
- RJ45, audio, power, antenna, and service connections placed on the top panel or a side interface area
- Fan airflow path defined before PCB connector placement is finalized

## Shock And Vibration Protection

- Treat portable-field shock, vehicle vibration, handling drops, and repeated
  connector insertion as production mechanical load cases.
- Support the top panel continuously on the custom four-side frame. Use a thin
  closed-cell EPDM or silicone isolation/sealing strip between the aluminum
  panel and support frame where the final stack-up allows it.
- Use a dedicated flexible PE/chassis bonding strap from the aluminum panel to
  protective earth. Do not depend on anodized panel screws or the isolation
  strip for electrical bonding.
- Mount each suspended PCB to rigid M3 captive threaded standoffs on the panel
  underside. Place standoffs near panel-mounted connectors, board corners,
  large inductors/capacitors, heatsinks, CM5 mounting points, M.2 sockets, and
  cable headers so the PCB cannot flex or resonate.
- Do not soft-float an audio PCB relative to panel-mounted XLR connectors. The
  connector flanges and nearby rigid standoffs must keep the panel, connector,
  and PCB stack aligned so vibration is not transferred into solder joints.
- Keep panel-frame screws, PCB standoffs, and connector-flange screws as three
  separately defined mechanical fastener systems.
- Use captive or prevailing-torque hardware, appropriate thread locking, and
  witness marks. Select thread-locking chemistry that is compatible with nearby
  plastics and remains field-serviceable.
- Mechanically retain the CM5, M.2 Wi-Fi card, cellular modem, heatsinks, fans,
  Gold Mount dock, PSU, large capacitors, inductors, and transformers. Do not
  rely only on solder joints, board-to-board connectors, or thermal pads.
- Add harness clamps and strain relief close to every PCB connector. Provide
  controlled service loops without allowing HDMI, USB, RF coax, fan, audio, or
  power cables to strike the boards during transport. Reserve the H03 display
  bundle in its own protected hinge corridor and maintain at least 15 mm from
  the actual cable envelope to the grounded PSU guard during lid and panel
  service motion.
- Evaluate 2.0 mm PCB thickness or local stiffeners for long boards after the
  final stack-ups and controlled-impedance requirements are known.
- Consider conformal coating after connectors, sockets, test pads, thermal
  interfaces, and grounding contacts are masked; coating helps the field
  environment but does not replace mechanical retention.

## Case Fit Review For 15.6-Inch HDMI Touch Monitor

Current monitor candidate:

- JUNEBOX / DTM MALL Amazon ASIN `B0GK5X95D9`
- Listed screen size: 15.6 in
- Online enclosure dimensions are contradictory and prohibited as fabrication
  data. Listings reuse the same model string across multiple screen sizes.
- Listed/displayed features: 1920 x 1080, IPS, HDMI input, DVI/VGA support,
  touch support, 450 cd/m2 class brightness, 7H tempered glass, VESA/wall-mount
  hardware, 12 V power

Selected iM2300 fit:

| Case | Interior L x W x D | Lid depth | Bottom depth | Monitor planar clearance | Lid depth spare |
| --- | ---: | ---: | ---: | ---: | ---: |
| iM2300 | 17.00 x 11.70 x 6.20 in | 2.00 in | 4.20 in | Sample-controlled | Sample-controlled |

Interpretation:

- The iM2300 is large enough for a 15.6-inch 16:9 active area in principle,
  but the selected monitor body, connector bosses, mount, and cable bends are
  not verified. Base and lid fit remain on physical hold.
- Keep iM2300 as the selected case unless the owner explicitly reopens the
  enclosure decision later.

Do not release CAD from the published dimensions alone. Buy or borrow the
exact case and monitor sample, then measure the real lid cavity, corner radii,
hinge/latch intrusion, panel-bezel mounting plane, VESA screw depth, monitor
power connector, HDMI connector, touch USB connector, DVI/VGA connector
keepouts, and cable bend envelopes.

## Reference Layout

Use the existing ProComm field unit photo documentation as the visual/mechanical
reference:

- Pelican iM2300 case with the operator display mounted in the lid
- Base-mounted custom top panel carrying most user/service connections
- Main PCB/electronics mounted underneath the top panel
- Audio channel connectors grouped in a left-side XLR bank on the panel
- XLR bank starts 15.0 mm (0.59 in) from the finished left panel edge to clear
  the four-side support frame
- XLR bank contains 8 balanced outputs and 8 balanced inputs
- XLR bank follows the photo reference: two vertical columns, eight rows,
  `CH1` at top through `CH8` at bottom
- Left column uses male XLRs labeled `CH1 OUT` through `CH8 OUT`
- Right column uses female XLRs labeled `CH1 IN` through `CH8 IN`
- No vertical label strips; each XLR has its own label directly under the
  connector
- Headset jack near the operator-facing/service area
- Ethernet/service jack on the top panel
- Power switch near the front/operator edge
- Vent/perforation grilles in the panel above internal electronics
- Antennas mounted through the top panel, standing vertically when the case is open
- Larger compute/radio/electronics section occupying the right side of the base
- Cables exiting the front/top-panel area need clearance and strain relief

For the new Radxa CM5 design, keep the same general user posture: case open,
screen in the lid, connectors and controls in the base panel, electronics below
the panel.

The separate legacy folder `/Users/viewvision/Desktop/ProComm enclosure and PCB boards`
is also useful as a reference for mechanical discipline, connector envelope
control, XLR mounting strategy, and harness planning. Do not copy its old layout
or electrical design directly; the Radxa CM5 unit has a different architecture.

## Top Panel Envelope

Source-checked dimensions:

- Published general interior/cargo size: 17.00 in x 11.70 in x 6.20 in
- Official Pelican base bezel drawing nominal panel reference: 17.00 in x 11.733 in
- Metric bezel reference: 431.8 mm x 298.0 mm nominal

Working orientation is 17.00 in left-to-right and 11.733 in nominal
front-to-back at the base/top-panel bezel reference.

The previous 11.90 in project target is not source-verified. It may reflect a
specific measurement at the top opening, but it must be checked on the actual
case and panel frame before final CAD release.

Pelican's official bezel drawing says to measure the actual case inside corner
to inside corner, subtract 0.094 in from length and width for outside plate
size, and subtract another 0.018 in from each dimension for every 0.25 in the
plate is installed below the parting line.

## Top Panel Stack-Up

Preferred mechanical stack:

- Pelican iM2300 case
- Custom top panel
- Touchscreen mounted in the lid
- User-facing connectors mounted through the top panel or side interface area
- `CM5-CARRIER` and `AUDIO-8X8` PCBs mounted underneath the top panel
- Standoffs between panel and PCB
- Bottom-panel-mounted MEAN WELL `RPS-400-24-C` PSU with guarded AC wiring,
  protective-earth bond, and low-voltage 24 V harness to the carrier/source
  selector
- Separate bottom-mounted `PWR-SELECT` PCB near the PSU/battery wiring
- Cable harnesses kept short between panel connectors and board headers, or board-mounted connectors aligned directly to panel cutouts

## Panel Recess And Closed-Lid Clearance

The mechanical target is to mount the top-panel plane 1.50 in (38.1 mm) below
the upper case edge/parting-line reference.

Using the published nominal depths and the selected nominal panel:

- Base depth below the parting line: 4.20 in (106.7 mm)
- Finished top-panel face above the nominal deepest floor: 68.6 mm
- Panel thickness: 3.175 mm nominal
- Remaining nominal depth below the panel underside: 65.425 mm
- Bottom equipment tray top: no more than 3.0 mm above the deepest floor
- Nominal tray-top to panel-underside budget: at least 62.425 mm
- Lid depth: 2.00 in (50.8 mm)
- Monitor total lid protrusion: sample-controlled
- Monitor-front to panel-top gap:
  measured lid depth + measured panel recess - measured display protrusion

No closure claim can be made until the monitor sample is measured. Preserve at
least 8 mm of final dynamic clearance from the display front to every permanent
panel item after case tolerance, gasket compression, lid flex, impact, and
monitor-mount tolerance. Verify the actual closed-lid gap with the real case,
monitor, panel frame, dust-capped RF bulkheads, and representative connectors
before fabrication.

The Gold Mount battery and antennas are separate closure checks. The 58 mm
Dionic XT90 plus the approximately 12.7 mm QRC-GOLD body creates an
approximately 70.7 mm protrusion before latch tolerance, which is expected to
interfere with the lid monitor. The locked transport rule is: remove the
battery, remove all eight external antennas, and fit low-profile dust caps
before closing the case. An installed-battery or folded-antenna alternative
requires its own signed sweep record with at least 8 mm dynamic clearance.

Orient the Gold Mount dock so the battery engages horizontally from left to
right, moving from the XLR side toward the network side. Removal is the reverse
motion. Preserve at least 20 mm of unobstructed left-side insertion and hand
clearance, with 30 mm preferred, and validate the complete slide travel using
the actual dock and battery while representative panel cables are connected.

At a 1.50 in recess, the official Pelican bezel rule adds 0.108 in of plate
size reduction beyond the initial 0.094 in allowance: six 0.25 in increments
times 0.018 in. Therefore the nominal 431.8 x 298.0 mm envelope cannot be used
directly as the finished plate outline; measure the actual case at the chosen
mounting plane and apply the Pelican rule.

Design constraints:

- Leave enough clearance between top panel, PCB, CM5 heatsink/fan, modem, Wi-Fi module, and enclosure lid.
- Leave enough clearance around the bottom-mounted PSU for the approximate
  130 x 86 x 43 mm covered supply body, connectors/wiring, remote-sense and
  status wiring if used, wire bend radius, service guard, and natural
  convection airflow.
- Limit the complete bottom-tray-mounted PSU and terminal-guard envelope to
  48.0 mm above the deepest measured floor. Maintain at least 10 mm from that
  envelope to carrier B.Cu. Make a physical section gauge before freezing PCB
  mounting holes.
- Rotate the PSU footprint 90 degrees in plan and place its grounded guard in
  the hinge-side digital bay. Maintain at least 125 mm from the AUDIO-8X8 quiet
  boundary to the nearest guard edge; the current nominal geometry is 146 mm.
  Reserve the overlapping carrier area as a B.Cu component and switch-node
  copper keepout, and verify at least 10 mm vertical clearance to the guard.
- Provide a hinge-safe cable service loop for HDMI, USB touch, and display power.
- Make service headers accessible without fully removing the board if possible.
- Use connector keepouts and panel nut/washer clearances in the PCB outline.
- Preserve 15.0 mm (0.59 in) left-side clearance before the XLR bank. Increase
  it if the measured case wall, gasket/lip, or panel frame requires more room.
- Reserve a continuous 15 mm minimum no-PCB band on all four sides. The current
  maximum board envelopes are 78 x 268 mm for `AUDIO-8X8` and 166 x 268 mm for
  `CM5-CARRIER`; lock the actual frame before routing either board.
- Support heavier connectors mechanically from the panel, not only from the PCB.
- Use at least six supports on AUDIO-8X8 and six on CM5-CARRIER. The 268 mm
  audio board may not rely on only four corner standoffs.
- Reserve eight RF bulkheads in the right-side RF bank: four Wi-Fi above four
  cellular/GNSS. Keep the bank and its coax corridor away from the lid display
  metal, AC/PSU bay, XLR bank, Ethernet magnetics, fans, and high-current wiring.

## Thermal Implication

The unmodified iM2300 is watertight/dustproof. This product's right-wall intake
and operator-wall exhaust intentionally reduce that rating; the top panel has
no cooling opening. Gaskets, filters, guards, and splash-directed louvers do
not restore the original Pelican rating. Internal baffles must force the air
through the CM5, modem, and regulator zones before exhaust.

Route a low-velocity clean-air branch across the guarded PSU bay and measure
the PSU inlet-air temperature; the guard may not form a sealed hot box. At
45 C ambient and 151.7 W continuous load, keep PSU inlet air at or below 50 C,
measure at least 15 CFM through-case with a clean filter, and at least 12 CFM
at the released filter-maintenance limit.

If directed-air testing cannot reject the 151.7 W continuous design load at
45 C / 113 F ambient, use a
  sealed air-to-air heat exchanger, increase airflow/heat spreading, or reduce
the load. The product specification must explicitly state the reduced
environmental sealing caused by the open fan paths.

The CPU fan, dedicated cellular modem fan, and two enclosure fans should be
designed around this thermal choice.

The bottom-mounted AC/DC PSU is also part of the thermal load. Install it in a
guarded hinge/display-side bay, rotated and shifted into the digital side so
the grounded guard remains at least 125 mm from the audio quiet boundary. Keep
it away from both sidewall fans and their PWM/power harnesses. Its covered case
uses natural convection and must be checked for derating in the sealed iM2300,
especially when the CM5, Wi-Fi AP, cellular modem, Ethernet controllers, HDMI
display power, audio rails, and fans are all active.

## Connector And Service Notes

- Any external cutouts affect water/dust sealing.
- Use gasketed panel connectors or a replaceable I/O panel if rugged sealing matters.
- Keep AC mains inlet/fuse wiring and PSU terminals isolated from
  low-voltage service wiring; add a service barrier or guarded compartment for
  the bottom-panel PSU area.
- Plan strain relief for HDMI, USB touch, antennas, power, and Ethernet.
- Add strain relief and abrasion protection for the lid-to-base display harness.
- Keep cellular/Wi-Fi antennas clear of dense metal panels and noisy electronics.
- Leave panel/service access for USB recovery and SIM slots. Keep debug UART,
  reset/recovery buttons, and service test points internal/underside and
  reachable without removing the main carrier.

## Open Decisions

- Exact touchscreen size and lid mounting method.
- Lid-to-base cable path and hinge/service-loop design.
- Whether the operator uses the system with the case open, closed, or both.
- Whether all external connectors stay on the top panel like the reference unit, or whether some move to a side wall.
- Exact XLR connector part numbers, row/column pitch, latch-tab orientation,
  per-connector label size/clearance, and service clearance.
- Exact bottom-panel PSU mounting bracket/standoffs, fused no-switch C14 inlet
  position, protective-earth/chassis bond, service cover, and low-voltage
  harness route.
- Exact right-wall intake and operator-wall exhaust centers, wall reinforcement,
  gaskets, guards/louvers, baffles, and reduced-ingress qualification.
- Panel material and thickness.
- PCB maximum outline and mounting-hole locations.
