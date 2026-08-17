# CM5 Carrier Detailed Capture Status

## Milestone

- Revision: A1
- Date: 2026-08-16
- Scope: detailed CM5-carrier connectivity and engineering PCB layout baseline
- Source of truth: `../generate_interface_schematics.py`
- Release state: engineering capture; not a fabrication release

## Completed Sheets

| Sheet | Locked content |
| --- | --- |
| `CM5-Core-Allocated.kicad_sch` | Exact U33-A, U33-B, and J24 100-contact mates, source-derived relative geometry, four grounded module mounts, 76 owned allocation contacts (74 connected and two assigned no-connects), VCC_SYSIN, power-on, reset, recovery, boot, GPIO reference, and debug UART |
| `Network-PCIe.kicad_sch` | Native WAN1, PI7C9X2G608GP in 606 mode, three LAN7430 PCIe endpoints, four Wurth 74991114412 1 GbE MagJacks, PHY-side ESD, and the AW7915-NP1 4T4R interface through a Molex 0679101002 Mini PCIe socket |
| `WWAN-SIM.kicad_sch` | TE 2199230-3 M.2 B-key socket, USB3 and USB2, modem control signals, supply filtering/protection, FSA2567 dual-SIM mux, and two nano-SIM holders |
| `Display-Harness.kicad_sch` | Molex 208658-1001 HDMI, Wurth 692122030100 USB-A touch, ESD, dedicated 4.984 V / 2 A display-interface rail, and 12 V / 2.5 A monitor harness |
| `Audio-Control.kicad_sch` | I2S0/TDM LVDS transport with 3.3 V PCA9517A bus isolation, explicit 3.3 V/1.8 V I2S1 and I2C translation, ES8316 codec enable/decoupling, TPA6132A2 at 0 dB, Kycon CTIA map, one headset-ground bond, and dedicated clean rails |
| `Thermal-IO.kicad_sch` | PCA9306 control-bus translation, two TCA9535 expanders, EMC2305 fan controller, three TMP117 temperature zones, status outputs, and four independently controlled PWM/tach fan headers; intake/exhaust are Delta `THA0412AD-TZW3` at 1 kHz PWM |
| `Power-Regulators-A1.kicad_sch` | Protected raw input from floor-mounted PWR-SELECT, `SYS_4V0`, revised 8 A `AUX_12V` starting design, dedicated `FAN_CPU_12V` and `FAN_AUX_12V` branches, modem/Wi-Fi/network/logic rails, point-of-load rails, display/audio branches, isolated bipolar audio power, clean AKM/headset LDOs, sequencing, and rail test points |
| `../AUDIO-8X8/Audio-8x8.kicad_sch` | Eight XLR inputs, eight XLR outputs, direct shield-to-chassis strategy, and one controlled chassis-to-AGND RF/static bond |
| `../AUDIO-8X8/Audio-TDM-Clock.kicad_sch` | 30-conductor carrier harness, four terminated SN65LVDT2 clock/data receivers, one SN65LVDS1 ADC-return driver, reset/mute defaults, and the locked 48 kHz TDM256 clock contract |
| `../AUDIO-8X8/AK5558-ADC.kicad_sch` | Exact AK5558VN 64-pin capture, eight differential inputs, references and bypassing, slave-mode/TDM256 straps, and I2C address `0x10` |
| `../AUDIO-8X8/AK4458-DAC.kicad_sch` | Exact AK4458VN 48-pin capture, eight differential outputs on `L1/R1` through `L4/R4`, references and bypassing, serial-control/TDM256 defaults, and I2C address `0x11` |
| `../AUDIO-8X8/Audio-Inputs.kicad_sch` | Eight repeated THAT1206/OPA1652 active-balanced input channels with RFI, ESD, fault protection, AC coupling, level shift, and anti-alias networks |
| `../AUDIO-8X8/Audio-Outputs.kicad_sch` | Eight repeated OPA1652/THAT1646 active-balanced output channels with reconstruction/gain networks, fail-silent TQ2 relays, ferrites, RFI, ESD, and fault protection |
| `../AUDIO-8X8/Audio-Power.kicad_sch` | Protected `AUDIO_12V_IN`, isolated bipolar line-stage power, low-noise preregulation, separate ADC/DAC analog LDOs, AKM digital rail, sequencing, and the single digital/analog ground star |

## Locked Interface Parts

