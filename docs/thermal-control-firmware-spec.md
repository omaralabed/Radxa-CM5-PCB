# ProComm Thermal-Control Firmware Specification

Document status: Rev A implementation specification

Applies to: Radxa CM5 ProComm carrier and Pelican iM2300 assembly

Hardware source: `cad/kicad/CM5-CARRIER/Thermal-IO.kicad_sch`

Thermal policy source: `notes/thermal-fans.md`

## 1. Purpose

This document defines the Linux and board-software configuration required to
control the four ProComm cooling fans from temperature and tachometer feedback.
It is the handoff specification for the production Radxa operating-system
image.

The fans do not contain user-programmable firmware. The CM5 Linux image must
configure the EMC2305 fan controller, read the CM5 and board temperature
sensors, apply the fan policy, monitor faults, and report thermal health.

No end-user setup is permitted. The complete configuration must start
automatically on every boot and remain safe if Linux, I2C, or the control
service fails.

## 2. Current Implementation Status

| Item | Status |
| --- | --- |
| EMC2305 and fan-channel schematic | Captured |
| Three TMP117 sensor schematic | Captured |
| Hardware PWM pull-up fail-safe | Captured |
| Thermal policy and preliminary fan curve | Documented |
| Radxa device-tree integration | Not implemented |
| Production kernel configuration | Not locked |
| EMC2305 1 kHz low-speed PWM support | Driver work required |
| ProComm thermal-control service | Not implemented |
| Chamber-tested release curve | Not available |

This file is a specification, not evidence that the runtime software has been
installed or tested.

## 3. Controlled Hardware Map

### 3.1 Control Bus

- CM5 source bus: `SYS_I2C7_SCL` / `SYS_I2C7_SDA`
- Board-side bus: `CTRL_I2C_SCL` / `CTRL_I2C_SDA`
- Logic translation: 1.8 V CM5 side to 3.3 V control side
- EMC2305 7-bit SMBus address: `0x2E`
- EMC2305 clock source: internal clock

### 3.2 Fan Channels

| EMC2305 channel | Function | PWM net | Tach net | Fan status |
| ---: | --- | --- | --- | --- |
| 1 | CM5 heatsink fan | `CPU_FAN_PWM` | `CPU_FAN_TACH` | Delta `FFB0412EN-00Y2E` starting selection |
| 2 | Cellular-modem fan | `MODEM_FAN_PWM` | `MODEM_FAN_TACH` | Exact model remains to be locked |
| 3 | Right-wall filtered enclosure intake | `INTAKE_FAN_PWM` | `INTAKE_FAN_TACH` | Delta `THA0412AD-TZW3` |
| 4 | Operator-wall center-right enclosure exhaust | `EXHAUST_FAN_PWM` | `EXHAUST_FAN_TACH` | Delta `THA0412AD-TZW3` |
| 5 | Spare | Reserved | Reserved | Do not assign without a design revision |

The intake and exhaust channels must remain independent. Do not join their PWM
or tachometer nets in hardware, device tree, or software.

### 3.3 Temperature Inputs

| Source | Address/interface | Controlled use |
| --- | --- | --- |
| CM5 SoC thermal zones | Linux thermal subsystem | CM5 fan and system overtemperature |
| `TMP117_CM5` | I2C `0x48` | CM5 local-zone cross-check |
| `TMP117_MODEM` | I2C `0x49` | Modem fan and enclosure demand |
| `TMP117_BOARD_POWER` | I2C `0x4A` | Enclosure fans and regulator protection |
| Modem internal temperature | QMI, MBIM, or AT command if supported | Modem fan demand and modem shutdown |

Linux mainline exposes TMP117 measurements through the IIO subsystem. The
control service must discover sensors by device identity and label rather than
assuming fixed `iio:deviceN` numbers.

All three TMP117 open-drain outputs share `TEMP_ALERT_N` on TCA9535 `U1001`
pin 10 (`P0.6`). On assertion, firmware reads addresses `0x48`, `0x49`, and
`0x4A` to identify every active source. `U1001` pin 11 (`P0.7`) is reserved
for the separate INA228 `PWR_MON_ALERT_N`; see
`power-telemetry-software-spec.md`.

## 4. Required Linux Support

The production kernel must enable at least:

```text
CONFIG_I2C=y
CONFIG_I2C_CHARDEV=y
CONFIG_HWMON=y
CONFIG_SENSORS_EMC2305=y or m
CONFIG_IIO=y
CONFIG_TMP117=y or m
CONFIG_THERMAL=y
CONFIG_THERMAL_OF=y
```

The final symbols must be verified against the exact Radxa production kernel;
symbol names and built-in/module choices can differ between BSP releases.

Required upstream interfaces:

- EMC2305 hwmon: `pwm1` through `pwm5`, `fan1_input` through `fan5_input`,
  and `fan1_fault` through `fan5_fault`
