# Electrical Schematic Audit A2

## Decision

**SCHEMATIC ELECTRICAL REVIEW PASS / ENGINEERING PCB LAYOUT AUTHORIZED**

The three electrically authoritative KiCad board roots currently pass ERC with
`0 errors / 0 warnings`:

- `cad/kicad/PWR-SELECT/PowerSelector.kicad_sch`
- `cad/kicad/CM5-CARRIER/CM5-Carrier.kicad_sch`
- `cad/kicad/AUDIO-8X8/Audio-8x8.kicad_sch`

The system overview is a navigation and documentation sheet. It is not a PCB
netlist and must not be substituted for any of those roots. Standalone child
sheets lack their parent-sheet power drivers and interface context; their
expected findings are checked against an exact allowlist by
`cad/kicad/review_detailed_capture.sh`. Any changed finding fails the review.

This pass means the captured electrical logic is internally consistent and
matches the controlled source documents listed below. It does not prove that a
first article will have zero failures. PCB signal/power integrity, regulator
stability, thermal behavior, source transfer, EMC, safety, harnesses, and
mechanical fit still require layout review and measured qualification.

## Datasheet Corrections Closed

1. Reconciled all 76 owned CM5 contacts across the generator, controlled
   workbook, official Radxa V2.21 workbook, and exported KiCad netlist. Seventy
   four contacts are connected and two are explicitly assigned no-connects:
   unused WAN1 `LED2` and unused HDMI `SBDN/HEAC-N`.
2. Separated the CM5 PCIe reset request from the hardware-qualified switch
   reset. The PI7C9X2G608GP can leave reset only when the CM5 command,
   `NET_3V3_PG`, and `PCIE_1V0_PG` are all valid.
3. Added the RM520N-GL socket-local low-band VCC network: two 220 uF polymer
   capacitors, the specified high-frequency capacitor ladder, and an
   SMF4L5.0AT1G TVS at the M.2 power pins. The regulator board's upstream bulk
   does not replace these local parts.
4. Tied each LAN7430 `VAUX_DET` low to disable unsupported D3cold PME and left
   `ADV_PM_DISABLE` open so its internal pull-down retains advanced power
   management. Verified PCIe AC coupling, reference clocks, reset, local rails,
   and Ethernet front ends.
5. Qualified the AW7915-NP1 interface as a 4T4R Mini PCIe endpoint on a
   dedicated 3.3 V / 4 A rail. The vendor specifies 9.1 W maximum and recommends
   a 3.5 A supply capability, so the captured rail has startup margin.
6. Corrected AK5558VN and AK4458VN supply/reference capture and added a hardware
   fail-silent gate: DAC unmute and output-relay enable require both ADC and DAC
   power-good signals.
7. Corrected the ES8316 I2C level-shifter bias, retained the CTIA headset map,
   and kept headset, AKM, and line-stage power on their controlled clean rails.
8. Verified power-good sequencing, load-switch default pulldowns, telemetry,
   fan control, temperature sensing, HDMI/USB protection, and cross-board TDM,
   power, fan, XLR, and chassis-ground contracts.

## Automated Evidence

| Gate | Result |
| --- | --- |
| Authoritative board-root ERC | Three roots, each `0 errors / 0 warnings` |
| PWR-SELECT validator | 186 checks, 0 failures |
| CM5 pin-allocation validator | 9 checks, 0 failures |
| Power-regulator validator | 49 checks, 0 failures |
| Network/PCIe validator | 29 checks, 0 failures |
| WWAN/SIM validator | 23 checks, 0 failures |
| Display validator | 20 checks, 0 failures |
| Audio-control validator | 22 checks, 0 failures |
| Thermal/fan validator | 22 checks, 0 failures |
| AUDIO-8X8 validator | 581 checks, 0 failures |
| Cross-board interface validator | 174 pin/net checks, 0 failures |
| System-project validator | 58 electrical symbols, 294 named interconnects, all 13 child sheets exposed |
| Full release export | 17 reviewed PDF pages |
| Root-counted footprint audit | 1203 unique components; 10 routing blockers and 11 production blockers |

The generated review files under each board's `REVIEW` folder are controlled
evidence. Run the full gate after every generated or manual schematic change:

