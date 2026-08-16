# Pre-Schematic Open Decisions

## Purpose

This is the remaining decision list for progressing the Radxa CM5 ProComm A0
interface baseline into complete detailed schematics.

## Must Lock Before Detailed Capture

- CAD tool and release format are locked to native KiCad 10 projects under
  `cad/kicad/`. The A0 interboard contract is captured and machine-validated.
- Board strategy is locked: separate `PWR-SELECT`, `CM5-CARRIER`, and
  `AUDIO-8X8` low-voltage assemblies plus the commercial bottom-mounted PSU.
- Board stackup: likely 6 layers minimum, with impedance-controlled pairs for
  HDMI, USB 3, PCIe, Ethernet, and clean audio reference planes.
- Exact Radxa CM5 hardware revision and connector pinout.
- Display/touchscreen model is locked to JUNEBOX / DTM MALL Amazon ASIN
  `B0GK5X95D9`; still verify exact brightness/current draw, bezel, connector
  orientation, mounting hardware, and lid harness on the received sample.
- Ethernet is locked to Rev A 1 GbE: native WAN1 plus three `LAN7430`
  controllers behind `PI7C9X2G608GP` for WAN2/LAN1/LAN2. The same PCIe switch
  feeds the `AW7915-NP1` Mini PCIe 4T4R Wi-Fi AP validation module.
- ProComm-style cellular M.2 B-Key WWAN slot details: SIM8260G-M2 global 3052
  validation target, 3042/3052 retention, dual Nano-SIM, four cellular/GNSS RF
  paths, Radxa GPIO assignments, region/carrier bands, GNSS behavior, and
  peak-current 3.8 V-class rail.
- Bottom-panel PSU integration: locked MEAN WELL `RPS-400-24-C` production
  supply, top-panel fused no-switch C14 inlet, EMI/PE plan, service barrier,
  low-voltage harness route, remote-sense/status wiring decisions, and thermal
  validation using its 252 W convection-rated design basis.
- Power architecture baseline selected from
  `/Users/viewvision/Desktop/ProComm enclosure and PCB boards`: 24 V primary,
  D-Tap second, Gold Mount third, LTC4418 backup preselector, LTC4421 main
  selector, telemetry, and protected raw-DC output.
- C14 production starting part is Qualtek `719W-00/03`, fused and unswitched.
  Its official rating is 10 A / 250 Vac, not the previously requested literal
  15 A / 120 Vac marking. Accept that agency/nameplate difference or select a
  different inlet before mechanical release; also confirm panel fit,
  gasket/cover, and fuse coordination.
- Main power switch in KiCad: copy the ProComm E-Switch `RA812C1121` DPST
  arrangement as `SW201` through keyed four-wire harness `J204`. Pole A enables
  LTC4421 `SHDN_MAIN`; pole B enables LTC4418 `SHDN_PRE`. Do not put the switch
  inside the IEC inlet or route AC mains/high-current source rails through it.
- Regulator targets and starting ICs are locked in
  `rev-a-hardware-architecture.md`; complete detailed calculations, simulation,
  layout, efficiency, transient, EMI, and thermal proof for every rail.
- No-blink/no-mute transfer budget: source-selector timing, protected raw-DC
  hold-up, local rail hold-up, regulator UVLO/dropout, display 12 V buck-boost,
  and oscilloscope acceptance limits.
- Thermal architecture is locked to a filtered right-wall intake, an
  operator-wall center-right exhaust, and downward-facing CM5/modem cooling
  cartridges. Complete wall measurements, baffles, guards, and 151.7 W
  closed-case validation; use a sealed heat exchanger if reduced sealing is
  unacceptable.
- Fans are locked to four independent 12 V PWM/tach channels controlled by an
  `EMC2305`. The two sidewall enclosure fans are Delta
  `THA0412AD-TZW3`; use one Qualtek `09150-F/30` filter guard on the intake and
  a low-restriction exhaust guard. Select the exact modem fan and place three
  `TMP117` sensors. Enclosure fan 1 is filtered
  right-wall intake and enclosure fan 2 is operator-wall exhaust. Baffles must
  route air through the hot zones. Keep fan/PWM wiring out of the XLR quiet zone
  and guarded hinge-side PSU corridor.
- Top-panel mechanical layout inside the source-checked 17.00 in x 11.733 in
  nominal base bezel reference: XLR bank position, network/power/service
  connector positions, antenna placement, vents, labels, and service clearance.

