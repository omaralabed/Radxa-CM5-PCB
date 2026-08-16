# ProComm Power-Telemetry Hardware And Software Specification

Document status: Rev A implementation specification

Applies to: Radxa CM5 ProComm carrier, PWR-SELECT A1, and touchscreen UI

Hardware sources:

- `cad/kicad/PWR-SELECT/PowerSelector.kicad_sch`
- `cad/kicad/CM5-CARRIER/CM5-Carrier.kicad_sch`
- `cad/kicad/CM5-CARRIER/Thermal-IO.kicad_sch`

## 1. Purpose And Status

The system shall display and log voltage, current, and power for the primary
24 V source, the selected backup source, and the delivered protected raw load.
The implementation follows the proven ProComm three-monitor architecture but
uses Radxa-specific source-shunt values and the carrier control I2C bus.

| Item | Status |
| --- | --- |
| Three INA228 monitor channels | Captured in PWR-SELECT A1 |
| Kelvin source and load sensing | Captured |
| Six-wire carrier telemetry harness | Captured and contract-validated |
| Shared alert into TCA9535 `U1001` | Captured and contract-validated |
| Linux device-tree nodes | Specified below; not implemented |
| UI service, logging, and alarms | Specified below; not implemented |
| Production calibration | Required on assembled hardware |

The monitors read protected low-voltage DC. They do not measure AC mains input
voltage, AC current, power factor, or PSU conversion efficiency.

## 2. Hardware Channels

| Function | Ref | Address | Shunt | Measurement point | Nominal full scale |
| --- | --- | ---: | ---: | --- | ---: |
| Primary 24 V DC | `U601` | `0x40` | `R111`, 1.50 mOhm | After primary fuse and ideal-diode path | 27.307 A |
| Selected backup | `U602` | `0x41` | `R211`, 1.50 mOhm | After backup fuse and ideal-diode path | 27.307 A |
| Delivered raw load | `U603` | `0x44` | `R311`, 1.00 mOhm | After selector hold-up bank, before carrier | 40.96 A |

The full-scale values assume the INA228 `+/-40.96 mV` shunt range. `R111` and
`R211` are also the LTC4421 current-limit shunts. Their 1.50 mOhm starting
value produces a nominal `25 mV / 1.50 mOhm = 16.667 A` current limit and
`0.3375 W` shunt dissipation at 15 A.

The final shunt tolerance, temperature coefficient, pulse rating, PCB copper,
LTC4421 threshold tolerance, MOSFET SOA, and cooling shall be reviewed before
fabrication release. The schematic value is a controlled engineering starting
point, not completed production qualification.

## 3. Inter-Board Interface

PWR-SELECT `J402` mates with CM5-CARRIER `J103` using a keyed six-position
Molex PicoBlade harness.

| Pin | PWR-SELECT | CM5-CARRIER | Function |
| ---: | --- | --- | --- |
| 1 | `MON_3V3` | `LOGIC_3V3` | Monitor power supplied by carrier |
| 2 | `GND` | `GND` | Ground |
| 3 | `PWR_MON_SDA` | `CTRL_I2C_SDA` | 3.3 V I2C data |
| 4 | `PWR_MON_SCL` | `CTRL_I2C_SCL` | 3.3 V I2C clock |
| 5 | `PWR_MON_ALERT_N` | `PWR_MON_ALERT_N` | Wired-OR active-low alert |
| 6 | `GND` | `GND` | Ground return/shield reference |

The carrier owns the SDA, SCL, and alert pull-ups. Do not add another strong
set of I2C pull-ups on PWR-SELECT. Keep the harness short and route SDA/SCL with
ground adjacency away from fan PWM, switching nodes, RF coax, and XLR audio.

`PWR_MON_ALERT_N` is read by TCA9535 `U1001` physical pin 11 (`P0.7`). The
three TMP117 sensors share `TEMP_ALERT_N` on `U1001` pin 10 (`P0.6`), freeing
the expander input needed for power telemetry.

## 4. Linux Integration Starting Point

The production kernel shall enable the INA238-family hwmon driver:

```text
CONFIG_I2C=y
CONFIG_HWMON=y
CONFIG_SENSORS_INA238=y or m
```

The final Radxa I2C controller label and regulator phandle must come from the
locked production BSP. This is a device-tree starting point:

