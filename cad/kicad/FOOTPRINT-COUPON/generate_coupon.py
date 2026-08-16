#!/usr/bin/env python3
"""Generate the A1 footprint qualification coupon and local footprint library."""

from __future__ import annotations

import csv
import json
import os
import re
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
COUPON_DIR = Path(__file__).resolve().parent
LIB_DIR = COUPON_DIR / "FootprintCoupon.pretty"
BOARD_PATH = COUPON_DIR / "Footprint-Coupon.kicad_pcb"
PROJECT_PATH = COUPON_DIR / "Footprint-Coupon.kicad_pro"
VIA_CSV = COUPON_DIR / "filled_via_coordinates.csv"

KICAD_SHARED = Path(
    os.environ.get(
        "KICAD_SHARED_SUPPORT",
        "/Applications/KiCad/KiCad.app/Contents/SharedSupport",
    )
)
QFN_LIB = KICAD_SHARED / "footprints" / "Package_DFN_QFN.pretty"

SOURCES = {
    "ak5558": QFN_LIB / "QFN-64-1EP_9x9mm_P0.5mm_EP6x6mm_ThermalVias.kicad_mod",
    "ak4458": QFN_LIB / "QFN-48-1EP_7x7mm_P0.5mm_EP5.15x5.15mm_ThermalVias.kicad_mod",
    "relay": ROOT
    / "cad/kicad/CM5-CARRIER/CM5Carrier.pretty/Panasonic_TQ2-12V_PRELIMINARY.kicad_mod",
    "jack": ROOT
    / "cad/kicad/CM5-CARRIER/CM5Carrier.pretty/Kycon_STX-353K7A-6N-KTTR_PRELIMINARY.kicad_mod",
}

FOOTPRINT_NAMES = {
    "ak5558_open": "AK5558_QFN64_OPEN_CONTROL",
    "ak5558_tented": "AK5558_QFN64_BOTTOM_TENTED",
    "ak5558_type7": "AK5558_QFN64_TYPE_VII_CANDIDATE",
    "ak4458_open": "AK4458_QFN48_OPEN_CONTROL",
    "ak4458_tented": "AK4458_QFN48_BOTTOM_TENTED",
    "ak4458_type7": "AK4458_QFN48_TYPE_VII_CANDIDATE",
    "relay": "Panasonic_TQ2_12V_FIT_COUPON",
    "jack": "Kycon_STX_353K7A_6N_FIT_COUPON",
}


def deterministic_uuid(label: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"radxa-cm5-footprint-coupon-a1:{label}"))


def load_source(key: str) -> str:
    path = SOURCES[key]
    if not path.exists():
        raise FileNotFoundError(f"Required footprint source not found: {path}")
    return path.read_text(encoding="utf-8")


def rename_footprint(text: str, name: str, value: str | None = None) -> str:
    text = re.sub(r'^\(footprint "[^"]+"', f'(footprint "{name}"', text, count=1)
    text = re.sub(
        r'(\(property "Reference"\s+")([^"]+)(")',
        r'\g<1>REF**\g<3>',
        text,
        count=1,
    )
    text = re.sub(
        r'(\(property "Value"\s+")([^"]+)(")',
        rf'\g<1>{value or name}\g<3>',
        text,
        count=1,
    )
    return text


def make_open_via_control(text: str) -> str:
    """Expose thermal via barrels on B.Mask; F.Mask is already open at the EP."""
    return re.sub(
        r'(\(pad "(?:49|65)" thru_hole circle.*?\(layers )"\*\.Cu"(\))',
        r'\1"*.Cu" "B.Mask"\2',
        text,
        flags=re.DOTALL,
    )


def refine_relay_fit_coupon(text: str) -> str:
    text = re.sub(
        r'^\s*\(fp_line .*?\(layer "F\.SilkS"\).*?\)\s*$',
        "",
        text,
        flags=re.MULTILINE,
    )
    return text.replace(
        "PRELIMINARY - DRAWING/COUPON",
        "A1 FIT COUPON - SAMPLE REQUIRED",
    )


