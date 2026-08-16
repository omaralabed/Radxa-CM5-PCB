#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
PACKAGE="$ROOT/fabrication/footprint-coupon-a1"
COUPON="$ROOT/cad/kicad/FOOTPRINT-COUPON"
BOARD="$COUPON/Footprint-Coupon.kicad_pcb"
OUTPUT="$PACKAGE/output"
GERBERS="$OUTPUT/gerbers"
DRILL="$OUTPUT/drill"
DRAWINGS="$OUTPUT/drawings"
PLACEMENT="$OUTPUT/placement"
RENDERS="$OUTPUT/renders"
KICAD_CLI=${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}

mkdir -p "$GERBERS" "$DRILL" "$DRAWINGS" "$PLACEMENT" "$RENDERS"
find "$GERBERS" "$DRILL" "$DRAWINGS" "$PLACEMENT" "$RENDERS" -type f -delete
find "$OUTPUT" -maxdepth 1 -type f -delete

"$COUPON/review_coupon.sh"

"$KICAD_CLI" pcb export gerbers \
  --output "$GERBERS" \
  --layers F.Cu,In1.Cu,In2.Cu,In3.Cu,In4.Cu,B.Cu,F.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask \
  --precision 6 \
  "$BOARD"

"$KICAD_CLI" pcb export drill \
  --output "$DRILL" \
  --format excellon \
  --excellon-units mm \
  --excellon-separate-th \
  --generate-map \
  --map-format pdf \
  --generate-report \
  --report-path "$DRILL/Footprint-Coupon-drill-report.txt" \
  "$BOARD"

"$KICAD_CLI" pcb export pdf \
  --output "$DRAWINGS/Footprint-Coupon-fabrication.pdf" \
  --layers F.Cu,F.SilkS,Dwgs.User,Edge.Cuts \
  --exclude-value \
  --black-and-white \
  --drill-shape-opt 2 \
  --mode-single \
  --scale 2 \
  "$BOARD"

"$KICAD_CLI" pcb export pdf \
  --output "$DRAWINGS/Footprint-Coupon-assembly-top.pdf" \
  --layers F.Cu,F.SilkS,Edge.Cuts \
  --exclude-value \
  --black-and-white \
  --drill-shape-opt 2 \
  --mode-single \
  --scale 2 \
  "$BOARD"

"$KICAD_CLI" pcb export pos \
  --output "$PLACEMENT/Footprint-Coupon-all-pos.csv" \
  --side both \
  --format csv \
  --units mm \
  "$BOARD"

"$KICAD_CLI" pcb render \
  --output "$RENDERS/Footprint-Coupon-top.png" \
  --width 2400 \
  --height 1600 \
  --side top \
  --background opaque \
  --quality high \
  "$BOARD"

"$KICAD_CLI" pcb render \
  --output "$RENDERS/Footprint-Coupon-bottom.png" \
  --width 2400 \
  --height 1600 \
  --side bottom \
  --background opaque \
  --quality high \
  "$BOARD"

cp "$COUPON/filled_via_coordinates.csv" "$OUTPUT/filled_via_coordinates.csv"
cp "$COUPON/Footprint-Coupon-drc.rpt" "$OUTPUT/Footprint-Coupon-drc.rpt"
cp "$PACKAGE/PCBWAY_RFQ.md" "$OUTPUT/FAB_NOTES.txt"

(
  cd "$OUTPUT"
  zip -X -q -r Footprint-Coupon-A1-Gerber-Drill.zip \
    gerbers drill filled_via_coordinates.csv FAB_NOTES.txt
  find . -type f ! -name SHA256SUMS.txt -print0 \
    | sort -z \
    | xargs -0 shasum -a 256 > SHA256SUMS.txt
)

echo "Fabrication release generated: $OUTPUT"
