# Footprint Qualification Coupon A1

## Purpose

This coupon is the physical release gate for four currently unqualified package
interfaces:

- AKM AK5558VN, 64-pin QFN, 9 x 9 mm, 0.5 mm pitch, exposed pad.
- AKM AK4458VN, 48-pin QFN, 7 x 7 mm, 0.5 mm pitch, exposed pad.
- Panasonic TQ2-12V relay, standard PC-board terminals.
- Kycon STX-353K7A-6N-KTTR vertical CTIA jack.

The coupon is not functional circuitry. It verifies land geometry, stencil
behavior, thermal-via treatment, soldering, lead insertion, seating, and pin
mapping before the AUDIO-8X8 and CM5-CARRIER boards are routed.

## Controlled design

The generated KiCad project is in `cad/kicad/FOOTPRINT-COUPON`.

| Site | Device | Treatment | Purpose |
|---|---|---|---|
| U101 | AK5558VN | Thermal vias open on the bottom | Solder-wicking control |
| U102 | AK5558VN | Bottom-tented thermal vias | Low-cost process comparison |
| U103 | AK5558VN | Selective IPC-4761 Type VII filled/capped vias | Production candidate |
| U201 | AK4458VN | Thermal vias open on the bottom | Solder-wicking control |
| U202 | AK4458VN | Bottom-tented thermal vias | Low-cost process comparison |
| U203 | AK4458VN | Selective IPC-4761 Type VII filled/capped vias | Production candidate |
| K1 | Panasonic TQ2-12V | 0.90 mm finished holes | Lead fit, seating, and pin map |
| J1 | Kycon STX-353K7A-6N | 0.80 mm finished holes, 1.10 x 1.80 mm lands | Lead fit, retention, seating, and CTIA/switch map |

The J1 pattern corrects the old preliminary pattern's overlapping copper. The
Kycon drawing shows 0.5 x 0.2 mm leads but does not publish a recommended PCB
land pattern, so J1 remains sample-and-coupon controlled.

## Board construction

- Finished board: 100.0 x 80.0 mm.
- Six copper layers, 1.60 mm nominal.
- 1 oz final copper on all layers.
- FR-4, Tg 150 C minimum.
- ENIG finish, green solder mask, white legend.
- Four 3.20 mm NPTH tooling holes and three global fiducials.
- Separate 0.80, 0.90, 1.00, and 1.10 mm finished-hole gauge.
- Fifty selective 0.20 mm Type VII vias: U103 and U203 only.

The stackup in the KiCad file follows PCBWay's published 1.6 mm six-layer
starting construction. PCBWay must confirm the final production stackup and
selective via-fill process in writing before fabrication.

## Build matrix

Order five bare coupons. Assemble three:

| Assembly | Populate | Purpose |
|---|---|---|
| A | U101-U103, U201-U203, K1, J1 | Compare all process variants and THT fit |
| B | U103 and U203 only | Type VII repeatability |
| C | U103 and U203 only | Type VII repeatability |

Keep two bare boards for dimensional inspection, solderability troubleshooting,
or destructive sectioning if the supplied witness microsection is insufficient.

## Acceptance summary

Physical release requires all of the following:

1. Bare-board dimensions and finished holes pass incoming inspection.
2. PCBWay supplies a Type VII process confirmation and microsection evidence for
   the selective U103/U203 vias.
3. All populated QFN perimeter joints are free of opens and bridges.
4. X-ray shows at least 65 percent exposed-pad solder coverage, no more than 25
   percent total exposed-pad void area, no individual void over 10 percent, and
   no continuous void path to the package edge.
5. U103 and U203 pass on assemblies A, B, and C without solder loss into thermal
   vias, package tilt, or rework.
6. K1 inserts by hand without lead forming and seats within 0.20 mm of the PCB.
7. J1 inserts without lead damage, seats within 0.20 mm, survives plug/unplug
   handling without land or barrel damage, and its six-terminal map is confirmed.
8. A signed copy of `fabrication/footprint-coupon-a1/coupon-results-template.csv`
   records the measurements, images, disposition, inspector, and date.

These are project acceptance limits, not a claim of formal product
certification. Any failure keeps the related routing gate open and requires a
new coupon revision.

## Source evidence

- AK5558VN datasheet: <https://www.akm-semi.com/pdf-0f/ak5558vn.pdf>
- AK4458VN datasheet: <https://www.akm-semi.com/pdf-c1/ak4458vn.pdf>
- Panasonic TQ2-12V product page: <https://na.industrial.panasonic.com/products/relays-contactors/mechanical-signal-relays/lineup/signal-relays/series/119572/model/119888>
- Kycon STX-353K7A drawing: <https://www.kycon.com/Catalog_PDF/STX-353K7A.pdf>
- PCBWay six-layer stackup: <https://www.pcbway.com/blog/Engineering_Technical/stackup___pcbway.html>
- PCBWay capabilities: <https://www.pcbway.com/capabilities.html>
- PCBWay via covering / IPC-4761 Type VII description: <https://www.pcbway.com/pcb_prototype/PCB_Via_Covering.html>

## Regeneration

Run:

```sh
cad/kicad/FOOTPRINT-COUPON/review_coupon.sh
fabrication/footprint-coupon-a1/build_release.sh
```

Both commands must pass before sending the fabrication archive.
