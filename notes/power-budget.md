# Preliminary Power Budget

## Purpose

First-pass engineering power budget for the Radxa CM5 ProComm carrier. This is
not a production rating yet. It is meant to verify margin against the locked
24 V production PSU and to size the first regulator tree.

## Measurement Status

No physical bench measurements have been taken yet for the Radxa CM5 build.
The numbers below are engineering estimates from module requirements,
datasheets, product listings, and design margin.

Treat these as sizing targets for the prototype schematic, not as proven field
measurements. The final release budget must be replaced with measured current
for the CM5, radios, display, audio rails, fans, and regulator losses.

Current status by load group:

| Load group | Status | Needed measurement |
| --- | --- | --- |
| CM5 | Estimated | Measure idle, SIP/audio load, CPU/GPU/NPU stress, boot surge, shutdown. |
| 4 Ethernet ports | Estimated | Measure all four ports linked at 1 GbE with traffic. |
| Wi-Fi AP | Vendor-based estimate | Measure AP mode with about 25 associated clients and active traffic. |
| Cellular modem | Vendor/use-case estimate | Measure attach/register burst, weak-signal transmit, and sustained uplink. |
| HDMI touchscreen | User-provided 12 V / 25 W rating | Measure selected 15.6-inch display at max brightness, startup, and with touch active. |
| AK5558 / AK4458 audio | Estimated | Measure converters plus analog line stages at nominal and max line level. |
| ES8316 headset | Estimated | Measure codec, headphone amp, mic bias/preamp, and plug/unplug events. |
| Fans | Estimated | Measure startup/inrush, full-speed current, and PWM operating current. |
| Regulator losses | Estimate allowance | Measure efficiency and temperature per rail at 24 V and battery input. |

## Current Answer

The locked production PSU is the MEAN WELL `RPS-400-24-C`, used as a 24 V /
10.5 A / 252 W convection-rated supply unless forced-air PSU cooling is
intentionally designed and validated.

- Estimated continuous worst-case load after conversion loss: about 151.7 W.
- Locked 252 W PSU margin at that point: about 100.3 W, or about 40 percent.
- Estimated all-load transient case after conversion loss: about 184.2 W.
- Locked 252 W PSU transient margin: about 67.8 W.

Recommendation: keep `RPS-400-24-C` as the production baseline. The previous
120 W Bel/CUI supply is now only a prior candidate/prototype reference and is
not the production target.

## Assumptions

- Locked production PSU: MEAN WELL `RPS-400-24-C`, 24 V, 10.5 A, 252 W
  convection-rated design basis.
- Power architecture: same ProComm source-selection baseline, with Radxa-specific
  downstream rails.
- Conversion/source-selection loss allowance: about 10 percent at high load
  until exact regulators, MOSFETs, inductor losses, and thermals are selected.
- Cellular modem rail: dedicated 3.8 V-class rail sized around 5 A for 5G burst
  margin.
- Wi-Fi AP rail: separate 3.3 V rail sized at least 3 A.
- Display model is locked to JUNEBOX / DTM MALL `B0GK5X95D9`; its supplied
  rating is 12 V / 25 W, or 2.08 A nominal. Keep a 12 V / 2.5 A branch and
  verify startup and full-brightness current on the received sample.
- CPU cooling is locked to the Radxa `5540A` plus Delta
  `FFB0412EN-00Y2E`. The modem fan remains to be selected; the two enclosure
  fans are locked to Delta `THA0412AD-TZW3`, each 0.43 A nominal / 0.52 A
  maximum with 0.60 A label current.

## Load Budget Table

