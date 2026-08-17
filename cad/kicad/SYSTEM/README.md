# Complete System Schematic

Open `Radxa-CM5-ProComm-System.kicad_pro` to navigate the complete design from
one KiCad project. Its index page links all sixteen reviewed schematic sheets.

This project is a controlled navigation and factory-review entry point. It does
not merge the three physical PCB netlists:

- `PWR-SELECT` remains the source-selector PCB;
- `CM5-CARRIER` remains the compute/network/radio/control PCB;
- `AUDIO-8X8` remains the balanced-audio PCB.

Run ERC, BOM export, netlist export, and PCB update from the corresponding board
project. The system index sheets are excluded from BOM and board update so a
user cannot accidentally create one mixed PCB from the complete-system view.

Regenerate and validate with:

```sh
PYTHONPATH=/tmp/radxa-cm5-kicad-deps \
  python3 cad/kicad/SYSTEM/generate_system_schematic.py
python3 cad/kicad/SYSTEM/validate_system_schematic.py
```

The factory-readable whole-system PDF remains
`../../../outputs/schematic-release-a1/Radxa-CM5-ProComm-Schematic-Release-A1.pdf`.
