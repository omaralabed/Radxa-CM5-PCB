# Complete System Schematic

Open `Radxa-CM5-ProComm-System.kicad_pro` to navigate the complete design from
one KiCad project. Page 1 is the pin-level system electrical interconnect for
AC/PSU/backup power, board-to-board harnesses, display, cooling, network,
service, RF, and all sixteen balanced XLR channels. Pages 2-18 are the seventeen
reviewed component-level circuit sheets, including the socketed SIM-SERVICE
daughterboard.

This project is the controlled whole-system electrical and factory-review entry
point. It does not merge the four physical PCB netlists:

- `PWR-SELECT` remains the source-selector PCB;
- `CM5-CARRIER` remains the compute/network/radio/control PCB;
- `AUDIO-8X8` remains the balanced-audio PCB.
- `SIM-SERVICE` remains the direct-socket dual-SIM daughterboard.

Run ERC, BOM export, netlist export, and PCB update from the corresponding board
project. The detailed sheet instances are excluded from BOM and board update so a
user cannot accidentally create one mixed PCB from the complete-system view.
The page-1 connector representations are also excluded; their purpose is to
document exact system wiring between the three board netlists and field wiring.

Regenerate and validate with:

```sh
PYTHONPATH=/tmp/radxa-cm5-kicad-deps \
  python3 cad/kicad/SYSTEM/generate_system_schematic.py
python3 cad/kicad/SYSTEM/validate_system_schematic.py
```

The native 18-page whole-system PDF is
`../../../outputs/schematic-release-a1/Radxa-CM5-ProComm-Complete-Electrical-A2.pdf`.
The cover-plus-review master remains
`../../../outputs/schematic-release-a1/Radxa-CM5-ProComm-Schematic-Release-A1.pdf`.
