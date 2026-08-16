# Main Power Switch

## Selected Part

- Reference: `SW201`
- Manufacturer: E-Switch
- Part number: `RA812C1121`
- Function: maintained DPST OFF-ON
- Mounting: snap-in panel rocker
- Marking: white I/O on black actuator
- Terminals: four 0.187-inch quick-connect tabs
- Manufacturer product page:
  https://www.e-switch.com/product/ra8-series-illuminated-power-rocker-switch-with-pvc-cap/?part-number=RA812C1121
- Controlled local drawing:
  `../docs/mechanical-parts/e-switch-ra812c1121-drawing.pdf`

## Electrical Function

The switch disconnects both source-selector enable paths. It does not carry AC
mains or the 10-15 A raw-DC load.

| Pole | ON connection | Controlled path |
| --- | --- | --- |
| A | `J204-1 INTVCC` to `J204-2 SHDN_MAIN` | Enables LTC4421 primary-versus-backup selector |
| B | `J204-3 PRE_INTVCC` to `J204-4 SHDN_PRE` | Enables LTC4418 D-Tap-versus-Gold-Mount preselector |

Use separate 47 kOhm pull-downs from `SHDN_MAIN` and `SHDN_PRE` to their
respective grounds so OFF or an unplugged harness fails safely to OFF. Do not
connect the LTC4421 and LTC4418 INTVCC rails together.

With the switch ON, source priority and no-blink transfer remain automatic:

1. Internal 24 V PSU
2. D-Tap/LEMO backup
3. Gold Mount battery

With the switch OFF, both selector controllers are disabled and no source may
energize `PROTECTED_RAW`.

## Panel Cutout

The manufacturer drawing controls. The rectangular opening is 13.0 mm high;
its width depends on finished panel thickness.

| Finished thickness at switch | Cutout width |
| ---: | ---: |
| 0.75-1.25 mm | 19.2 mm |
| 1.25-2.00 mm | 19.4 mm |
| 2.00-3.00 mm | 19.62 mm |

The selected 3.2 mm panel concept exceeds the switch's listed snap-in range.
Machine a shallow rear pocket so the finished thickness at the switch is no
more than 3.0 mm, or use a 3.0 mm panel. Confirm the opening and snap retention
with a physical switch in a material/finish coupon before panel release.

## Harness

Use the parts in `../docs/power_switch_bom.csv`:

- Four 22 AWG stranded conductors
- Four TE Connectivity `2-520182-2` insulated FASTON receptacles
- Molex `0430250400` four-circuit Micro-Fit housing
- Four Molex `0430300007` socket contacts
- Molex `43045-0412` PCB header at `J204`

Preserve J204 pin numbering in the harness drawing. Add strain relief and keep
the harness outside the guarded AC mains zone.

## Acceptance Tests

1. Verify OFF removes `PROTECTED_RAW` with only the 24 V PSU connected.
2. Repeat with only D-Tap/LEMO, only Gold Mount, and all sources connected.
3. Unplug J204 and verify the power selector fails OFF.
4. With the switch ON and backup valid, remove and restore primary 24 V; confirm
   no CM5 reset, audio mute, network reset, or display blink.
5. Scope `PROTECTED_RAW`, `SYS_5V15`, `SHDN_MAIN`, `SHDN_PRE`, and CM5 reset.
6. Require an orderly software shutdown before the operator moves the rocker to
   OFF to protect writable eMMC data.
