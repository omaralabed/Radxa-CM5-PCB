# Panel-Mounted Parts Selection

## Status

This is the preliminary mechanical part freeze for the iM2300 top panel. It
supports schematic and 3D floorplanning, but it is not permission to cut the
production panel. The current Rev I connector-placement artwork remains the
authoritative layout.

The factory cut drawing can be released only after:

- the actual iM2300 opening is measured at the 38.1 mm panel recess;
- one sample of every panel-interfacing part is fitted to a 3.2 mm coupon; the
  RA812 switch location must be locally rear-pocketed to no more than 3.0 mm or
  use a 3.0 mm panel;
- PCB-to-panel Z height and connector protrusion are fixed;
- the Gold Mount bracket drawing and lid monitor sample are measured;
- the hinge harness, SIM access, and RF pigtail interfaces are resolved.

## Selected Parts

| Function | Qty | Manufacturer part | Mechanical status |
| --- | ---: | --- | --- |
| XLR outputs | 8 | Neutrik `NC3MAV` | Selected; use official A-series drawing and sample coupon |
| XLR inputs | 8 | Neutrik `NC3FAV` | Selected; use official A-series drawing and sample coupon |
| WAN/LAN MagJacks | 4 | Bel `V8BR-1AX1-GH` | Selected for PCB; panel opening waits for PCB Z height |
| Fused C14 inlet | 1 | Qualtek `719W-00/03` | Conditional; exact cutout known, current-rating acceptance required |
| Backup inlet | 1 | LEMO `EGG.1B.302.CLL` | Selected; M12 panel drill, IP50 only |
| Main power control | 1 | E-Switch `RA812C1121` | Selected; maintained DPST OFF-ON rocker; thickness-dependent rectangular cutout |
| Headset jack | 1 | Kycon `STX-353K7A-6N-KTTR` | Selected for PCB; panel clearance waits for PCB Z height |
| Status indicators | 6 | Bulgin `DX06` wire-lead, 12 V, black brass | Selected family; 6 mm cutouts |
| Panel lights | 2 | YIS Marine `LS102W` | Selected concept; 22 mm cutout, 38 mm matte diffused face, 12 V warm-white SMD light, IP67 |
| Night-light touch control | 1 | E-Switch `CS7L2FR` | Selected; 22.20 +0.25/-0.00 mm cutout, latching capacitive low-side output, IP68 |
| Top enclosure fans | 2 | Delta `THA0412AD-TZW3` | Selected; fan 1 filtered intake, fan 2 exhaust; 40 x 40 x 20 mm, 12 V, 4-wire PWM/tach, IP55 fan body |
| Intake filter guard | 1 | Qualtek `09150-F/30` | Selected for intake; 40 mm frame, 30 PPI media |
| Exhaust guard/louver | 1 | TBD | Low-restriction, finger-safe, splash-resistant 40 mm guard with outward-facing louver |
| Nano-SIM holders | 2 | Wurth `693043020611` | Selected electrically; requires vertical service daughterboard |
| Wi-Fi RF pigtails | 4 | TE `2016695-4` | Conditional on AW7915-NP1 IPEX receptacle and 200 mm route check |
| Cellular RF pigtails | 4 | TE `2016694-4` | Conditional on modem receptacle and 200 mm route check |
| Gold Mount battery | 1 | Anton/Bauer Dionic XT90 `8675-0125` | Selected battery; 99 Wh, 14.1 V, 12 A continuous |
| Gold Mount bracket | 1 | Anton/Bauer QRC-GOLD `8375-0094` | User-selected compact bracket; approximately 119.4 x 76.2 x 12.7 mm; mounts to the top panel/custom frame, never to a PCB; controlled drawing/sample still required |
| Lid display | 1 | JUNEBOX, Amazon ASIN `B0GK5X95D9` | User-locked; connector and mounting details require sample |

## Indicator Assignment

All six indicators use 200 mm wire leads, a 12 V internal resistor, black
plated brass, and an IP67 front-panel construction.

| Label | Color | Part number |
| --- | --- | --- |
| `PWR` | Green | `DX06WG012B` |
| `BACKUP` | Yellow | `DX06WY012B` |
| `WIFI` | Blue | `DX06WB012B` |
| `CELL` | White | `DX06WW012B` |
| `TEMP` | Red | `DX06WR012B` |
| `AUDIO` | Green | `DX06WG012B` |

The repeated green color is acceptable because every indicator has a permanent
label. Change colors only by BOM revision; the 6 mm mechanical interface stays
the same.

## Preliminary Cutout Schedule

Dimensions below are millimeters. The manufacturer's drawing controls if this
table and a drawing disagree.

