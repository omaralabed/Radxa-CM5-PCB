# KiCad Hardware Projects

## Tool And Status

- Native CAD tool: KiCad 10.0.5.
- Capture milestone: A1 detailed CM5-carrier schematic suite.
- These files are not a fabrication release.
- Carrier and audio PCB files are intentionally deferred until the measured
  panel geometry, board outlines, connector footprints, and controlled-
  impedance stackup are released.

## Project Split

- `SYSTEM/Radxa-CM5-ProComm-System.kicad_pro`: one native KiCad electrical
  project for the complete design. Page 1 captures the exact system harness,
  power, display, fan, network, service, RF, and XLR pin/net interconnects;
  pages 2-17 contain the sixteen component-level sheets. System connector and
  sheet instances are excluded from BOM and board update; the three physical
  PCB netlists remain controlled by their board projects below.

- `PWR-SELECT/PowerSelector.kicad_pro`: Radxa A1 source-selector capture with
  1.50 mOhm source-shunt starting values, three INA228 telemetry channels, and
  a delivered-load shunt. Four 6800 uF / 50 V Nichicon snap-ins plus 660 uF of
  local hybrids form the floor-mounted hold-up bank; all 15 A-class thermal,
  SOA, inrush, tolerance, retention, and transfer assumptions still require
  release validation.
- `CM5-CARRIER/CM5-Carrier.kicad_pro`: carrier interface overview and shared
  interboard connector contract.
- `CM5-CARRIER/CM5-Core-Allocated.kicad_pro`: exact 300-contact CM5 connector
  representation with all 76 locked allocations, power/service controls, and
  debug UART.
- `CM5-CARRIER/Network-PCIe.kicad_pro`: native WAN1, PI7C9X2G608GP PCIe switch,
  three LAN7430 endpoints, four protected MagJacks, and the AW7915-NP1 4T4R
  Wi-Fi interface through a Molex 0679101002 Mini PCIe socket.
- `CM5-CARRIER/WWAN-SIM.kicad_pro`: USB3/USB2 cellular B-key interface, modem
  controls, protection, dual nano-SIM holders, and FSA2567 SIM mux.
- `CM5-CARRIER/Display-Harness.kicad_pro`: HDMI, USB touch, and the locked
  12 V / 2.5 A monitor branch.
- `CM5-CARRIER/Audio-Control.kicad_pro`: differential I2S0/TDM interboard link,
  I2S1 ES8316 CTIA headset path, and TPA6132A2 headphone amplifier.
- `CM5-CARRIER/Power-Regulators-A1.kicad_pro`: calculated 10.5-30 V power tree,
  protected input from the no-blink selector, dedicated system/radio/network/audio rails, branch
  protection, sequencing, and rail test access.
- `CM5-CARRIER/Thermal-IO.kicad_pro`: I2C translation, GPIO expansion, three
  temperature zones, status outputs, and four independent PWM/tach fans.
- `AUDIO-8X8/Audio-8x8.kicad_pro`: native audio interface sheet with the
  carrier contract and eight `NC3MAV` outputs plus eight `NC3FAV` inputs.
- `AUDIO-8X8/Audio-TDM-Clock.kicad_pro`: differential TDM harness receivers,
  ADC return driver, reset/mute defaults, and clock contract.
- `AUDIO-8X8/AK5558-ADC.kicad_pro`: exact eight-channel ADC pin capture,
  references, bypassing, mode straps, and I2C address `0x10`.
- `AUDIO-8X8/AK4458-DAC.kicad_pro`: exact eight-channel DAC pin capture,
  references, bypassing, mode defaults, and I2C address `0x11`.
- `AUDIO-8X8/Audio-Inputs.kicad_pro`: eight THAT1206/OPA1652 active-balanced
  input channels with protection and anti-alias networks.
- `AUDIO-8X8/Audio-Outputs.kicad_pro`: eight OPA1652/THAT1646 active-balanced
  output channels with fail-silent relays and connector protection.
- `AUDIO-8X8/Audio-Power.kicad_pro`: isolated bipolar line-stage power,
  low-noise AKM rails, sequencing, and controlled ground star.
- `INTERBOARD_INTERFACE_CONTRACT.md`: controlled pin assignment shared by all
  three projects.
- `../../notes/cm5-pin-allocation-a0.md` and
  `../../outputs/cm5-pin-allocation-a0/radxa_cm5_pin_allocation_a0.xlsx`:
  controlled Radxa CM5 V2.21 module-pin ownership and mux-conflict audit for
  detailed `CM5-CARRIER` capture.

Enclosure fan 1 is the filtered right-wall intake. Enclosure fan 2 is the
operator-wall center-right exhaust. Both are Delta `THA0412AD-TZW3` units.
They have independent 1 kHz PWM and tach nets from the EMC2305; internal
baffles must force intake air across the hot zones before it reaches the
separate exhaust opening.

## Regenerate And Validate

The carrier and audio sheets are generated through the structured
`kicad-sch-api` package. The generator is the source of truth; do not make a
manual edit to a generated `.kicad_sch` file without also updating it.

