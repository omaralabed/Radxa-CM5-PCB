# TDM Audio Architecture

## Goal

Add 8-channel capture and 8-channel playback to the Radxa CM5 carrier using:

- AK5558VN 8-channel differential-input ADC
- AK4458VN 8-channel differential-output DAC
- Balanced analog inputs and balanced analog outputs
- CM5 I2S0/TDM interface
- I2C control for both audio converters

The operator headset jack is a separate subsystem. Keep it off this bus; see
`headset-audio.md`.

## Preferred Digital Topology

Use one shared TDM clock domain:

- CM5 `I2S0_MCLK` to AK5558VN and AK4458VN MCLK pins
- CM5 `I2S0_SCLK_TX` as shared TDM bit clock
- CM5 `I2S0_LRCK_TX` as shared TDM frame sync
- CM5 `I2S0_SDO0` to AK4458VN TDM serial audio input
- AK5558VN TDM serial audio output to CM5 `I2S0_SDI0`
- I2C bus to AK5558VN and AK4458VN control ports
- Separate reset/control GPIOs for ADC reset, DAC reset, and DAC mute

Default bring-up mode:

- CM5 provides BCLK/LRCK/MCLK
- Both AKM converters consume clocks
- PCM/TDM, 8 slots, 32-bit slot width
- Start with 48 kHz and 96 kHz sample rates before attempting 192 kHz or higher

## Candidate CM5 Pins

Based on the Radxa CM5 V2.21 pinout table.

| Function | CM5 connector | CM5 pin | Radxa signal | RK3588S ball | Board net |
| --- | --- | ---: | --- | --- | --- |
| Audio master clock | U13-A | 50 | `I2S0_MCLK` | U36 | `AUD_MCLK` |
| TDM bit clock | U13-A | 46 | `I2S0_SCLK_TX` | M42 | `AUD_BCLK` |
| TDM frame sync | U13-A | 48 | `I2S0_LRCK_TX` | P39 | `AUD_FSYNC` |
| TDM playback data | U13-A | 34 | `I2S0_SDO0` | P41 | `AUD_DAC_SDIN` |
| TDM capture data | U13-A | 54 | `I2S0_SDI0` | N42 | `AUD_ADC_SDOUT` |
| I2C control SCL | U13-A | 80 | `I2C7_SCL_M2` | AY30 | `AUD_I2C_SCL` |
| I2C control SDA | U13-A | 82 | `I2C7_SDA_M2` | AY31 | `AUD_I2C_SDA` |

Reserve optional extra I2S0 pins only if needed:

- J1 pin 75: `I2S0_LRCK_RX`
- J1 pin 79: `I2S0_SCLK_RX`
- J1 pin 44: `I2S0_SDO1`
- J1 pin 46: `I2S0_SDO2` / `I2S0_SDI3`
- J1 pin 83: `I2S0_SDO3` / `I2S0_SDI2`
- J1 pin 24: `I2S0_SDI1`

## Clocking Notes

The first revision should route CM5-generated audio clocks directly, with optional footprints for clock cleanup:

- 0-ohm links or source-selection resistors for MCLK/BCLK/FSYNC
- Optional low-jitter oscillator or clock generator footprint if later required
- Optional small series resistors near the clock source for edge-rate control

For high-end audio performance, revisit clocking before final layout. The AKM parts support high sample rates, but a clean clock tree and validated Rockchip TDM driver configuration matter more than the headline converter limit.

## Power And Analog Notes

- Main program audio inputs must be balanced.
- Main program audio outputs must be balanced.
- Use differential/balanced input conditioning before the AK5558VN.
- Use balanced line-driver/output stages after the AK4458VN.
- Keep analog and digital supplies filtered separately per AKM datasheets.
- Place local decoupling at every supply pin.
- Keep differential analog input/output routing short and symmetric.
- Avoid routing HDMI, USB3, PCIe, Ethernet, or switching regulator nodes through the converter analog area.
- Keep the ADC input network and DAC output filter/op-amp stage as their own quiet analog section.

Locked Rev A line-level target:

- `+4 dBu` nominal input and output.
- `+24 dBu` maximum input and output, for 20 dB nominal headroom.
- 10 kohm or higher is the normal output load.
- The output must remain stable and meet level into a 600 ohm compatibility/test
  load; 600 ohm is not the expected normal load.
- No mic-level mode and no phantom power in Rev A.

## Balanced Analog I/O

Required:

