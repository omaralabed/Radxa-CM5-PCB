# Component and Footprint Audit

Generated from all sixteen native KiCad sheets. This report is deterministic and contains no audit timestamp.

## Current gate

- Components audited: 1023
- Route-ready components: 1007
- Intentional non-board symbols: 6
- Routing blockers: 10
- Production/BOM blockers: 78

A routing blocker has no footprint, references an unresolved footprint, or still requires a routing-critical mechanical coupon. A production blocker also includes any board-mounted component without a locked manufacturer and MPN.

## By sheet

| Sheet | Components | Routing blockers | Production blockers |
|---|---:|---:|---:|
| PWR-SELECT | 108 | 0 | 67 |
| CM5-Carrier | 9 | 0 | 0 |
| CM5-Core-Allocated | 7 | 0 | 0 |
| Network-PCIe | 64 | 0 | 0 |
| WWAN-SIM | 23 | 0 | 0 |
| Display-Harness | 13 | 0 | 0 |
| Audio-Control | 57 | 0 | 1 |
| Power-Regulators-A1 | 155 | 0 | 0 |
| Thermal-IO | 66 | 0 | 0 |
| Audio-8x8 | 21 | 0 | 0 |
| Audio-TDM-Clock | 18 | 0 | 0 |
| AK5558-ADC | 36 | 1 | 1 |
| AK4458-DAC | 23 | 1 | 1 |
| Audio-Inputs | 176 | 0 | 0 |
| Audio-Outputs | 200 | 8 | 8 |
| Audio-Power | 47 | 0 | 0 |

## Gate commands

```sh
python3 cad/kicad/audit_footprint_readiness.py
python3 cad/kicad/audit_footprint_readiness.py --routing
python3 cad/kicad/audit_footprint_readiness.py --release
```

The default command refreshes this report. `--routing` fails while placement/routing blockers remain. `--release` also fails while production-part evidence is incomplete.

See `component-footprint-audit.csv` for every reference designator and its exact blocking reason.
