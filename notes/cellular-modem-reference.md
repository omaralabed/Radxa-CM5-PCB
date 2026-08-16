# Cellular Modem Reference

## Source Reference

Use the cellular modem concept from:

- `/Users/viewvision/Desktop/ProComm enclosure and PCB boards/CELLULAR_RF_INTERFACE.md`
- `/Users/viewvision/Desktop/ProComm enclosure and PCB boards/ADVANCED_SCHEMATIC_WORK/CELLULAR_RF_INTERFACE.md`
- `/Users/viewvision/Desktop/ProComm enclosure and PCB boards/PCB_SOURCE/CELLULAR_M2_SLOT/README.md`
- `/Users/viewvision/Desktop/ProComm enclosure and PCB boards/ADVANCED_SCHEMATIC_WORK/CM5_ProComm_Carrier_RevF.kicad_sch`
- `/Users/viewvision/Desktop/ProComm enclosure and PCB boards/ADVANCED_SCHEMATIC_WORK/ProComm_Cellular.kicad_sym`

This legacy folder is read-only reference for the Radxa CM5 design.

## Selected Architecture

Use a native, replaceable M.2 Socket-2 Key-B cellular modem slot. Do not use a
Waveshare or other third-party modem carrier board in the final product.

Mechanical target:

- M.2 Socket 2, Key B, 67 positions, 0.50 mm pitch.
- Reference connector: TE Connectivity `2199230-3`, 4.2 mm height.
- Support both `3042` and `3052` modules on the same socket centerline.
- Provide two retention positions: `M2-3042` and `M2-3052`.
- Install only the matching removable standoff.
- Keep the unused retention position flush because a 3052 modem overlaps the
  3042 standoff location.
- Keep a full 3052 courtyard/component-height keepout.
- Use the TE `C-2199230` drawing for the final connector land pattern and paste
  apertures.

## Module Direction

Primary global production/validation target from the ProComm reference:

- SIMCom `SIM8260G-M2`
- 3052 M.2 module
- USB data/control path
- Four cellular/GNSS RF ports
- Supply range controlled by the current SIMCom hardware guide

Regional options:

- `SIM8262A-M2` or `SIM8262E-M2` only after pin, power, SIM, RF, firmware, and
  carrier compatibility are checked against current official SIMCom guides.

Compatibility goal:

- Keep the socket broadly M.2 B-Key WWAN-compatible, but do not claim support
  for every modem. Every modem SKU still needs electrical, software, RF,
  thermal, mechanical, regulatory, and carrier validation.

## Radxa Interface Plan

Use the Radxa CM5 high-speed group as a dedicated modem USB interface:

- Route `USB30_2` SuperSpeed TX/RX pairs to the M.2 socket.
- Route USB 2.0 D+/D- to the socket.
- Treat the link as 90-ohm differential routing with continuous reference
  planes, short return paths, no branches, and no test-pad stubs.
- Normal modem management, AT commands, firmware update, QMI/MBIM, and network
  data use USB.
- Optional PCIe to the socket is allowed only if the final modem and PCIe switch
  budget justify it.

Do not copy Raspberry Pi GPIO numbers from the old design. Assign Radxa CM5
GPIOs later for:

- `MODEM_3V8_EN`
- `MODEM_FULL_CARD_POWER_OFF_N`
- `MODEM_W_DISABLE1_N`
- `MODEM_RESET_N` or reset-assert transistor drive
- `MODEM_SIM2_SELECT`
- status/wake signals if used by the selected modem

## Modem Power

Use a dedicated high-current modem rail. Never power the modem directly from the
CM5 system rail without the proper converter, current limit, power switch, and
bulk capacitance.

The ProComm advanced schematic remains a behavior/reference concept, but Rev A
uses a new regulator sized for the Radxa protected-raw bus:

- `MODEM_3V8`: 3.8 V / 6 A converter using TI `LM61460` as the schematic
  starting part.
- `TPS25982` eFuse/load disconnect, adjusted to provide at least 5 A usable
  modem current while containing a slot or module fault.
- Start with at least 1000 uF low-ESR bulk near the M.2 socket plus ceramics.
  Final capacitance follows the selected modem guide and scope measurements.
- Add correctly selected overvoltage/transient protection and high-frequency
  bypassing without exceeding modem input limits.
- Regulator defaults off through a pulldown on enable.
- Provide software-controlled power-cycle and current/test access.

Final current limit, soft-start, compensation/stability, brownout threshold,
capacitance, and thermal design must be calculated from the selected modem
hardware-design guide and verified at 24 V and backup input.

Power-up concept:

