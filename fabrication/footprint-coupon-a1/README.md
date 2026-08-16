# Footprint Coupon A1 Fabrication Package

This directory contains the controlled manufacturing package for the Radxa CM5
ProComm footprint qualification coupon.

## Release state

- CAD generation: complete.
- KiCad validation: complete.
- KiCad DRC: zero violations.
- Bare-board fabrication: pending.
- Assembly and X-ray qualification: pending.
- AUDIO-8X8 / CM5-CARRIER routing release: blocked pending signed results.

## Factory files

Run `build_release.sh` to regenerate:

- `output/gerbers/`: six copper layers, paste, mask, legend, and outline.
- `output/drill/`: separate plated and non-plated Excellon files, drill map,
  and drill report.
- `output/drawings/`: fabrication and assembly PDFs.
- `output/placement/`: CSV component positions.
- `output/renders/`: top and bottom board renders.
- `output/filled_via_coordinates.csv`: the 50 selective Type VII vias.
- `output/Footprint-Coupon-A1-Gerber-Drill.zip`: upload archive.
- `output/SHA256SUMS.txt`: release checksums.

Read `PCBWAY_RFQ.md` and `ASSEMBLY_AND_INSPECTION.md` before quoting. Do not
substitute via treatment, hole sizes, finish, stackup, stencil, or component
part numbers without written engineering approval.
