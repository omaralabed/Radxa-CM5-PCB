# Connector Protection Matrix

## Purpose

Schematic starting point for protection at every external connector. Exact
parts remain subject to signal-integrity simulation, availability, compliance
test results, and the selected connector pinout.

| Interface | Starting protection | Placement and return rule | Release check |
| --- | --- | --- | --- |
| IEC C14 mains | Active `T6.3A H 250V` ceramic fuse, 10 A EMI filter, thermally protected 275 Vac MOV, PE bond | Fuse and PE immediately at inlet; MOV after fuse; guarded mains bay | Fuse coordination, inrush, leakage, hi-pot, ground bond, surge/EFT, temperature |
| 24 V PSU harness | Connector fuse, reverse/ORing MOSFET path, TVS selected for regulator/transient limits, current telemetry | At source-selector entry; short high-current return | Short circuit, hot plug, surge, wiring fault, transfer SOA |
| D-Tap/LEMO backup | Fuse, reverse-polarity blocking, back-to-back MOSFETs, TVS, UV/OV sensing | At panel entry before long traces | Reverse battery, 13.0-16.8 V load, hot plug, cable drop, transfer |
| Gold Mount | Fuse, reverse-current blocking, back-to-back MOSFETs, TVS, telemetry | At battery-dock entry | Reverse/backfeed, overcurrent, connector heating, battery BMS trip |
| HDMI | Two `TPD4E05U06` arrays for four TMDS pairs; low-capacitance ESD for DDC/CEC/HPD; protected 5 V | Immediately behind HDMI connector with direct chassis/ground stitching | HDMI mode/eye, hot plug, IEC 61000-4-2 |
| USB 3 | `TPD4EUSB30` for SuperSpeed pairs; USB2 low-capacitance ESD; VBUS eFuse/current limit and discharge | At connector, with straight-through differential routing | USB3 link margin, ESD, shorted VBUS, inrush, backfeed |
| USB recovery/service | USB2 low-capacitance ESD, VBUS current limit, recessed/service access | At service connector | Recovery from blank eMMC, ESD, misplug and short |
| RJ45 x4 | Integrated magnetics, PHY-side `RClamp03322P`-class TVS per pair, Bob Smith termination, shield/chassis bond | At each connector; shield surge returns to chassis, not through logic ground | 10/100/1000 link, cable discharge, ESD/EFT, common-mode emissions |
| XLR inputs x8 | THAT1206 reference RFI/ESD network, series impedance, common-mode capacitance to chassis as calculated | At XLR pins; pin 1 bonds directly to chassis | +24 dBu, RF immunity, ESD, hum, miswire |
| XLR outputs x8 | THAT1646 reference output isolation/RFI network, transient clamps, phantom-fault protection | At XLR pins; pin 1 bonds directly to chassis | +24 dBu into 600 ohm, short/open, accidental phantom, RF/ESD |
| CTIA headset | `TPD4E101`-class low-capacitance four-line ESD plus audio RF series/filter parts | At TRRS jack with short return and controlled jack-detect path | Plug/unplug pop, ESD, mic/headphone routing, shorted contacts |
| Nano-SIM x2 | `TPD3F303` dedicated SIM EMI/ESD array plus protected SIM VCC clamp | Beside each SIM holder; follow modem trace-length rules | 1.8/3.0 V SIM operation, hot handling ESD, dual-SIM switching |
| Wi-Fi RF x2 | 0.1 pF-class RF ESD footprint such as `PESD5V0R1BSF`, optionally DNI after RF test | At bulkhead with shortest chassis return | S11/insertion loss, ESD, AP throughput and coexistence |
| Cellular/GNSS RF x4 | 0.1 pF-class RF ESD footprint, optionally DNI after RF test | At bulkhead; no RF surge path through digital ground | S11, TRP/TIS, GNSS sensitivity, ESD and coexistence |
| Fan headers x4 | Branch current limiting, reverse protection, PWM/tach series resistance and ESD | At each header; contain a failed fan to its branch | Stall, short, hot plug, tach fault, startup current |
| External buttons/LEDs | Series resistance, RC debounce/filter, low-capacitance ESD where exposed | At panel connector/service board | ESD, stuck button, cable fault, accidental reset |

## Layout Rules

- Keep TVS-to-connector and TVS-to-return paths shorter than the protected
  signal path.
- Do not add stubs to HDMI, USB 3, PCIe, Ethernet, or RF pairs.
- Stitch connector shields to the chassis reference at the panel boundary.
- Maintain separate dirty-entry and protected-side zones.
- Provide `DNI` options for common-mode chokes and RF shunts so the prototype
  can be tuned without PCB rework.
- Use the protection vendor's current reference layout and package land pattern.
- Validate all high-speed and RF choices in the final stackup and enclosure.
