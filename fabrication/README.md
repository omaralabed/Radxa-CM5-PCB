# Fabrication Outputs

Place manufacturing outputs here when the design is ready.

The controlled one-shot PCBWay release gate is under `pcbway-release/`. Its
manifest covers all production PCBs, machined enclosure parts, harnesses,
source files, test instructions, and physical signoffs. The archive builder
will not run while any required release item is open or missing.

Expected outputs:

- Gerbers
- Drill files
- Pick-and-place / CPL
- BOM
- Assembly drawing
- Fabrication drawing
- Design rule report

Controlled harness work instructions are under `harnesses/`. They remain
prototype-controlled until their finished lengths are verified in the first
mechanical article.

The current mechanical gate is `mechanical-release/` revision A2 and remains
`HOLD_FOR_MEASUREMENT`. Rev L nominal envelopes and controlled PCB support
coordinates may be used for engineering layout. Production panel, tray,
sidewall, and final drilling files are prohibited until all M001-M080 checks
and signoffs are complete.