def refine_jack_fit_coupon(text: str) -> str:
    # The drawing shows 0.5 x 0.2 mm leads. The coupon uses 0.8 mm finished
    # holes and 1.1 x 1.8 mm pads so pins 1 and 5 retain 0.2 mm copper gap.
    text = text.replace(
        "(size 1.80 1.80) (drill 1.00)",
        "(size 1.10 1.80) (drill 0.80)",
    )
    text = re.sub(
        r'(\(pad "[2-6]" thru_hole) circle',
        r'\1 oval',
        text,
    )
    text = re.sub(
        r'^\s*\(fp_line .*?\(layer "F\.SilkS"\).*?\)\s*$',
        "",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r'(\(property "Reference".*?\(layer "F\.SilkS"\))',
        r'\1 (hide yes)',
        text,
        count=1,
    )
    return text.replace(
        "PRELIMINARY - COUPON REQUIRED",
        "A1 FIT COUPON - SAMPLE REQUIRED",
    )


def write_library() -> dict[str, str]:
    LIB_DIR.mkdir(parents=True, exist_ok=True)
    qfn64 = load_source("ak5558")
    qfn48 = load_source("ak4458")

    variants = {
        "ak5558_open": make_open_via_control(
            rename_footprint(qfn64, FOOTPRINT_NAMES["ak5558_open"])
        ),
        "ak5558_tented": rename_footprint(
            qfn64, FOOTPRINT_NAMES["ak5558_tented"]
        ),
        "ak5558_type7": rename_footprint(
            qfn64, FOOTPRINT_NAMES["ak5558_type7"]
        ),
        "ak4458_open": make_open_via_control(
            rename_footprint(qfn48, FOOTPRINT_NAMES["ak4458_open"])
        ),
        "ak4458_tented": rename_footprint(
            qfn48, FOOTPRINT_NAMES["ak4458_tented"]
        ),
        "ak4458_type7": rename_footprint(
            qfn48, FOOTPRINT_NAMES["ak4458_type7"]
        ),
        "relay": rename_footprint(
            refine_relay_fit_coupon(load_source("relay")),
            FOOTPRINT_NAMES["relay"],
            "TQ2-12V",
        ),
        "jack": rename_footprint(
            refine_jack_fit_coupon(load_source("jack")),
            FOOTPRINT_NAMES["jack"],
            "STX-353K7A-6N-KT-TR",
        ),
    }

    for key, content in variants.items():
        (LIB_DIR / f"{FOOTPRINT_NAMES[key]}.kicad_mod").write_text(
            content.rstrip() + "\n", encoding="utf-8"
        )
    return variants


def instantiate(text: str, library_name: str, ref: str, x: float, y: float) -> str:
    text = re.sub(
        r'^\(footprint "[^"]+"',
        f'(footprint "FootprintCoupon:{library_name}"',
        text,
        count=1,
    )
    text = re.sub(
        r'(\(layer "F\.Cu"\))[ \t]*\r?\n[ \t]*',
        rf'\1\n\t(uuid "{deterministic_uuid(ref)}")\n\t(at {x:g} {y:g})\n\t',
        text,
        count=1,
    )
    text = re.sub(
        r'(\(property "Reference"\s+")([^"]+)(")',
        rf'\g<1>{ref}\g<3>',
        text,
        count=1,
    )
    return "\n".join("\t" + line if line else line for line in text.splitlines())


def text_effects(size: float = 1.0, thickness: float = 0.15) -> str:
    return (
        f'(effects (font (size {size:g} {size:g}) '
        f'(thickness {thickness:g})))'
    )


def board_text(label: str, x: float, y: float, size: float = 1.0) -> str:
    escaped = label.replace('"', '\\"')
    return (
        f'\t(gr_text "{escaped}" (at {x:g} {y:g}) (layer "F.SilkS") '
        f'(uuid "{deterministic_uuid(f"text:{label}:{x:g}:{y:g}")}") '
        f'{text_effects(size)})'
    )


def drawing_text(label: str, x: float, y: float, size: float = 1.0) -> str:
    escaped = label.replace('"', '\\"')
    return (
        f'\t(gr_text "{escaped}" (at {x:g} {y:g}) (layer "Dwgs.User") '
        f'(uuid "{deterministic_uuid(f"drawing:{label}:{x:g}:{y:g}")}") '
        f'{text_effects(size)})'
    )


