# Requirements Draft

## Board Intent

Custom carrier board for the Radxa CM5 module with multichannel TDM audio.

## Selected Requirements And Remaining Inputs

- CAD target:
- Board outline:
- PCB/board partition: separate `PWR-SELECT`, `CM5-CARRIER`, and `AUDIO-8X8`
  low-voltage boards plus the commercial AC/DC PSU
- Enclosure: Pelican Storm Case iM2300 with custom top panel and PCB mounted underneath
- Portable-field durability: panel, PCB standoffs, connector flanges, modules,
  heatsinks, fans, PSU, battery dock, and harnesses must withstand transport
  shock and vibration without PCB flex, connector-solder stress, loose
  fasteners, intermittent resets, audio dropouts, or cable damage
- Connector/top-panel source-checked envelope: 17.00 in x 11.733 in nominal base bezel reference (431.8 mm x 298.0 mm nominal)
- Power input: same ProComm source-selection architecture from
  `/Users/viewvision/Desktop/ProComm enclosure and PCB boards`, with internal
  bottom-panel MEAN WELL `RPS-400-24-C` 24 V AC/DC PSU as the locked production
  primary source,
  D-Tap / LEMO backup, and Gold Mount battery dock
- Power transfer: no interruption/no blink between primary and valid backup;
  CM5, HDMI touchscreen, main audio, headset, Ethernet, Wi-Fi, cellular, and fan
  control must ride through source transfer without reset or mute
- Full load budget: 151.7 W continuous design estimate and 184.2 W transient
  estimate; replace estimates with prototype measurements
- Storage/boot: CM5 eMMC only
- Main use case:
- Must-have interfaces:
- Audio converters: AK5558VN ADC and AK4458VN DAC over TDM
- Audio channel count: 8-channel capture and 8-channel playback
- Audio reliability: 8x8 TDM program audio must not mute, drop out, or lose
  clock sync during CPU, network, Wi-Fi AP, cellular, storage, or display load
  spikes.
- Main audio analog I/O: left-side two-column XLR bank like the photo reference, with CH1-CH8 OUT male XLRs in the left column and CH1-CH8 IN female XLRs in the right column; XLR size/spacing basis comes from `/Users/viewvision/Desktop/2026/ProComm PCB XLRs + Transformer`
- Headset audio: integrated 3.5 mm CTIA TRRS jack with headphone output and
  microphone input, using a separate ES8316-class codec plus headphone
  amplifier/driver, mic bias/preamp/input conditioning, and dedicated low-noise
  headset regulator
- Network ports: two wired WAN ports and two shared wired LAN ports
- Wireless: high-speed Wi-Fi AP broadcast for about 25 simultaneous devices
- Cellular: global-coverage modem WAN path for failover or policy routing
- Local display: locked lid-mounted 15.6-inch HDMI touchscreen, JUNEBOX Amazon
  ASIN `B0GK5X95D9`; 1920 x 1080 IPS, HDMI input, USB touch, 12 V display
  power rated 25 W / 2.08 A, locked 12 V / 2.5 A carrier branch, and rugged USB
  Type-B SuperSpeed panel/service connector where practical
- Night operation: two diffused 12 V warm-white courtesy lights above the Gold
  Mount zone, controlled together by one latching capacitive touch switch. The
  lighting target is approximately 3000 K with broad, low-glare coverage so
  connector colors and labels remain distinguishable. The lighting circuit is
  hardware-only, separately fused, and does not depend on
  the CM5, Linux, or a GPIO expander.
- Cooling: four fans total. The CM5 is mounted on carrier B.Cu with a downward-
  facing Radxa `5540A` and attached Delta `FFB0412EN-00Y2E`; a structural
  bracket carries fan mass/vibration and the inlet retains at least 10 mm floor
  clearance. The modem uses a similar downward heatsink/fan cartridge. Two
  Delta `THA0412AD-TZW3` 40 x 40 x 20 mm enclosure fans provide a filtered
  right-wall intake and operator-wall center-right exhaust. All four PWM/tach
  channels are board controlled; the top panel has no cooling openings.
