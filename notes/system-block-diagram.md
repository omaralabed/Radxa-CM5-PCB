# System Block Diagram

## Purpose

Top-level block diagram for the Radxa CM5 ProComm carrier. This captures the
selected architecture before schematic partitioning.

## Power And System Blocks

```mermaid
flowchart LR
  AC["Top-panel Qualtek 719W-00/03<br/>fused C14, no switch"] --> EMI["Fuse / EMI filter / MOV<br/>PE bond / service barrier"]
  EMI --> PSU["Bottom-panel 24 V PSU<br/>MEAN WELL RPS-400-24-C<br/>24 V / 10.5 A / 252 W convection"]

  LEMO["LEMO EGG.1B.302 backup<br/>13.0-16.8 V / 15 A path"] --> PRE["LTC4418 backup preselector"]
  GOLD["Gold Mount battery dock<br/>14.1 V nominal"] --> PRE
  PRE --> BAT["BAT_SELECTED"]

  PSU --> MAINSEL["LTC4421 main selector<br/>24 V first, backup second"]
  BAT --> MAINSEL
  MAINSEL --> RAW["Protected raw DC<br/>telemetry / 22 mF hold-up start<br/>no-blink transfer"]

  RAW --> SYS5["LM5146 SYS_5V15<br/>5.15 V / 12 A"]
  RAW --> WIFI33["LM61440 WIFI_3V3<br/>3.3 V / 4 A"]
  RAW --> MODEM38["LM61460 MODEM_3V8<br/>3.8 V / 6 A + eFuse"]
  RAW --> AUDIO["Clean audio rails<br/>+/-15 V, 5 V, 3.3 V"]
  RAW --> HSPWR["Dedicated HEADSET_3V3<br/>low-noise regulator"]
  RAW --> AUX12["LM5176 AUX_12V<br/>revised 12 V / 8 A minimum target"]
  RAW --> ETHPWR["NET_3V3 4 A<br/>PCIE_1V0 2 A"]

  AUX12 --> DISP["Fused DISPLAY_12V harness<br/>12 V / 2.5 A"]
  AUX12 --> FAN["Protected FAN_CPU_12V<br/>12 V / 3 A Delta CPU fan"]
  AUX12 --> FANREST["Protected FAN_AUX_12V<br/>12 V / 3 A"]

  SYS5 --> CM5["Radxa CM5<br/>eMMC only"]
  WIFI33 --> WIFI["Mini PCIe Wi-Fi AP<br/>AW7915-NP1 4T4R<br/>4 antennas"]
  MODEM38 --> WWAN["M.2 B-Key WWAN<br/>SIM8260G-M2 target<br/>3042/3052 support"]
  AUDIO --> ADC["AK5558VN ADC<br/>8-ch balanced in"]
  AUDIO --> DAC["AK4458VN DAC<br/>8-ch balanced out"]
  HSPWR --> HS["ES8316 headset codec<br/>headphone amp + mic preamp<br/>separate I2S1"]
  DISP --> TOUCH["15.6-inch JUNEBOX lid HDMI touchscreen<br/>12 V / 25 W, HDMI + USB touch"]
  FAN --> FANS["EMC2305 + 4 PWM/tach fans<br/>CPU, modem, board 1, board 2"]
  ETHPWR --> ETH["PI7C9X2G608GP<br/>3 x LAN7430"]

  FANS --> SPREADER["Internal aluminum heat spreader"]
  SPREADER --> BULKHEAD["Gasketed side-wall thermal bulkhead"]
  BULKHEAD --> SINK["External finned heat sink"]
```

## Data And I/O Blocks

```mermaid
flowchart TB
  CM5["Radxa CM5"]

  CM5 -- "I2S0 TDM<br/>8 slots x 32-bit" --> AKM["AK5558VN + AK4458VN"]
  AKM --> XLR["8 XLR inputs + 8 XLR outputs<br/>active balanced analog stages"]

  CM5 -- "I2S1" --> HSCODEC["ES8316 headset codec"]
  HSCODEC --> HSAMP["Headphone amp + mic bias/preamp"]
  HSAMP --> HJACK["3.5 mm CTIA TRRS headset<br/>headphones + mic"]

  CM5 -- "Native GbE MDI" --> WAN1["WAN1 RJ45"]
  CM5 -- "PCIe 2.0 x1" --> PCIESW["PCIe switch"]
  PCIESW --> NIC2["LAN7430"]
  PCIESW --> NIC3["LAN7430"]
  PCIESW --> NIC4["LAN7430"]
  NIC2 --> WAN2["WAN2 RJ45"]
  NIC3 --> LAN1["LAN1 RJ45"]
  NIC4 --> LAN2["LAN2 RJ45"]
  PCIESW --> WIFI["Wi-Fi AP module<br/>4 external antennas"]

  CM5 -- "USB30_2 + USB2" --> MODEM["M.2 B-Key cellular modem"]
  MODEM --> SIMMUX["Dual Nano-SIM mux"]
  SIMMUX --> SIM1["SIM 1"]
  SIMMUX --> SIM2["SIM 2"]
  MODEM --> CELLANT["4 cellular antennas<br/>CELL 1, CELL 2, CELL 3, CELL 4 / GNSS"]

  CM5 -- "HDMI" --> DISPLAY["15.6-inch JUNEBOX lid touchscreen"]
  CM5 -- "USB touch" --> DISPLAY

  CM5 -- "I2C / thermal zones" --> THERMAL["EMC2305 + 3 x TMP117<br/>CPU temp + modem internal temp"]
  THERMAL --> FAN1["CPU fan"]
  THERMAL --> FAN2["Cell modem fan"]
  THERMAL --> FAN3["Board fan 1"]
  THERMAL --> FAN4["Board fan 2"]

  CM5 -- "GPU" --> UI["Touch UI, meters, waveform/spectrum, graphics"]
  CM5 -- "NPU" --> AI["Future AI noise/classification and smart monitoring"]
```

## Partition Notes

- `PWR-SELECT` is a separate bottom-mounted low-voltage source-selector board.
- `CM5-CARRIER` contains digital, network, radio, display/USB, headset, fan
  control, and downstream low-voltage regulation.
- `AUDIO-8X8` contains the AKM converters and all 16 active-balanced XLR paths.
- Heavy XLR connectors are panel-supported, with PCB/harness interconnects.
- The AC/DC PSU is bottom-panel-mounted; the top panel carries the fused C14
  inlet and connector/PCB panel.
- The Wi-Fi AP rail and cellular modem rail are separate supplies.
- Source transfer is no-blink/no-mute when a valid backup source is present;
  protected raw DC and critical downstream rails need hold-up.
- The cellular modem gets both a heatsink/thermal spreader and a dedicated fan.
- The two board/enclosure fans are controlled from board temperature sensors.
- The real heat exit is a gasketed metal side-wall bulkhead connected to an
  external finned heat sink; the Pelican plastic wall is not used as a heat sink.
- Audio/SIP runtime should stay on protected CPU resources; GPU/NPU acceleration
  is for UI, meters, graphics, and future AI monitoring.
