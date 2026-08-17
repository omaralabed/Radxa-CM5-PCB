#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
KICAD_CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
KICAD_PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3

cd "$ROOT"

"$KICAD_PY" cad/kicad/generate_pcb_projects.py

mkdir -p cad/kicad/PCB-REVIEW
"$KICAD_CLI" pcb drc --format json --severity-all --schematic-parity \
  --output cad/kicad/PCB-REVIEW/Audio-8x8-PCB-A0-DRC.json \
  cad/kicad/AUDIO-8X8/Audio-8x8.kicad_pcb
"$KICAD_CLI" pcb drc --format json --severity-all --schematic-parity \
  --output cad/kicad/PCB-REVIEW/CM5-Carrier-PCB-A0-DRC.json \
  cad/kicad/CM5-CARRIER/CM5-Carrier.kicad_pcb
"$KICAD_CLI" pcb drc --format json --severity-all --schematic-parity \
  --output cad/kicad/PCB-REVIEW/PowerSelector-PCB-A0-DRC.json \
  cad/kicad/PWR-SELECT/PowerSelector.kicad_pcb

python3 cad/kicad/CM5-CARRIER/validate_cm5_mating_geometry.py
"$KICAD_PY" cad/kicad/validate_pcb_placement.py
python3 cad/kicad/validate_pcb_drc_baseline.py
python3 fabrication/mechanical-release/validate_mechanical_release.py

printf '%s\n' \
  'PCB-A0 review passed: exact mating geometry, controlled supports, process rules, and DRC baseline are unchanged.'