- Thermal strategy: measured sidewall airflow through the digital/power hot
  zones with baffles, reinforcement plates, gaskets, and splash louvers; a
  sealed heat exchanger remains the fallback if field sealing is re-required
- Enclosure: Pelican Storm Case iM2300 with custom top panel and PCB mounted underneath
- Storage/boot: use CM5 eMMC only
- Recovery/provisioning: USB recovery, debug UART, and network provisioning
- Nice-to-have interfaces:
- Prototype quantity:
- PCB/assembly vendor:
- Enclosure or mounting constraints:

## Rev A Interface Set

Start from the Radxa CM5 IO reference design and remove anything not needed.

- Power input and sequencing
- Protected ProComm-style power-entry/source selector using internal `24V_PSU`
  > D-Tap > Gold Mount priority
- No-blink source transfer using PowerPath controllers, hold-up capacitance,
  wide-input regulators, and a buck-boost `DISPLAY_12V` rail if the display is
  powered from the carrier during backup operation
- Bottom-panel MEAN WELL `RPS-400-24-C` AC/DC PSU, 24 V / 10.5 A / 252 W
  convection-rated design basis, with top-panel fused C14 inlet, no integrated
  inlet switch, EMI/PE treatment, service barrier, and low-voltage harness to
  the carrier/source-selector assembly
- Backup inlet based on 15 A LEMO `EGG.1B.302.CLL`, 13.0-16.8 V operating
  range; any D-Tap source cable must also carry the measured backup load
- Gold Mount battery dock based on Anton/Bauer Dionic XT 90 and user-locked
  QRC-GOLD bracket `8375-0094`; the dock mounts only to the top panel/custom
  frame and connects by a strain-relieved removable harness to the
  power-selector PCB; production release requires sample-verified mounting,
  latch travel, polarity, release sweep, and 12 A thermal performance
- CM5 board-to-board connectors
- Debug UART
- USB recovery/service connector or external USB-C recovery path
- Recovery/reset controls as required by CM5 boot flow
- 8-channel balanced TDM audio using AK5558VN and AK4458VN
- Left-side XLR bank: two vertical columns and eight rows; CH1 at top, CH8 at bottom; left column Neutrik `NC3MAV`-size male outputs, right column Neutrik `NC3FAV`-size female inputs; start from the legacy board's 28 mm row pitch and 43.38 mm circular-center column spacing; 15.0 mm / 0.59 in clearance from the finished left panel edge to the XLR bank outer edge
- 3.5 mm headset jack using ES8316-class stereo codec on separate I2S bus, with
  headset headphone amplifier/driver, mic bias/preamp/input conditioning, and
  a dedicated headset regulator
- Native CM5 1 GbE WAN1 plus `PI7C9X2G608GP` and three `LAN7430` controllers
  for 1 GbE WAN2/LAN1/LAN2
- Dedicated Mini PCIe `AW7915-NP1` true 4T4R Wi-Fi AP module with four antennas
- Separate dedicated Wi-Fi AP power rail
- Universal M.2 B-Key WWAN cellular modem socket with USB 2.0/USB 3.x, dual
  Nano-SIM support, and 3042/3052 mechanical support
- Separate dedicated cellular modem power rail
- HDMI display output for locked 15.6-inch HDMI touchscreen
- USB host port for touchscreen touch controller, with USB Type-B SuperSpeed
  panel/service connector preferred for the product interface where practical
- Lid-to-base HDMI/USB/display-power harness through one centered notch that
  opens directly at the top panel's hinge edge
- USB 2.0/3.0
- Locked Delta `FFB0412EN-00Y2E` CPU-fan power, PWM, and tach control
- Dedicated Delta `AFB0412SHB-SP04` cellular modem fan header/control and
  module-specific modem heatsink/thermal spreader
- Two board/enclosure fan headers controlled by board temperature sensors
- RTC battery
- Six system-status LEDs plus two night-illumination LEDs and one touch
  on/off control

## Early Risk Items