| Load group | Rail / source | Typical W | Continuous design W | Peak / transient W | Confidence | Notes |
| --- | --- | ---: | ---: | ---: | --- | --- |
| Radxa CM5 module, eMMC, CPU/GPU/NPU | 5.15 V system | 12.0 | 25.0 | 30.0 | Estimate | Must verify on selected CM5 SKU and OS load. |
| Carrier logic, clocks, sensors, LEDs, GPIO, RTC | 5.15 V / 3.3 V / 1.8 V | 2.0 | 4.0 | 5.0 | Estimate | Includes housekeeping, not radios/audio power. |
| Main 8x8 audio: AK5558VN, AK4458VN, balanced line stages | clean audio rails | 5.0 | 10.0 | 12.0 | Estimate | Final +/- analog rail current depends on line level and load. |
| ES8316 headset codec, headphone amp, mic bias/preamp | dedicated low-noise headset regulator | 0.8 | 2.0 | 3.0 | Estimate | Separate headset sound card with real headphone drive, mic input conditioning, and its own clean regulator path. |
| Native WAN1 Ethernet magnetics/LEDs/support | Ethernet rails | 1.0 | 1.5 | 2.0 | Estimate | Depends on final PHY/magnetics implementation. |
| PCIe switch plus three LAN7430 1 GbE controllers | `NET_3V3` / `PCIE_1V0` | 4.5 | 7.0 | 8.0 | Medium | Includes PI7C9X2G608GP, three controllers, clocks, magnetics, and LEDs. |
| Wi-Fi AP module, AW7915-NP1 4T4R | dedicated 3.3 V | 7.0 | 9.0 | 10.0 | High | Vendor lists 4-8 W average, 9 W max, 3.3 V 3 A recommended. |
| Cellular modem, SIM8260G-M2-class | dedicated 3.8 V-class | 6.0 | 12.0 | 20.0 | Medium | Rail sized for registration/transmit bursts and ProComm 5 A buck concept. |
| 15.6-inch JUNEBOX HDMI touchscreen and USB touch | 12 V display/touch rail | 20.0 | 25.0 | 30.0 | User rating | Rated 12 V / 25 W (2.08 A nominal); 30 W peak budget matches the locked 12 V / 2.5 A branch. |
| USB service/accessory power reserve | 5 V USB rail | 2.0 | 5.0 | 8.0 | Estimate | Final external USB current limits must be chosen. |
| CM5 CPU fan, Delta FFB0412EN-00Y2E | protected `FAN_CPU_12V` | 8.7 | 21.0 | 21.0 | High | Locked 12 V fan; 17.4 W nominal at full rated operation and 21 W datasheet maximum input. Typical column assumes reduced PWM duty. |
| Modem fan, two enclosure fans, and fan drivers | protected `FAN_AUX_12V` branch | 5.0 | 18.0 | 20.0 | Medium | Two locked THA0412AD-TZW3 fans consume 10.32 W nominal / 12.48 W maximum as a pair; allowance includes the still-TBD modem fan and controller. |
| Two YIS LS102W warm-white panel lights and E-Switch CS touch control | `NIGHT_LIGHT_12V` | 0.6 | 0.7 | 0.7 | High | Two 0.25 W 12 V courtesy lights plus low-current touch electronics on a 0.25 A fused branch. |
| Miscellaneous margin: buttons, status, losses not otherwise captured | mixed | 0.5 | 1.5 | 2.5 | Estimate | Keep until schematic/BOM is closed. |
| Subtotal regulated loads | mixed | 75.1 | 141.7 | 172.2 | Estimate | Before conversion/source-selection losses. |
| Conversion/source-selector thermal loss allowance | regulators / MOSFETs | 5.0 | 10.0 | 12.0 | Estimate | Replace with calculated efficiency by rail later. |
| Estimated total from 24 V source | 24 V source | 80.1 | 151.7 | 184.2 | Estimate | Fits locked 252 W convection-rated production PSU; peak exceeds old 120 W and 150 W candidates. |

## PSU Check

| Item | Value |
| --- | ---: |
| Locked production PSU output | 24 V x 10.5 A = 252 W convection-rated |
| Estimated continuous design demand | 151.7 W |
| Estimated continuous 24 V current | 6.32 A |
| Continuous spare margin | 100.3 W |
| Continuous spare margin percent | 39.8 percent |
| Estimated all-load transient demand | 184.2 W |
| Estimated transient 24 V current | 7.68 A |
| Transient spare margin vs 252 W | 67.8 W |

Interpretation:

- The locked 252 W convection-rated PSU gives comfortable electrical margin
  against the present estimates.
- The old 120 W candidate is not sufficient for the all-load transient estimate.
- The biggest swing items are the HDMI touchscreen, cellular modem burst load,
  USB accessory-current policy, audio analog rail current, and fan choice.
- A 150 W supply is below the present all-load transient estimate, and
  USB ports capable of powering external gear would increase the requirement.
- For the current all-load estimate, 200 W is the minimum comfortable production
  class, and a compact 252 W convection-rated supply gives better field margin.

## Production PSU Target

Preferred production sizing:

| PSU class | Output | Margin at 151.7 W continuous | Margin at 184.2 W burst | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Old 120 W candidate | 120 W | -31.7 W | -64.2 W | Inadequate for continuous or transient operation. |
| 150 W class | 150 W | -1.7 W | -34.2 W | Inadequate for continuous and transient operation. |
| Minimum production class | 200 W | 48.3 W / 24.2 percent | 15.8 W | Conditional on measured loads and thermal testing. |
| Preferred production target | 252 W | 100.3 W / 39.8 percent | 67.8 W | Preferred field and transient margin. |