def tooling_hole(ref: str, x: float, y: float) -> str:
    return f'''\t(footprint "FootprintCoupon:TOOLING_HOLE_3P2"\n\t\t(layer "F.Cu")\n\t\t(uuid "{deterministic_uuid(ref)}")\n\t\t(at {x:g} {y:g})\n\t\t(attr exclude_from_pos_files exclude_from_bom)\n\t\t(property "Reference" "{ref}" (at 0 -3) (layer "F.Fab") (hide yes) {text_effects(0.8, 0.12)})\n\t\t(property "Value" "NPTH 3.2 mm" (at 0 3) (layer "F.Fab") (hide yes) {text_effects(0.8, 0.12)})\n\t\t(fp_circle (center 0 0) (end 2 0) (stroke (width 0.15) (type solid)) (fill none) (layer "F.SilkS"))\n\t\t(pad "" np_thru_hole circle (at 0 0) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask"))\n\t)'''


def fiducial(ref: str, x: float, y: float) -> str:
    return f'''\t(footprint "FootprintCoupon:FIDUCIAL_1MM"\n\t\t(layer "F.Cu")\n\t\t(uuid "{deterministic_uuid(ref)}")\n\t\t(at {x:g} {y:g})\n\t\t(attr smd exclude_from_pos_files exclude_from_bom)\n\t\t(property "Reference" "{ref}" (at 0 -2.2) (layer "F.Fab") (hide yes) {text_effects(0.7, 0.1)})\n\t\t(property "Value" "FIDUCIAL 1 mm" (at 0 2.2) (layer "F.Fab") (hide yes) {text_effects(0.7, 0.1)})\n\t\t(fp_circle (center 0 0) (end 1.5 0) (stroke (width 0.1) (type solid)) (fill none) (layer "F.Mask"))\n\t\t(pad "1" smd circle (at 0 0) (size 1 1) (layers "F.Cu" "F.Mask") (solder_mask_margin 0.5))\n\t)'''


def hole_gauge(x: float, y: float) -> str:
    pads = []
    labels = []
    for index, drill in enumerate((0.8, 0.9, 1.0, 1.1), start=1):
        px = (index - 2.5) * 4.0
        pads.append(
            f'\t\t(pad "{index}" thru_hole circle (at {px:g} 0) '
            f'(size {drill + 0.8:g} {drill + 0.8:g}) (drill {drill:g}) '
            '(layers "*.Cu" "*.Mask"))'
        )
        labels.append(
            f'\t\t(fp_text user "{drill:.1f}" (at {px:g} 2.4) '
            f'(layer "F.SilkS") {text_effects(0.8, 0.12)})'
        )
    header = (
        f'\t(footprint "FootprintCoupon:PTH_HOLE_GAUGE"\n'
        '\t\t(layer "F.Cu")\n'
        f'\t\t(uuid "{deterministic_uuid("HG1")}")\n'
        f'\t\t(at {x:g} {y:g})\n'
        '\t\t(attr through_hole exclude_from_pos_files exclude_from_bom)\n'
        f'\t\t(property "Reference" "HG1" (at 0 -2.4) (layer "F.SilkS") {text_effects(0.8, 0.12)})\n'
        f'\t\t(property "Value" "PTH 0.8/0.9/1.0/1.1" (at 0 4) (layer "F.Fab") (hide yes) {text_effects(0.8, 0.12)})\n'
    )
    return header + "\n".join(labels) + "\n" + "\n".join(pads) + "\n\t)"