- Verify the exact CM5 hardware revision and pinout before assigning connector pins.
- Keep all GPIO at 3.3 V max unless the Radxa docs specify a lower limit; SARADC is lower voltage.
- Keep the headset codec off `I2S0`; that bus is reserved for the AK5558VN/AK4458VN TDM converters.
- Prior Raspberry Pi testing showed I2S audio could go silent during CPU spikes;
  treat TDM underrun/xrun recovery and long-duration stress testing as a
  product requirement, not a bring-up detail.
- High-speed interfaces need controlled impedance, length matching, clean reference planes, and connector-specific routing rules.
- Multi-port Ethernet and Wi-Fi AP support likely require PCIe resource planning before finalizing the board outline.
- Cellular modem requires global-band validation, peak-current power design, SIM ESD/protection, RF antenna placement, carrier/regulatory planning, and a universal M.2 B-Key WWAN socket approach.
- HDMI and USB touchscreen routing need ESD protection, connector placement,
  and enough 12 V accessory power for the selected 15.6-inch display/touch
  assembly.
- Lid-mounted touchscreen needs hinge-safe harness routing, strain relief, and
  enough clearance when the case opens/closes. Keep the actual HDMI,
  USB-touch, and 12 V cable envelope at least 15 mm from the grounded PSU guard
  through full lid and panel-service motion.
- Fan control needs PWM/tach GPIO allocation, current budget, acoustic planning,
  one modem-zone sensor placement, and at least two board temperature sensor
  placements for the two board/enclosure fans.
- eMMC-only boot means USB recovery, network provisioning, and debug UART must be available.
- Power input and load switch/current-limit choices need to match peak CM5 and peripheral current.
- The locked `RPS-400-24-C` PSU must be validated mechanically and thermally in
  the iM2300; use the 252 W convection rating unless forced-air PSU cooling is
  intentionally designed and tested. Its guarded floor bay is on the
  hinge/display side, rotated 90 degrees in plan, with 146 mm nominal and 125
  mm minimum separation from the AUDIO-8X8 quiet boundary.
- AC mains entry requires a fused C14 inlet with no built-in rocker switch, PE bonding, guarded service isolation, strain relief, and separation from audio/RF/high-speed low-voltage wiring.
- Qualtek `719W-00/03` is the production C14 starting part; RS PRO `811-7204`
  remains only the fused/no-switch panel-style reference. Do not claim a 15 A
  marking unless the final ordered part and agency file support it. The current
  Qualtek drawing specifies 10 A / 250 Vac.
- ProComm source-selection architecture is selected as the baseline, but the
  Radxa load budget, regulator sizing, hold-up capacitance, MOSFET SOA, fusing,
  telemetry scaling, and thermal validation still need to be recalculated.
- No-blink transfer must be measured under full system load; do not accept a
  schematic-only claim of seamless switchover.
- LAN7430, PCIe switch, Wi-Fi AP module, cellular modem, and SIM circuits must
  use the exact voltages, sequencing, current limits, and protection required
  by their selected datasheets.
- Mechanical placement must respect CM5 connector stack height, keepouts, antenna clearances, and mounting holes.
- XLR placement should use the extracted legacy ProComm XLR geometry in `notes/xlr-bank-reference.md`, then verify final Neutrik mechanical drawings, latch orientation, panel cutouts, and label clearance.
- Top-panel connector placement must fit inside the source-checked 17.00 in x 11.733 in nominal base bezel reference after real connector cutouts, cable clearance, panel fasteners, gasket/lip, and case taper are included.
- Top panel layout should follow the existing ProComm field unit reference: left-side XLR audio connector bank, headset/service area, antennas, vents, and right-side electronics area.
- Top-facing SIM access uses the controlled horizontal SIM-SERVICE
  daughterboard, insulating panel guide, four structural M3 supports, and
  direct 20-pin Hirose DF40 connection to the carrier. No SIM harness is used.
- Pelican iM2300 starts sealed, but the selected sidewall intake/exhaust makes
  this product intentionally vented. Validate ingress and 45 C thermal behavior.