- TMP117 IIO: raw temperature plus scale and calibration bias
- CM5 SoC temperature: Linux thermal-zone interface

## 5. Device-Tree Starting Point

The final CM5 I2C controller label and 3.3 V regulator phandle must be taken
from the locked Radxa BSP. The following is an integration starting point, not
a drop-in production overlay:

```dts
#include <dt-bindings/pwm/pwm.h>

&i2c7 {
    status = "okay";

    fan_controller: fan-controller@2e {
        compatible = "microchip,emc2305";
        reg = <0x2e>;
        #address-cells = <1>;
        #size-cells = <0>;
        #pwm-cells = <3>;

        fan@0 {
            reg = <0>;
            pwms = <&fan_controller 26000 PWM_POLARITY_NORMAL 0>;
            fan-shutdown-percent = <100>;
            #cooling-cells = <2>;
        };

        fan@1 {
            reg = <1>;
            pwms = <&fan_controller 26000 PWM_POLARITY_NORMAL 0>;
            fan-shutdown-percent = <100>;
            #cooling-cells = <2>;
        };

        fan@2 {
            reg = <2>;
            pwms = <&fan_controller 26000 PWM_POLARITY_NORMAL 0>;
            fan-shutdown-percent = <100>;
            #cooling-cells = <2>;
        };

        fan@3 {
            reg = <3>;
            pwms = <&fan_controller 26000 PWM_POLARITY_NORMAL 0>;
            fan-shutdown-percent = <100>;
            #cooling-cells = <2>;
        };
    };

    temperature-sensor@48 {
        compatible = "ti,tmp117";
        reg = <0x48>;
        vcc-supply = <&control_3v3>;
        label = "cm5-local";
    };

    temperature-sensor@49 {
        compatible = "ti,tmp117";
        reg = <0x49>;
        vcc-supply = <&control_3v3>;
        label = "cellular-modem";
    };

    temperature-sensor@4a {
        compatible = "ti,tmp117";
        reg = <0x4a>;
        vcc-supply = <&control_3v3>;
        label = "board-power";
    };
};
```

The EMC2305 PWM output must remain open-drain so the hardware pull-ups command
full fan speed if the controller is absent or unpowered.

## 6. EMC2305 Initialization Requirements

Program and verify these settings on every boot:

1. Select direct-duty control for all four installed channels.
2. Configure tachometer sampling for the actual fan pole count.
3. Enable spin-up at 100 percent before allowing reduced duty.
4. Enforce a minimum running command of 30 percent for the two enclosure fans.
5. Configure intake and exhaust for 1.000 kHz PWM using the 26.00 kHz base and
   low-speed divide value `0x1A`.
6. Enable stall detection and alert reporting.
7. Configure the continuous watchdog so four seconds without host SMBus
   activity forces full-scale fan drive and asserts `ALERT#`.
8. Set shutdown duty to 100 percent for every populated fan channel.

The current upstream EMC2305 Linux driver exposes the supported base-frequency
selection, but the production image must be checked for support for the
low-speed divide needed for exact 1 kHz output. If the selected Radxa kernel
does not expose it, add a reviewed board-specific driver extension. Do not use
uncoordinated `i2cset` writes while the kernel EMC2305 driver is bound.

The CPU and final modem fan frequencies must be taken from their released fan
datasheets. Do not assume that the 1 kHz enclosure-fan setting applies to every
fan model.

## 7. ProComm Thermal-Control Service

Use a dedicated service, provisionally named `procomm-thermald`. It must start
after I2C, hwmon, IIO, and modem-management devices are available and before
high-load ProComm applications begin.

Required behavior:

- Run automatically under `systemd` and restart after an unexpected exit.
- Discover thermal, IIO, and hwmon devices by identity instead of numeric index.
- Command all four fans to 100 percent for at least three seconds at startup.
- Confirm valid tachometer feedback before reducing any fan duty.
- Poll temperatures, tachometers, and fault bits at least once per second.
- Generate enough valid SMBus traffic to keep the EMC2305 continuous watchdog
  serviced during normal operation.
- Apply hysteresis or rate limiting so duty does not oscillate around a trip
  point.
- Publish fan RPM, commanded duty, temperatures, and fault state to the local
  ProComm health/status service.
- Log state transitions and faults without high-rate log flooding.

Hardcoded `/sys/class/hwmon/hwmonN` or `/sys/bus/iio/devices/iio:deviceN`
numbers are prohibited because enumeration order can change between boots.

## 8. Preliminary Enclosure-Fan Policy

This table is a starting calibration and is not production-released until the
45 C chamber test is complete.

| Hottest board/modem sensor | Intake duty | Exhaust duty |
| --- | ---: | ---: |
| Startup for 3 seconds | 100% | 100% |
| Below 45 C | 40% | 35% |
| 45-55 C | 60% | 55% |
| 55-65 C | 80% | 75% |
| 65 C or above | 100% | 100% |