def write_mechanical_library_footprints() -> None:
    footprints = {
        "TOOLING_HOLE_3P2": '''(footprint "TOOLING_HOLE_3P2"
  (version 20260206)
  (generator "radxa_cm5_coupon_generator")
  (layer "F.Cu")
  (attr exclude_from_pos_files exclude_from_bom)
  (property "Reference" "REF**" (at 0 -3) (layer "F.Fab") (hide yes) (effects (font (size 0.8 0.8) (thickness 0.12))))
  (property "Value" "NPTH 3.2 mm" (at 0 3) (layer "F.Fab") (hide yes) (effects (font (size 0.8 0.8) (thickness 0.12))))
  (fp_circle (center 0 0) (end 2 0) (stroke (width 0.15) (type solid)) (fill none) (layer "F.SilkS"))
  (pad "" np_thru_hole circle (at 0 0) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask"))
)
''',
        "FIDUCIAL_1MM": '''(footprint "FIDUCIAL_1MM"
  (version 20260206)
  (generator "radxa_cm5_coupon_generator")
  (layer "F.Cu")
  (attr smd exclude_from_pos_files exclude_from_bom)
  (property "Reference" "REF**" (at 0 -2.2) (layer "F.Fab") (hide yes) (effects (font (size 0.8 0.8) (thickness 0.12))))
  (property "Value" "FIDUCIAL 1 mm" (at 0 2.2) (layer "F.Fab") (hide yes) (effects (font (size 0.8 0.8) (thickness 0.12))))
  (fp_circle (center 0 0) (end 1.5 0) (stroke (width 0.1) (type solid)) (fill none) (layer "F.Mask"))
  (pad "1" smd circle (at 0 0) (size 1 1) (layers "F.Cu" "F.Mask") (solder_mask_margin 0.5))
)
''',
        "PTH_HOLE_GAUGE": '''(footprint "PTH_HOLE_GAUGE"
  (version 20260206)
  (generator "radxa_cm5_coupon_generator")
  (layer "F.Cu")
  (attr through_hole exclude_from_pos_files exclude_from_bom)
  (property "Reference" "REF**" (at 0 -2.4) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))
  (property "Value" "PTH 0.8/0.9/1.0/1.1" (at 0 4) (layer "F.Fab") (hide yes) (effects (font (size 0.8 0.8) (thickness 0.12))))
  (fp_text user "0.8" (at -6 2.4) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))
  (fp_text user "0.9" (at -2 2.4) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))
  (fp_text user "1.0" (at 2 2.4) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))
  (fp_text user "1.1" (at 6 2.4) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))
  (pad "1" thru_hole circle (at -6 0) (size 1.6 1.6) (drill 0.8) (layers "*.Cu" "*.Mask"))
  (pad "2" thru_hole circle (at -2 0) (size 1.7 1.7) (drill 0.9) (layers "*.Cu" "*.Mask"))
  (pad "3" thru_hole circle (at 2 0) (size 1.8 1.8) (drill 1.0) (layers "*.Cu" "*.Mask"))
  (pad "4" thru_hole circle (at 6 0) (size 1.9 1.9) (drill 1.1) (layers "*.Cu" "*.Mask"))
)
''',
    }
    for name, content in footprints.items():
        (LIB_DIR / f"{name}.kicad_mod").write_text(content, encoding="utf-8")