## Audio Decisions

- XLR bank order is selected from the photo reference: two vertical columns,
  eight rows, left male outputs `CH1 OUT`-`CH8 OUT`, right female inputs
  `CH1 IN`-`CH8 IN`.
- XLR size source is selected from
  `/Users/viewvision/Desktop/2026/ProComm PCB XLRs + Transformer`: Neutrik
  `NC3MAV` outputs and `NC3FAV` inputs, starting from 28 mm row pitch,
  43.38 mm circular-center column spacing, and 22.8 mm reference circle
  diameter. Preserve 15.0 mm (0.59 in) from the finished left panel edge to the
  XLR bank outer edge so the bank clears the four-side frame boundary.
- Still confirm official panel cutouts, STEP models, latch-tab orientation, and
  whether the 28 mm pitch leaves enough room for labels under each connector.
- Audio level is locked to +4 dBu nominal and +24 dBu maximum, 10 kohm normal
  load, 600 ohm compatibility/test load, line level only, and no phantom power.
- Confirm AK5558VN/AK4458VN clocking: CM5 master first, external master clock
  option only if needed.
- Confirm sample rates for first bring-up: 48 kHz and 96 kHz.
- Define the audio stress-test target based on the prior Raspberry Pi issue:
  no silent audio, no lost sync, and no unrecovered ALSA xruns during CPU,
  network, Wi-Fi AP, cellular, HDMI/touch, and storage load spikes.
- Confirm balanced input receiver/output driver parts and analog supply rails.
- Define audio ground/chassis bonding, connector shield treatment, and ESD/RFI
  protection at every XLR.
- Define mute/pop protection for outputs during boot, reset, shutdown, and
  source switchover.
- Confirm ES8316 headset jack standard, likely CTIA TRRS, with headphone
  amplifier/driver, mic bias/preamp/input conditioning, headphone detect, ESD
  protection, dedicated headset regulator, mute/pop behavior, and software
  mixer routing.

## System I/O Decisions

- Debug UART is an internal keyed 3.3 V header; select its exact location.
- USB recovery must remain panel/service accessible. Reset/recovery buttons
  stay internal or on the PCB underside and must remain reachable during service
  without removing the main carrier.
- External service USB ports and current limits.
- Status LED functions are selected; finish color, drive, light-pipe, label,
  and panel location details. Top-panel indicators are now the Bulgin `DX06`
  12 V wire-lead family listed in `panel-mounted-parts-selection.md`.
- The two top-facing SIM openings require a vertical SIM service daughterboard;
  the selected Wurth `693043020611` side-entry holder cannot be mounted flat
  below those openings.
- RTC battery or supercap requirement.
- Hardware watchdog requirement.
- Factory-test pads and programming headers.

## Software Decisions

- Target OS: Radxa Debian/Ubuntu, OpenWrt-derived image, or custom Linux build.
- Device tree plan for I2S0 TDM, I2S1 headset codec, PCIe, USB, fan PWM/tach,
  LEDs, buttons, and recovery controls.
- ALSA naming and channel map for 8x8 program audio plus headset.
- Audio runtime policy: CPU governor, IRQ affinity, buffer sizes, real-time
  scheduling, watchdog/recovery behavior, and logging for TDM underruns.
- Accelerator policy selected: use GPU for HDMI touchscreen UI, meters,
  waveform/spectrum display, and graphics; reserve NPU for future AI
  noise/classification and smart monitoring; keep I2S/TDM timing, ALSA DMA, and
  SIP/RTP real-time behavior on protected CPU/kernel paths.
- Router/firewall stack: `nftables`, NetworkManager, ModemManager, `hostapd`,
  and WAN failover policy.
- Factory provisioning flow for eMMC-only systems.

## Release Gates

- Electrical schematic ERC and manual review.
- No-blink power-transfer test: primary-to-backup and backup-to-primary under
  full system load with CM5, display, audio, Wi-Fi AP, cellular, Ethernet, and
  fans active.
- PCB DRC, impedance rules, and high-speed routing review.
- Mechanical 2D/3D fit check in the Pelican iM2300 with lid, panel, battery,
  XLR connectors, antennas, fans, and harnesses.
- Power, thermal, RF, audio-noise, Ethernet, Wi-Fi AP, cellular, HDMI/touch, and
  recovery tests on the acceptance prototype.
