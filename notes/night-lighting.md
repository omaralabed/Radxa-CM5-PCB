# Top-Panel Warm-White Lighting

## Locked Function

- Two matte diffused warm-white courtesy lights illuminate the full control
  panel while preserving connector and label colors.
- One latching capacitive touch switch turns both LEDs on and off together.
- Operation is hardware-only and remains independent of the CM5, Linux, and
  the GPIO expanders.
- Default state after loss and return of `AUX_12V` follows the E-Switch
  latching-switch power-up behavior and must be confirmed on a sample. The
  preferred product behavior is lights off after cold power-up.

## Selected Parts

| Function | Part | Controlled interface |
| --- | --- | --- |
| Panel light 1 and 2 | YIS Marine `LS102W` | 22.0 mm cutout / M22 x 1.5 body, 38 mm matte diffused face, warm white, 12 VDC, 0.25 W each, IP67 |
| Touch on/off | E-Switch `CS7L2FR` | Latching SPST capacitive switch, 22.20 +0.25/-0.00 mm cutout, 1 A at 5-24 VDC, IP68, 150 mm six-wire lead |
| Branch fuse | Littelfuse `0453.250MR` | 0.25 A fast fuse from `AUX_12V` to `NIGHT_LIGHT_12V` |

Manufacturer references:

- https://www.e-switch.com/product/cs-series-illuminated-touch-sensor-anti-vandal-switch/
- https://www.yismarine.com/en/product/LED_Step_Light_LS102.html
- https://www.littelfuse.com/products/fuses-overcurrent-protection/fuses/surface-mount-fuses/nano-2-fuses/453/0453-250

## Panel Datums

Centers are millimeters from the nominal panel upper-left datum:

| Item | X | Y |
| --- | ---: | ---: |
| Warm-white light 1 | 108.0 | 37.0 |
| Touch on/off | 153.0 | 37.0 |
| Warm-white light 2 | 198.0 | 37.0 |

The lighting zone occupies `x = 86-218 mm`, `y = 15-59 mm`. It remains above
the Gold Mount keepout and left of the Ethernet bank. Final datums follow the
measured panel outline, not the nominal case envelope.

## Wiring

E-Switch `CS7L2FR` wire/connector pin use:

| Pin | Wire/function | Project net |
| ---: | --- | --- |
| 1 | Black, ground | `GND` |
| 2 | Blue ring cathode | No connect |
| 3 | Green ring cathode | Through `R1070` 1 kOhm to `NIGHT_LIGHT_SINK` |
| 4 | Red ring cathode | No connect |
| 5 | Brown, NPN low-side load output | `NIGHT_LIGHT_SINK` |
| 6 | Orange, 5-24 V input | `NIGHT_LIGHT_12V` |

Connect both YIS light positive leads to `NIGHT_LIGHT_12V` and both negative
leads to `NIGHT_LIGHT_SINK`. The two 0.25 W lamps draw about 42 mA total at
12 V, well below the CS-series 1 A rating. The extra ring resistor keeps the
touch control's ON indication subdued.

`LS102W` is the warm-white ordering choice. The manufacturer describes the
output as warm white but does not publish a specific LS102 CCT bin on the
current product page. Procurement must approve a physical sample near 3000 K
and reject cool-white substitutions before the panel is released.

## Prototype Checks

- Verify the switch powers up with the lamps off.
- Verify touch operation with wet and gloved fingers and with the panel bonded
  to chassis.
- Check full-panel coverage, reflected light on the lid display, XLR label
  readability, connector-color recognition, and accidental activation while
  handling the battery.
- Verify both matte lenses produce uniform light without bright hotspots.
- Strain-relieve all three panel harnesses and insulate exposed terminations.
- Confirm O-ring compression, nut torque, rear-body clearance, and cable bend
  radius on a 3.175 mm nominal panel coupon before release.
