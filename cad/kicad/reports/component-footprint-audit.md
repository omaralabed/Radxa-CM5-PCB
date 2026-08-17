# Component and Footprint Audit

Generated once from each physical board root so hierarchical child components are not double-counted. This report is deterministic and contains no audit timestamp.

## Current gate

- Components audited: 1203
- Route-ready components: 1188
- Intentional non-board symbols: 5
- Routing blockers: 10
- Production/BOM blockers: 11

A routing blocker has no footprint, references an unresolved footprint, or still requires a routing-critical mechanical coupon. A production blocker also includes any board-mounted component without a locked manufacturer and MPN.

## By sheet

| Sheet | Components | Routing blockers | Production blockers |
|---|---:|---:|---:|
| PWR-SELECT | 111 | 0 | 0 |
| CM5-Carrier | 518 | 0 | 1 |
| Audio-8x8 | 574 | 10 | 10 |

## Gate commands

```sh
python3 cad/kicad/audit_footprint_readiness.py
python3 cad/kicad/audit_footprint_readiness.py --routing
python3 cad/kicad/audit_footprint_readiness.py --release
```

The default command refreshes this report. `--routing` fails while placement/routing blockers remain. `--release` also fails while production-part evidence is incomplete.

See `component-footprint-audit.csv` for every reference designator and its exact blocking reason.
