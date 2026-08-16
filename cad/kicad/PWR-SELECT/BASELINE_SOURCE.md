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
- Replace the 660 uF raw-output baseline with the calculated, precharged
  22,000-47,000 uF stuffing plan after transfer measurements.
- Recalculate MOSFET SOA, shunts, fuses, TVS parts, copper, connectors, inrush,
  thresholds and timers for the 252 W PSU and Radxa load.
- Create and validate a new PCB; the controlled source directory contains no
  production selector PCB.