def board_header() -> str:
    return '''(kicad_pcb
\t(version 20260206)
\t(generator "radxa_cm5_coupon_generator")
\t(generator_version "1.0")
\t(general (thickness 1.6) (legacy_teardrops no))
\t(paper "A4")
\t(title_block
\t\t(title "Radxa CM5 ProComm Footprint Qualification Coupon A1")
\t\t(date "2026-08-16")
\t\t(rev "A1")
\t\t(company "ProComm / Omar Alabed")
\t\t(comment 1 "NOT FUNCTIONAL - PHYSICAL PROCESS QUALIFICATION ONLY")
\t)
\t(layers
\t\t(0 "F.Cu" signal)
\t\t(4 "In1.Cu" power)
\t\t(6 "In2.Cu" signal)
\t\t(8 "In3.Cu" signal)
\t\t(10 "In4.Cu" power)
\t\t(2 "B.Cu" signal)
\t\t(9 "F.Adhes" user "F.Adhesive")
\t\t(11 "B.Adhes" user "B.Adhesive")
\t\t(13 "F.Paste" user)
\t\t(15 "B.Paste" user)
\t\t(5 "F.SilkS" user "F.Silkscreen")
\t\t(7 "B.SilkS" user "B.Silkscreen")
\t\t(1 "F.Mask" user)
\t\t(3 "B.Mask" user)
\t\t(17 "Dwgs.User" user "User.Drawings")
\t\t(19 "Cmts.User" user "User.Comments")
\t\t(21 "Eco1.User" user "User.Eco1")
\t\t(23 "Eco2.User" user "User.Eco2")
\t\t(25 "Edge.Cuts" user)
\t\t(27 "Margin" user)
\t\t(31 "F.CrtYd" user "F.Courtyard")
\t\t(29 "B.CrtYd" user "B.Courtyard")
\t\t(35 "F.Fab" user)
\t\t(33 "B.Fab" user)
\t)
\t(setup
\t\t(stackup
\t\t\t(layer "F.SilkS" (type "Top Silk Screen"))
\t\t\t(layer "F.Paste" (type "Top Solder Paste"))
\t\t\t(layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
\t\t\t(layer "F.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 1" (type "prepreg") (thickness 0.11) (material "FR4") (epsilon_r 4.29) (loss_tangent 0.02))
\t\t\t(layer "In1.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 2" (type "core") (thickness 0.53) (material "FR4") (epsilon_r 3.96) (loss_tangent 0.02))
\t\t\t(layer "In2.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 3" (type "prepreg") (thickness 0.11) (material "FR4") (epsilon_r 4.29) (loss_tangent 0.02))
\t\t\t(layer "In3.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 4" (type "core") (thickness 0.53) (material "FR4") (epsilon_r 3.96) (loss_tangent 0.02))
\t\t\t(layer "In4.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 5" (type "prepreg") (thickness 0.11) (material "FR4") (epsilon_r 4.29) (loss_tangent 0.02))
\t\t\t(layer "B.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
\t\t\t(layer "B.Paste" (type "Bottom Solder Paste"))
\t\t\t(layer "B.SilkS" (type "Bottom Silk Screen"))
\t\t\t(copper_finish "ENIG")
\t\t\t(dielectric_constraints no)
\t\t)
\t\t(pad_to_mask_clearance 0)
\t\t(allow_soldermask_bridges_in_footprints no)
\t\t(tenting (front yes) (back yes))
\t\t(covering (front no) (back no))
\t\t(plugging (front no) (back no))
\t\t(capping no)
\t\t(filling no)
\t)
'''


def extract_thermal_vias(text: str, ep_number: str) -> list[tuple[float, float]]:
    pattern = re.compile(
        rf'\(pad "{ep_number}" thru_hole circle\s+\(at ([+-]?[0-9.]+) ([+-]?[0-9.]+)\).*?\(drill 0\.2\)',
        re.DOTALL,
    )
    return [(float(x), float(y)) for x, y in pattern.findall(text)]


def write_filled_vias(variants: dict[str, str]) -> None:
    rows = []
    for ref, key, ep, origin, package in (
        ("U103", "ak5558_type7", "65", (98.0, 43.0), "AK5558VN QFN-64"),
        ("U203", "ak4458_type7", "49", (98.0, 69.0), "AK4458VN QFN-48"),
    ):
        for index, (dx, dy) in enumerate(extract_thermal_vias(variants[key], ep), 1):
            rows.append(
                {
                    "reference": ref,
                    "package": package,
                    "via_index": index,
                    "x_mm": f"{origin[0] + dx:.4f}",
                    "y_mm": f"{origin[1] + dy:.4f}",
                    "finished_hole_mm": "0.20",
                    "treatment": "IPC-4761 Type VII resin filled and copper capped",
                }
            )
    with VIA_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def write_project() -> None:
    project = {
        "board": {
            "design_settings": {
                "rules": {
                    "min_clearance": 0.1,
                    "min_copper_edge_clearance": 0.25,
                    "min_hole_to_hole": 0.25,
                    "min_through_hole_diameter": 0.2,
                    "min_via_annular_width": 0.15,
                }
            }
        },
        "meta": {"filename": "Footprint-Coupon.kicad_pro", "version": 1},
        "net_settings": {"classes": [], "meta": {"version": 3}},
    }
    PROJECT_PATH.write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8")