```dts
&i2c7 {
    status = "okay";

    primary_power: power-monitor@40 {
        compatible = "ti,ina228";
        reg = <0x40>;
        label = "primary-24v";
        shunt-resistor = <1500>;  /* micro-ohms */
        ti,shunt-gain = <1>;      /* +/-40.96 mV range */
        vs-supply = <&control_3v3>;
    };

    backup_power: power-monitor@41 {
        compatible = "ti,ina228";
        reg = <0x41>;
        label = "selected-backup";
        shunt-resistor = <1500>;
        ti,shunt-gain = <1>;
        vs-supply = <&control_3v3>;
    };

    load_power: power-monitor@44 {
        compatible = "ti,ina228";
        reg = <0x44>;
        label = "delivered-raw-load";
        shunt-resistor = <1000>;
        ti,shunt-gain = <1>;
        vs-supply = <&control_3v3>;
    };
};
```

The upstream `ina238` hwmon driver exposes bus voltage, current, power, die
temperature, thresholds, alarms, averaging, and update interval. Discover
hwmon devices by their `name` and label; never assume fixed `hwmonN` numbers.

## 5. Touchscreen And Logging Requirements

The ProComm monitor screen shall show:

| Display field | Source |
| --- | --- |
| Primary DC volts, amps, watts | INA228 `0x40` |
| Backup DC volts, amps, watts | INA228 `0x41` |
| Delivered system volts, amps, watts | INA228 `0x44` |
| Active source | `CH_24V_N`, `CH_BAT_N`, `VALID_DTAP_N`, `VALID_GOLD_N` |
| Backup-low warning | `BAT_LOW_N` plus backup voltage trend |
| Estimated backup time | Configured usable battery energy divided by measured backup input power |

Use a two-sample-per-second UI refresh and log raw samples at least once per
second. Apply display smoothing without delaying alarms or transfer events.
Log source transitions, invalid-source states, low battery, current/power
threshold alarms, monitor communication failures, and unexpected differences
between source power and delivered-load power.

Treat negative current as a fault or reverse-current diagnostic until verified
on hardware. Do not hide it with an absolute-value operation.

## 6. Backup Runtime Estimate

Voltage alone is not a reliable battery state-of-charge measurement. Runtime
shall use a configured usable-energy value for the installed battery:

```text
remaining_minutes = 60 x remaining_usable_Wh / max(backup_input_W, minimum_W)
```

`remaining_usable_Wh` should come from a smart battery/dock interface when one
is available. Otherwise it is a conservative estimate derived from the exact
battery model, rated capacity, measured discharge curve, age/health factor,
temperature factor, and present voltage under load.

Do not ship a fixed runtime number. Gold Mount and D-Tap sources may have
different capacity, cutoff behavior, cable loss, and battery-management limits.

## 7. Calibration And Acceptance

1. Record zero-current offset for all three channels with sources energized.
2. Calibrate gain at multiple known loads using a traceable external DMM and
   current reference.
3. Verify primary and backup polarity and active-source indications.
4. Compare `U601` or `U602` input power with `U603` delivered power; confirm
   the difference agrees with selector loss and measurement tolerance.
5. Exercise primary removal/restoration at maximum load and verify continuous
   telemetry through the no-blink transfer.
6. Test alert thresholds, I2C failure handling, unplugged harness behavior, and
   reboot recovery.
7. Store calibration coefficients and hardware revision in a versioned,
   read-only production configuration.

## 8. Future Release Note

Before firmware release, implement a `procomm-powerd` service that owns hwmon
discovery, calibration, filtering, alarms, event logging, and the touchscreen
API. Keep power measurements out of the real-time audio process; publish a
small cached status object over IPC so UI work cannot disturb SIP/TDM timing.

Still required for the future production release:

- Lock the exact shunt ordering code and verify availability.
- Lock the battery dock/data interface and supported battery-capacity profiles.
- Validate the final Radxa kernel driver and device-tree overlay.
- Select conservative warning/shutdown thresholds from chamber and transfer
  tests, including operation at 45 C ambient.
- Add manufacturing calibration and serialized test results.

## 9. Primary References

- TI INA228 datasheet: https://www.ti.com/lit/ds/symlink/ina228.pdf
- Linux INA238/INA228 hwmon driver: https://docs.kernel.org/hwmon/ina238.html
- Linux INA2xx device-tree binding: https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/hwmon/ti,ina2xx.yaml
- ADI LTC4421 datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/LTC4421.pdf
- Vishay WSK2512 datasheet: https://www.vishay.com/docs/30108/wsk2512.pdf
