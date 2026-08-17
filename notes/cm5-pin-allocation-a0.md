# Radxa CM5 Pin Allocation A0

## Purpose

This document locks the Radxa CM5 interface ownership needed to continue the
`CM5-CARRIER` schematic without assigning one muxed pin to two subsystems.

Primary source:

- Official Radxa CM5 V2.21 connector pinout:
  `https://dl.radxa.com/cm5/v2210/radxa_cm5_v2210_pinout.xlsx`
- Local controlled copy: `docs/radxa_cm5_v2210_pinout.xlsx`
- Official Radxa CM5 IO V2.2 reference design:
  `references/radxa-cm-projects/cm5/radxa-cm5-io-board/`
- Reference repository commit: `30ced6754b31ff048245a4def8aaf27319991426`

The companion workbook is the row-level audit record. This note records the
decisions that schematic capture must follow.

## Locked High-Level Ownership

| CM5 resource | Product owner | Decision |
| --- | --- | --- |
| Native Ethernet MDI and LEDs | `WAN1` | Direct CM5 PHY MDI to magnetics/RJ45. Do not add another PHY. |
| `PCIE20_0` plus `PCIE20X1_2` sidebands | `PI7C9X2G608GP` upstream | Feeds three LAN7430 endpoints and the Mini PCIe AW7915-NP1 through the PCIe switch. |
| `USB30_2` plus `USB20_HOST0` | M.2 B-Key WWAN | Dedicated to the SIM8260G-M2-class modem socket. |
| `USB20_HOST1` | Lid touchscreen touch | Dedicated USB2 host pair for touch data. |
| Type-C0 USB2 OTG | Internal recovery/provisioning | No top-panel recovery connector. Keep internal service access. |
| `HDMI_TX0` | Lid touchscreen video | Dedicated HDMI path to the underside-facing lid harness connector. |
| `I2S0` transmit group plus `I2S0_SDI0` | AK5558VN/AK4458VN TDM | Main 8-input/8-output audio link. |
| `I2S1_M0` | ES8316 headset codec | Separate headset playback/capture bus. |
| `UART2_M0` | Debug UART | Preserved because the headset does not use `I2S1_M1`. |
| `I2C7_M2` | System/audio control bus | AKM control, fan controller, sensors, GPIO expanders, and monitored control devices. |
| `I2C3_M1` | ES8316 control bus | Separate headset codec control bus. |

## Main Audio TDM Pins

| Function | Connector | Pin | Selected signal | Carrier net |
| --- | --- | ---: | --- | --- |
| DAC data | U13-A | 34 | `I2S0_SDO0` | `AUD_DAC_SDIN` |
| Bit clock | U13-A | 46 | `I2S0_SCLK_TX` | `AUD_BCLK` |
| Frame sync | U13-A | 48 | `I2S0_LRCK_TX` | `AUD_FSYNC` |
| Master clock | U13-A | 50 | `I2S0_MCLK` | `AUD_MCLK` |
| ADC data | U13-A | 54 | `I2S0_SDI0` | `AUD_ADC_SDOUT` |
| Control clock | U13-A | 80 | `I2C7_SCL_M2` | `SYS_I2C7_SCL` |
| Control data | U13-A | 82 | `I2C7_SDA_M2` | `SYS_I2C7_SDA` |

The carrier-to-audio-board line drivers keep the existing differential harness
net names defined in `cad/kicad/INTERBOARD_INTERFACE_CONTRACT.md`.

## Headset Pins

| Function | Connector | Pin | Selected signal | Carrier net |
| --- | --- | ---: | --- | --- |
| Headset MCLK | U13-A | 100 | `I2S1_MCLK_M0` | `HS_MCLK` |
| Headset BCLK | U13-A | 28 | `I2S1_SCLK_TX_M0` | `HS_BCLK` |
| Headset LRCK | U13-A | 30 | `I2S1_LRCK_TX_M0` | `HS_LRCK` |
| Playback data | U13-A | 31 | `I2S1_SDO1_M0` | `HS_SDOUT_TO_CODEC` |
| Capture data | J1 | 40 | `I2S1_SDI0_M0` | `HS_SDIN_FROM_CODEC` |
| I2C data | J1 | 4 | `I2C3_SDA_M1` | `HS_I2C_SDA` |
| I2C clock | J1 | 6 | `I2C3_SCL_M1` | `HS_I2C_SCL` |
| Jack detect | J1 | 36 | `HP_DET_L` | `HS_JACK_DET_N` |

This selection consumes the `SPI0_M1` pin group and related
`PCIE20X1_1_*_M1` alternate functions. They are unavailable elsewhere.

`I2S1_M1` is prohibited because its MCLK/BCLK choices collide with the locked
`UART2_M0` debug pins on U13-A pins 55 and 51.

## Network And PCIe Pins

- Native Ethernet MDI: U13-A pins 3, 4, 5, 6, 9, 10, 11, and 12.
- Native Ethernet LEDs: U13-A pins 15, 17, and 19.
- PCIe sidebands: U13-A pin 24 (`WAKE_N`), U13-B pin 102 (`CLKREQ_N`), and
  U13-B pin 109 (`PERST_N`).
- PCIe reference clock: U13-B pins 110 and 112.
- PCIe receive pair: U13-B pins 116 and 118.
- PCIe transmit pair: U13-B pins 122 and 124.