def write_board(variants: dict[str, str]) -> None:
    placements = (
        ("ak5558_open", "U101", 42, 43),
        ("ak5558_tented", "U102", 70, 43),
        ("ak5558_type7", "U103", 98, 43),
        ("ak4458_open", "U201", 42, 69),
        ("ak4458_tented", "U202", 70, 69),
        ("ak4458_type7", "U203", 98, 69),
        ("relay", "K1", 43, 89),
        ("jack", "J1", 70, 87),
    )
    items = [board_header()]
    for key, ref, x, y in placements:
        items.append(
            instantiate(variants[key], FOOTPRINT_NAMES[key], ref, float(x), float(y))
        )

    for ref, x, y in (
        ("H1", 24, 24),
        ("H2", 116, 24),
        ("H3", 24, 96),
        ("H4", 116, 96),
    ):
        items.append(tooling_hole(ref, x, y))
    for ref, x, y in (("FID1", 29, 27), ("FID2", 111, 27), ("FID3", 111, 93)):
        items.append(fiducial(ref, x, y))
    items.append(hole_gauge(99, 88))

    items.extend(
        [
            board_text("RADXA CM5 PROCOMM - FOOTPRINT COUPON A1", 70, 24, 1.2),
            board_text("NOT FUNCTIONAL | 6L 1.6 mm ENIG | 2026-08-16", 70, 27, 0.8),
            board_text("AK5558VN QFN-64 9x9 P0.5 EP6x6", 70, 33, 0.9),
            board_text("OPEN CONTROL", 42, 35.5, 0.8),
            board_text("BOTTOM TENTED", 70, 35.5, 0.8),
            board_text("TYPE VII FILLED/CAPPED", 98, 35.5, 0.8),
            board_text("AK4458VN QFN-48 7x7 P0.5 EP5.15", 70, 59, 0.9),
            board_text("OPEN CONTROL", 42, 61.5, 0.8),
            board_text("BOTTOM TENTED", 70, 61.5, 0.8),
            board_text("TYPE VII FILLED/CAPPED", 98, 61.5, 0.8),
            board_text("TQ2-12V FIT / PIN MAP", 43, 81.5, 0.8),
            board_text("KYCON CTIA JACK FIT", 81, 77, 0.8),
            board_text("PTH FINISHED-HOLE GAUGE", 99, 81.5, 0.8),
            board_text("ASSEMBLE 3 BOARDS MINIMUM - X-RAY ALL AKM SITES", 70, 97, 0.8),
            drawing_text(
                "OUTLINE 100.00 x 80.00 mm | 6 LAYERS | 1.60 mm | ENIG",
                70,
                104,
                1.0,
            ),
            drawing_text(
                "SELECTIVE TYPE VII: U103/U203 ONLY, 25 x 0.20 mm FINISHED VIAS EACH",
                70,
                107,
                0.85,
            ),
            drawing_text(
                "K1: 8 x 0.90 mm FINISHED | J1: 6 x 0.80 mm FINISHED",
                70,
                110,
                0.85,
            ),
            '\t(gr_rect (start 20 20) (end 120 100) (stroke (width 0.25) (type solid)) (fill none) (layer "Edge.Cuts") (uuid "'
            + deterministic_uuid("board-outline")
            + '"))',
            '\t(gr_rect (start 30 30) (end 110 54) (stroke (width 0.15) (type dash)) (fill none) (layer "Dwgs.User") (uuid "'
            + deterministic_uuid("qfn64-zone")
            + '"))',
            '\t(gr_rect (start 30 56) (end 110 80) (stroke (width 0.15) (type dash)) (fill none) (layer "Dwgs.User") (uuid "'
            + deterministic_uuid("qfn48-zone")
            + '"))',
            ")\n",
        ]
    )
    BOARD_PATH.write_text("\n".join(items), encoding="utf-8")


def write_tables() -> None:
    (COUPON_DIR / "fp-lib-table").write_text(
        '(fp_lib_table\n  (lib (name "FootprintCoupon")(type "KiCad")'
        '(uri "${KIPRJMOD}/FootprintCoupon.pretty")(options "")(descr "A1 qualification coupon footprints"))\n)\n',
        encoding="utf-8",
    )


def main() -> None:
    variants = write_library()
    write_mechanical_library_footprints()
    write_board(variants)
    write_project()
    write_filled_vias(variants)
    write_tables()
    print(f"Generated {BOARD_PATH.relative_to(ROOT)}")
    print(f"Generated {len(variants)} controlled footprint variants")


if __name__ == "__main__":
    main()
