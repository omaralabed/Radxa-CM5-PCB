# Native PCB-A0 Placement Baseline

## Release State

**ENGINEERING PLACEMENT BASELINE - NOT ROUTED - NOT FABRICATION READY**

The three native KiCad PCB files now exist and carry their complete schematic
netlists. Only source-controlled mating connectors and controlled structural
supports are inside the board outlines. Every other footprint is deliberately
staged outside its board, so no tentative placement can be mistaken for an
approved physical location.

## No-Guesswork Geometry Rule

- Never redraw, resize, move, or "clean up" a connector pad or hole to satisfy
  DRC. Correct the process rule or stop the release for manufacturer review.
- A footprint enters the board only after its drawing or official reference
  design fixes the local pad/hole pattern and the mechanical drawing fixes its
  board datum.
- The validators compare locked XLR, RJ45, and SIM pad positions, sizes,
  drills, shapes, orientations, attributes, and layer sets to their source
  libraries. The CM5 validator separately compares all 304 generated connector
  pad records to Radxa's official V2.20 PADS source.
- Parts without authoritative geometry remain in the off-board staging area.

## Locked Mating Geometry

| Interface | Controlled source | Locked result |
|---|---|---|
| Radxa CM5 | Radxa CM5 IO V2.20 PADS board and BOM; V2.21 pin workbook; Hirose `DF40C-100DS-0.4V(51)` drawing | Three 100-contact receptacles plus four grounded module mounts; one rigid bottom-side transform |
| Balanced audio | Neutrik `NC3MAV` and `NC3FAV` source footprints; Rev L face-center datums | 16 connector origins and all pad/hole geometry locked |
| Ethernet | Wurth `74991114412` manufacturer footprint/STEP; Rev L opening centers | Four MagJack origins and pad/hole geometry locked |
| Nano-SIM | Wurth `693043020611` manufacturer footprint; Rev L service centers | Two holder origins and pad/hole geometry locked |
| PCB supports | `pcb-support-pattern-a2.csv` and project M3 footprint | Six supports on each long PCB, 3.40 mm NPTH |

The CM5 source relation is `J24 - U33 = (11.405, -25.415) mm` at `-90 deg`.
The installed carrier uses the common underside transform
`T(x,y) = R90 * mirror-X(x,y) = (-y,-x)`, producing:

- `J501` and `J502`: `(127.000, 245.000) mm`, `90 deg`, `B.Cu`.
- `J503`: `(152.415, 233.595) mm`, `180 deg`, `B.Cu`.

## Native Boards

| Board | Outline | Stack starting point | Netlist footprints | Locked connectors | Supports |
|---|---:|---:|---:|---:|---:|
| AUDIO-8X8 | 78 x 268 mm | 6 layers, 1.60 mm | 572 | 16 | 6 |
| CM5-CARRIER | 166 x 268 mm | 10 layers, 1.60 mm | 507 | 9 | 6 |
| PWR-SELECT | 116 x 80 mm | 6 layers, 1.60 mm | 111 | 0 | 0 pending tray datum |

These rectangles are controlled maximum board envelopes. Final routed-edge
details and the selector support pattern require released mechanical datums.

## PCBWay Process Contract

The boards encode a `0.20 mm` minimum mechanical drill and `0.20 mm`
NPTH-to-copper clearance. This preserves the unmodified Wurth MagJack pattern,
whose closest NPTH-to-copper distance is `0.2312 mm`.

PCBWay's published capability table permits a 0.20 mm mechanical drill on a
1.60 mm board. Its engineering guidance states 0.20 mm minimum spacing from an
NPTH to adjacent copper. Sources accessed 2026-08-17:

- <https://www.pcbway.com/capabilities.html>
- <https://www.pcbway.com/helpcenter/Engineering_Questions/the_spacing_from_hole_to_trace.html>

The 10-layer carrier must receive PCBWay engineering/advanced-process review.
PCBWay may not enlarge or move connector holes or pads. If CAM cannot accept
the documented geometry and stackup together, the release stops for a written
engineering disposition.

## DRC Baseline

| Board | Errors | Warnings | Meaning |
|---|---:|---:|---|
| AUDIO-8X8 | 0 | 8 | Expected library-mismatch notices because the overhanging male-XLR outline ink is moved from `F.SilkS` to `F.Fab`; pads and holes remain byte-for-byte equivalent by geometry signature |
| CM5-CARRIER | 18 | 0 | Only staged `Q1110`, `Q1111`, and preliminary `J910`; no locked connector or support appears in a violation |
| PWR-SELECT | 0 | 0 | Clean placement baseline; all parts remain staged |

Unconnected and schematic-parity findings are retained in the JSON reports;
they are expected before placement/routing and are not excluded. Final release
requires fully routed boards with zero real DRC errors, resolved parity, and
signed exceptions only where an immutable manufacturer land pattern demands
one.

## Rebuild And Check

```sh
python3 cad/kicad/generate_interface_schematics.py
python3 cad/kicad/SYSTEM/generate_system_schematic.py
'/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3' cad/kicad/generate_pcb_projects.py
python3 cad/kicad/CM5-CARRIER/validate_cm5_mating_geometry.py
'/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3' cad/kicad/validate_pcb_placement.py
python3 cad/kicad/validate_pcb_drc_baseline.py
```

The controlled DRC reports are under `cad/kicad/PCB-REVIEW/`.
For the complete repeatable gate, run `cad/kicad/review_pcb_baseline.sh`.
