# Display And Touchscreen

## Goal

Add a local touchscreen interface for the ProComm operator UI.

The touchscreen will be mounted in the Pelican iM2300 lid.

## Required Interfaces

- HDMI output from the CM5 to the display
- USB host connection from the CM5/carrier to the touchscreen touch controller
- Rugged USB Type-B SuperSpeed panel/service connector for the touch link
  where practical; route at least USB 2.0 D+/D- for the touch controller and
  only route SuperSpeed pairs if the selected display/touch controller actually
  uses them.
- 12 V display/touchscreen power from a simple fused `AUX_12V` harness branch;
  no dedicated electronic display eFuse/current limiter. Keep this branch at
  12 V / 2.5 A for the monitor's 25 W / 2.08 A nominal rating, then verify
  startup and full-brightness current on the received sample.
- Lid-to-base `H03` bundle for HDMI, USB touch, and display power. Start each
  cable at 1000 +/- 25 mm finished length for the first mechanical article.

## Hardware Notes

- Use the CM5 HDMI pins from the official Radxa CM5 pinout/reference schematic.
- Add HDMI ESD protection and follow controlled-impedance differential routing.
- Place HDMI connector so the cable path works with the enclosure.
- Provide a USB host port or internal USB header for the touch controller.
- Locked display selection from user link: JUNEBOX / DTM MALL Amazon ASIN
  `B0GK5X95D9`, currently listed as a 15.6-inch industrial touchscreen, 1920 x
  1080 IPS, 16:9, 60 Hz, 450 cd/m2 class brightness, matte finish, 7H tempered
  glass, HDMI input, DVI/VGA support, touch support, VESA/wall-mount hardware,
  and 12 V power.
- Do not use any online monitor body dimension for fabrication. Current
  listings reuse contradictory dimensions and the same model string across
  several screen sizes; one reported body width is smaller than the active
  width of a 15.6-inch 16:9 panel.
- The listing does not provide a controlled mechanical drawing. USB Type-B
  SuperSpeed is therefore a carrier interface preference, not a verified
  monitor connector.
- The earlier Waveshare 13.3-inch DSI and HDMI candidates are no longer the
  active display path.
- Add two controlled service loops to each display cable: one for repeated lid
  travel and one that can be released when the top panel is lifted for service.
- The released bundle must permit full lid travel while the top panel is
  lifted at least 300 mm and tilted at least 45 degrees, with no tension at any
  connector and no cable below its manufacturer's moving bend radius.
- In the closed operating position, retain both loops in cushioned releasable
  clamps clear of every fan, PSU airflow path, PCB keepout, and sharp edge.
- Route HDMI, USB touch, and 12 V through a centered notch that opens directly
  at the panel's hinge edge. Do not use an enclosed hole farther inside the
  top panel for this harness.
- Add USB ESD protection and current limiting if the port/header supplies power.
- Confirm whether the touchscreen needs separate display power beyond USB.
- Transport closure is qualified with the Gold-mount battery removed and all
  eight external antennas removed and replaced by low-profile dust caps. The
  measured display-front to tallest-permanent-panel-hardware gap must remain
  at least 8 mm after tolerance, gasket compression, lid flex, and impact
  allowance.

## Open Decisions

- Verify whether the JUNEBOX touch port is standard USB 2.0 Type-B, USB-C, or
  true USB 3.x Type-B SuperSpeed on the exact received unit. Touch only needs
  USB 2.0 HID, but the product connector requirement says Type-B SuperSpeed.
- Verify the JUNEBOX mechanical drawing, real bezel size, VESA pattern,
  mounting screw depth, lid clearance, 12 V power input connector, current
  draw, HDMI connector orientation, DVI/VGA keepout, and whether any built-in
  USB hub should be disabled or left unused.
- Whether the final touch connector is direct USB Type-B SuperSpeed on our
  panel/harness, or an internal adapter from Type-B SuperSpeed to the display
  controller's actual USB touch connector.
- Lid mounting hardware, bezel, and protective overlay.
- Internal HDMI cable vs board-to-panel adapter.
- Internal USB cable/header for touch.
- Final 12 V display connector, branch fuse, wiring gauge, and lid-harness
  conductor count.
- Final hinge-edge notch width, depth, edge radius/grommet, and harness bend
  radius after the actual cable assembly is selected.
- Final H03A/H03B/H03C finished lengths after the fully dressed first-article
  lid-travel and panel-service tests. The 1000 mm starting length is not a
  fabrication-release datum.