The CM5 PCIe receive pair connects to the switch transmit pair, and the CM5
transmit pair connects to the switch receive pair. Naming in the schematic must
include the endpoint direction to prevent a false same-name connection.

## USB Ownership

| Function | Connector pins | Owner |
| --- | --- | --- |
| `USB30_2` SuperSpeed TX | J1 51/53 | WWAN M.2 B-Key |
| `USB30_2` SuperSpeed RX | J1 57/59 | WWAN M.2 B-Key |
| `USB20_HOST0` D+/D- | J1 63/65 | WWAN M.2 B-Key |
| `USB20_HOST1` D+/D- | J1 45/47 | Lid touchscreen touch |
| Type-C0 OTG D-/D+ | U13-B 103/105 | Internal recovery USB |
| Type-C0 OTG ID | U13-B 101 | Internal recovery USB role control |
| Type-C0 OTG VBUS detect | J1 97 | Internal recovery USB VBUS sense |

Selecting `USB30_2` makes the J1 high-speed lane group unavailable for
`PCIE20_2` or `SATA30_2`.

The selected monitor has a SuperSpeed Type-B receptacle, but the product
allocation only provides a USB2 host pair for touch. Before schematic release,
bench-test the exact monitor and cable and confirm that its touch controller
enumerates and operates over the receptacle's USB2 D+/D- contacts. If it
requires SuperSpeed, the present allocation conflicts with the dedicated WWAN
link and the USB architecture must be redesigned.

## HDMI Ownership

Use the full `HDMI_TX0` video group on U13-B:

- Data 2: pins 170/172.
- Data 1: pins 176/178.
- Data 0: pins 182/184.
- Clock: pins 188/190.
- CEC: pin 151.
- HPD: pin 153.
- DDC SDA/SCL: pins 199/200.

Pins 145/147 are the HDMI sideband/HEAC pair. Keep them reserved and do not
repurpose them until the final HDMI connector implementation decides whether
they are routed or left unpopulated.

## Control And GPIO Policy

Do not spend direct CM5 pins on four fan PWM/tach channels, seven source-status
signals, all status LEDs, modem controls, and every audio reset/mute signal.

- Put fan PWM/tach control on the I2C fan controller.
- Put source-status inputs, status LEDs, modem power/reset/SIM controls, Wi-Fi
  rail enable, and AKM reset/mute controls on I2C7 GPIO expanders or dedicated
  controllers.
- Reserve U13-A pin 20 (`GPIO0_A0`) as the direct `AUD_IRQ_N` input.
- Use J1 pin 36 as the direct headset jack-detect input.
- Any expander interrupt output must receive one intentionally selected direct
  GPIO during detailed schematic capture; do not assign one informally.

I2C addresses and interrupt GPIO assignments remain schematic actions. The
bus-level resource allocation itself is locked.

## Power And Service Pins

- Connect all six U13-A `VCC_SYSIN` pins: 77, 79, 81, 83, 85, and 87.
- Drive those six pins from `SYS_4V0`; the nominal calculated setpoint is
  4.006 V. This follows the Radxa carrier design note's 4 V recommendation for
  RK806 efficiency and peak performance.
- Set U13-A pin 78 `GPIO_VREF` to the selected 3.3 V I/O domain. Do not expose
  any assigned CM5 GPIO to 5 V.
- U13-B pin 106 `5V_HDMI` receives `IO_5V0` because `VCC_SYSIN` is below 5 V.
  The same 4.984 V rail supplies separately fused HDMI source 5 V and USB-touch
  VBUS branches.
- Keep U13-A pins 92 (`RESET_L`), 93 (`SARADC_VIN0_BOOT`), and 99 (`PWRON_L`)
  accessible internally for bring-up and recovery. They are not top-panel
  controls.
- J1 pin 26 (`SARADC_VIN1_KEY/RECOVERY`) remains an internal service input.

Bench qualification must still confirm regulator tolerance, remote-sense
overshoot, hot-plug transient, CM5 connector drop, and full-load stability.
The schematic nominal is locked at 4.006 V; changing it requires a new CM5
power and HDMI-pin audit.

## Schematic Integration Actions

1. Replace generic CM5 interface labels in `CM5-CARRIER` with the exact
   connector, pin, SoC ball, and selected mux names in the workbook.
2. Add explicit no-connect flags for unused alternate-function pins; never
   imply that an alternate mux is simultaneously available.
3. Add the USB host ownership labels at both CM5 and destination connectors.
4. Add the headset `I2S1_M0` pins and preserve `UART2_M0` as debug UART.
5. Add I2C address and pull-up analysis for every device on `I2C7_M2` and
   `I2C3_M1`.
6. Add one controlled GPIO-expander interrupt assignment after the expander
   part and interrupt behavior are selected.
7. Verify device-tree pinctrl names against the production Radxa kernel before
   board release; the connector allocation does not by itself prove software
   support for every mux.

## Release Gate

This A0 allocation is suitable for continuing schematic capture. It is not a
fabrication release. Close the conditional items in the workbook, complete the
monitor USB2 touch test, verify the 4 V CM5 input rail under load, and run ERC plus a
net-by-net connector audit before layout begins.
