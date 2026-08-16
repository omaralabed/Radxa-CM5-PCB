# ProComm Capacitor XLR Audio Reference

## Source Folder

Reference source:

`/Users/viewvision/Desktop/ProComm enclosure and PCB boards`

Use this folder for the active capacitor-coupled balanced XLR electrical
reference. This is different from the transformer XLR board in
`/Users/viewvision/Desktop/2026/ProComm PCB XLRs + Transformer`.

## Source Files Checked

- `ADVANCED_SCHEMATIC_WORK/XLR_INPUT_README.md`
- `ADVANCED_SCHEMATIC_WORK/XLR_OUTPUT_README.md`
- `ADVANCED_SCHEMATIC_WORK/ProComm_XLR_Input_5CH.kicad_sch`
- `ADVANCED_SCHEMATIC_WORK/ProComm_XLR_Output_5CH.kicad_sch`
- `ADVANCED_SCHEMATIC_WORK/ProComm_XLR_Input_5CH_BOM.csv`
- `ADVANCED_SCHEMATIC_WORK/ProComm_XLR_Output_5CH_BOM.csv`
- `PCB_SOURCE/XLR_INPUT_5CH/README.md`
- `PCB_SOURCE/XLR_OUTPUT_5CH/README.md`

## What This Reference Is

This is the capacitor/active-balanced ProComm audio direction:

- No audio transformers in the XLR signal path
- Balanced line inputs with THAT1206 receivers
- Balanced line outputs with THAT1646 drivers
- Capacitor-coupled/filter/protection networks around the line stages
- XLR pin 1 / shell handled as chassis, with the system chassis-to-circuit
  ground bond reviewed at the power-entry/system level

For the Radxa CM5 product, use the analog input/output protection and line-stage
ideas from this folder. Do not copy the old PCM1861/PCM5102A digital converter
portion because the Radxa design uses AK5558VN and AK4458VN over TDM.

## Input Channel Reference

Old ProComm input chain:

```text
NC3FAV2 -> THAT Figure 13 RFI/ESD network -> THAT1206S08-U
        -> level/AC-coupling/anti-alias network -> PCM1861DBTR
```

Per-channel reference parts/values from channel 1:

- XLR input: Neutrik `NC3FAV2`
- Balanced receiver: THAT `THAT1206S08-U`, -6 dB
- Series/input resistors: `100R`, `100R`
- RFI capacitors: `470pF C0G`, `470pF C0G`, `100pF C0G`
- RFI/protection resistor: `4.7k`
- Signal diodes: four Diodes Inc. `1N4148W-7-F`
- Clamp zeners: two Diodes Inc. `BZT52C12-7-F`, 12 V
- Receiver rail/local capacitors: `220uF 6.3V`, `100nF 50V`, `100nF 50V`
- Level network: `2.80k 0.1%` series and `1.21k 0.1%` shunt
- AC-coupling capacitor: Nichicon `UES1H100MPM`, `10uF 50V BI-POLAR`
- ADC isolation resistor: `100R 1%`
- Final anti-alias capacitor: `1.0nF C0G`

Old calculation target:

- +24 dBu at XLR = 12.283 Vrms differential
- THAT1206 at -6 dB = 6.156 Vrms single-ended
- The old PCM1861 network targeted about 1.774 Vrms at the ADC pin, around
  -1.47 dBFS relative to PCM1861's typical 2.1 Vrms full-scale input
- +4 dBu mapped around -21.47 dBFS

Radxa adaptation:

- Keep the THAT1206 input receiver/protection concept as the preferred starting
  point for balanced line inputs.
- Recalculate the level network, AC-coupling, biasing, and anti-alias filter
  for AK5558VN input full-scale, input structure, common-mode/bias
  requirements, and chosen analog rails.
- Do not copy the PCM1861 hardware-control or unused-channel logic into the
  AK5558 design.

## Output Channel Reference

Old ProComm output chain:

```text
PCM5102APWR -> 470R / 2.2nF reconstruction network -> OPA165x gain stage
             -> THAT1646S08-U -> THAT Figure 8 RFI/phantom-fault protection
             -> NC3MAV
```

Per-channel reference parts/values from channel 1:

- DAC source in old board: TI `PCM5102APWR`
- Reconstruction filter: `470R 1%` and `2.2nF C0G`
- Gain stage: TI `OPA1654AIDR` / `OPA1652AIDR`
- Gain resistors: `10.0k 0.1%` and `4.70k 0.1%`
- Balanced driver: THAT `THAT1646S08-U`
- Sense capacitors: two Nichicon `UES1H100MPM`, `10uF 50V BI-POLAR`
- Driver rail decoupling: `100nF 50V` on each rail
- Rail clamps: four Diodes Inc. `S1G-13-F`, 1 A / 400 V SMA
- Output ferrites: Murata `BLM21PG221SN1D`, `220R@100MHz`
- RFI returns to chassis: two KEMET `C0603C101J1GACTU`, `100pF 100V C0G 5%`
- XLR output: Neutrik `NC3MAV`

Old output target:

- PCM5102A full-scale: 2.1 Vrms
- OPA165x non-inverting gain: `1 + 4.70k / 10.0k = 1.470`
- THAT1646 balanced gain: 2.000 into high impedance
- Nominal high-impedance differential full-scale output: about 6.174 Vrms,
  approximately +18.03 dBu
- Into 600 ohm load: about 5.682 Vrms, approximately +17.30 dBu

Radxa adaptation:

- Keep the OPA165x plus THAT1646 active balanced output/protection concept as
  the preferred starting point for balanced line outputs.
- Recalculate the DAC reconstruction/gain network for AK4458VN output level,
  output structure, full-scale voltage, target headroom, and chosen analog
  rails.
- Keep pop/mute behavior, rail-good gating, and output fault recovery as
  first-class release tests.
- Do not copy the PCM5102A BCK-PLL/sample-rate constraints into the AK4458VN
  design.

## Radxa Direction

For the Radxa CM5 8-in / 8-out board:

- Use AK5558VN and AK4458VN as the program ADC/DAC over TDM.
- Use the capacitor/active-balanced ProComm XLR folder as the analog line-stage
  reference.
- Use the transformer XLR folder only for prior XLR footprint/spacing reference
  unless transformers are intentionally selected later.
- Recalculate all analog gains, filters, coupling capacitors, headroom, and
  protection limits for the AKM converters and final line-level target.
- Validate noise, THD+N, frequency response, CMRR, crosstalk, clipping,
  hot-plug behavior, phantom-fault survival, and source-switchover pops on
  hardware.
