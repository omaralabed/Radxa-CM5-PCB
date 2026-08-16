# PCB And Connector Mechanical Protection A2

## Controlled Rule

Every user-accessible connector must transfer insertion, extraction, downward
push, cable-side load, and transport vibration into the 3.175 mm aluminum top
panel or the custom four-side frame. PCB laminate, solder joints, connector
pins, board-to-board connectors, and thermal pads are not structural members.

This rule applies even when a selected connector is electrically soldered to a
PCB. A panel flange, bulkhead nut, capture bracket, supported service
daughterboard, or backplate must provide the mechanical load path.

## Long-PCB Support Pattern

The controlled support coordinates are in
`../fabrication/mechanical-release/pcb-support-pattern-a2.csv` and are shown on
`../cad/mechanical/im2300-underside-pcb-floorplan-rev-l.svg`.

- AUDIO-8X8: six supports `A1` through `A6` in three two-point rows.
- CM5-CARRIER: six supports `C1` through `C6` at four Y stations so the
  center/right supports clear the modem and CM5 cooling cartridges.
- Maximum longitudinal distance between support rows: 128 mm.
- PCB mounting hole: 3.4 mm finished NPTH for M3 hardware.
- All-layer copper keepout: 8.0 mm diameter, centered on each hole.
- Component/body keepout: 10.0 mm diameter, both PCB sides.
- Hardware: rigid captive metal M3 standoff at the panel underside with an M3
  SEMS or captive-washer screw and a field-serviceable prevailing-torque or
  locking feature.
- The NPTH and copper keepout isolate the PCB from the standoff. Any chassis
  connection must be a separate intentional bond with its own net and hardware.

Do not replace the rigid standoffs with soft rubber PCB mounts. Case shock
isolation is provided between the panel and custom support frame by the
released EPDM/silicone strip. The connector-to-PCB stack must remain rigidly
aligned.

The support coordinates are pre-routing datums. Confirm standoff height, panel
flatness, connector Z stack, and tool access on a mechanical coupon before
locking the board outline.

## Connector Load Paths

The machine-readable matrix is
`../fabrication/mechanical-release/connector-load-path-a2.csv`.

### XLR Bank

Install both flange screws on every Neutrik XLR. The flange carries mating and
downward loads into the top panel; the six AUDIO-8X8 standoffs preserve PCB
alignment. The solder pins must not clamp the panel or carry panel preload.

### RJ45 Bank

The Bel vertical MagJacks require a custom four-port capture bracket because a
clearance hole alone would leave the solder joints carrying plug forces. Use a
2.0 mm 5052-H32 bracket fixed to the panel/frame that positively restrains the
MagJack bodies in insertion, extraction, and downward directions. Assemble
with zero preload on the carrier PCB. Release the bracket only after a coupon
test using actual MagJacks and latched Ethernet plugs.

### Headset And SIM Service

Mount the CTIA headset jack on a small four-M3-supported service daughterboard
with a panel capture bezel. Mount both Nano-SIM holders on a guided four-M3
service daughterboard with a panel guide/cover. These assemblies connect to the
carrier with short flexible harnesses, so repeated plug or card operation
cannot bend the main carrier.

### Other Panel Interfaces

C14, LEMO, rocker, panel lights, touch switch, status indicators, RF bulkheads,
and the Gold Mount dock are panel/frame hardware. Use every specified flange
fastener, nut, anti-rotation feature, or backplate. Clamp each rear harness near
the interface so cable motion cannot reach a PCB header.

The internal HDMI, USB-touch, and 12 V display harness uses two-stage strain
relief: one clamp near the carrier and one at the hinge corridor. Maintain a
service loop that permits at least 300 mm panel lift and full lid travel without
loading a connector.

## Factory Inspection

1. Verify every `A1-A6` and `C1-C6` coordinate against the support CSV.
2. Confirm all twelve holes are NPTH and free of copper within 8.0 mm diameter.
3. Torque and witness-mark all PCB, flange, bracket, bulkhead, and backplate
   fasteners; keep these fastener systems independent.
4. Measure worst-case mating, unmating, and downward hand force with actual
   plugs/cards, then proof the released fixture at twice each measured force in
   the corresponding axis. No visible PCB flex, connector-body movement,
   solder-joint loading, continuity interruption, or permanent panel set is
   allowed. Do not exceed a connector manufacturer's stated proof-load limit.
5. Perform the released vibration and transport tests with representative cable
   masses and with all heavy heatsink/fan assemblies mechanically restrained.

Routing remains blocked until the RJ45 capture bracket and headset/SIM service
daughterboard coupons are released and the actual panel/frame survey confirms
the controlled support coordinates.
