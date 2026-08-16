# Audio Control A1

## Scope

`cad/kicad/CM5-CARRIER/Audio-Control.kicad_sch` captures the two independent
CM5 audio paths:

- `I2S0` program audio crosses to AUDIO-8X8 over five LVDS pairs.
- `I2S1` serves the local ES8316 CTIA headset codec and TPA6132A2 amplifier.

The sheet is an engineering capture, not a fabrication release.

## Locked Program-Audio Transport

- LVDS driver: TI `SN65LVDS047PWR`.
- Return-data receiver: TI `SN65LVDT2DR`, including its internal termination.
- Off-board I2C isolation: NXP `PCA9517ADP,118`, with both sides at 3.3 V.
- Board headers: two Molex `87832-6423` 30-circuit Milli-Grid headers.
- Cable housings: two Molex `51110-3051` polarized 30-circuit housings.
- Crimp terminals: 60 Molex `50394-8052` terminals plus process spares.
- Pin and conductor contract: `docs/audio_tdm_harness_a1.csv`.

The five LVDS channels must use five separate 100 ohm differential twisted
pairs. Do not twist two different pairs together. The remaining conductors are
low-speed controls, logic supply, returns, and two reserved positions.

Harness cut length is not released. Measure the final carrier-to-AUDIO-8X8
stack and service path first. Keep the prototype assembly at or below 300 mm,
then verify eye margin and clock jitter at maximum TDM rate before approving a
longer assembly. Add positive lacing or a clamp within 25 mm of each housing so
field vibration and panel service loads do not reach the SMT headers.

## Locked Headset Digital Boundary

The CM5 audio GPIO domain is 3.3 V. The ES8316 digital domain is 1.8 V; no
codec digital pin connects directly to a CM5 audio net.

- NXP `PCA9306DP,118`: bidirectional 3.3 V/1.8 V headset I2C translation.
- TI `SN74AVC4T245PWR`: MCLK, BCLK, LRCK, and playback-data translation from
  the CM5 to the codec.
- TI `SN74LVC1T45DCKR`: capture-data translation from the codec to the CM5.
- ES8316 `CE`: 10 kohm pull-up to `HEADSET_1V8`; it is not tied low.

## Locked Headset Analog Path

- Dedicated TI `LP5907` 3.3 V and 1.8 V low-noise rails.
- One `0R` bond, `R900`, connects system ground to `HEADSET_AGND`.
- TI `TPA6132A2RTER` headphone driver at 0 dB hardware gain (`G0=1`, `G1=0`).
- Kycon `STX-353K7A-6N-KTTR` jack with CTIA mapping:
  pin 1 sleeve/microphone, pin 2 ring 2/ground, pin 3 ring 1/right,
  pin 4 tip/left, and pins 5/6 as the isolated detect switch.
- TI `TPD4E05U06DQAR` protects the exposed headset contacts.

## Mandatory Open Gates

1. Obtain a Kycon sample and verify terminal diameter, terminal-center
   locations, insertion-switch polarity, panel bezel, and insertion force.
2. Fabricate a plated-hole coupon for the preliminary Kycon footprint. J910 is
   route-ready for prototype capture but production-blocked by the footprint
   audit until the coupon is signed.
3. Measure output level, THD+N, noise, pop/click behavior, and microphone gain
   with the selected production headset and Logitech H111.
4. Validate I2S setup/hold margin at maximum sample rate and thermal load.
5. Complete Linux device-tree, pinctrl, clock, and pop-free sequencing tests.

## Verification

Run:

```sh
python3 cad/kicad/CM5-CARRIER/validate_audio_control.py
python3 cad/kicad/audit_footprint_readiness.py
```

The audio validator checks the exact parts, voltage-domain crossings, codec
enable, amplifier gain, CTIA map, decoupling, ground bond, and preliminary jack
geometry. The global audit must continue to report J910 as
`BLOCKED_MECHANICAL_COUPON` until physical validation is complete.
