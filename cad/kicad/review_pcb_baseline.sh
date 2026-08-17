#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
KICAD_CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
KICAD_PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3

cd "$ROOT"

"$KICAD_PY" cad/kicad/generate_pcb_projects.py

mkdir -p cad/kicad/PCB-REVIEW/3D
"$KICAD_CLI" pcb drc --format json --severity-all --schematic-parity \
  --output cad/kicad/PCB-REVIEW/Audio-8x8-PCB-A1-DRC.json \
  cad/kicad/AUDIO-8X8/Audio-8x8.kicad_pcb
"$KICAD_CLI" pcb drc --format json --severity-all --schematic-parity \
  --output cad/kicad/PCB-REVIEW/CM5-Carrier-PCB-A1-DRC.json \
  cad/kicad/CM5-CARRIER/CM5-Carrier.kicad_pcb
"$KICAD_CLI" pcb drc --format json --severity-all --schematic-parity \
  --output cad/kicad/PCB-REVIEW/Sim-Service-PCB-A1-DRC.json \
  cad/kicad/SIM-SERVICE/Sim-Service.kicad_pcb
"$KICAD_CLI" pcb drc --format json --severity-all --schematic-parity \
  --output cad/kicad/PCB-REVIEW/PowerSelector-PCB-A1-DRC.json \
  cad/kicad/PWR-SELECT/PowerSelector.kicad_pcb

for side in top bottom; do
  "$KICAD_CLI" pcb render --side "$side" --quality high --background opaque \
    --width 1600 --height 1000 \
    --output "cad/kicad/PCB-REVIEW/3D/Audio-8x8-PCB-A1-${side}.png" \
    cad/kicad/AUDIO-8X8/Audio-8x8.kicad_pcb
  "$KICAD_CLI" pcb render --side "$side" --quality high --background opaque \
    --width 1600 --height 1000 \
    --output "cad/kicad/PCB-REVIEW/3D/CM5-Carrier-PCB-A1-${side}.png" \
    cad/kicad/CM5-CARRIER/CM5-Carrier.kicad_pcb
  "$KICAD_CLI" pcb render --side "$side" --quality high --background opaque \
    --width 1600 --height 1000 \
    --output "cad/kicad/PCB-REVIEW/3D/Sim-Service-PCB-A1-${side}.png" \
    cad/kicad/SIM-SERVICE/Sim-Service.kicad_pcb
  "$KICAD_CLI" pcb render --side "$side" --quality high --background opaque \
    --width 1600 --height 1000 \
    --output "cad/kicad/PCB-REVIEW/3D/PowerSelector-PCB-A1-${side}.png" \
    cad/kicad/PWR-SELECT/PowerSelector.kicad_pcb
done

python3 cad/kicad/CM5-CARRIER/validate_cm5_mating_geometry.py
"$KICAD_PY" cad/kicad/validate_pcb_placement.py
python3 cad/kicad/validate_pcb_drc_baseline.py
python3 fabrication/mechanical-release/validate_mechanical_release.py

printf '%s\n' \
  'PCB-A1 review passed: exact mating geometry, in-board placement, controlled supports, DRC baseline, and 3D renders are current.'
