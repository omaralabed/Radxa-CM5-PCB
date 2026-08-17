# PCBWay One-Shot Release Package

## Status

**HOLD_ENGINEERING**

This directory is the only controlled entry point for the final PCBWay
submission. Do not upload concept SVGs, schematic-only projects, partial BOMs,
or preliminary Gerbers as a production order. The final archive is built only
after `validate_release.py --release` passes.

The current repository is not yet a production package:

- the sixteen detailed schematic sheets pass ERC;
- `CM5-CARRIER`, `AUDIO-8X8`, and `PWR-SELECT` now have native `.kicad_pcb`
  placement baselines with complete netlists, but they are deliberately
  unrouted and are not fabrication files;
- no production-board Gerber, NC-drill, CPL, assembly-drawing, or board STEP
  outputs exist;
- ten physical footprint-coupon results still block final route freeze and fabrication release;
- 11 component rows still block production release;
- mechanical release A2 remains `HOLD_FOR_MEASUREMENT`.

The footprint coupon is a separate qualification order. Its ready-to-upload
factory package is in `../footprint-coupon-a1/`. Passing CAD review on that
coupon does not close the physical X-ray, microsection, insertion, seating,
and pin-map requirements.

## One-Shot Rule

PCBWay receives one controlled archive after every required row in
`release-manifest-a0.csv` is `READY`, all referenced files exist, the physical
signoffs are attached, and the release validator passes. Any replacement made
after archive creation requires a new package revision and checksum file.

PCBWay's current PCBA guidance requires Gerbers, BOM, and centroid/pick-and-
place data. Their detailed assembly guidance also calls for copper,
silkscreen, solder-paste, NC-drill, and fabrication/assembly information. The
project adds schematic PDFs, 3D STEP, controlled stackup/impedance data,
polarity drawings, harness instructions, programming data, and acceptance
tests because this assembly is too complex to rely on minimum upload fields.

Official references:

- https://www.pcbway.com/assembly-file-requirements.html
- https://www.pcbway.com/assembly-process.html
- https://www.pcbway.com/helpcenter/Findproducts/How_do_I_place_an_order_.html

## Package Structure

The final archive contains five independently reviewable packages:

1. `01-cm5-carrier`: routed carrier fabrication, assembly, source, and test
   data.
2. `02-audio-8x8`: routed balanced-audio fabrication, assembly, source, and
   audio test data.
3. `03-pwr-select`: routed no-blink source-selector fabrication, assembly,
   source, and power-transfer test data.
4. `04-mechanical`: released top panel, four-side frame, bottom tray, sidewall
   fan openings/reinforcements, guards, hoods, datums, tolerances, material,
   finish, and inspection drawings.
5. `05-harness-test`: H01/H02/H03 and interboard harness drawings, wire tables,
   labels, lengths, strain relief, firmware/programming package, bring-up,
   calibration, and final acceptance procedure.

## Release Sequence

1. Build and sign Footprint Coupon A1.
2. Complete the actual-case mechanical register M001-M080 and pass
   `validate_mechanical_release.py --release`.
3. Freeze the PCBWay-controlled stackups and impedance tables.
4. Route the three production boards and complete SI, PI, thermal, safety, and
   current-density review.
5. Close every production MPN, DNP, polarity, and customer-supplied-part row.
6. Generate and independently inspect Gerber, NC drill, BOM, CPL, drawings,
   STEP, and source archives for each board.
7. Complete harness, programming, calibration, and acceptance files.
8. Run `python3 validate_release.py --release`, then
   `python3 build_submission.py`.

## Factory Change Control

- PCBWay may not substitute a component, alter copper, resize holes, change
  stackup, modify paste apertures, or change machined geometry without written
  engineering approval.
- All questions must reference the package revision, manifest item ID, board
  revision, and affected designators.
- The package checksum list controls every uploaded file.
- First build is an engineering first article. Production quantity is released
  only after electrical, thermal, RF, audio, source-transfer, mechanical,
  vibration, and safety acceptance passes.