- Enable modem rail.
- Wait at least 100 ms.
- Release `FULL_CARD_POWER_OFF_N`.
- After graceful shutdown, wait at least 12 s before disabling the modem rail,
  unless the selected modem guide gives a different requirement.

## SIM Interface

Use two user-accessible Nano-SIM slots:

- Label as `SIM 1` and `SIM 2`.
- SIM8260G-M2 exposes one external UIM interface, so the ProComm reference uses
  `FSA2567MPX` to switch UIM power, reset, clock, and data between two SIM
  holders.
- Reference SIM holder: Wurth `693043020611`.
- Because this is a right-angle, side-entry holder, use a vertical service
  daughterboard for the two top-facing panel slots.
- The selected Wurth holder has no card-detect contact in the old design; if it
  is reused, software must not require hot-swap/card-detect.
- Only one SIM is active at a time unless the modem guide explicitly allows
  another mode.
- SIM voltage is controlled by the modem, commonly 1.8 V or about 2.95/3.0 V.
- Add SIM ESD protection and keep SIM routing short with clean return paths and
  no branches.

Do not assume a Waveshare dual-SIM circuit is correct for this product.

## RF And Antennas

Cellular antenna plan:

- Four cellular/GNSS antenna paths for the SIM8260G-M2-class module.
- Rear labels from the ProComm reference:
  - `CELL 1`
  - `CELL 2`
  - `CELL 3`
  - `CELL 4 / GNSS`

SIM8260G-M2 controlled mapping from the ProComm reference:

| Rear label | Module port | Assembly label rule |
| --- | --- | --- |
| `CELL 1` | `ANT0` | Mark both pigtail ends `CELL 1 / ANT0` |
| `CELL 2` | `ANT1` | Mark both pigtail ends `CELL 2 / ANT1` |
| `CELL 3` | `ANT2` | Mark both pigtail ends `CELL 3 / ANT2` |
| `CELL 4 / GNSS` | `ANT3` | Mark both pigtail ends `CELL 4/GNSS / ANT3` |

The SIM8260G-M2 antenna guide identifies the module receptacle as ECT
`ECT818000500`, a 2.0 mm x 2.0 mm x 0.6 mm USS RF IV interface. Do not assume
generic MHF4 pigtails for this module.

Reference pigtail from the ProComm note:

- ECT `818033349`
- USS RF IV to female SMA bulkhead
- 0.81 mm coax
- 120 +/- 3 mm reference length
- 1/4-36UNS-2A bulkhead thread
- 8.0 mm hex
- D-shaped panel opening: 6.4 mm diameter envelope with 6.0 mm flat

The 120 mm length is only a reference. Final pigtail length must be measured in
the complete Radxa enclosure assembly with bend radius, strain relief, and
service access included.

## Radxa-Specific Changes From Legacy ProComm

- Replace all Raspberry Pi CM5 interface assumptions with Radxa CM5 pinout and
  device-tree assignments.
- Keep the M.2 cellular socket concept, but reassign GPIO/control pins on Radxa.
- Keep dual SIM, but verify the mux and holder parts against the selected modem
  guide.
- Keep four cellular antennas; Wi-Fi is separate and fixed at four antennas for
  the AW7915-NP1 4T4R AP module.
- Recalculate the modem power rail from the 24 V PSU / source-selector system
  and final regulator tree.
- Add both a dedicated modem heatsink/thermal spreader and a dedicated modem
  fan. A fan-only carrier-board style is acceptable for lab testing, but the
  final sealed Pelican design needs a real heat spreader plus airflow and/or a
  conductive path to the enclosure.
- Recheck thermal placement because the Radxa board also carries AKM 8x8 audio,
  PCIe Ethernet, Wi-Fi AP, HDMI touchscreen, and four fans.

## Verification Before Release

- Obtain the current official SIM8260G-M2 hardware design guide, reference
  schematic, layout checklist, and antenna-port guide.
- Confirm M.2 pin assignment, reserved pins, USB interface, control voltage
  domains, reset timing, and SIM method.
- Import the exact M.2 connector, modem, standoffs, pigtails, and SMA bulkhead
  models into the Radxa enclosure assembly.
- Verify 3042 and 3052 insertion/removal and standoff configurations.
- Validate modem rail droop with an oscilloscope during registration, 4G
  transmit, and 5G transmit bursts.
- Test both SIM trays, all four antenna paths, GNSS behavior, USB enumeration,
  modem reset, modem power-cycle, thermal throttling, and WAN failover.
- Complete radio, antenna, regional regulatory, and carrier-certification
  review for each modem SKU and antenna set sold.