- 8 balanced line inputs on XLR connectors
- 8 balanced line outputs on XLR connectors
- Left-side XLR connector bank on the top panel
- Two-column vertical XLR bank like the photo reference:
  - Left column: male XLR outputs, `CH1 OUT` at top through `CH8 OUT` at bottom
  - Right column: female XLR inputs, `CH1 IN` at top through `CH8 IN` at bottom
  - Output/input channels align by row
  - No vertical label strips
  - Each XLR has its own label directly under the connector
- Input ESD/protection and RF filtering at the connector boundary
- Output short-circuit/ESD protection appropriate for exposed connectors
- Analog ground/chassis strategy that avoids hum loops

Likely input path:

- Balanced connector -> protection/RF filter -> differential buffer or instrumentation/front-end amplifier -> anti-alias filter -> AK5558VN differential input

Likely output path:

- AK4458VN differential output -> reconstruction/low-pass filter -> balanced line driver -> protection -> balanced connector

The AKM converters are differential internally, but the board still needs proper
analog front-end and line-driver circuits to behave like professional balanced
I/O in the real world.

Use the capacitor/active-balanced ProComm XLR reference as the preferred analog
starting point:

- Source folder: `/Users/viewvision/Desktop/ProComm enclosure and PCB boards`
- Local extracted note: `procomm-capacitor-xlr-audio-reference.md`
- Input concept: Neutrik `NC3FAV2` -> THAT Figure 13 RFI/ESD network ->
  `THAT1206S08-U` receiver -> recalculated level/coupling/filter network ->
  AK5558VN
- Output concept: AK4458VN -> recalculated reconstruction/gain/filter stage ->
  OPA165x -> `THAT1646S08-U` -> THAT Figure 8 RFI/phantom-fault protection ->
  Neutrik `NC3MAV`

The old capacitor XLR boards are valuable because they capture the active
balanced line-stage, RFI/protection, bipolar coupling capacitor, chassis-return,
and validation thinking. Their old PCM1861/PCM5102A converter sections are not
copied because this product uses AK5558VN and AK4458VN. All resistor/capacitor
values around the AKM converters must be recalculated from the AKM datasheets,
target line level, headroom, and analog rails.

The separate transformer XLR folder is useful only for prior XLR bank
footprint/spacing reference unless transformer isolation is intentionally
selected later.

## Software Notes

Linux has upstream ASoC codec drivers for both AK5558 and AK4458 families. Both are I2C-controlled codec drivers with TDM slot configuration hooks.

Likely device-tree direction:

- Enable the CM5/RK3588 I2S0 controller in TDM mode.
- Add AK5558VN and AK4458VN nodes on the selected I2C bus.
- Configure an audio card with 8 playback and 8 capture channels.
- Use 8 slots and 32-bit slot width for first bring-up.

Exact device-tree syntax depends on the Radxa kernel branch used for the target OS image.

## Reliability Requirement

Prior Raspberry Pi testing showed I2S audio could go silent during CPU spikes.
The Radxa CM5 has more CPU and I/O headroom for this product, but it does not
automatically eliminate Linux audio underruns, DMA starvation, bad clock
recovery, or driver xrun bugs.

Design and bring-up must prove that the 8x8 TDM program audio card survives
load spikes without muting or losing sync:

- Stress CPU, Ethernet routing, Wi-Fi AP traffic, cellular traffic, HDMI/touch,
  storage writes, and fans while recording and playing all 8 channels.
- Log ALSA xruns, kernel ASoC errors, clock loss, mute GPIO state, and channel
  map integrity.
- Prefer a fixed performance CPU governor or real-time tuned profile for the
  production audio image.
- Use larger ALSA/JACK/PipeWire buffers where latency allows.
- Give audio DMA/IRQ handling priority through kernel configuration, IRQ
  affinity, and process scheduling.
- Keep optional hardware hooks for clock-source selection, reset, and mute
  recovery so the prototype can recover cleanly if the SoC clock path proves
  fragile.

## Open Decisions

- Final sample-rate target: 48/96 kHz only, 192 kHz, or higher.
- Exact XLR connector part numbers, panel cutouts, latch-tab orientation, and
  row/column pitch.
- Input stage: active balanced THAT1206-class receiver is preferred; final AK5558
  interface values still need calculation.
- Output stage: OPA165x plus THAT1646-class active balanced driver is preferred;
  final AK4458 interface values still need calculation.
- Clocking strategy: CM5 clock master for simplicity, or external low-jitter
  audio clock source for performance and robustness if stress testing exposes
  clock/dropout problems.
