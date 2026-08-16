# Fabrication Readiness Audit A2

## Release State

**HOLD_FOR_MEASUREMENT**

This audit is the factory-facing mechanical and thermal gate before PCB
routing. The Rev K top-panel connector placement remains the approved concept
layout, but it is not a cut file. No production panel, sidewall, bottom tray,
PCB outline, or mounting-hole pattern may be released until every row
M001-M080 is complete and the A2 validator passes with the release option.

## Corrections Made In A2

1. The prior 68.6 mm value was the nominal distance from the deepest base floor
   to the top face of the recessed panel. It was incorrectly described as
   usable space below the panel. With a 3.175 mm panel, nominal clear height
   below the panel underside is 65.425 mm.
2. The Gold-mount closure study omitted the QRC-GOLD plate. The Dionic XT90 is
   58 mm deep and the plate is approximately 12.7 mm before latch tolerance,
   producing an approximately 70.7 mm protrusion. This is expected to interfere
   with the lid monitor. The battery must be removed before closing the case.
3. Upright RF antennas cannot close under the lid. The transport configuration
   keeps the released compact hinged antenna set installed and folds all eight
   antennas inboard. The linked 163 mm Sierra paddle is a form-factor reference,
   not the released part: its folded arm crosses other panel controls. Current
   candidates are Taoglas `GW.05.0153` for Wi-Fi and `TG.66.A113` for cellular.
   Actual samples still require a measured sweep and signoff.
4. The locked monitor listing documents a nominal body envelope of 15.6 W x
   8.0 H x 0.8 D inches, or 396.24 x 203.20 x 20.32 mm. These dimensions are
   controlled for lid CAD. Physical verification is limited to the installed
   stack: mount buildup, VESA details, connector positions and protrusions,
   cable bends, lid placement, and the final closure sweep.
5. The RPS-400-24-C is 43 mm high, and the carrier overlaps it in plan. The
   complete tray-mounted PSU and terminal guard is limited to 48 mm above the
   deepest floor, with 10 mm minimum to carrier B.Cu. This is a tight measured
   stack, not a nominal promise.
6. AUDIO-8X8 now requires at least six supports. Four corner supports are not
   enough for a 268 mm portable-field board carrying sixteen XLR interfaces.
7. The cellular modem fan is selected as Delta AFB0412SHB-SP04, 40 x 40 x
   15 mm, 12 V, four-wire PWM/tach. Its 15 mm depth improves the bottom inlet
   margin compared with the earlier 20 mm placeholder.
8. The exhaust finger guard is selected as Qualtek 09150-G. A custom formed
   5052-H32 downward splash hood remains a custom mechanical part and must be
   validated for restriction and recirculation.
9. The closed-lid drawing is a composite side projection, not a literal cut
   through one XY station. The PSU and CM5 cooling cartridge are separated in
   the hinge-to-handle direction by the Rev K floorplan; their horizontal
   positions are separated in the projection for readability. Rev K and the
   final STEP model, not the side projection, control XY collision checks.

## Controlled Materials

| Assembly | Material / construction | Release rule |
| --- | --- | --- |
| Top panel | 3.175 mm nominal 5052-H32 aluminum | Accept 3.0-3.3 mm coupon; matte black powder coat; mask PE and chassis-bond points; local RA812 rear pocket no thicker than 3.0 mm |
| Four-side support frame | 5052-H32 or 6061-T6 aluminum, final section from measured case | Continuous support, 15 mm minimum support/no-PCB band, panel screws independent of PCB standoffs |
| Bottom equipment tray | 2.0 mm nominal 5052-H32 aluminum | Rigid low-profile tray; top no more than 3.0 mm above deepest local floor; no thick compressible foam under PSU |
| PSU terminal guard | Grounded perforated aluminum or UL94 V-0 insulating cover as required by safety review | No exposed mains; maintain airflow, creepage, service-tool clearance, and 48 mm total installed envelope |
| Fan reinforcement plates | 1.5-2.0 mm 5052-H32 aluminum | Separate plate and closed-cell gasket at each modified HPX sidewall |
| Splash hoods | Formed 5052-H32 aluminum | Downward-facing, finger-safe, drainable, and tested for pressure loss and hot-air recirculation |
| PCB supports | Captive M3 metal standoffs with prevailing-torque hardware | Six minimum per long PCB; add supports beside heavy parts and panel connectors |
| Seals / isolation | Closed-cell EPDM or silicone chosen by coupon | Do not rely on coated fasteners for PE continuity; do not soft-float panel-mounted XLRs |

## Verified Manufacturer Interfaces

