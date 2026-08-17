# ProComm System Power Switch

## Locked production part

- Reference: `SW201`
- Manufacturer: E-Switch
- Manufacturer part number: `RA812C1121`
- Function: maintained DPST OFF-ON
- Mounting: snap-in panel rocker
- Marking: white `O` / `-` on black actuator
- Terminals: four 0.187-inch quick-connect tabs
- DigiKey order code: `EG5633-ND`
- DigiKey: https://www.digikey.com/en/products/detail/e-switch/RA812C1121/3778076
- Mouser order code: `612-RA812C1121`
- Mouser: https://www.mouser.com/ProductDetail/E-Switch/RA812C1121
- Manufacturer drawing: https://configured-product-images.s3.amazonaws.com/2D/specs/RA812C1121.pdf

The panel CAD must use the manufacturer drawing, not the concept render. The distributor lists a nominal rectangular cutout of 19.00 x 13.10 mm. The exact production cutout must be selected from the drawing for the actual enclosure panel thickness and confirmed with a physical switch sample before cutting the acceptance enclosure.

## Electrical connection

`SW201` carries only controller-enable current. It does not carry the 10-15 A system load.

- Pole A closes `J204-1 INTVCC` to `J204-2 SHDN_MAIN` in ON.
- Pole B closes `J204-3 PRE_INTVCC` to `J204-4 SHDN_PRE` in ON.
- `R541` and `R542` pull the two shutdown nets low when the switch is OFF or the harness is unplugged.
- OFF disables both the LTC4421 main selector and LTC4418 backup preselector. Rear 24 V, D-Tap and Gold Mount therefore cannot energize `RAW_OUT`.
- ON enables both selectors; normal automatic priority and seamless source transfer remain active.

Do not connect the two INTVCC rails together. Each switch pole is electrically independent.

## Harness

The exact harness components are in `POWER_SWITCH_BOM.csv`. Use four 22 AWG stranded conductors, four TE Connectivity `2-520182-2` insulated FASTON receptacles at the rocker, one Molex `0430250400` housing and four Molex `0430300007` socket contacts at `J204`. Production harness drawing must preserve the J204 pin numbers and include a continuity test for OFF and ON states.

## Required validation

1. With only rear 24 V connected, verify OFF removes `RAW_OUT` and ON starts normally.
2. Repeat with only D-Tap, only Gold Mount, and all sources present.
3. Unplug J204 and verify the board fails OFF.
4. While ON, remove and restore rear 24 V and verify automatic source transfer does not reset the CM5.
5. Record `RAW_OUT`, `SYS_4V0`, `IO_5V0`, both SHDN nodes and CM5 reset during switching with an oscilloscope.
6. Define the operating instruction for safe CM5 shutdown before moving the maintained switch to OFF, because hard removal of power can corrupt writable storage.
