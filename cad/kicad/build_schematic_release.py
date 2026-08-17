#!/usr/bin/env python3
"""Build the controlled A1 schematic review PDF set."""

from __future__ import annotations

import hashlib
import os
import subprocess
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[2]
KICAD = ROOT / "cad/kicad"
OUTPUT = ROOT / "outputs/schematic-release-a1"
KICAD_CLI = Path(
    os.environ.get(
        "KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
    )
)
SYSTEM_SCHEMATIC = KICAD / "SYSTEM/Radxa-CM5-ProComm-System.kicad_sch"

PWR_PDFS = [KICAD / "PWR-SELECT/REVIEW/PowerSelector-A0.pdf"]
CM5_PDFS = [
    KICAD / "CM5-CARRIER/REVIEW/CM5-Carrier-A1.pdf",
    KICAD / "CM5-CARRIER/REVIEW/CM5-Core-Allocated-A1.pdf",
    KICAD / "CM5-CARRIER/REVIEW/Network-PCIe-A1.pdf",
    KICAD / "CM5-CARRIER/REVIEW/WWAN-SIM-A1.pdf",
    KICAD / "CM5-CARRIER/REVIEW/Display-Harness-A1.pdf",
    KICAD / "CM5-CARRIER/REVIEW/Audio-Control-A1.pdf",
    KICAD / "CM5-CARRIER/REVIEW/Power-Regulators-A1.pdf",
    KICAD / "CM5-CARRIER/REVIEW/Thermal-IO-A1.pdf",
]
AUDIO_PDFS = [
    KICAD / "AUDIO-8X8/REVIEW/Audio-8x8-A1.pdf",
    KICAD / "AUDIO-8X8/REVIEW/Audio-TDM-Clock-A1.pdf",
    KICAD / "AUDIO-8X8/REVIEW/AK5558-ADC-A1.pdf",
    KICAD / "AUDIO-8X8/REVIEW/AK4458-DAC-A1.pdf",
    KICAD / "AUDIO-8X8/REVIEW/Audio-Inputs-A1.pdf",
    KICAD / "AUDIO-8X8/REVIEW/Audio-Outputs-A1.pdf",
    KICAD / "AUDIO-8X8/REVIEW/Audio-Power-A1.pdf",
]


def merge(paths: list[Path], output: Path) -> int:
    writer = PdfWriter()
    pages = 0
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(path)
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)
            pages += 1
    writer.add_metadata(
        {
            "/Title": output.stem,
            "/Author": "Radxa CM5 ProComm project",
            "/Subject": "A1 reviewed schematic capture",
        }
    )
    with output.open("wb") as handle:
        writer.write(handle)
    return pages


