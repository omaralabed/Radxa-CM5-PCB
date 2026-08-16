# Bring-Up Checklist

## Before Fabrication

- Schematic ERC reviewed.
- PCB DRC reviewed.
- CM5 connector pin mapping reviewed against official Radxa V2.21 pinout.
- Power rails checked for voltage, current, sequencing, and protection.
- Every regulator design worksheet, compensation result, inductor saturation,
  MOSFET SOA, eFuse limit, copper loss, and worst-case thermal calculation is
  independently reviewed.
- ProComm-style source selector checked for 24 V, D-Tap, and Gold Mount priority behavior.
- USB, HDMI, PCIe, Ethernet, TDM-clock, and RF impedance/routing rules documented.
- Connector protection matches `connector-protection-matrix.md` and is placed
  at the connector boundary.
- PE/chassis schematic, mains barrier, creepage/clearance, fuse coordination,
  MOV/EMI filter, wire, terminal, strain-relief, and ground-bond details receive
  a qualified safety review.
- Connector orientation and pin 1 markings verified.
- Mounting holes, board outline, and component heights verified.
- BOM availability checked.
- Assembly drawings and polarity marks checked.

## First Power

- Inspect PCB and assembly under magnification.
- Check input-to-ground resistance before applying power.
- Current-limit bench supply for first power-up.
- Verify standby and main power rails before installing CM5.
- Verify source-selector output and regulator rails from rear 24 V, D-Tap, and Gold Mount inputs before installing CM5.
- Verify no-blink source transfer with a scope before installing CM5:
  `24V_PSU`, `BAT_SELECTED`, protected raw DC, `SYS_5V15`, `DISPLAY_12V`,
  `AUX_12V`, `FAN_CPU_12V`, `FAN_AUX_12V`, `MODEM_3V8`, `WIFI_3V3`, `NET_3V3`, `PCIE_1V0`,
  audio rails, reset lines, and mute lines must stay inside limits.
- Use the ProComm PowerSelector Rev C bench-test style as the starting point,
  but repeat it at Radxa current levels and with the locked `RPS-400-24-C`
  primary PSU.
- Confirm no rail exceeds documented maximum voltage.
- Install CM5 and repeat with current limit.
- Check debug UART output.
- Boot from known-good OS image.
- Verify USB recovery and eMMC provisioning path.

## Interface Tests

- Verify all four 1 GbE ports independently and simultaneously, including
  WAN/LAN isolation and shared PCIe-upstream saturation behavior.
- USB 2.0 and USB 3.0 enumeration.
- HDMI display output at all supported modes.
- HDMI touchscreen USB input.
- PCIe switch, three LAN7430 controllers, and AW7915-NP1 enumeration.
- All four Wi-Fi RF chains, AP band selection, and 25-client closed-case load test.
- M.2 WWAN USB 2/3 enumeration, both SIM trays, power cycle, and all four RF paths.
- RTC battery retention.
- Fan PWM/tach if populated.
- CPU fan speed control.
- Cellular modem fan speed control from modem-zone temperature.
- Board/enclosure fan 1 and fan 2 speed control from board temperature sensors.
- Thermal alarm and fan-fail behavior for all four fans if tach feedback is
  populated.
- Confirm all four fans default to full speed when I2C/control is removed.
- Confirm each enclosure-fan channel starts at 100% duty, runs at 1 kHz PWM,
  provides valid tach feedback, and is never commanded below 30% duty.
- Run the 151.7 W continuous design case in the closed enclosure at 45 C / 113 F
  ambient; record internal sensors, CM5/modem telemetry, PSU, spreader,
  bulkhead, external-fin, lid, and connector temperatures.
- Apply ESD, EFT, surge, short-circuit, hot-plug, and fault tests in a controlled
  compliance/pre-compliance setup before field use.
- Perform powered and unpowered shock/vibration testing in all three axes with
  the production monitor, battery, modem, Wi-Fi module, heatsinks, fans, PSU,
  and harnesses installed. Test both transport configuration and normal
  operating configuration.
- During powered vibration, log rail voltage, source transfer, CM5 resets,
  Ethernet links, Wi-Fi/cellular registration, fan tach, storage errors, audio
  clocks, and ALSA xruns.
- After testing, inspect panel and PCB fasteners, standoffs, XLR and RJ45 solder
  joints, CM5 board-to-board connectors, M.2 retainers, large components,
  heatsinks, fan mounts, battery dock, PSU mounts, and every harness clamp.
- Require no loose hardware, cracked solder joints, fretting, connector motion,
  intermittent operation, enclosure contact, or visible PCB deformation.

## Audio Stress Tests

- Confirm 8-channel capture and 8-channel playback enumerate with the expected
  ALSA names and channel map.
- Verify +4 dBu nominal and +24 dBu maximum input/output on every channel;
  confirm outputs remain stable into 600 ohm and meet noise/distortion targets
  with a normal 10 kohm load.
- Run simultaneous 8x8 playback/capture while applying CPU stress.
- Repeat the same audio test while routing WAN/LAN traffic, broadcasting Wi-Fi
  AP traffic, using the cellular modem, displaying HDMI video, using USB touch,
  and writing logs to eMMC.
- Confirm no audible mute, no lost channels, no ALSA xruns, no kernel ASoC
  errors, and no converter reset/mute glitches during load spikes.
- Power-cycle and warm-reboot repeatedly to verify that ADC/DAC clocks, reset,
  and mute sequencing recover every time.
- Repeat the simultaneous 8x8 audio stress test while removing and restoring
  AC power with a valid backup source installed; confirm no display blink, no
  CM5 reset, no audible mute/click, and no ALSA xrun.