Current recommended compact production candidate: MEAN WELL `RPS-400-24-C`,
used as a 252 W convection-rated supply unless forced-air PSU cooling is
intentionally designed and validated. TDK-Lambda `CUS200M-24/A` remains a good
200 W alternate. Use TDK-Lambda `CUS200M-24` only if the enclosure design adds a
proper finger-safe mains/service barrier around the open-frame supply.

## Source Current Check

These are first-pass source currents using the estimated total-from-source
values above.

| Source | Nominal voltage | Continuous current at 151.7 W | Transient current at 184.2 W | Check |
| --- | ---: | ---: | ---: | --- |
| 24 V PSU | 24.0 V | 6.32 A | 7.68 A | Fits locked 10.5 A / 252 W production PSU with margin. |
| D-Tap / LEMO low end | 13.0 V | 11.67 A | 14.17 A | Use 15 A LEMO 1B connector/path; transient margin is limited and the source/cable must be validated. |
| Gold Mount nominal | 14.1 V | 10.76 A | 13.06 A | Continuous case fits the 12 A rating nominally; transient uses validated peak capability. |
| Gold Mount high/full | 16.8 V | 9.03 A | 10.96 A | Easier current case, still needs MOSFET/fuse review. |

## Gold Mount Battery Backup Estimate

Locked planning battery: Anton/Bauer Dionic XT 90 Gold Mount, SKU `8675-0125`.
Anton/Bauer lists 99 Wh capacity, 14.1 V nominal voltage, and 12 A continuous
maximum current. The product literature also advertises a 20 A peak capability;
use that only for validated short transients, not as a continuous design rating.

First-order runtime uses:

```text
runtime_minutes = usable_battery_Wh / system_input_W x 60
```

The conservative planning column uses 80 percent of the 99 Wh nameplate, or
79.2 Wh. That 20 percent reserve is an engineering allowance for shutdown
reserve, battery aging, temperature, high-rate discharge, BMS cutoff, and
converter/path losses not captured perfectly by the preliminary load model.

| System case | Input power | Current at 14.1 V nominal | 99 Wh ideal runtime | 79.2 Wh planning runtime |
| --- | ---: | ---: | ---: | ---: |
| Typical operation | 80.1 W | 5.68 A | 74.2 min | 59.3 min |
| Continuous design load | 151.7 W | 10.76 A | 39.2 min | 31.3 min |
| All-load transient held continuously for comparison only | 184.2 W | 13.06 A | 32.2 min | 25.8 min |

The 151.7 W continuous case reaches about 13.37 A at the present 11.35 V Gold
Mount falling-UV target, above the battery's 12 A continuous rating. The
184.2 W transient reaches about 16.23 A at that voltage. Backup firmware must
therefore shed display/USB load or reduce CPU and fan demand near end of
discharge; the transient also depends on validated short-duration peak
capability.

Use **about 31 minutes** as the preliminary full-feature backup-runtime target
for a healthy, fully charged XT 90. The production shutdown warning and load
shedding thresholds must be set from measured pack voltage, current, remaining
runtime telemetry, temperature, and repeated end-of-discharge tests.

## A1 Regulator Capture

The calculated A1 regulator tree is now captured in
`cad/kicad/CM5-CARRIER/Power-Regulators-A1.kicad_sch`. Exact selected parts and
starting values are documented in `notes/power-regulators-a1.md`; the exported
BOM and machine-checkable calculations are in
`docs/power_regulator_bom_a1.csv` and
`docs/power_regulator_calculations_a1.csv`.

The values below are locked engineering starting values for prototype capture,
not measured production limits. Controlled footprints, layout, Bode response,
thermal behavior, radio bursts, inrush, and no-blink transfer still require
bench validation.

## Regulator Sizing Targets

