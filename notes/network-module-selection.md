# Network Module Selection

## Locked Rev A Direction

Use a modular network/radio architecture:

- Native Radxa CM5 Gigabit Ethernet for `WAN1`
- PCIe packet switch for added Ethernet controllers and Wi-Fi AP
- ProComm-style native M.2 B-Key WWAN modem socket for cellular
- Cellular modem validated first with SIMCom `SIM8260G-M2` as the global 3052
  target, but socketed so future compatible M.2 WWAN modules can be swapped

This gives the product real WAN/LAN separation while keeping the cellular modem
field-replaceable.

## CM5 Interface Budget

From the local Radxa CM5 V2.21 pinout:

- U13-A exposes native Ethernet MDI pairs for one direct Gigabit Ethernet port.
- U13-B exposes `PCIE20_0`.
- J1 exposes a multi-use high-speed group that can be configured as
  `PCIE20_2`, `SATA30_2`, or `USB30_2`.
- J1 also exposes USB 2.0 host pairs for lower-speed peripherals.

Recommended allocation:

- Native Ethernet MDI -> `WAN1`
- `PCIE20_0` -> PCIe switch
- J1 multi-use group -> `USB30_2` for the M.2 B-Key cellular modem socket
- USB 2.0 host -> touchscreen touch controller and/or internal service hub
- Type-C/OTG path -> recovery/provisioning/service access

## Locked PCIe Tree

Selected PCIe switch:

- Diodes `PI7C9X2G608GP`
- PCIe 2.0, 6 ports / 8 lanes
- One upstream port can run as x1
- Supports 4 or 5 downstream x1 ports

Selected downstream endpoints:

- Added Ethernet controller -> `WAN2`
- Added Ethernet controller -> `LAN1`
- Added Ethernet controller -> `LAN2`
- Full-size Mini PCIe 4T4R Wi-Fi AP module
- One downstream port reserved/tested if the selected switch mode exposes it

This does put several devices behind one PCIe 2.0 x1 upstream link, so aggregate
throughput is not full line rate for every interface at once. It is still a
cleaner production architecture than using USB dongle-style Ethernet devices.

## Added WAN/LAN Controller Lock

Rev A wired Ethernet speed is locked to 1 GbE.

Selected added Ethernet controller:

- Microchip `LAN7430`, one per added port
- Single-port 10/100/1000 Ethernet with integrated PHY
- PCIe 3.1 endpoint operating at 2.5 GT/s
- Single external 3.3 V supply; use the datasheet external parts for its
  internal 1.2 V switcher and 2.5 V LDO
- Mainline Linux driver support

Alternative if multi-gig wired ports become mandatory:

- A production-supported PCIe 2.5 GbE controller selected in a future revision
- PCIe x1
- More power/thermal and driver-validation risk than 1 GbE for this product

Do not use 2.5 GbE only because it looks better on paper. For a rugged field
unit, stable 1 GbE WAN/LAN ports plus a strong Wi-Fi AP may be the better first
hardware revision.

## Wi-Fi AP Selection

Primary validation module:

- AsiaRF `AW7915-NP1`
- MediaTek `MT7915AN`
- Full-size Mini PCIe, 50.95 x 30 mm
- Wi-Fi 6, true 4T4R, up to 2401 Mbps PHY rate
- PCIe device with four external IPEX antenna connectors
- 2.4 GHz and 5 GHz bands are selectable; the selected AP band uses all four
  radio chains
- Supply: 3.3 V, 3 A recommended; design for 9 W thermal/power margin
- Linux driver support required in target Radxa kernel/OpenWrt image

Why this over the Radxa A8:

- Radxa A8 is useful as a compatibility reference, but it is Realtek
  RTL8852BE-based, 2T2R, and better treated as a client-style Wi-Fi card.
- ProComm needs AP/broadcast behavior for about 25 clients, so the board should
  use a four-chain module that is validated in AP mode on the target OS.
- The 4T4R radio improves airtime and spatial-stream margin, but 25-client
  performance still must be proven with simultaneous clients, real traffic,
  the enclosure closed, and the cellular radio active.

Board requirements:

- Full-size 52-pin Mini PCIe socket and 50.95 x 30 mm card keepout
- Selected host connector: Molex `0679101002`; import and verify the official
  Molex land pattern before PCB release
- Dedicated 3.3 V / 4 A rail at the Wi-Fi slot
- Local bulk capacitance, load switch, reset/wake controls, and RF keepouts
- Thermal pad or heatsink path to the internal heat spreader/case strategy
- Four short, independently identified RF pigtails to `WIFI 1` through
  `WIFI 4`

## Universal Cellular Modem Slot

Use the native cellular slot approach from
`cellular-modem-reference.md`: a universal-style M.2 B-Key WWAN slot, not a
soldered-down modem and not a third-party modem carrier/HAT.

Mechanical target:

- M.2 Socket 2 Key-B, 67 positions, 0.50 mm pitch
- Reference connector TE Connectivity `2199230-3`, with land pattern from TE
  drawing `C-2199230`
- Support 3042 and 3052 module lengths on the same socket centerline
- Keepout for heatsink/thermal pad above the modem
- Retention screw positions for both supported lengths, with only the selected
  removable standoff populated

