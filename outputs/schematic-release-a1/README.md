# Schematic Release A1

## State

**ELECTRICAL_CAPTURE_COMPLETE / PCB_ROUTING_HELD**

This folder contains the factory-review PDF set generated from all sixteen
controlled KiCad schematic sheets. The editable whole-system entry point is
`../../cad/kicad/SYSTEM/Radxa-CM5-ProComm-System.kicad_pro`.

- `Radxa-CM5-ProComm-Complete-Electrical-A2.pdf`: native KiCad 17-page export;
  page 1 is the real system electrical interconnect and pages 2-17 are the
  complete component-level circuits.
- `Power-Selector-Schematic-A1.pdf`: no-blink primary/backup selector,
  hold-up, telemetry, and protected output.
- `CM5-Carrier-Schematic-A1.pdf`: CM5 allocation, network, Wi-Fi, cellular,
  display, headset, power, fan, sensor, and service interfaces.
- `Audio-8x8-Schematic-A1.pdf`: AK5558VN ADC, AK4458VN DAC, TDM clock/control,
  balanced line stages, relays, XLRs, and audio power.
- `Radxa-CM5-ProComm-Schematic-Release-A1.pdf`: cover plus the complete master
  set in electrical review order.
- `SHA256SUMS.txt`: controlled hashes for all five release PDFs.

Regenerate only after the complete capture gate passes:

```sh
cad/kicad/review_detailed_capture.sh
/Users/viewvision/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  cad/kicad/build_schematic_release.py
```

The schematic set is electrically reviewed but does not authorize PCB routing.
Ten routing-critical footprint coupons and the measured enclosure/mechanical
release remain open. See `../../cad/kicad/FOOTPRINT_RELEASE.md` and
`../../fabrication/mechanical-release/README.md`.
