# Network Architecture

## Goal

The Radxa CM5 carrier should support:

- Two wired WAN ports
- Two wired LAN ports that share the same private LAN
- High-speed Wi-Fi used for broadcasting as an access point, capable of about 25 simultaneous client devices
- Cellular modem for another WAN path
- 8-channel TDM audio on AK5558VN + AK4458VN without interface conflicts

## Recommended Logical Network Model

Use Linux as the router/firewall:

- `wan0` - WAN 1, isolated from LAN
- `wan1` - WAN 2, isolated from LAN
- `wwan0` - cellular WAN
- `lan0` - LAN wired port 1
- `lan1` - LAN wired port 2
- `wlan0` - Wi-Fi access point only
- `br-lan` - bridge containing `lan0`, `lan1`, and `wlan0`

Routing/firewall services:

- DHCP server on `br-lan`
- NAT/firewall from `br-lan` to selected WAN
- WAN failover or load balancing between `wan0`, `wan1`, and `wwan0`
- Optional VLANs if managed-switch hardware is used

## Preferred Hardware Direction

Use the CM5 native Gigabit Ethernet as one WAN, and add the rest with PCIe.

Selected first-pass topology:

- CM5 native Ethernet PHY MDI -> magnetics/RJ45 -> `WAN1`
- CM5 `PCIE20_0` x1 -> PCIe packet switch
- `PI7C9X2G608GP` downstream port -> `LAN7430` -> `WAN2`
- `PI7C9X2G608GP` downstream port -> `LAN7430` -> `LAN1`
- `PI7C9X2G608GP` downstream port -> `LAN7430` -> `LAN2`
- `PI7C9X2G608GP` downstream port -> Mini PCIe `AW7915-NP1` 4T4R Wi-Fi AP
- J1 high-speed multi-use group configured as `USB30_2` -> ProComm-style M.2
  B-Key WWAN modem socket

This gives Linux true independent network interfaces. It is more complex than a
single managed switch, but it avoids hiding WAN separation behind VLAN setup and
makes firewalling/failover easier to validate.

See `network-module-selection.md` for the current module/socket choices.

## Power-Rail Requirements

The network/radio rail plan is part of the design, not an afterthought:

- WAN/LAN RJ45 connectors do not receive raw 24 V or battery voltage unless PoE
  is explicitly added later.
- The three LAN7430 controllers use `NET_3V3`; the PCIe switch uses `NET_3V3`
  and `PCIE_1V0` with datasheet sequencing, reset, and clock requirements.
- Wi-Fi AP hardware uses dedicated `WIFI_3V3`, 3.3 V / 4 A, with a controlled
  load switch, local bulk, and thermal path.
- The cellular modem uses a universal M.2 B-Key WWAN socket with its own
  high-peak-current 3.8 V-class supply, dual-SIM support, four RF paths, and
  power-cycle controls; do not power it directly from the CM5 5 V rail.
- SIM/eSIM voltage and ESD protection must follow the chosen modem design guide.

## Rejected Lower-Cost Alternative

Use a managed Ethernet switch with VLANs:

- One CPU-facing Ethernet interface carries VLAN-tagged WAN/LAN traffic.
- Physical switch ports are assigned as WAN1, WAN2, LAN1, and LAN2.
- LAN1 and LAN2 share a LAN VLAN.

This can reduce Ethernet-controller count, but the CPU-facing link becomes a
shared bottleneck. It is also more software-sensitive because a VLAN mistake can
bridge WAN traffic into LAN.

## Wi-Fi AP Requirement

The Wi-Fi radio is for broadcasting a ProComm access point. It should be treated
as AP infrastructure, not as a client/station Wi-Fi interface.

Do not rely on a generic laptop/client Wi-Fi card unless AP mode and client
capacity are proven on the exact OS image.

Preferred Wi-Fi hardware:

- Dedicated PCIe Wi-Fi 6 or Wi-Fi 6E AP module
- True 4T4R radio with four external Wi-Fi antennas
- External antennas, with antenna count matching radio chain count
- Good thermal path and a strong 3.3 V rail
- Linux/OpenWrt support through `hostapd`
- AP/client-concurrent mode is not required unless a future feature asks for wireless uplink.
- 25-client AP performance must be validated with the final module, antenna
  placement, enclosure, and OS image.

Rev A validation module: AsiaRF `AW7915-NP1`, based on MediaTek `MT7915AN`,
using a full-size Mini PCIe host socket and the Linux `mt76` stack. The radio
uses four RF chains on the selected 2.4 GHz or 5 GHz AP band.

Avoid for first revision unless proven:

- Intel AX/BE client modules for AP duty
- USB Wi-Fi dongles for production AP duty
- Any client-class two-antenna module that cannot prove stable AP mode under
  25-client load

## Cellular Modem Requirement

Preferred hardware approach:

- Use the ProComm-style native M.2 Socket-2 Key-B WWAN cellular modem socket.
- Support 3042 and 3052 modules, with SIMCom `SIM8260G-M2` as the first global
  3052 validation target.
- Route USB 2.0 and USB 3.x; many LTE/5G modems expose control/data over USB.
- Add dual Nano-SIM support with ESD protection and correct modem-controlled
  SIM voltage handling.
- Provide modem power enable, reset, wake, status, and optional airplane-mode GPIOs.
- Budget a high peak-current modem supply; cellular transmit bursts can be much higher than average current.
- Add four cellular/GNSS antenna paths to rear-panel bulkheads as required by
  the selected modem.

Software expectation:

- Use ModemManager/NetworkManager or direct `qmi_wwan`/`mbim` tooling on Radxa Debian/Ubuntu.
- Treat cellular as `wwan0` for WAN failover and policy routing.
- Validate the exact modem on the exact kernel before committing to production.

## CM5 Interface Notes

From the Radxa CM5 V2.21 pinout:

- Native Ethernet MDI pairs are available on U13-A pins 3/4/5/6/9/10/11/12.
- PCIe 2.0 x1 group `PCIE20_0` is available on U13-B pins 110/112/116/118/122/124 plus control pins.
- Another high-speed group on J1 can be configured as `PCIE20_2`, `SATA30_2`, or `USB30_2` depending on design choice.
- Audio TDM uses I2S0 pins already reserved in `audio-tdm-architecture.md`.

## Remaining Validation

- Verify `PI7C9X2G608GP` switch mode straps, endpoint count, reset sequencing,
  reference clocking, and all-endpoints-active behavior.
- Validate `AW7915-NP1` 4T4R AP mode for 25 associated devices on the target OS.
- Cellular target: global full 5G NR validation first, with LTE/5G fallback module support through the M.2 B-Key WWAN slot.
- Modem interface: universal M.2 B-Key WWAN socket with USB 2.0/USB 3.x.
- SIM hardware: dual Nano-SIM with modem-controlled voltage and ESD protection;
  eSIM is deferred unless a production requirement is added.
- Antenna count is six total; select exact bulkhead connector and cable parts.
- OS/network stack: Radxa Debian/Ubuntu with `nftables` + `hostapd`, or OpenWrt if available for the exact CM5 target.
- WAN behavior: wired failover, cellular failover, load balancing, or policy routing per service.
