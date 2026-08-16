# Component and Footprint Audit

Generated from all ten native KiCad sheets. This report is deterministic and contains no audit timestamp.

## Current gate

- Components audited: 527
- Route-ready components: 165
- Intentional non-board symbols: 1
- Routing blockers: 361
- Production/BOM blockers: 429

A routing blocker has no footprint or references a footprint that cannot be resolved. A production blocker also includes any routed component without a locked manufacturer and MPN.

## By sheet

| Sheet | Components | Routing blockers | Production blockers |
|---|---:|---:|---:|
| PWR-SELECT | 104 | 0 | 67 |
| CM5-Carrier | 9 | 5 | 5 |
| CM5-Core-Allocated | 7 | 4 | 4 |
| Network-PCIe | 59 | 42 | 43 |
| WWAN-SIM | 18 | 14 | 14 |
| Display-Harness | 13 | 10 | 10 |
| Audio-Control | 38 | 36 | 36 |
| Power-Regulators-A1 | 198 | 186 | 186 |
| Thermal-IO | 60 | 60 | 60 |
| Audio-8x8 | 21 | 4 | 4 |

## Gate commands

```sh
python3 cad/kicad/audit_footprint_readiness.py
python3 cad/kicad/audit_footprint_readiness.py --routing
python3 cad/kicad/audit_footprint_readiness.py --release
```

The default command refreshes this report. `--routing` fails while placement/routing blockers remain. `--release` also fails while production-part evidence is incomplete.

See `component-footprint-audit.csv` for every reference designator and its exact blocking reason.