| Part | Verified fact | Factory status |
| --- | --- | --- |
| Pelican iM2300 | 431.8 x 297.2 x 157.5 mm general interior; 50.8 mm lid and 106.7 mm base; HPX resin; P111-0095 Rev C controls bezel sizing | Case sample and 38.1 mm recessed opening still required |
| Mean Well RPS-400-24-C | Enclosed -C body 130 x 86 x 43 mm; 24 V, 10.5 A convection / 16.7 A with forced air; 93 percent efficiency; output derates with ambient temperature | Selected; measure installed terminal guard, conductor bends, local inlet air, and case temperature |
| Anton/Bauer Dionic XT90 8675-0125 | 99 x 132 x 58 mm; 99 Wh; 14.1 V; 12 A continuous | Selected; remove for transport closure |
| Anton/Bauer QRC-GOLD 8375-0094 | Universal compact plate, blind-mounted with 6-32 screws; supplied backplate; shaded areas require flat support | Selected; panel/frame load path and full latch sweep required |
| Delta THA0412AD-TZW3 | 40 x 40 x 20 mm; 12 V; PWM/tach; 20.56 CFM free-air; IP55 fan body | Selected for right intake and operator-side exhaust |
| Delta FFB0412EN-00Y2E | 40 x 40 x 28 mm; 12 V; high-power PWM/tach CPU fan | Selected with Radxa 5540A and structural carrier/frame support |
| Delta AFB0412SHB-SP04 | 40 x 40 x 15 mm; 12 V; 0.25 A; 3 W; 14.83 CFM; PWM/tach | Selected for modem cartridge; exact modem heatsink remains module-dependent |
| Qualtek 09150-F/30 | 40 mm intake filter assembly; 32 mm hole centers; 4.3 mm holes; 4.75 mm thick | Selected; clean and loaded CFM tests required |
| Qualtek 09150-G | 40 mm exhaust guard; 32 mm hole centers; 4.3 mm holes; 4.75 mm thick | Selected with custom downward splash hood |
| Neutrik NC3MAV / NC3FAV | Rear-mount A-series XLR interfaces | Use manufacturer cut geometry. Central panel opening is at least 22 mm, not 19.8 mm; verify mounting face and latch orientation on coupon |

Local source drawings are archived in docs/mechanical-parts.

## Monitor And Closed-Lid Gate

The display must be bought before lid CAD is released. A 15.6 inch 16:9 panel
has an active image width of approximately 345 mm, so a published 302 mm body
width cannot describe the selected 15.6 inch unit. The actual sample must be
measured at its maximum body, screw head, button, connector, and cable-bend
envelopes.

Use this closure equation:

**display-front to panel-top gap = measured lid depth + measured panel recess - measured total display protrusion**

The tallest permanent panel hardware under the display must be at least 8 mm
shorter than that gap after tolerance, gasket compression, lid flex, and
impact allowance. Test with the case latched and with pressure applied at the
lid center and corners. The transport test is:

- Gold-mount battery removed;
- all eight released external antennas installed and folded inboard;
- all panel plugs removed unless a separate connected-transport condition is
  intentionally qualified;
- hinge bundle clamped in its operating loop with no contact against display,
  PSU, fan, or sharp edges.

## Bottom Stack Gate

The current planning stack is:

| Interface | Planning value |
| --- | ---: |
| Deepest floor to panel top A | 68.6 mm nominal |
| Panel thickness | 3.175 mm nominal |
| Deepest floor to panel underside | 65.425 mm nominal |
| Bottom tray top above deepest floor | 3.0 mm maximum |
| Tray top to panel underside | 62.425 mm nominal |
| Complete PSU/guard top above deepest floor | 48.0 mm maximum |
| PSU guard to carrier B.Cu | 10.0 mm minimum |
| Carrier F.Cu/highest ordinary part to panel underside | 4.0 mm minimum |
| CM5 and modem fan inlet to floor/tray/harness | 10.0 mm minimum |

This stack has little tolerance reserve. The factory must make a simple section
gauge representing the tray, 48 mm PSU guard, carrier B.Cu, PCB thickness,
panel connector Z, and panel underside before PCB mounting holes are frozen.
If the gauge fails, change the tray/guard or split/reposition the carrier. Do
not reduce the 10 mm PSU or fan clearances.

## Thermal And Power Logic

The preliminary electrical budget is 151.7 W continuous and 184.2 W transient.
The RPS-400-24-C has enough room at moderate temperature, but its convection
rating derates as local air warms. At 93 percent efficiency it rejects roughly
11.4 W while supplying 151.7 W. The guarded hinge-side bay therefore needs a
low-velocity branch of the clean intake airflow or a validated conductive path;
the guard may not become a sealed hot box.

Acceptance at 45 C ambient:

