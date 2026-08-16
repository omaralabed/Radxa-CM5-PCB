# PCBWay RFQ - Footprint Coupon A1

## Order parameters

| Parameter | Requirement |
|---|---|
| Quantity | 5 bare boards |
| Size | 100.0 x 80.0 mm |
| Layers | 6 |
| Thickness | 1.60 mm nominal |
| Material | FR-4, Tg 150 C minimum |
| Copper | 1 oz finished, all six layers |
| Finish | ENIG |
| Solder mask | Green, both sides |
| Legend | White, both sides where supplied |
| Electrical test | 100 percent bare-board test |
| Edge | Routed, no V-score or mouse bites on finished coupon |
| Finished-hole tolerance | PCBWay standard or better; report measured coupon values |
| Impedance control | Not required for this nonfunctional coupon |

Use PCBWay's published 1.6 mm six-layer stackup as the starting construction:

`F.Cu 35 / PP 0.11 / In1 35 / Core 0.53 / In2 35 / PP 0.11 / In3 35 / Core 0.53 / In4 35 / PP 0.11 / B.Cu 35`, all dimensions in micrometers for copper and millimeters for dielectric.

Confirm the final pressed stackup, material family, Tg, finished thickness, and
copper values before production. The KiCad stackup is an RFQ target, not
permission to change the factory-approved laminate construction silently.

## Selective via treatment

The coupon intentionally contains three exposed-pad treatments. Preserve the
difference:

- U101 and U201: bottom solder-mask openings remain open; no fill or cap.
- U102 and U202: bottom-tented vias; no fill or cap.
- U103 and U203: IPC-4761 Type VII, non-conductive resin filled, planarized,
  copper capped, and plated over.

Apply Type VII processing only to the 50 coordinates in
`output/filled_via_coordinates.csv`. Finished hole is 0.20 mm. Do not globally
fill all vias and do not alter U101/U201 or U102/U202. If selective Type VII is
not supported on one panel, stop and request engineering disposition; do not
manufacture a substituted coupon.

Supply:

- Written DFM confirmation of the selective Type VII process.
- A finished stackup table.
- Final drill chart and finished-hole tolerance.
- Type VII fill/cap process certificate.
- Microsection of a same-panel Type VII witness via showing continuous fill,
  planarization, and copper cap.
- Bare-board electrical-test report.
- Dimensional inspection report for board outline, 0.20 mm vias, 0.80 mm J1
  holes, and 0.90 mm K1 holes.

## Fabrication hold points

1. Hold before tooling if any Gerber, drill, stackup, or selective-fill conflict
   exists.
2. Send DFM questions and proposed changes in writing.
3. Release fabrication only after the stackup and selective-fill map are
   acknowledged by both parties.

Reference data:

- PCBWay capabilities: <https://www.pcbway.com/capabilities.html>
- PCBWay six-layer stackup: <https://www.pcbway.com/blog/Engineering_Technical/stackup___pcbway.html>
- PCBWay Type VII via process: <https://www.pcbway.com/pcb_prototype/PCB_Via_Covering.html>