Electrical target:

- Route USB 2.0 and USB 3.x to the socket
- Route optional PCIe to the socket if PCIe switch resources and layout allow
- Provide modem `FULL_CARD_POWER_OFF`, `W_DISABLE`, reset, wake, status LED,
  power-enable/control, and SIM-select signals as supported by the final module
- Provide two user-accessible Nano-SIM slots, with eSIM option only if selected
  later
- Support SIM voltage as controlled by the modem, commonly 1.8 V or 2.95/3.0 V
- Add SIM ESD protection and follow modem-vendor SIM routing rules
- Add current measurement or test points for modem power

Power target:

- Dedicated `MODEM_3V8` high-peak-current supply using an `LM61460` starting
  converter and protected load-disconnect/eFuse
- Support the common 3.135-4.4 V WWAN modem input range
- Default design target around 3.8 V for the SIM8260G-M2-class validation module
- Include assembly option or regulator trim option for 3.3 V-only modules if
  required by a future modem
- Do not power the modem directly from the CM5 rail without a dedicated current
  limit/load switch and transient budget

Reference ProComm implementation details to reuse/adapt:

- Dedicated 3.8 V-class buck rail; old reference used `SY8105IADC`
- Start with at least 1000 uF low-ESR bulk capacitance near the M.2 socket plus
  ceramics, then tune from the final modem guide and scope measurements
- Software-controlled modem power-cycle path
- Dual-SIM switching with `FSA2567MPX` between two Wurth `693043020611`
  Nano-SIM holders, if still validated with the selected modem
- Mount those right-angle holders on a small vertical service daughterboard so
  card insertion aligns with the two top-panel SIM openings; do not mount them
  flat on the horizontal carrier
- Four cellular/GNSS RF pigtails from the modem directly to rear-panel SMA
  bulkheads

Important limitation:

No carrier board can literally guarantee "any modem." The goal is a broad M.2
B-Key WWAN-compatible slot. Each modem still needs validation for voltage range,
USB/PCIe interface mode, SIM behavior, antennas, firmware, drivers, region
bands, carrier certification, thermal behavior, and mechanical keepout.

## Global Cellular Coverage

Primary validation modem:

- SIMCom `SIM8260G-M2`
- M.2 30 x 52 mm
- Wide 5G SA/NSA, LTE, WCDMA band support
- Supply voltage listed as 3.135-4.4 V
- SIM voltage listed as 1.8 V / 2.95 V
- USB and Linux support listed by SIMCom

Secondary compatibility target:

- Quectel `RM520N-GL`
- 5G/4G/3G multi-mode M.2 module
- Useful compatibility family: Quectel RM50xQ, EM06, EM12/EM12xR/EM120K, and
  EM160R-GL-class M.2 modules

For production, global coverage also requires:

- Region-specific regulatory approvals
- Carrier certification for intended markets
- Antenna certification and RF test plan
- eSIM/multi-carrier provisioning plan
- Clear supported band matrix in the product documentation

## Antenna Plan

Locked external antenna planning:

- Wi-Fi: 4 antenna connectors/bulkheads for the AW7915-NP1 4T4R module
- Cellular: 4 antenna paths for 4x4 MIMO-capable 5G modules
- GNSS: combine with the cellular module port only if the selected module
  supports that mapping; for SIM8260G-M2 reference labeling use
  `CELL 4 / GNSS`

Use eight bulkheads total in the narrow right-side RF bank: `WIFI 1-4` above
`CELL 1-4 / GNSS`. The current panel concept uses 34 mm vertical pitch because
the available strip cannot hold eight connectors at 50 mm pitch. Validate
antenna isolation, diversity, cable loss, and closed-enclosure throughput; use
greater spacing if the measured production panel permits it.
Keep RF paths away from the XLR analog bank, PSU/AC bay, power converters, fan
motors, Ethernet magnetics, HDMI, USB 3, and high-current wiring. Detailed
placement rules are in `rev-a-hardware-architecture.md`.

## Source Links

- Radxa CM5 product page: https://www.radxa.com/products/cm/cm5/
- Radxa CM5 hardware interface: https://docs.radxa.com/en/som/cm/cm5/hardware/hw-interface
- Diodes PI7C9X2G608GP: https://www.diodes.com/part/view/PI7C9X2G608GP
- Microchip LAN7430: https://www.microchip.com/en-us/product/lan7430
- AsiaRF AW7915-NP1: https://asiarf.com/product/wifi-6-11ax-4t4r-mini-pcie-module-mt7915-aw7915-np1/
- Molex 0679101002 host socket: https://www.digikey.com/en/products/detail/molex/0679101002/2405684
- Linux Wireless MediaTek driver support: https://wireless.docs.kernel.org/en/latest/en/users/drivers/mediatek.html
- Radxa Wireless A8: https://www.radxa.com/products/accessories/wireless-module-a8/
- Quectel RM520N series: https://www.quectel.com/product/5g-rm520n-series/
- SIMCom SIM8260G-M2: https://www.simcom.com/product/SIM8260G-M2.html