```sh
python3 -m pip install --target /tmp/radxa-cm5-kicad-deps -r cad/kicad/requirements.txt
PYTHONPATH=/tmp/radxa-cm5-kicad-deps python3 cad/kicad/generate_interface_schematics.py
PYTHONPATH=/tmp/radxa-cm5-kicad-deps python3 cad/kicad/PWR-SELECT/generate_power_selector.py

KICAD=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
"$KICAD" sch export netlist --format kicadxml \
  --output cad/kicad/PWR-SELECT/REVIEW/PowerSelector-A0.xml \
  cad/kicad/PWR-SELECT/PowerSelector.kicad_sch
"$KICAD" sch erc --format report --units mm \
  --output cad/kicad/PWR-SELECT/REVIEW/PowerSelector-A0-ERC.rpt \
  cad/kicad/PWR-SELECT/PowerSelector.kicad_sch
"$KICAD" sch export netlist --format kicadxml \
  --output cad/kicad/CM5-CARRIER/REVIEW/CM5-Carrier-A1.xml \
  cad/kicad/CM5-CARRIER/CM5-Carrier.kicad_sch
"$KICAD" sch export netlist --format kicadxml \
  --output cad/kicad/CM5-CARRIER/REVIEW/Thermal-IO-A1.xml \
  cad/kicad/CM5-CARRIER/Thermal-IO.kicad_sch
"$KICAD" sch export netlist --format kicadxml \
  --output cad/kicad/AUDIO-8X8/REVIEW/Audio-8x8-A1.xml \
  cad/kicad/AUDIO-8X8/Audio-8x8.kicad_sch

python3 cad/kicad/PWR-SELECT/validate_power_selector.py
python3 cad/kicad/CM5-CARRIER/validate_power_regulators.py
python3 cad/kicad/AUDIO-8X8/validate_audio_8x8.py
python3 cad/kicad/validate_interface_contracts.py
python3 cad/kicad/audit_footprint_readiness.py
python3 cad/kicad/export_schematic_bom.py \
  --schematic cad/kicad/CM5-CARRIER/Power-Regulators-A1.kicad_sch \
  --output docs/power_regulator_bom_a1.csv \
  --exclude U1180 --exclude TP1190 --exclude TP1191 --exclude TP1192 --exclude TP1193
python3 cad/kicad/AUDIO-8X8/export_audio_8x8_bom.py
```

The complete A1 gate is automated:

```sh
cad/kicad/review_detailed_capture.sh
```

After that gate passes, build the combined schematic review PDFs with:

```sh
/Users/viewvision/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  cad/kicad/build_schematic_release.py
```

The controlled outputs and electrical/physical release distinction are under
`../../outputs/schematic-release-a1/` and
`../../docs/schematic-release-status-a1.md`.

The generators use deterministic UUIDs. The review script writes temporary
ERC, netlist, and PDF outputs, then updates controlled review artifacts only
when their electrical content or rendered appearance changes. `pdftoppm` is
required for this visual comparison. Repeating the complete gate without a
source change must leave the working tree unchanged.

The interface validator checks 174 critical connector and control pin/net
assignments, including all three selector harnesses, power/temperature alerts,
the 30-pin buffered TDM/control link, separate audio power, four fan headers,
and all 16 XLR connectors.

The footprint audit covers every component on all sixteen sheets. Its default mode
updates the controlled CSV and Markdown reports. Use `--routing` to enforce the
placement/routing gate and `--release` to additionally require a manufacturer
and MPN for every board-mounted item. The drawing-backed connector evidence and
the Molex 0679101002 datum contract are recorded in
[`FOOTPRINT_RELEASE.md`](FOOTPRINT_RELEASE.md).

The current audit covers 1038 components. Ten items intentionally block PCB
routing until physical coupons are approved: the two AKM exposed-pad packages
and eight Panasonic TQ2 relay lands. The stricter production audit also holds
the Kycon headset jack coupon, for 11 production blockers total.

Every A1 detailed sheet and AUDIO-8X8 currently reports zero ERC errors. The
remaining warnings are isolated off-sheet interface labels or deliberately
unused package pins and are classified in
`CM5-CARRIER/DETAILED_CAPTURE_STATUS.md`. The AUDIO-8X8 XLR shield pins now bond
directly to `XLR_CHASSIS`; one controlled 1 Mohm / 4.7 nF bond joins chassis to
`AGND` for static and RF control.

After every generated or manual schematic revision, export the full sheet to
PDF and inspect the dense areas at high resolution. Labels, wires, symbol
fields, connector identifiers, and sheet notes must not overlap or collide.
Electrical validation does not replace this visual readability gate.

## Next Engineering Order

1. Close the controlled footprint/MPN audit for Thermal-IO, Network-PCIe,
   WWAN-SIM, Display-Harness, and Audio-Control. Power-Regulators-A1 is closed
   at the schematic/BOM footprint gate but still requires first-article,
   copper-current, thermal, loop-response, and compensation review.
2. Complete selector shunt/current-limit tolerance, hold-up/precharge, SOA,
   telemetry calibration, and 15 A thermal review, then create its PCB.
3. Release the measured enclosure datums, custom four-side frame drawing, and
   controlled-impedance PCB stackup. Enforce the Rev L underside limits of 78
   x 268 mm for `AUDIO-8X8` and 166 x 268 mm for `CM5-CARRIER`, with controlled
   support patterns `A1-A6` and `C1-C6` and no board, copper, component, or
   standoff entering the 15 mm frame/screw keepout, then
   convert the schematic suite into the routed carrier hierarchy.
4. Approve the AK5558VN/AK4458VN exposed-pad and TQ2 relay coupons, then bench
   validate the locked 48 kHz TDM256 mode, +4/+24 dBu level plan, 600 ohm
   compatibility load, mute sequencing, crosstalk, noise, and THD+N.
5. Run SI/PI, thermal, EMC, and fabrication DFM reviews before release.