```sh
cad/kicad/review_detailed_capture.sh
```

Release-mode checks were also exercised during this audit. They remain blocked
for the intended physical work, not for an additional captured electrical
error: the routing audit reports ten unresolved footprint coupons, the
mechanical release reports 37 missing measurement/signoff records, and the
PCBWay package reports 54 open or missing package rows including the three
unrouted PCB sources and harness test evidence. These holds must remain active
until the listed evidence exists.

## Mandatory Holds

| Hold | Required evidence before release |
| --- | --- |
| AK5558VN and AK4458VN lands | Exposed-pad, via, paste, stencil, assembly, and X-ray coupon approval |
| Eight Panasonic TQ2 relay lands | Pin map, insertion, seating, solder, and physical coupon approval |
| Kycon headset jack | Physical sample, plated holes, bezel, CTIA map, and detect-switch polarity |
| Wi-Fi and WWAN sockets/modules | 3D/sample fit, rail transient capture, thermal interface, antenna map, and regulatory integration review |
| PCB routing | Controlled stackup, PCIe/USB/HDMI/TDM impedance, return paths, length matching, crosstalk, via budget, and SI review |
| Power integrity | DC drop, plane/via current, regulator compensation, startup, current limit, load step, and worst-tolerance review |
| Backup operation | Oscilloscope proof of no reset, display blink, audio mute, or network reset during source transfer |
| Battery limit | Firmware load shedding below the controlled battery threshold; 151.7 W at 11.35 V is 13.37 A, above the 12 A continuous battery rating |
| Thermal | Closed-enclosure 45 C / 113 F chamber run at simultaneous CPU/GPU/NPU, Wi-Fi, cellular, display, audio, and fan load |
| Audio | All 16 channels at +4 dBu nominal, +24 dBu maximum, 600 ohm compatibility, noise, THD+N, crosstalk, mute, and fault tests |
| Safety and EMC | PE/chassis continuity, mains barrier, creepage/clearance, fuse/abnormal test, ESD/EFT/surge, radiated/conducted emissions and immunity |
| Mechanics | Actual case, monitor, folded antennas, sidewall fans, panel, PCB supports, connector insertion loads, vibration, and lid-closure validation |

The 184.2 W short transient at 11.35 V is 16.23 A and must not be treated as a
sustainable battery operating point. The locked 24 V RPS-400-24-C supply has
adequate nominal wattage for the 151.7 W continuous design case, but its final
temperature and airflow remain qualification items.

## Controlled Primary Sources

- Radxa CM5 design files and V2.21 pin allocation:
  https://docs.radxa.com/en/som/cm/cm5/download
- Radxa CM5 IO V2.2 schematic, including the ES8316 reference implementation:
  https://dl.radxa.com/cm5/radxa_cm5_io_board_v2200_schematic.pdf
- Microchip LAN7430/LAN7431 data sheet:
  https://ww1.microchip.com/downloads/aemDocuments/documents/UNG/ProductDocuments/DataSheets/LAN7430-LAN7431-Data-Sheet-DS00002631.pdf
- AsiaRF AW7915-NP1 data sheet:
  https://asiarf.com/wp-content/uploads/2023/09/AW7915-NP1_V1231004.pdf
- Quectel RM520N hardware design guide used for the socket-local VCC network:
  https://forums.quectel.com/uploads/short-url/1zkjPRnxF5BZ2woox386baCZx4g.pdf
- Littelfuse SMF4L5.0AT1G product data:
  https://www.littelfuse.com/products/overvoltage-protection/tvs-diodes/surface-mount/smf4l-t1g/smf4l5-0at1g
- Texas Instruments SN74LVC1G11, TPS62913, TPS25982, and TPS22990 data sheets:
  https://www.ti.com/lit/ds/symlink/sn74lvc1g11.pdf
  https://www.ti.com/lit/ds/symlink/tps62913.pdf
  https://www.ti.com/lit/ds/symlink/tps25982.pdf
  https://www.ti.com/lit/ds/symlink/tps22990.pdf
- NXP PCA9306 data sheet:
  https://www.nxp.com/docs/en/data-sheet/PCA9306.pdf
- Analog Devices LT3045 data sheet:
  https://www.analog.com/media/en/technical-documentation/data-sheets/3045fa.pdf
