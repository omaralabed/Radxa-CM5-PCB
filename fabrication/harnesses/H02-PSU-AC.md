# H02 Fused-Inlet to PSU AC Harness

## Status

Preliminary safety-controlled definition. A qualified product-safety engineer
must release the finished mains harness, PE bond, routing, guarding, and strain
relief before any production build.

## PSU Connector

The white connector shown on the `RPS-400-24-C` is AC input `CN1`, not the
24 V output. MEAN WELL specifies a JST `B3P-VH` or equivalent.

| CN1 cavity | Assignment | Conductor |
| ---: | --- | --- |
| 1 | `AC/L` | brown, fused line from C14 inlet |
| 2 | no pin | no contact; leave empty |
| 3 | `AC/N` | blue, neutral from C14 inlet |

Use JST `VHR-3N` housing with two JST `SVH-21T-P1.1` contacts. Use 18 AWG
stranded copper, 600 V, 105 C minimum wire unless the final safety review
requires a larger conductor or a different recognized wiring style.

Prototype finished length is 750 +/- 20 mm from the released C14 terminal
reference to the rear face of the VHR-3N housing. This is a first-article
service-loop target, not a final production dimension.

## Protective Earth

Protective earth does not pass through CN1. Use a separate green/yellow
conductor from the C14 earth terminal to the primary chassis stud, with a
separate branch or approved bond to the PSU chassis grounding point. Use ring
terminals, toothed washers, locking hardware, and a dedicated earth stud. Do
not rely on painted panel contact or ordinary PSU mounting screws as the sole
protective-earth path.

## Production Controls

- Mark both ends `DANGER MAINS H02`.
- Put H02 and PE inside the guarded AC zone and physically separate them from
  H01 and all SELV/data/audio harnesses.
- Store the closed-case service loop in releasable, insulated cushioned clamps.
  With those clamps released, H02 must allow the top panel to rise at least
  300 mm and tilt at least 45 degrees without tension or loss of guarding.
- The flexible panel-to-chassis PE bond must remain slack throughout that same
  service position and must be the last conductor disconnected during panel
  removal.
- No part of the released or stored loop may enter a fan, PSU airflow path,
  sharp-edge zone, or low-voltage PCB keepout.
- Position 2 of the VHR-3N housing must remain empty.
- Perform continuity, polarity, PE-bond, dielectric-withstand, leakage-current,
  fuse, strain-relief, and enclosure safety tests to the applicable final
  product standard.
- Do not substitute a generic marketplace JST-lookalike harness without proof
  of connector authenticity, wire recognition, voltage/temperature rating,
  crimp qualification, and lot traceability.
- Release the final H02 and PE lengths only after the closed-case retention and
  full service-opening tests pass in the first mechanical article.

Manufacturer source:
https://www.meanwell.com/Upload/PDF/RPS-400/RPS-400-SPEC.PDF
