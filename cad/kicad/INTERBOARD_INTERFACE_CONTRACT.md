# Inter-Board Interface Contract

## Status

This is the A0 schematic-capture contract for the three-board architecture.
Connector families marked TBD must not receive a production footprint until
signal-integrity, vibration, current, keying, and cable-bend checks are complete.

## PWR-SELECT To CM5-CARRIER Raw Power

`PWR-SELECT J301` mates with `CM5-CARRIER J101` using a four-circuit Micro-Fit
3.0 harness. Two contacts are paralleled per polarity.

| Pin | Net |
| ---: | --- |
| 1 | `RAW_OUT_LOAD` |
| 2 | `RAW_OUT_LOAD` |
| 3 | `GND` |
| 4 | `GND` |

The connector, contacts, wire gauge, copper and temperature rise must be
validated at 15 A. Do not assume the nominal per-contact rating survives the
finished enclosure temperature and vibration environment.

## PWR-SELECT To CM5-CARRIER Status

`PWR-SELECT J401` mates with `CM5-CARRIER J102` using an eight-circuit
PicoBlade harness.

| Pin | Net | Meaning |
| ---: | --- | --- |
| 1 | `GND` | Signal reference |
| 2 | `CH_24V_N` | Primary channel selected, active low |
| 3 | `CH_BAT_N` | Backup channel selected, active low |
| 4 | `VALID_24V_N` | Primary source valid, active low |
| 5 | `VALID_BAT_N` | Selected backup valid, active low |
| 6 | `BAT_LOW_N` | Backup low warning, active low |
| 7 | `VALID_DTAP_N` | LEMO/D-Tap valid, active low |
| 8 | `VALID_GOLD_N` | Gold Mount valid, active low |

All status outputs are open drain and receive 3.3 V pull-ups on CM5-CARRIER.

## PWR-SELECT To CM5-CARRIER Power Telemetry

`PWR-SELECT J402` mates with `CM5-CARRIER J103` using a six-circuit
PicoBlade harness. Net names change at the connector to reflect board-local
ownership; pin order is identical.

| Pin | PWR-SELECT net | CM5-CARRIER net | Meaning |
| ---: | --- | --- | --- |
| 1 | `MON_3V3` | `LOGIC_3V3` | Carrier-supplied monitor power |
| 2 | `GND` | `GND` | Signal reference |
| 3 | `PWR_MON_SDA` | `CTRL_I2C_SDA` | I2C data |
| 4 | `PWR_MON_SCL` | `CTRL_I2C_SCL` | I2C clock |
| 5 | `PWR_MON_ALERT_N` | `PWR_MON_ALERT_N` | Wired-OR active-low alert |
| 6 | `GND` | `GND` | Additional ground return |

The carrier owns all 3.3 V pull-ups. INA228 addresses are `0x40` primary,
`0x41` selected backup, and `0x44` delivered raw load.

## CM5-CARRIER To AUDIO-8X8 TDM And Control

`CM5-CARRIER J201` mates with `AUDIO-8X8 J101`. The production connector is
TBD. Use a short keyed shielded harness or board-to-board connector with 100 ohm
differential-pair support and positive retention.

| Pins | Nets | Direction at carrier |
| --- | --- | --- |
| 1, 2 | `AUD_MCLK_P/N` | Output |
| 3, 4 | `GND`, `GND` | Reference |
| 5, 6 | `AUD_BCLK_P/N` | Output |
| 7, 8 | `AUD_FSYNC_P/N` | Output |
| 9, 10 | `GND`, `GND` | Reference |
| 11, 12 | `AUD_DAC_SDIN_P/N` | Output |
| 13, 14 | `AUD_ADC_SDOUT_P/N` | Input |
| 15, 16 | `GND`, `GND` | Reference |
| 17, 18 | `AUD_I2C_SCL`, `AUD_I2C_SDA` | Bidirectional control |
| 19, 20 | `AUD_ADC_RST_N`, `AUD_DAC_RST_N` | Output |
| 21, 22 | `AUD_DAC_MUTE_N`, `AUD_IRQ_N` | Output, input |
| 23, 24 | `AUDIO_PRESENT_N`, `AUDIO_ENABLE` | Input, output |
| 25, 26 | `LOGIC_3V3`, `GND` | Low-current interface reference only |
| 27, 28 | `TDM_SPARE_1`, `TDM_SPARE_2` | Reserved |
| 29, 30 | `GND`, `GND` | Reference |

The five TDM signals use line drivers/receivers at the connectors. Do not route
raw single-ended CM5 I2S clocks over a long unshielded harness.

## CM5-CARRIER To AUDIO-8X8 Power

`CM5-CARRIER J202` mates with `AUDIO-8X8 J102` using a separate four-circuit
Micro-Fit 3.0 harness.

| Pin | Net |
| ---: | --- |
| 1 | `AUDIO_12V` |
| 2 | `AUDIO_12V` |
| 3 | `GND` |
| 4 | `GND` |

Audio power must not share conductors with fans, display, Wi-Fi, modem or
Ethernet power. Local AUDIO-8X8 conversion produces the clean bipolar and AKM
rails.

## Carrier Fan Connectors

All fan headers use the standard four-wire order below. Exact connector family
is TBD and must be keyed for field vibration.

| Pin | Function |
| ---: | --- |
| 1 | `GND` |
| 2 | Locally protected 12 V fan rail |
| 3 | Tachometer output |
| 4 | PWM control input |

Assignments:

| Connector | Fan | Direction |
| --- | --- | --- |
| `J401` | CM5 fan | `CPU_FAN_12V`; local heatsink airflow |
| `J402` | Modem fan | `MODEM_FAN_12V`; internal flow across modem heatsink/spreader |
| `J403` | Delta `THA0412AD-TZW3` | `INTAKE_FAN_12V`; filtered intake, air into case |
| `J404` | Delta `THA0412AD-TZW3` | `EXHAUST_FAN_12V`; exhaust, air out of case |

`J403` and `J404` require permanent harness and panel-underlay labels. Their
PWM/tach channels remain independent so pressure balance can be tuned with the
CM5 mesh and filter loading included.
The EMC2305 controls both enclosure channels at 1.000 kHz. Hardware pullups
command full speed if the controller is absent, unpowered, or disconnected.
