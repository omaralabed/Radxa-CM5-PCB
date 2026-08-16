# CAD Workspace

Native schematic tool: KiCad 10. The three-board A0 capture is under `kicad/`;
see `kicad/README.md` for project status, regeneration, validation, and the
detailed-capture order.

## Current Mechanical Concept

- `im2300-top-panel-layout-rev-i.svg` - current connector-placement concept. It
  reserves a 15 mm four-side frame/screw keepout, moves the XLR bank only 2.3
  mm right to clear that boundary, and retains the preliminary centered
  90 x 8 mm notch opening through the hinge edge for the HDMI, USB-touch, and
  12 V display harness. It also adds two diffused 12 V warm-white courtesy
  lights and one latching capacitive touch control in the clear strip above
  the Gold Mount keepout. It includes
  the 8x8 XLR bank, left-to-right Gold Mount engagement sweep, eight RF
  bulkheads, four Ethernet ports,
  lid-display harness, headset/SIM service, status, LEMO backup,
  separate DPST main source-enable rocker, two Delta `THA0412AD-TZW3`
  board-controlled intake/exhaust fans, and guarded fused C14 zone.

This SVG is a placement study, not a fabrication cut file. Replace every
connector representation with the final manufacturer's panel-cutout drawing
and replace the nominal panel outline with measurements from the actual case.

## Current Underside Study

- `mechanical/im2300-underside-pcb-floorplan-rev-h.svg` - current pre-routing
  floorplan. It limits `AUDIO-8X8` to 78 x 268 mm and `CM5-CARRIER` to 166 x
  268 mm, keeps both boards out of the 15 mm perimeter band, aligns the CM5
  mesh with the CM5, places the enclosure
  fans over the carrier power zones, locks the left fan as filtered intake and
  right fan as open exhaust, calls out independent 1 kHz PWM/tach control,
  requires a divider/shroud between them, and reserves the rear
  bodies plus fused 12 V harness route for the independent panel lights. It
  reserves the Gold Mount battery insertion corridor on the left and locks
  engagement toward the network side.