The small intake bias is preliminary. Final values must come from measured
airflow, pressure, filter loading, component temperature, and recirculation
tests.

The CM5 fan follows the hottest valid CM5 SoC thermal-zone reading and the
local `TMP117_CM5` reading. The modem fan follows the hottest valid value from
`TMP117_MODEM` and the modem internal temperature. Their final ramp tables are
release-time calibration items.

## 9. Mandatory Fail-Safe Behavior

Immediately command all four fans to 100 percent and raise a thermal/fan alarm
if any of these conditions occurs:

- Any required temperature input is missing, invalid, stale, or out of range.
- Any populated fan reports a stall or loses tachometer feedback after its
  spin-up allowance.
- The EMC2305 reports a watchdog, stall, or communication fault.
- The software cannot identify the expected sensor/channel map.
- I2C reads or PWM writes repeatedly fail.
- CPU, modem, board, or power-zone temperature reaches its emergency limit.
- The thermal-control service is intentionally stopped while the system remains
  powered.

If temperatures continue rising at full fan speed, the service must request a
controlled load reduction and then an orderly system shutdown. Hardware rail
protection and component thermal shutdown remain the final protection layer.

The board-level PWM pull-ups provide full-speed fallback if the EMC2305 is
absent or unpowered. The EMC2305 continuous watchdog provides full-speed
fallback if host SMBus activity stops. Both mechanisms must be tested.

## 10. Boot and Shutdown Sequence

### Boot

1. Hardware pull-ups hold all fan PWM inputs at the full-speed state.
2. Linux enables the control I2C bus and probes EMC2305 and TMP117 devices.
3. The EMC2305 driver applies safe output polarity and 100-percent shutdown
   behavior.
4. `procomm-thermald` verifies all expected devices and programs the final fan
   settings.
5. All fans run at 100 percent for at least three seconds.
6. The service validates temperatures and tachometers.
7. Only then may the service enter temperature-controlled operation.

### Shutdown or Service Stop

1. Command all fans to 100 percent.
2. Record the last temperature, RPM, duty, and fault state.
3. Stop high-load services and complete the operating-system shutdown.
4. Leave `fan-shutdown-percent = 100` in the device tree/driver configuration.

## 11. Verification and Release Tests

### Software bring-up

- Confirm I2C devices at `0x2E`, `0x48`, `0x49`, and `0x4A`.
- Confirm EMC2305 channel-to-connector mapping one fan at a time.
- Confirm intake and exhaust tach readings are plausible at 40, 60, 80, and
  100 percent command.
- Measure enclosure-fan PWM at the connector and verify 1.000 kHz, polarity,
  open-drain behavior, and duty accuracy.
- Confirm 100-percent startup and minimum 30-percent running command.
- Confirm each TMP117 label maps to its physical board location.

### Fault injection

- Stop `procomm-thermald`; all fans must reach full speed.
- Block host SMBus activity for more than four seconds; the EMC2305 watchdog
  must command full-scale drive and assert its fault indication.
- Disconnect each fan tachometer in turn; all fans must go to full speed and a
  persistent alarm must be logged.
- Remove or invalidate each temperature sensor in turn; all fans must go to
  full speed.
- Simulate an overtemperature event and verify load reduction and controlled
  shutdown behavior.
- Reboot repeatedly and confirm no fan enters an uncontrolled low-speed period.

### Production thermal qualification

- Test at 45 C / 113 F ambient under simultaneous maximum CPU/GPU/NPU, Wi-Fi
  AP, cellular uplink, 8x8 audio, Ethernet, display, and storage load.
- Log all temperatures, RPMs, PWM commands, faults, and throttling events until
  steady state.
- Verify at least 15 CFM measured through-case flow with a clean intake filter.
- Repeat with the filter loaded to its maintenance threshold.
- Verify no component exceeds its manufacturer limit and no unintended CM5 or
  modem thermal throttling occurs.

## 12. Production Software Deliverables

The firmware/software milestone is complete only when the project contains:

- Radxa BSP version and kernel commit lock
- Device-tree source and compiled deployment method
- Kernel configuration fragment
- Any reviewed EMC2305 low-frequency PWM driver patch
- `procomm-thermald` source, configuration, and unit tests
- `systemd` service and restart/watchdog policy
- Factory fan/sensor mapping test
- Fault-injection test report
- 45 C chamber qualification logs and released fan curves
- Recovery instructions that leave the fans at full speed

## 13. Primary References

- Linux EMC2305 hwmon documentation:
  https://www.kernel.org/doc/html/latest/hwmon/emc2305.html
- Linux EMC2305 device-tree binding:
  https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/hwmon/microchip%2Cemc2305.yaml
- Linux TMP117 device-tree binding:
  https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/iio/temperature/ti%2Ctmp117.yaml
- Microchip EMC2301/2/3/5 datasheet:
  https://ww1.microchip.com/downloads/en/DeviceDoc/EMC2301-2-3-5-Data-Sheet-DS20006532A.pdf