| Rail | First sizing target | Main loads | Notes |
| --- | ---: | --- | --- |
| `SYS_5V15` | 5.15 V / 12 A | CM5, carrier logic, selected 5 V loads | Captured with `LM5146RGYR`, external MOSFETs, and a 3.3 uH / 28.6 A inductor. |
| `AUX_12V` | 12 V / 8 A minimum revision target | Display, locked CPU fan, enclosure/modem fans, audio handoff, and night lights | Revised capture uses an 8 A stage target and about 8.33 A output limit; losses, compensation, copper, and thermal behavior still require calculation and bench qualification before routing. |
| `WIFI_3V3` | 3.3 V / 4 A | AW7915-NP1 4T4R AP module | Separate `LM61440` rail with controlled load switch and local bulk. |
| `MODEM_3V8` | 3.8 V / 6 A converter | SIM8260G-M2-class M.2 modem | `LM61460` plus `TPS25982`; 5 A minimum usable load and at least 1000 uF initial local bulk. |
| `NET_3V3` / `PCIE_1V0` | 3.3 V / 4 A and 1.0 V / 2 A | PI7C9X2G608GP and three LAN7430 controllers | Separate from Wi-Fi; obey PCIe-switch power sequence and reset timing. |
| `AUDIO_BIPOLAR` / `AKM_5V_A` | +/-15 V, 20 W class; clean 5 V | AKM converters, THAT/OPA stages | `TRI 20-1223` plus separate `TPS7A20` clean ADC, DAC, and AKM rails. |
| `HEADSET_3V3` | 3.3 V / 1 A plus clean 1.8 V | ES8316, headphone amplifier, mic bias/preamp | `TPS62913` pre-rail plus `TPS7A2018` local LDO. |
| `DISPLAY_12V` | 12 V / 2.5 A branch | 15.6-inch JUNEBOX HDMI touchscreen and USB touch | Simple fused harness branch from `AUX_12V`; no dedicated display eFuse/current limiter. Rated load is 25 W / 2.08 A; verify startup and max-brightness current. |
| `NIGHT_LIGHT_12V` | 12 V / 0.25 A protected branch | Two YIS LS102W warm-white panel lights and E-Switch CS touch control | About 0.6 W expected; included inside the existing miscellaneous-margin allocation. |
| `FAN_CPU_12V` | 12 V / 3 A branch | Delta `FFB0412EN-00Y2E` | Independently protected branch from `AUX_12V`; 25 kHz PWM and tach feedback. |
| `FAN_AUX_12V` | 12 V / 3 A branch | Modem fan and two THA0412AD-TZW3 enclosure fans | Separate 3 A time-lag source fuse plus 1 A local protection per fan; finalize modem allowance after selection. |

## Regulator Tree From 24 V

First-pass rail tree from the protected raw DC output. This is the working tree
for schematic planning and will be recalculated once final regulator ICs are
selected.

```text
24V_PSU / protected raw DC
  -> SYS_5V15 high-current buck
       -> Radxa CM5 5 V input
       -> controlled downstream 5 V service/USB loads
       -> local quiet LDOs where 5 V-derived analog/control rails are acceptable
  -> LOGIC_3V3 buck, 3.3 V / 3 A
       -> carrier logic, level shifters, sensors, LEDs, I/O control
       -> do not share as the main Wi-Fi AP supply
  -> LOGIC_1V8 point-of-load regulator, 1.8 V / 1.5 A
       -> I/O reference, codec/control, PCIe/Ethernet support as required
  -> WIFI_3V3 dedicated LM61440, 3.3 V / 4 A
       -> Mini PCIe AW7915-NP1 Wi-Fi AP module only, with local bulk capacitance
  -> MODEM_3V8 dedicated LM61460, 3.8 V / 6 A
       -> TPS25982 -> M.2 B-Key modem, with at least 1000 uF initial local bulk
  -> NET_3V3 dedicated LM61440, 3.3 V / 4 A
       -> three LAN7430 controllers and PCIe-switch I/O
       -> PCIE_1V0 point-of-load buck, 1.0 V / 2 A
  -> AUX_12V LM5176 buck-boost, revised 12 V / 8 A minimum target
       -> fused DISPLAY_12V harness branch, 12 V / 2.5 A
       -> fused NIGHT_LIGHT_12V hardware branch, 12 V / 0.25 A
       -> protected FAN_CPU_12V branch, 12 V / 3 A
       -> protected FAN_AUX_12V branch, 12 V / 3 A
  -> AUDIO_BIPOLAR isolated +/-15 V plus filtered clean AKM rails
       -> AK5558VN, AK4458VN, OPA165x/THAT1206/THAT1646 line stages
  -> HEADSET clean regulators
       -> ES8316, headphone amp, mic bias, mic preamp/input conditioning
```

