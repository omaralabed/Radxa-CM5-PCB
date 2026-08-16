# PWR-SELECT Baseline Source

This directory is a controlled copy of the ProComm Rev C selector from:

`/Users/viewvision/Desktop/ProComm enclosure and PCB boards/PCB_SOURCE/POWER_SELECTOR_24V_BATTERY`

The source folder remains read-only and unchanged. The copied schematic is the
topology baseline for Radxa CM5 work, not a production release.

The only retained review set is the current Radxa A0 export under `REVIEW/`.
Its validator proves that the copied topology, exact switch BOM, footprints,
and thresholds remain internally consistent; it does not approve the old
10 A-class path or hold-up values for production.

Carry forward:

- LTC4418 D-Tap/Gold-Mount backup preselector
- LTC4421 primary-versus-backup selector
- Reverse and cross-conduction blocking
- Source status telemetry
- E-Switch RA812C1121 two-pole controller-enable harness

Required before Radxa release:

- Increase the old 10 A-class selector operating limit to at least 14 A after
  full tolerance and thermal analysis, while rating the path for 15 A.
- Validate the A1 27.2 mF snap-in bank plus 660 uF local hybrid storage against
  measured transfer time, -20% tolerance, inrush, discharge, and hot-plug cases.
- Release the tray-supported capacitor clamp and final board envelope from the
  measured battery-dock underside and enclosure floor survey.
- Recalculate MOSFET SOA, shunts, fuses, TVS parts, copper, connectors, inrush,
  thresholds and timers for the 252 W PSU and Radxa load.
- Create and validate a new PCB; the controlled source directory contains no
  production selector PCB.
