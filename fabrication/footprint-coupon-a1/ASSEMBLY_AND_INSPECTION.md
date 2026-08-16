# Assembly And Inspection - Footprint Coupon A1

## Process controls

- Use the supplied F.Paste Gerber without undocumented aperture edits.
- Use a 0.10 mm laser-cut stainless stencil.
- Use fresh SAC305 Type 4 no-clean paste or an approved equivalent recorded in
  the result sheet.
- Use the assembler's qualified lead-free reflow profile, with thermocouples on
  one QFN-64 site and one QFN-48 site.
- Record paste lot, stencil identifier, oven/profile identifier, peak
  temperature, and time above liquidus.
- Place package pin 1 at the board marker.
- Do not hand-rework any site before initial AOI and X-ray.

## Build population

- Assembly A: U101-U103, U201-U203, K1, and J1.
- Assembly B: U103 and U203 only.
- Assembly C: U103 and U203 only.

Use only the exact manufacturer part numbers in `coupon-bom.csv`. K1 and J1 are
hand-inserted after their unsoldered fit measurements are recorded.

## Incoming bare-board inspection

Measure and record:

- Overall board width, height, thickness, and flatness.
- Four 3.20 mm NPTH tooling holes.
- The 0.80/0.90/1.00/1.10 mm hole gauge with calibrated pins.
- At least two J1 holes and two K1 holes.
- ENIG coverage and solder-mask registration at all QFN sites.
- U103/U203 via cap planarity and the supplier witness microsection.

## QFN inspection

Perform AOI and 2D/3D X-ray on every populated AKM site.

Pass criteria:

- No perimeter opens, bridges, solder balls, or package misorientation.
- Package offset no more than 0.10 mm in X or Y.
- Package tilt no more than 0.10 mm corner-to-corner.
- Exposed-pad solder coverage at least 65 percent.
- Total exposed-pad void area no more than 25 percent.
- No individual void greater than 10 percent of exposed-pad area.
- No continuous void or solder-depleted channel from the exposed-pad center to
  a package edge.
- No evidence of solder wicking at U103/U203.
- U103 and U203 meet every limit on assemblies A, B, and C without rework.

Record open and bottom-tented controls even if they fail; they are comparison
sites and their results determine whether the less expensive process is usable.

## Through-hole inspection

Before soldering K1 and J1:

- Insert the exact sample by hand without tools, force, or lead forming.
- Verify all leads enter simultaneously and the body seats within 0.20 mm.
- Photograph top and bottom seating.
- Verify terminal numbers against the manufacturer schematic.

After soldering:

- Confirm barrel wetting and fillet without bridge, land lift, or body damage.
- Check K1 coil and both Form-C contact maps.
- Check J1 CTIA tip/ring/ring/sleeve map and both switch states with a mating
  plug.
- Perform 100 plug/unplug cycles on J1, then repeat continuity and visual
  inspection. This is a coupon handling screen, not the connector's full rated
  life qualification.

## Release record

Complete `coupon-results-template.csv`, attach dimensional photographs,
microsection, AOI, X-ray, and electrical mapping records, then sign the final
disposition. Only an engineering `PASS` may clear the associated routing and
production gates.