- maximum stated continuous system load, full display brightness, CPU/GPU/NPU,
  Wi-Fi AP traffic, cellular uplink, and all audio channels active;
- at least 15 CFM measured through the case with a clean intake filter;
- at least 12 CFM at the released filter-maintenance loading limit;
- PSU inlet-air temperature no higher than 50 C;
- no unintended CM5, modem, regulator, or PSU throttling/shutdown;
- every PWM command, tach signal, board temperature, modem temperature, CM5
  thermal zone, source voltage/current, and load voltage/current logged.

The two enclosure fans form one series flow path; their CFM values are not
added. Right wall remains intake. Operator wall center-right remains exhaust.
The audio/XLR side remains free of fan bodies, PWM wiring, and switching-power
loops.

## Power And Harness Checks

- AC inlet, fuse, PE bond, PSU chassis, bottom tray, support frame, and top panel
  need one documented protective-earth path. Coating is masked at bond points.
- The RPS AC connector is JST VH B3P-VH; DC output uses its specified M3.5
  screw terminals. H02 and H01 remain removable, touch-safe, strain-relieved,
  and long enough to raise the top panel for service.
- H03 HDMI, USB touch, and 12 V display cables start at 1000 +/-25 mm only for
  the first article. Final lengths come from the full lid and 300 mm panel-lift
  test. No connector carries service-loop tension.
- Battery source current exceeds 12 A near low-voltage operation at the full
  continuous design load. Existing load-shed behavior remains mandatory on
  backup. Do not advertise full 151.7 W operation through the 12 A battery down
  to cutoff.
- The monitor branch remains 12 V / 2.5 A with a simple replaceable fuse, per
  the project decision.

## PCB And Routing Preconditions

- Do not route until the final panel connector Z datum is measured.
- The current footprint audit covers 527 components and reports 361 routing
  blockers and 429 production blockers. These are unresolved exact-footprint,
  pad-map, courtyard, 3D-model, or production-data gates; see
  `cad/kicad/reports/component-footprint-audit.md`. Zero ERC errors does not
  clear these blockers or authorize routing.
- AUDIO-8X8: six supports minimum, panel-supported XLRs, controlled chassis
  shield connection, no PWM/fan harness crossing the quiet boundary.
- CM5-CARRIER: six supports minimum, 15 mm perimeter frame keepout, no B.Cu
  parts or switch-node copper above the PSU guard, and exact 3D keepouts for
  CM5/5540A/fan, Wi-Fi, WWAN/heatsink/fan, RF pigtails, RJ45s, and lid harness.
- M.2 modem support means B-key 3042/3052 with an adjustable standoff and
  verified USB2/USB3, SIM, power, and thermal interfaces. It does not mean
  every modem on the market.
- Final DXF/STEP must be generated from controlled manufacturer drawings,
  documented nominal envelopes, and measured installation details. Concept
  SVG shapes may not be traced as cut geometry.

## Required First-Article Records

1. Completed im2300-measurement-register.csv, M001-M080.
2. Updated mechanical-release-a2.json.
3. Case serial/asset ID and calibrated-tool list.
4. Panel/frame gauge-plate photos and drawing.
5. Bottom stack section-gauge photo and measurements.
6. Monitor documented-envelope traceability, connector/VESA installation
   survey, and closed-lid pressure test.
7. Battery insertion/removal sweep and QRC backplate inspection.
8. Eight-antenna installed/folded closure record, including the maximum folded
   hinge height and full closing/latched sweep.
9. Sidewall scan, fan reinforcement, guard, gasket, and splash-hood drawings.
10. Clean/loaded-filter CFM and 45 C thermal report.
11. PE continuity and mains barrier inspection.
12. Full H01/H02/H03 harness motion and strain-relief record.

## Source Files

- Pelican iM2300 base-bezel drawing: mechanical-parts/pelican-im2300-base-bezel-rev-c.pdf
- Mean Well RPS-400 series: mechanical-parts/mean-well-rps-400-spec.pdf
- Anton/Bauer QRC-GOLD: mechanical-parts/anton-bauer-qrc-gold-installation.pdf
- Delta modem fan: mechanical-parts/delta-afb0412shb-sp04-spec.pdf
- Delta enclosure fans: mechanical-parts/delta-tha0412ad-tzw3-spec.pdf
- Qualtek intake/exhaust guards: mechanical-parts/qualtek-09150f-filter-drawing.pdf and mechanical-parts/qualtek-09150g-guard-drawing.pdf
- Taoglas Wi-Fi fold-down antenna: mechanical-parts/taoglas-gw05-0153-wifi-antenna.pdf
- Taoglas cellular fold-down antenna: mechanical-parts/taoglas-tg66-a113-cellular-antenna.pdf
