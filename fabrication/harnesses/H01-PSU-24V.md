# H01 Bottom-PSU 24 V Harness

## Purpose

`H01` carries the low-voltage output of the bottom-mounted MEAN WELL
`RPS-400-24-C` to `PWR-SELECT J101`. It is not an AC mains harness.

## Electrical Definition

| Circuit | PSU end | Wire | PCB end |
| --- | --- | --- | --- |
| `+24V_PSU` | `CN3 +V`, M3.5 closed ring | 14 AWG red | `P101-1` -> `J101-1 V24_IN` |
| `0V_PSU` | `CN2 -V`, M3.5 closed ring | 14 AWG black | `P101-2` -> `J101-2 GND` |

The connector cavity numbers and continuity test control polarity. Do not use
wire color alone as the acceptance method.

## Mechanical Definition

- Prototype finished length: 750 +/- 20 mm, measured from each ring center to
  the rear face of the fully assembled Mega-Fit receptacle.
- Use 14 AWG stranded copper, UL1015 or equivalent, 600 V, 105 C minimum.
- Keep red and black conductors together in abrasion-resistant sleeving except
  for the minimum breakout needed at both ends.
- Install the Molex `105415-0002` TPA after both contacts pass the primary-lock
  tug check.
- Label the connector end `H01 / PWR-SELECT J101 / PIN 1 +24V`.
- Label the ring ends `CN3 +V` and `CN2 -V` individually.
- Clamp the dressed harness within 50 mm of J101 and near the PSU so neither
  the PCB header nor PSU screws carry vibration or service strain.
- Store the closed-case service loop in releasable cushioned clamps. The loop
  must not enter either fan inlet, the PSU airflow path, or a board keepout.
- With the clamps released, H01 must let the top panel rise at least 300 mm
  above its support frame and tilt at least 45 degrees without connector,
  terminal, or conductor tension.
- Keep H01 outside the guarded mains corridor and away from sharp sheet-metal
  edges. Fit an edge grommet anywhere a crossing cannot be avoided.

## Assembly

1. Cut one red and one black conductor to the controlled build length.
2. Crimp TE `320619` rings at the PSU ends with the approved PIDG tooling.
3. Crimp Molex `76823-0344` contacts at the PCB ends with tooling qualified to
   Molex application specification `768232000-AS`.
4. Insert red into housing cavity 1 and black into cavity 2 until the primary
   latches engage.
5. Perform a light individual contact tug check, then install TPA
   `105415-0002` fully seated.
6. Apply abrasion sleeve, identification labels, and strain-relief features.
7. Connect red to PSU `CN3 +V` and black to PSU `CN2 -V`. Use a calibrated
   driver and never exceed the PSU limit of 8 lb-in / 90 cN-m.

## Acceptance Tests

1. Visual inspection: correct parts, no exposed conductor, no cut insulation,
   TPA fully seated, ring barrels and contact insulation wings correctly
   formed.
2. Point-to-point continuity: `CN3 +V` ring to P101 cavity 1; `CN2 -V` ring to
   P101 cavity 2.
3. Isolation: greater than 20 MOhm between the two circuits at 100 VDC.
4. Four-wire resistance: record each circuit; reject either circuit above
   25 mOhm before mating-contact resistance is added to the system record.
5. Polarity at J101: with current-limited 24 V applied at the PSU end, verify
   `J101-1` is positive relative to `J101-2` before connecting PWR-SELECT.
6. Retain the crimp-height and pull-force records required by the terminal
   manufacturers for each production lot.

## Release Gate

The 750 mm length is the first-article service-loop target, not a final
production dimension. Release the final length only after the installed
harness passes both the closed-case retention check and the 300 mm lift / 45
degree tilt service-opening test. Do not coil unused cable in the PSU airflow
path.

## Manufacturer Sources

- MEAN WELL RPS-400 specification:
  https://www.meanwell.com/Upload/PDF/RPS-400/RPS-400-SPEC.PDF
- Molex `76825-0002` PCB header:
  https://www.molex.com/en-us/products/part-detail/768250002
- Molex `171692-0202` receptacle series:
  https://www.molex.com/en-us/products/series-chart/171692
- Molex `76823-0344` terminal:
  https://www.molex.com/en-us/products/part-detail/0768230344
- Molex `105415-0002` TPA series:
  https://www.molex.com/en-us/products/series-chart/105415
- TE Connectivity `320619` ring terminal:
  https://www.te.com/en/product-320619.html
