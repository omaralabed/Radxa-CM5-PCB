# Documents

Place downloaded datasheets, pinout tables, and exported design PDFs here.

Official Radxa resources are listed in the project README. The reference design is cloned under `references/radxa-cm-projects/cm5/radxa-cm5-io-board/`.

Preliminary engineering tables:

- `power_budget_preliminary.csv` - typical, continuous-design, and transient
  load budget.
- `source_current_check_preliminary.csv` - source current at PSU and backup
  voltages.
- `battery_runtime_preliminary.csv` - Dionic XT 90 ideal and conservative
  backup-runtime estimates.
- `panel_mechanical_bom_preliminary.csv` - exact panel-part candidates,
  mechanical status, controlled drawing references, and fabrication blockers.
- `power_switch_bom.csv` - exact DPST panel-switch and four-wire harness parts.
- `power_regulator_bom_a1.csv` - A1 regulator-sheet BOM exported directly from
  KiCad, including selected manufacturers and MPNs.
- `power_regulator_calculations_a1.csv` - machine-checkable rail, source,
  protection, and hold-up calculations for the A1 regulator capture.

Firmware and operating-system integration:

- `thermal-control-firmware-spec.md` - controlled EMC2305/TMP117 Linux
  integration, fan-channel mapping, device-tree starting point, fan curves,
  watchdog behavior, fail-safe requirements, and release tests.
- `power-telemetry-software-spec.md` - INA228 primary/backup/load channel map,
  I2C harness, Linux hwmon starting point, touchscreen requirements,
  calibration, runtime estimation, and future firmware checklist.

Controlled interface allocation:

- `radxa_cm5_v2210_pinout.xlsx` - local controlled copy of the official Radxa
  CM5 V2.21 connector pinout.
- `../outputs/cm5-pin-allocation-a0/radxa_cm5_pin_allocation_a0.xlsx` - A0
  physical-pin assignment, resource map, GPIO/control allocation, conflict
  ledger, and normalized official source rows.

Mechanical manufacturer drawings are archived under `mechanical-parts/`.
