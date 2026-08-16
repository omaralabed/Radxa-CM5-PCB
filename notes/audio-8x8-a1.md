# AUDIO-8X8 A1 Detailed Capture

Status: detailed schematic capture complete; PCB routing remains gated.

## Architecture

- One AK5558VN provides eight balanced ADC channels.
- One AK4458VN provides eight DAC channels.
- The CM5 carrier and AUDIO-8X8 board exchange differential MCLK, BCLK,
  frame sync, DAC data, and ADC data through Molex `87832-6423`.
- SN65LVDT2 receivers terminate the four carrier-to-audio pairs. An
  SN65LVDS1 transmitter returns ADC data.
- The baseline is 48 kHz, TDM256, eight 32-bit I2S-compatible slots,
  12.288 MHz BCLK, and 12.288 MHz MCLK.
- On the AK4458, `L1/R1` through `L4/R4` are the eight physical outputs.
  They occupy `SDTI1` in TDM256. `SDTI2` is not required for this one-device
  eight-output design and is tied low with the other unused serial inputs.

## Control And Start-Up

- AK5558 address: `0x10` with `CAD1:0=00`.
- AK4458 address: `0x11` with `CAD1:0=01`.
- Keep the DAC muted and all output relays de-energized through power-up.
- Verify rails, MCLK, BCLK, LRCK, both I2C addresses, and register readback
  before releasing converter reset.
- Release the eight output relays only after stable zero data has been sent
  and the DAC soft mute ramp has completed.
- Reassert mute and drop the relays before changing clocks, TDM format, or
  sampling speed.

The exact baseline values are in
`docs/akm_clock_mode_matrix_a1.csv`. Firmware must read back each write and
must treat a mismatch as a latched audio fault.

## Input Path

Each input uses THAT1206, OPA1652, RF/ESD protection, bipolar AC coupling,
and the AK5558 differential input. The +4 dBu nominal level maps to about
`-21.03 dBFS`. The +24 dBu maximum maps to `2.487 Vpp` differential, about
`1.03 dB` below the AK5558 typical `2.8 Vpp` full-scale value.

## Output Path

Each output uses the AK4458 reconstruction network, OPA1652 gain stage,
THAT1646 balanced driver, fail-silent TQ2 relay, ferrites, and protection.
The OPA feedback pair is `21.5k/10k` at 0.1 percent. Calculated full-scale
output is about +25.03 dBu into 600 ohm. The documented adverse component
corner remains +24.23 dBu, leaving 0.23 dB of calculated margin. Production
firmware should apply about 1 dB digital attenuation for a calibrated
+24 dBu operating ceiling.

The detailed calculations are in `docs/audio_8x8_level_budget_a1.csv`.

## Power And Grounding

- `AUDIO_12V_IN` enters through the protected interboard connector.
- TRACO `TRI 20-1223` generates the isolated bipolar line-stage supply.
- TPS62913 creates the low-noise preregulator rail.
- Separate LT3045 LDOs create `ADC_5V_A` and `DAC_5V_A`.
- TPS7A2033 creates `AKM_3V3_D`.
- `GND` and `AGND` meet once through the entry zero-ohm star link.
- XLR shells use `CHASSIS_GND`; the functional/chassis bond uses the
  documented 1 Mohm plus Vishay VY1 Y-capacitor network.

## Routing Release Gates

Routing is blocked until all of these are closed:

1. AK5558 exposed-pad, via, paste, and stencil coupon approved.
2. AK4458 exposed-pad, via, paste, and stencil coupon approved.
3. Panasonic TQ2 relay pad and insertion coupon approved for K501-K508.
4. Controlled-impedance TDM harness stack-up and cable sample approved.
5. 600-ohm output, +24 dBu input, crosstalk, noise, THD+N, mute, hot-plug,
   source-transfer, and thermal chamber tests pass on the first article.

## Primary Sources

- AK5558VN datasheet: https://www.akm-semi.com/pdf-0f/ak5558vn.pdf
- AK4458VN datasheet: https://www.akm-semi.com/pdf-c1/ak4458vn.pdf
- THAT1646 datasheet: https://thatcorp.com/datashts/THAT_1606-1646_Datasheet.pdf
- Vishay VY1 safety capacitor datasheet: https://www.vishay.com/docs/28537/vy1series.pdf
