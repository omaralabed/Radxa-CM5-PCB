#!/usr/bin/env python3
"""Validate the generated A1 footprint qualification coupon."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
BOARD = HERE / "Footprint-Coupon.kicad_pcb"
LIB = HERE / "FootprintCoupon.pretty"
VIA_CSV = HERE / "filled_via_coordinates.csv"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def thermal_via_blocks(text: str, pad_number: str) -> list[str]:
    return re.findall(
        rf'\(pad "{pad_number}" thru_hole circle.*?\(drill 0\.2\).*?\n\s*\)',
        text,
        flags=re.DOTALL,
    )


def validate_variant(prefix: str, pad_number: str) -> None:
    paths = {
        "open": LIB / f"{prefix}_OPEN_CONTROL.kicad_mod",
        "tented": LIB / f"{prefix}_BOTTOM_TENTED.kicad_mod",
        "type7": LIB / f"{prefix}_TYPE_VII_CANDIDATE.kicad_mod",
    }
    for path in paths.values():
        require(path.exists(), f"missing footprint variant: {path.name}")

    expected_count = 25
    for name, path in paths.items():
        blocks = thermal_via_blocks(path.read_text(encoding="utf-8"), pad_number)
        require(
            len(blocks) == expected_count,
            f"{path.name}: expected {expected_count} thermal vias, found {len(blocks)}",
        )
        bottom_mask_openings = sum('"B.Mask"' in block for block in blocks)
        if name == "open":
            require(
                bottom_mask_openings == expected_count,
                f"{path.name}: every control via must open B.Mask",
            )
        else:
            require(
                bottom_mask_openings == 0,
                f"{path.name}: production-side thermal vias must be bottom tented",
            )


def main() -> int:
    require(BOARD.exists(), "coupon board has not been generated")
    board = BOARD.read_text(encoding="utf-8")

    for layer in ("F.Cu", "In1.Cu", "In2.Cu", "In3.Cu", "In4.Cu", "B.Cu"):
        require(f'"{layer}"' in board, f"missing copper layer {layer}")
    require(
        '(gr_rect (start 20 20) (end 120 100)' in board,
        "board outline must remain 100 x 80 mm",
    )
    require('(thickness 1.6)' in board, "board thickness must remain 1.6 mm")
    require('(copper_finish "ENIG")' in board, "surface finish must remain ENIG")

    expected_refs = {
        "U101",
        "U102",
        "U103",
        "U201",
        "U202",
        "U203",
        "K1",
        "J1",
        "H1",
        "H2",
        "H3",
        "H4",
        "FID1",
        "FID2",
        "FID3",
        "HG1",
    }
    for ref in expected_refs:
        require(
            re.search(rf'\(property "Reference" "{re.escape(ref)}"', board)
            is not None,
            f"missing board reference {ref}",
        )

    validate_variant("AK5558_QFN64", "65")
    validate_variant("AK4458_QFN48", "49")

    jack = (LIB / "Kycon_STX_353K7A_6N_FIT_COUPON.kicad_mod").read_text(
        encoding="utf-8"
    )
    require(jack.count("(drill 0.80)") == 6, "Kycon coupon must have six 0.8 mm holes")
    require(
        jack.count("(size 1.10 1.80)") == 6,
        "Kycon coupon must retain elongated 1.1 x 1.8 mm lands",
    )

    relay = (LIB / "Panasonic_TQ2_12V_FIT_COUPON.kicad_mod").read_text(
        encoding="utf-8"
    )
    require(relay.count("(drill 0.9)") == 8, "TQ2 coupon must have eight 0.9 mm holes")

    with VIA_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 50, "filled-via list must contain 50 selective Type VII vias")
    require({row["reference"] for row in rows} == {"U103", "U203"}, "filled-via refs changed")
    require(
        all(row["finished_hole_mm"] == "0.20" for row in rows),
        "all selective Type VII vias must remain 0.20 mm finished",
    )

    print("Coupon validation passed")
    print("  Board: 100.0 x 80.0 mm, 6 layers, 1.6 mm, ENIG")
    print("  AK5558VN sites: open / bottom-tented / Type VII")
    print("  AK4458VN sites: open / bottom-tented / Type VII")
    print("  Selective Type VII vias: 50")
    print("  THT fit sites: Panasonic TQ2-12V and Kycon STX-353K7A-6N")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"Coupon validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