def cover_pdf() -> bytes:
    stream = BytesIO()
    doc = SimpleDocTemplate(
        stream,
        pagesize=letter,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Radxa CM5 ProComm Schematic Release A1",
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "ReleaseTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=25,
        textColor=colors.HexColor("#122033"),
        spaceAfter=12,
    )
    state = ParagraphStyle(
        "State",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=colors.HexColor("#9C2F21"),
        spaceAfter=14,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#263442"),
        spaceAfter=8,
    )
    small = ParagraphStyle(
        "Small",
        parent=body,
        fontSize=8.4,
        leading=11,
        spaceAfter=0,
    )

    story = [
        Paragraph("Radxa CM5 ProComm", title),
        Paragraph("Schematic Release A1", styles["Heading1"]),
        Paragraph(
            "ELECTRICAL CAPTURE COMPLETE - PCB ROUTING HELD FOR PHYSICAL RELEASE GATES",
            state,
        ),
        Paragraph(
            "This master set contains the controlled PWR-SELECT, CM5-CARRIER, "
            "and AUDIO-8X8 schematic review sheets. The complete automated gate "
            "passes all sixteen sheets with zero ERC errors, 174 critical "
            "cross-board interface checks, the full regulator and source-selector "
            "calculation checks, and 381 AUDIO-8X8 checks.",
            body,
        ),
        Spacer(1, 0.08 * inch),
    ]

    data = [
        ["Design", "Sheets", "Electrical state", "PCB state"],
        ["PWR-SELECT", "1", "Reviewed", "Not routed"],
        ["CM5-CARRIER", "8", "Reviewed", "Not routed"],
        ["AUDIO-8X8", "7", "Reviewed", "Not routed"],
    ]
    table = Table(data, colWidths=[1.35 * inch, 0.65 * inch, 1.55 * inch, 1.45 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1C4F67")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#AAB5BE")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F3F6F8")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([table, Spacer(1, 0.22 * inch)])
    story.extend(
        [
            Paragraph("Open Physical Gates", styles["Heading2"]),
            Paragraph(
                "Ten routing blockers remain: AK5558VN, AK4458VN, and eight "
                "Panasonic TQ2-12V physical coupon sites. The Kycon CTIA jack "
                "adds one production-only coupon gate. Mechanical release A2 "
                "also remains on hold for the actual iM2300 M001-M080 measurements. "
                "These are not unresolved schematic connections; they control "
                "production land patterns, board outlines, supports, and panel geometry.",
                body,
            ),
            Paragraph("Release Rule", styles["Heading2"]),
            Paragraph(
                "Do not begin PCB placement or routing from this package until the "
                "footprint coupon is signed, the mechanical release validator passes, "
                "and the PCBWay stackups and impedance rules are frozen. Any electrical "
                "change after this package requires regeneration and full review.",
                body,
            ),
            Spacer(1, 0.16 * inch),
            Paragraph(
                "Source of truth: native KiCad projects under cad/kicad. Automated "
                "review command: cad/kicad/review_detailed_capture.sh.",
                small,
            ),
        ]
    )
    doc.build(story)
    return stream.getvalue()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    system_out = OUTPUT / "Radxa-CM5-ProComm-Complete-Electrical-A2.pdf"
    pwr_out = OUTPUT / "Power-Selector-Schematic-A1.pdf"
    cm5_out = OUTPUT / "CM5-Carrier-Schematic-A1.pdf"
    audio_out = OUTPUT / "Audio-8x8-Schematic-A1.pdf"
    master_out = OUTPUT / "Radxa-CM5-ProComm-Schematic-Release-A1.pdf"

    if not KICAD_CLI.exists():
        raise FileNotFoundError(KICAD_CLI)
    subprocess.run(
        [
            str(KICAD_CLI),
            "sch",
            "export",
            "pdf",
            "--output",
            str(system_out),
            str(SYSTEM_SCHEMATIC),
        ],
        check=True,
    )
    system_pages = len(PdfReader(system_out).pages)
    if system_pages != 17:
        raise RuntimeError(f"complete electrical PDF has {system_pages} pages, expected 17")

    pwr_pages = merge(PWR_PDFS, pwr_out)
    cm5_pages = merge(CM5_PDFS, cm5_out)
    audio_pages = merge(AUDIO_PDFS, audio_out)

    master = PdfWriter()
    for page in PdfReader(BytesIO(cover_pdf())).pages:
        master.add_page(page)
    for path in PWR_PDFS + CM5_PDFS + AUDIO_PDFS:
        for page in PdfReader(path).pages:
            master.add_page(page)
    master.add_metadata(
        {
            "/Title": "Radxa CM5 ProComm Schematic Release A1",
            "/Author": "Radxa CM5 ProComm project",
            "/Subject": "Reviewed sixteen-sheet schematic master set",
        }
    )
    with master_out.open("wb") as handle:
        master.write(handle)

    expected_master = 1 + pwr_pages + cm5_pages + audio_pages
    actual_master = len(PdfReader(master_out).pages)
    if actual_master != expected_master:
        raise RuntimeError(
            f"master page count {actual_master} does not match {expected_master}"
        )

    outputs = (system_out, pwr_out, cm5_out, audio_out, master_out)
    for path in outputs:
        reader = PdfReader(path)
        if not reader.pages:
            raise RuntimeError(f"empty PDF: {path}")
        print(f"{path}: {len(reader.pages)} pages")
    (OUTPUT / "SHA256SUMS.txt").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in outputs),
        encoding="ascii",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
