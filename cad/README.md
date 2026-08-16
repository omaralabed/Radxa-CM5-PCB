# CAD Workspace

Native schematic tool: KiCad 10. The three-board A0 capture is under `kicad/`;
see `kicad/README.md` for project status, regeneration, validation, and the
detailed-capture order.

## Current Mechanical Concept

- `im2300-top-panel-layout-rev-k.svg` - current connector-placement concept. It
  reserves a 15 mm four-side frame/screw keepout, moves the XLR bank only 2.3
  mm right to clear that boundary, and retains the preliminary centered
  90 x 8 mm notch opening through the hinge edge for the HDMI, USB-touch, and
  12 V display harness. It also adds two diffused 12 V warm-white courtesy
  lights and one latching capacitive touch control in the clear strip above
  the Gold Mount keepout. It includes
  the 8x8 XLR bank, left-to-right Gold Mount engagement sweep, four RP-SMA
  Wi-Fi and four SMA cellular bulkheads with inboard folded-transport
  projections, four Ethernet ports,
  lid-display harness, headset/SIM service, status, LEMO backup,
  separate DPST main source-enable rocker, and guarded fused C14 zone. It has
  no fan or mesh cooling openings; enclosure airflow is on the case sidewalls.

This SVG is a placement study, not a fabrication cut file. Replace every
connector representation with the final manufacturer's panel-cutout drawing
and replace the nominal panel outline with measurements from the actual case.

## Current Underside Study

- `mechanical/im2300-underside-pcb-floorplan-rev-k.svg` - current pre-routing
  floorplan. It limits `AUDIO-8X8` to 78 x 268 mm and `CM5-CARRIER` to 166 x
  268 mm, keeps both boards out of the 15 mm perimeter band, places the CM5 and
  modem on B.Cu with downward cooling cartridges, rotates the PSU 90 degrees
  in a guarded hinge-side floor bay at least 125 mm from the audio quiet
  boundary, and defines the right-wall intake/operator-wall exhaust airflow
  corridor. The nominal guard separation is 146 mm, and the lid-display bundle
  has a separate protected route with at least 15 mm guard clearance. It
  reserves the rear bodies plus fused 12 V harness route
  for the independent panel lights. It
  reserves the Gold Mount battery insertion corridor on the left and locks
  engagement toward the network side.