| Interface | Preliminary panel work | Release condition |
| --- | --- | --- |
| `NC3MAV` / `NC3FAV` | A-series opening, nominal `>=19.8` center opening and two `3.2` mounting holes; retain 32.0 row pitch and 43.38 column centers | Confirm front/rear mounting convention, latch orientation, connector sample, and screw engagement |
| `V8BR-1AX1-GH` | Rectangular clearance around top-entry RJ45 mouth | Derive from the final PCB Z datum, panel thickness, plug latch travel, LED visibility, and official Bel drawing |
| `719W-00/03` | 36 x 44 flange; use the exact front-mounted or rear-mounted cutout in the Qualtek drawing; two `3.5` mounting holes | Select mounting side and verify finger-safe mains barrier and fuse-drawer access |
| `EGG.1B.302.CLL` | `M12` panel drill | Confirm key orientation, nut access, cable bend radius, and IP50 acceptance |
| `RA812C1121` | `13.0` high x `19.2`, `19.4`, or `19.62` wide for panel thickness `0.75-1.25`, `1.25-2.0`, or `2.0-3.0` respectively | Use manufacturer drawing; 3.2 mm panel requires a rear pocket to `<=3.0`; verify snap retention and four FASTON clearances on a coupon |
| Bulgin `DX06` | `6.0` round cutout each | Confirm rear nut and lead clearance |
| YIS Marine `LS102W` | `22.0` round cutout each; `38.0` front-face envelope | Fit two samples, confirm the M22 x 1.5 body/nut, rear depth, warm-white CCT, beam coverage, glare, and lead exit |
| E-Switch `CS7L2FR` | `22.20 +0.25/-0.00` round cutout; maximum panel thickness 10 mm | Fit supplied O-ring/nut, retain 20.70 mm rear body/flats clearance and 150 mm six-wire lead bend radius |
| `THA0412AD-TZW3` + 40 mm guards | 40 x 40 fan envelope, 32 x 32 mounting-hole square, fan holes `3.5 +/-0.3`; the selected intake guard uses four `4.3` holes; center airflow opening to be finalized | Lock fan 1 intake/fan 2 exhaust labels; point external louvers in opposing directions; test panel stiffness, finger safety, filter service, pressure balance, and underside baffle effectiveness |
| SMA / RP-SMA bulkheads | Current SVG uses approximately `6.4` round placeholders | Replace with TE bulkhead drawing after pigtail/module confirmation; include wrench flats and washer clearance if required |
| `STX-353K7A-6N-KTTR` | No threaded panel bushing; panel clearance is concentric with PCB-mounted jack | Fix PCB Z height, plug insertion clearance, and jack-to-panel gap on a coupon |
| Nano-SIM access | Two service openings above a vertical daughterboard, not above a horizontal holder | Design daughterboard, card insertion path, retention, ESD shield, and service cover before cutting |
| QRC-GOLD | Existing 99 x 132 mm battery envelope is keepout only | Replace with Anton/Bauer bracket hole pattern and full battery release-sweep measurement; published bracket dimensions exclude the release latch |
| Lid harness | Open hinge-edge notch, no enclosed top-panel hole | Measure HDMI, USB touch, and 12 V cable overmolds and specify edge protection and service loop |

The QRC-GOLD is independent enclosure hardware. Its flying positive and
negative leads terminate in a strain-relieved, keyed, touch-safe high-current
harness that disconnects at the power-selector PCB. The dock mounting screws,
battery insertion load, and vibration load must be carried by the top panel and
custom frame, not by PCB laminate, standoffs, solder joints, or `J203`.

## Important Compatibility Findings

### SIM orientation

Wurth `693043020611` is a right-angle, push-pull Nano-SIM holder. On a
horizontal carrier PCB it accepts the card from the side, so it cannot align
directly with the two top-facing slots in the panel drawing. Use a small
vertical SIM service daughterboard with two holders, ESD protection, card
labels, and a keyed cable/board-to-board connection to the carrier.

### C14 current marking

Qualtek rates `719W-00/03` at 10 A / 250 Vac. It does not meet a literal
15 A / 120 Vac inlet-marking requirement. Its 10 A rating is well above the
approximately 2.8 A worst-case input current of a 252 W load at 100 Vac and
90 percent efficiency, but the product label and agency requirement must be
accepted explicitly or the inlet must be changed before release.

### Sealing

The LEMO `EGG.1B.302.CLL` is IP50, the Neutrik AV XLR parts are IP40, and the
two top-panel fan openings are intentionally vented. The assembled product is
therefore not an IP67 Pelican case. The RA812 switch is IP54 only when fitted
with optional E-Switch cap `ACC-P01`; the IP67 YIS lamps and IP68 CS touch
switch do not restore overall enclosure sealing.

### Display interface

The Amazon listing confirms one HDMI input, touch capability, and a listed
body size of 15.6 x 8.0 x 0.8 in, but it does not identify the touch USB
connector or provide a controlled mechanical drawing. Keep the user-locked
12 V / 2.5 A carrier branch and 25 W design allocation, but do not release the
HDMI, USB-touch, power connector, VESA holes, or hinge-notch dimensions until
the exact monitor sample is measured.

## Factory Release Rule

Every cutout in the final DXF must reference a BOM item, drawing revision,
mounting side, panel thickness, tolerance, and datum coordinate. Placeholders
from the concept SVG must never be traced into production CAD.
