#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
COUPON="$ROOT/cad/kicad/FOOTPRINT-COUPON"
KICAD_CLI=${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}

python3 "$COUPON/generate_coupon.py"
python3 "$COUPON/validate_coupon.py"
"$KICAD_CLI" pcb drc \
  --exit-code-violations \
  --output "$COUPON/Footprint-Coupon-drc.rpt" \
  "$COUPON/Footprint-Coupon.kicad_pcb"

if ! grep -q "Found 0 DRC violations" "$COUPON/Footprint-Coupon-drc.rpt"; then
  echo "Coupon DRC did not close cleanly" >&2
  exit 1
fi

echo "Footprint coupon review passed: zero DRC violations"
