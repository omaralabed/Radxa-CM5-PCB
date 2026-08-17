# AW7915-NP1 Wi-Fi Qualification A1

## Controlled module

- Manufacturer: AsiaRF.
- MPN: `AW7915-NP1`.
- Radio: MediaTek `MT7915AN`.
- Host interface: PCIe 2.1 through the full-size Mini PCIe socket.
- Mechanical envelope: 50.95 x 30 mm.
- RF architecture: Wi-Fi 6, selectable 2.4/5 GHz, true 4T4R, four IPEX ports.
- Supply: 3.3 V +/-5 percent, 3 A recommended, 9 W maximum.
- Vendor operating range: -10 to +70 C.
- Controlled local datasheet: `references/datasheets/AsiaRF-AW7915-NP1.pdf`.

The module is the locked Rev A procurement target. Production release still
requires the tests below because connector fit, AP firmware behavior, thermal
performance, and regulatory configuration cannot be proven by schematic review.

## Bench setup

1. Install the module in carrier connector `J620` and retain it at the full-size
   Mini PCIe mounting point.
2. Fit the production heatsink/thermal interface and connect all four numbered
   Wi-Fi pigtails and antennas in their released order.
3. Use the target Radxa production kernel or OpenWrt image with the upstream
   `mt76` driver family and the intended regulatory database.
4. Instrument `WIFI_3V3` at the slot for voltage, peak current, ripple, and
   startup droop. Log module and inlet-air temperature.
5. Close the iM2300 in its operating configuration. Antennas are raised for RF
   testing; folded antennas are transport-only.

## Required tests

- Enumerate repeatedly after cold boot, warm reboot, controlled rail cycle, and
  brownout recovery. No PCIe link loss or driver hang is allowed.
- Run AP mode for at least 24 hours with 25 simultaneously associated clients.
- Exercise mixed uplink/downlink traffic, multicast/broadcast, SIP traffic, and
  roaming/reassociation while the CM5, cellular modem, display, and 8x8 audio
  path are loaded.
- Test both 2.4 GHz and 5 GHz configurations allowed in the target market.
- Verify all four chains are active and record per-chain RSSI/error statistics.
- Qualify at 45 C ambient with the enclosure closed. The module must remain
  below its 70 C vendor limit with no thermal disconnect or throughput collapse.
- Confirm `WIFI_3V3` remains within 3.3 V +/-5 percent and that startup/traffic
  peaks remain within the 4 A carrier allocation.
- Perform coexistence checks with the cellular modem transmitting, all Ethernet
  ports active, fans at PWM extremes, and audio measured for added noise.

## Acceptance record

Record module serial number, firmware, kernel, driver commit/version, regulatory
domain, channel width, antenna/pigtail MPNs, ambient temperature, temperatures,
rail captures, client count, traffic profile, throughput, packet loss, and any
driver messages. Release requires a signed result with no unresolved reset,
thermal, power-integrity, or 25-client AP failure.

## Sources

- AsiaRF product page: <https://asiarf.com/product/wifi-6-11ax-4t4r-mini-pcie-module-mt7915-aw7915-np1/>
- AsiaRF datasheet: <https://asiarf.com/wp-content/uploads/2026/06/260701_Datasheet_AW7915-NP1_V1-1P.pdf>
- Linux Wireless MediaTek driver documentation: <https://wireless.docs.kernel.org/en/latest/en/users/drivers/mediatek.html>