| Rail | Suggested first target | Reason |
| --- | ---: | --- |
| `SYS_5V15` | 5.15 V / 12 A continuous | CM5 plus controlled 5 V support loads, with headroom for CPU/GPU/NPU stress. |
| `LOGIC_3V3` | 3.3 V / 3 A continuous | Carrier logic and low-power peripherals only; keep radios on separate rails. |
| `LOGIC_1V8` | 1.8 V / 1.5 A continuous | Control, reference, codec, PCIe/Ethernet support rails as selected. |
| `AUX_12V` | 12 V / 8 A minimum revision target | Buck-boost backbone for display, fan, audio, and night-light branches during backup transfer. Recalculate and bench-qualify the revised A1 power stage. |
| `WIFI_3V3` | 3.3 V / 4 A | Separate AP rail; radio transmit load must not pull down system logic. |
| `MODEM_3V8` | 3.8 V / 6 A converter | Separate cellular rail; 5 A minimum usable load for registration/transmit bursts. |
| `NET_3V3` | 3.3 V / 4 A | PCIe switch I/O and three LAN7430 controllers. |
| `PCIE_1V0` | 1.0 V / 2 A | PCIe switch core with required sequencing. |
| `DISPLAY_12V` | 12 V / 2.5 A branch | Locked 25 W touchscreen; verify startup and maximum-brightness current. |
| `NIGHT_LIGHT_12V` | 12 V / 0.25 A branch | Two 0.25 W warm-white courtesy lights plus touch control; expected load is covered by miscellaneous margin. |
| `FAN_CPU_12V` | 12 V / 3 A branch | Locked Delta CPU fan with independent protection. |
| `FAN_AUX_12V` | 12 V / 3 A branch | Modem fan and two THA0412AD-TZW3 enclosure fans; verify startup current and high-temperature fuse derating. |
| `AUDIO_BIPOLAR` | +/-15 V, 20 W class | Locked +24 dBu line-stage headroom; validate current and noise. |
| `HEADSET_3V3` | Clean 3.3 V, exact current TBD | Separate ES8316/headphone/mic path, isolated from radio/fan noise. |

## Open Items That Can Move The Answer

- Measured 15.6-inch JUNEBOX HDMI touchscreen startup and full-brightness power
  against its supplied 12 V / 25 W rating.
- Measured Delta CPU-fan startup/full-speed current and exact modem-fan current.
- Actual Radxa CM5 current under CPU/GPU/NPU load with the production OS image.
- Cellular modem average and peak current during 5G registration and transmit.
- Wi-Fi AP current with about 25 clients and enclosure closed.
- Whether external USB ports are limited to service/touch only or user-power
  capable.
- Final measured audio-stage current and filter values at the locked +24 dBu
  maximum level.
- Actual regulator efficiencies at 24 V input and at battery input voltages.
- Measured Dionic XT 90 usable energy and runtime at room, hot, and cold
  temperature, including aged-pack and end-of-discharge transient tests.
- Protected raw-DC and local rail hold-up capacitance needed for no-blink
  transfer from primary to backup.

## Design Rule From This Budget

Do not allow radio load spikes to pull down the CM5/system or audio rails:

- Cellular modem gets its own 3.8 V-class high-current rail.
- Wi-Fi AP gets its own 3.3 V rail.
- Audio rails get clean filtering and physical separation.
- Source selector and 24 V harness are sized for worst-case current and thermal
  rise, even if normal operation is far below peak.
- Source selector, hold-up capacitance, and downstream regulators must maintain
  critical rails during primary-to-backup and backup-to-primary transfer.

## Source Notes

- Radxa CM5 official docs list the RK3588S/RK3588S2 SoC, CPU/GPU/NPU blocks, and
  eMMC integration.
- Radxa CM5 hardware interface docs list the CM5 IO power approach, HDMI,
  Ethernet, USB, M.2, GPIO, and headset support.
- MEAN WELL / Newark / DigiKey list `RPS-400-24-C` as a 24 V, 10.5 A, 252 W
  convection-rated supply, with higher forced-air rating if airflow is designed
  and validated.
- DigiKey lists the old `VOF-120C-24-CNF` candidate as a 24 V / 5 A / 120 W
  AC/DC converter with 95 percent efficiency, 85-264 Vac input, and NRND status.
- AsiaRF lists `AW7915-NP1` as 3.3 V, 3 A recommended, 4-8 W average, 9 W max.
- SIMCom lists `SIM8260G-M2` as M.2, 52 x 30 x 2.3 mm, 3.135-4.4 V supply, USB
  and PCIe capable, with 1.8 V / 2.95 V SIM support.
- Microchip lists LAN7430 as an in-production, single-3.3-V PCIe-to-Gigabit
  Ethernet controller with an integrated PHY and mainline Linux support.
