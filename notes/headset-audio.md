# Headset Audio

## Goal

Add an integrated 3.5 mm TRRS headset jack for the operator with both
headphone output and microphone input.

This is separate from the main 8-channel program audio path:

- Main program audio: AK5558VN + AK4458VN over `I2S0` TDM
- Operator headset jack: ES8316 or similar stereo codec over `I2S1`, with
  external analog headset amplification/conditioning as needed

## Preferred Codec

Use ES8316 as the first-choice headset codec because:

- Radxa uses ES8316 for the headset jack on the CM5 IO reference board.
- Mainline Linux has an `everest,es8316` ASoC codec driver and device-tree binding.
- It supports stereo playback, microphone input, mic bias, and headphone detect.

The product should not rely on the codec pins alone as the complete headset
analog path. Treat ES8316 as the digital codec/control core, then add the
proper analog support around it:

- Headphone output amplifier / driver after the codec playback output.
- Output mute/pop suppression and ESD protection before the TRRS jack.
- Microphone bias, RF/ESD filtering, and mic preamp/PGA path before the codec
  ADC input.
- Optional analog gain setting or switchable pad after headset sample testing.

## Preferred Digital Topology

- CM5 `I2S1` to ES8316 audio interface
- I2C control bus to ES8316
- GPIO/interrupt for headphone detect
- Optional GPIO reset/power enable if needed
- 3.5 mm CTIA TRRS jack with headphone L/R, headset mic input, ground, and
  detect contacts

Keep `I2S0` dedicated to the AK5558VN/AK4458VN TDM bus.

## Dedicated Headset Power

Use a dedicated low-noise headset regulator path for the ES8316, headphone
amplifier/driver, mic bias, and mic preamp/input conditioning.

Rev A starting implementation:

- `HEADSET_3V3`: separate low-noise 3.3 V rail using a `TPS7A20`-class LDO.
- `TPA6132A2` DirectPath stereo headphone amplifier, with shutdown under
  software/hardware mute control.
- ES8316 mic bias and PGA first, with a footprint option for an external
  low-noise mic preamp only if headset measurements require more gain.

Power rules:

- Do not power the headset amplifier directly from noisy system, Wi-Fi, modem,
  fan, USB, or Ethernet rails.
- Feed the headset section from a quiet pre-regulator or filtered system rail,
  then use local low-noise LDO/regulator stages at the headset circuit.
- Put local bulk and high-frequency decoupling beside the ES8316, headphone
  amp, and mic preamp.
- Add an enable/shutdown line for the headphone amplifier so software can mute
  it during boot, shutdown, plug/unplug, and recovery events.
- Keep headset analog power physically close to the jack/codec area and away
  from switching regulator inductors and radio/modem current paths.

## Candidate CM5 Pins

Based on the Radxa CM5 V2.21 pinout. Final pins must be checked against every
other subsystem before schematic capture.

Candidate `I2S1` group:

| Function | CM5 connector | CM5 pin | Radxa signal | RK3588S ball | Board net |
| --- | --- | ---: | --- | --- | --- |
| Headset MCLK | U13-A | 100 | `SPIO_MISO_M1` as `I2S1_MCLK_M0` | AV19 | `HS_MCLK` |
| Headset BCLK | U13-A | 28 | `SPIO_MOSI_M1` as `I2S1_SCLK_TX_M0` | AW18 | `HS_BCLK` |
| Headset LRCK | U13-A | 30 | `SPIO_CLK_M1` as `I2S1_LRCK_TX_M0` | AV26 | `HS_LRCK` |
| Headset playback data | U13-A | 31 | `SPIO_CS0M1` as `I2S1_SDO1_M0` | AT15 | `HS_SDOUT_TO_CODEC` |
| Headset capture data | J1 | 40 | `GPIO4_A5` as `I2S1_SDI0_M0` | AU15 | `HS_SDIN_FROM_CODEC` |

Recommended I2C/control pins:

- J1 pin 4: `GPIO3_C0` as `I2C3_SDA_M1`
- J1 pin 6: `GPIO3_B7` as `I2C3_SCL_M1`
- J1 pin 36: reserve `HP_DET_L` for headset detect

Alternate I2C/control pins:

- J1 pin 20: `I2C3_SCL_M0`
- J1 pin 36: `I2C3_SDA_M0` only if headset detect moves elsewhere
- Other I2C options may be better after the full pin budget is complete.

## Jack And Analog Notes

- Use a CTIA/AHJ TRRS headset jack.
- Starting PCB jack is Kycon `STX-353K7A-6N-KTTR`: vertical through-hole,
  four-pole, non-threaded barrel, with switching/detect contact. Because it is
  not panel-threaded, its top-panel clearance must be derived from final PCB
  Z height and verified with a plug-insertion coupon.
- Headphone output needs a real headphone driver/amplifier sized for common
  operator headsets, not just a line-level output.
- Microphone input needs bias and input gain. Use the ES8316 mic PGA where it
  meets noise/headroom targets; add an external low-noise mic preamp if testing
  shows the headset mic level is too low or noisy.
- Add ESD protection on all exposed jack contacts.
- Route headphone L/R away from switching regulators, Ethernet magnetics, HDMI, USB3, PCIe, Wi-Fi, and modem RF sections.
- Keep mic bias and mic input filtering close to the codec.
- Add pop/click mitigation per codec datasheet recommendations.
- Add a headphone mute path or amplifier shutdown control for boot, shutdown,
  unplug/plug events, and source switching.
- Do not connect the headset mic path to the 8-channel balanced audio input
  path; it stays on the separate ES8316 headset sound card.

## Headset Candidates

The headset jack target is CTIA/AHJ TRRS:

- Tip: headphone left
- Ring 1: headphone right
- Ring 2: ground
- Sleeve: microphone

Recommended validation headsets:

| Priority | Headset | Why |
| --- | --- | --- |
| Preferred product-quality test headset | RODE `NTH-100M` | Professional over-ear headset with detachable boom mic and supplied TRRS cable. Good target for headphone-amp and mic-preamp validation. |
| Office/SIP validation headset | Jabra `Evolve 30 II` or `Evolve 40` 3.5 mm version | Jabra documents the 3.5 mm plug as CTIA, useful for SIP/voice-call testing. |
| Low-cost bench test headset | Logitech `H111` | Simple 3.5 mm headset with boom mic, useful for quick ES8316 bring-up and jack detection tests. |

Do not use USB headsets for this validation path. USB headsets bypass the
ES8316, headphone amplifier, mic preamp, and TRRS jack circuit.

## Software Notes

Linux direction:

- Add ES8316 codec node on the selected I2C bus.
- Enable the selected RK3588 `I2S1` controller.
- Add a separate sound card for the operator headset.
- Keep the main AKM TDM sound card as the 8-channel program audio card.

The ProComm application can keep the program audio card separate from the
operator headset card, matching the current software model where the headset is
independent of the 8-channel HAT audio path.

## Open Decisions

- Final `I2S1` pin group after PCIe, Wi-Fi, modem, HDMI, and GPIO conflicts are resolved.
- I2C bus selection and ES8316 address.
- Confirm Kycon `STX-353K7A-6N-KTTR` switching-contact mapping and detect
  polarity in schematic capture.
- Confirm `TPA6132A2` output level and noise with Logitech H111 and the selected
  production headset; change amplifier only if those measurements fail.
- Microphone gain/noise target and whether the ES8316 internal PGA is enough or
  an external mic preamp is required.
- Whether headset detect should interrupt the CM5 or be polled.
