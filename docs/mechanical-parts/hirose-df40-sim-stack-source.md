# Hirose DF40 Dual-SIM Board Stack

## Locked Architecture

The horizontal `SIM-SERVICE` daughterboard plugs directly into the
`CM5-CARRIER`. There is no cable harness in the SIM electrical path.

- Carrier J702: Hirose `DF40C-20DP-0.4V(51)` vertical plug.
- SIM-SERVICE J1: Hirose `DF40HC(2.5)-20DS-0.4V(51)` vertical receptacle/socket.
- Circuit count: 20.
- Nominal mated PCB spacing: 2.50 mm.
- Connector current rating: 0.30 A per contact.
- Published mating durability: 30 cycles.

Official source pages:

- Carrier plug: <https://www.hirose.com/en/product/p/CL0684-4010-9-51>
- 2.5 mm receptacle: <https://www.hirose.com/en/product/p/CL0684-4126-3-51>

The manufacturer drawings and STEP models are archived under
`references/components/hirose/DF40-SIM-20/`. Local KiCad footprints and STEP
links are under `cad/kicad/CM5-CARRIER/CM5Carrier.pretty/` and
`cad/kicad/CM5-CARRIER/CM5Carrier.3dshapes/`.

## Mechanical Rule

The DF40 pair is an electrical alignment datum, not a structural member. Four
matched M3 support pairs `SD1/S1` through `SD4/S4`, fitted with 2.50 +/-0.05 mm
precision metal sleeves, carry daughterboard mass, card insertion/extraction,
and vibration loads. An insulating panel guide carries lateral Nano-SIM card
loads at the two panel openings.

Do not use the screws to pull a misaligned connector pair together. The boards
must mate with the sleeves installed and without rocking or lateral force.

## Controlled Stack

The nominal distance from carrier F.Cu to the top-panel underside is 5.825 mm.
The nominal occupied stack is:

- DF40 mated spacing: 2.500 mm.
- SIM-SERVICE PCB: 1.600 mm.
- Wurth `693043020611` holder body: 1.200 mm nominal from the manufacturer
  drawing.
- Remaining nominal panel clearance: 0.525 mm.

This small residual is not a production tolerance allowance. PCBWay must build
and inspect the released stack coupon using production panel, PCB, connector,
holder, solder, and sleeve tolerances before main assembly release.

## Electrical Pin Map

| Pin | Net | Pin | Net |
| --- | --- | --- | --- |
| 1 | GND | 2 | CHASSIS_GND |
| 3 | SIM1_VCC | 4 | SIM1_RESET_RAW |
| 5 | GND | 6 | SIM1_CLK_RAW |
| 7 | GND | 8 | SIM1_DATA_RAW |
| 9 | SIM2_VCC | 10 | SIM2_RESET_RAW |
| 11 | GND | 12 | SIM2_CLK_RAW |
| 13 | GND | 14 | SIM2_DATA_RAW |
| 15 | GND | 16 | CHASSIS_GND |
| 17 | GND | 18 | CHASSIS_GND |
| 19 | GND | 20 | CHASSIS_GND |

The alternating return contacts reduce loop area and provide a controlled
ground/shield path across the separable board interface. SIM ESD/filter parts
remain on the daughterboard next to the card holders; modem-side control and
power remain on the carrier.
