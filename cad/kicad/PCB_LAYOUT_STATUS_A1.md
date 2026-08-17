# Native PCB-A1 Engineering Placement

## Release State

**ENGINEERING PLACEMENT BASELINE - NOT ROUTED - NOT FABRICATION READY**

The three native KiCad PCB files carry their complete schematic netlists and
all 1,190 schematic footprints are now inside their correct board outlines.
Source-controlled mating connectors and structural supports remain locked.
Internal parts have deterministic, functional engineering placements so the
PCB editor and 3D viewer describe one physical assembly instead of off-board
staging clouds.

This is still an unrouted placement baseline. Internal component coordinates
may move during power-integrity, signal-integrity, thermal, and routing review;
locked mating datums and support holes may not move.

## No-Guesswork Geometry Rule

- Never redraw, resize, move, or "clean up" a connector pad or hole to satisfy
  DRC. Correct the process rule or stop the release for manufacturer review.
- Every footprint uses its actual selected package land pattern. External mating
  parts enter only at drawing-controlled mechanical datums; internal placement
  is an explicit engineering decision and is not represented as a factory datum.
- The validators compare locked XLR, RJ45, and SIM pad positions, sizes,
  drills, shapes, orientations, attributes, and layer sets to their source
  libraries. The CM5 validator separately compares all 304 generated connector
  pad records to Radxa's official V2.20 PADS source.
- Preliminary package blockers remain clearly identified by the footprint audit
  and must close before route freeze; no part is hidden outside a board.

## Functional Placement

- `AUDIO-8X8`: all non-XLR circuitry is on `B.Cu`, split into digital/AKM,
  eight-channel analog, and isolated-power regions. The sixteen XLRs remain
  locked on `F.Cu`.
- `CM5-CARRIER`: unlocked circuitry is on `F.Cu`, split into network,
  service/WWAN/display/audio/thermal, power-conversion, and CM5-support regions.
  The exact CM5 mating assembly remains on `B.Cu`.
- `PWR-SELECT`: high-current and through-hole hardware is on `F.Cu`; compact
  control circuitry is on `B.Cu`.
- Dense internal reference/value fields are carried on Fab layers. This keeps
  the assembly data available without overlapping production silkscreen labels.

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
| AUDIO-8X8 | 69 | 76 | Errors are only KiCad opposite-side THT/NPTH-versus-XLR-courtyard notices; copper and support-hole clearances pass. Warnings are 68 placement silkscreen cleanups plus eight controlled male-XLR library notices. |
| CM5-CARRIER | 18 | 74 | Errors remain confined to preliminary `Q1110`, `Q1111`, and `J910` lands. Warnings are placement silkscreen cleanup items. |
| PWR-SELECT | 0 | 12 | No placement/copper errors; twelve silkscreen cleanup warnings. |

The audio courtyard notices come from KiCad checking through-hole pins against
body courtyards on both assembly sides. The validator permits them only when a
locked `F.Cu` XLR and an unlocked `B.Cu` part form the pair; ordinary pad,
hole, and same-side courtyard conflicts remain hard failures. Unconnected and
schematic-parity findings remain expected until routing. Final release still
requires zero unresolved DRC errors, completed silkscreen cleanup, resolved
parity, and signed exceptions only where immutable manufacturer geometry
requires one.

## 3D Review

Controlled top and bottom renders for all three assemblies are under
`cad/kicad/PCB-REVIEW/3D/`. Each render is generated from the native PCB file;
the validator prevents any schematic footprint from returning to off-board
staging.

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