| Function | Part |
| --- | --- |
| CM5 mezzanine | Hirose DF40 series matching the Radxa CM5 connector definition |
| PCIe switch | Diodes PI7C9X2G608GP, 606 mode |
| Additional Ethernet | Microchip LAN7430, three devices |
| RJ45/magnetics | Wurth 74991114412, four devices |
| Wi-Fi socket | Molex 0679101002, full-size 52-pin Mini PCIe; drawing-derived land pattern is machine checked, with first-article and 3D fit still open |
| Cellular socket | TE 2199230-3, M.2 B-key, 4.2 mm |
| SIM mux | onsemi FSA2567MPX |
| HDMI | Molex 208658-1001 |
| USB touch | Wurth 692122030100 |
| Program-audio TDM connector | Molex 87832-6423 headers; 51110-3051 housings; 50394-8052 terminals |
| Headset codec/amplifier | ES8316 and TI TPA6132A2RTER |
| CTIA headset jack | Kycon STX-353K7A-6N-KTTR; production blocked pending physical coupon |
| Fan controller | Microchip EMC2305-1-AP-TR |
| Enclosure fans | Delta THA0412AD-TZW3, two devices; independent 1 kHz PWM/tach |
| Temperature sensors | TI TMP117, three devices |
| 4.006 V CM5 system converter | TI LM5146RGYR with external MOSFETs |
| 4.984 V display-interface converter | TI TPS62913RPUT |
| 12 V buck-boost | TI LM5176PWP |
| Radio/network direct bucks | TI LM61460RJR and LM61440RJR |
| Low-noise point-of-load bucks | TI TPS62913RPUT |
| Cellular rail eFuse | TI TPS259827LNRGER |
| Wi-Fi startup load switch | TI TPS22990DMLR |
| Isolated audio converter | Traco Power TRI 20-1223 |
| Clean local audio LDOs | TI TPS7A20 family |
| Program-audio ADC | AKM AK5558VN, eight channels, TDM256 slave, I2C `0x10` |
| Program-audio DAC | AKM AK4458VN, eight physical outputs on `SDTI1`, TDM256 slave, I2C `0x11` |
| Balanced input receiver | THAT Corporation THAT1206S08-U, eight devices |
| ADC/output op amp | TI OPA1652AIDR, sixteen devices |
| Balanced output driver | THAT Corporation THAT1646S08-U, eight devices |
| Output fail-silent relay | Panasonic Industry TQ2-12V, eight devices; routing blocked pending pad/insertion coupon |

## ERC Classification

KiCad resolves power drive and hierarchical interfaces at each physical board
root. The three electrically authoritative roots are therefore the release ERC
gate, and each currently reports `0 errors / 0 warnings`:

| Physical board root | Errors | Warnings | Classification |
| --- | ---: | ---: | --- |
| `PWR-SELECT/PowerSelector.kicad_sch` | 0 | 0 | Clean authoritative netlist |
| `CM5-CARRIER/CM5-Carrier.kicad_sch` | 0 | 0 | Clean authoritative netlist |
| `AUDIO-8X8/Audio-8x8.kicad_sch` | 0 | 0 | Clean authoritative netlist |

Standalone child-sheet ERC reports lack their parent-sheet drivers and can
therefore contain expected endpoint or power-drive findings. The review script
compares every child finding against an exact message and location allowlist;
any added, removed, or changed finding fails the gate. Nothing is globally
suppressed merely to reduce a count. `SYSTEM/Radxa-CM5-ProComm-System.kicad_sch`
is a navigation/documentation overview and is not an authoritative PCB netlist.

## Gates Before Production Route Freeze

Engineering placement and routing may proceed from Rev L. Keep the named local
coupon regions provisional, then:

1. Close the ten final-routing blockers in the controlled audit: AK5558 `U201`,
   AK4458 `U301`, and Panasonic relays `K501-K508`. Independently inspect the
   Molex 0679101002 and drawing-derived power lands during first article, then
   complete placement and thermal review.
2. Bench-validate regulator stability, efficiency, thermal rise, startup,
   source transfer, current limits, fan startup/tach/fail-safe behavior, the
   45 C full-system thermal case, and the cellular weak-signal transmit case.
3. Release the measured CM5/module, connector, enclosure, fan, panel Z, and
   custom-frame datums plus the controlled-impedance stackup. The carrier PCB
   must remain at or below 166 x 268 mm and outside the 15 mm perimeter
   frame/screw keepout shown in the current underside mechanical floorplan.
4. Confirm selected Wi-Fi and global WWAN module power peaks, thermal solution,
   antenna cables, and regulatory integration requirements.
5. Approve AK5558/AK4458 exposed-pad, thermal-via, paste, and stencil coupons;
   approve the TQ2 relay pad/insertion coupon; then qualify the 30-conductor TDM
   harness at 12.288 MHz and the locked 48 kHz TDM256 mode.
6. Review all protection return paths, chassis bonds, creepage, and EMI zoning.
7. Close the Kycon headset-jack sample/coupon gate, verify detect-switch
   polarity, and bench-validate every audio channel at +4 dBu nominal, +24 dBu
   maximum, and 600 ohm compatibility load before production release.
