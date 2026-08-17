#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
KICAD_CLI="${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
PYTHONPATH="${PYTHONPATH:-/tmp/radxa-cm5-kicad-deps}"
export PYTHONPATH

if ! command -v pdftoppm >/dev/null 2>&1; then
    printf 'Missing required PDF renderer: pdftoppm\n' >&2
    exit 1
fi
if ! command -v pdfinfo >/dev/null 2>&1; then
    printf 'Missing required PDF inspector: pdfinfo\n' >&2
    exit 1
fi

REVIEW_TMP="$(mktemp -d "${TMPDIR:-/tmp}/radxa-cm5-review.XXXXXX")"
trap 'rm -rf "${REVIEW_TMP}"' EXIT

install_report_if_changed() {
    local source="$1"
    local destination="$2"
    if [[ -f "${destination}" ]] && cmp -s \
        <(sed -E '1s/ERC report \([^,]+,/ERC report (NORMALIZED,/' "${source}") \
        <(sed -E '1s/ERC report \([^,]+,/ERC report (NORMALIZED,/' "${destination}"); then
        return
    fi
    mv "${source}" "${destination}"
}

install_xml_if_changed() {
    local source="$1"
    local destination="$2"
    if [[ -f "${destination}" ]] && cmp -s \
        <(sed -E 's#<date>[^<]+</date>#<date>NORMALIZED</date>#' "${source}") \
        <(sed -E 's#<date>[^<]+</date>#<date>NORMALIZED</date>#' "${destination}"); then
        return
    fi
    mv "${source}" "${destination}"
}

pdf_visual_hash() {
    local source="$1"
    local stem="$2"
    local render_dir="${REVIEW_TMP}/${stem}"
    mkdir -p "${render_dir}"
    pdftoppm -r 96 "${source}" "${render_dir}/page" >/dev/null 2>&1
    shasum -a 256 "${render_dir}"/page-*.ppm | awk '{print $1}' | shasum -a 256 | awk '{print $1}'
}

install_pdf_if_changed() {
    local source="$1"
    local destination="$2"
    local stem="$3"
    if [[ -f "${destination}" ]]; then
        local new_hash old_hash
        new_hash="$(pdf_visual_hash "${source}" "${stem}-new")"
        old_hash="$(pdf_visual_hash "${destination}" "${stem}-old")"
        if [[ "${new_hash}" == "${old_hash}" ]]; then
            return
        fi
    fi
    mv "${source}" "${destination}"
}

python3 "${SCRIPT_DIR}/generate_interface_schematics.py"
python3 "${SCRIPT_DIR}/PWR-SELECT/generate_power_selector.py"
python3 "${SCRIPT_DIR}/SYSTEM/generate_system_schematic.py"

review_sheet() {
    local schematic="$1"
    local review_stem="$2"
    local review_dir
    local report_tmp pdf_tmp
    review_dir="$(dirname "${schematic}")/REVIEW"
    mkdir -p "${review_dir}"
    report_tmp="${REVIEW_TMP}/${review_stem}-ERC.rpt"
    pdf_tmp="${REVIEW_TMP}/${review_stem}.pdf"

    "${KICAD_CLI}" sch erc --format report --units mm \
        --output "${report_tmp}" "${schematic}"
    "${KICAD_CLI}" sch export pdf \
        --output "${pdf_tmp}" "${schematic}"

    if ! rg -q "Errors 0" "${report_tmp}"; then
        printf 'ERC failure: %s\n' "${schematic}" >&2
        exit 1
    fi
    install_report_if_changed "${report_tmp}" "${review_dir}/${review_stem}-ERC.rpt"
    install_pdf_if_changed "${pdf_tmp}" "${review_dir}/${review_stem}.pdf" "${review_stem}"
}

review_child_sheet() {
    local schematic="$1"
    local review_stem="$2"
    local review_dir report_tmp pdf_tmp
    review_dir="$(dirname "${schematic}")/REVIEW"
    mkdir -p "${review_dir}"
    report_tmp="${REVIEW_TMP}/${review_stem}-ERC.rpt"
    pdf_tmp="${REVIEW_TMP}/${review_stem}.pdf"

    "${KICAD_CLI}" sch erc --format report --units mm \
        --output "${report_tmp}" "${schematic}"
    "${KICAD_CLI}" sch export pdf \
        --output "${pdf_tmp}" "${schematic}"

    python3 - "${report_tmp}" "${review_stem}" <<'PY'
from pathlib import Path
import re
import sys

report = Path(sys.argv[1]).read_text()
stem = sys.argv[2]
expected = {
    "Network-PCIe-A1": {
        ("pin_not_driven", "U606", "1"),
        ("pin_not_driven", "U606", "3"),
        ("pin_not_driven", "U606", "6"),
        ("power_pin_not_driven", "U606", "2"),
        ("power_pin_not_driven", "U606", "5"),
    },
    "Thermal-IO-A1": {
        ("power_pin_not_driven", "U1000", "1"),
    },
    "WWAN-SIM-A1": {
        ("power_pin_not_driven", "J701", "3"),
    },
    "Display-Harness-A1": {
        ("power_pin_not_driven", "J801", "2"),
    },
    "Audio-Control-A1": {
        ("power_pin_not_driven", "U901", "4"),
        ("power_pin_not_driven", "U901", "5"),
        ("power_pin_not_driven", "U910", "1"),
    },
    "Audio-TDM-Clock-A1": {
        ("power_pin_not_driven", "U101", "5"),
        ("power_pin_not_driven", "U101", "8"),
        ("pin_not_driven", "U105", "2"),
        ("pin_not_driven", "U106", "3"),
        ("pin_not_driven", "U106", "6"),
    },
    "Audio-Outputs-A1": {
        ("pin_not_driven", "Q501", "1"),
    },
}[stem]

actual = set()
current_rule = None
current_is_error = False
for line in report.splitlines():
    rule = re.match(r"^\[([^]]+)\]", line)
    if rule:
        current_rule = rule.group(1)
        current_is_error = False
        continue
    if line.strip() == "; error":
        current_is_error = True
        continue
    if current_rule and current_is_error:
        pin = re.search(r"Symbol\s+(\S+)\s+Pin\s+(\S+)\s+\[", line)
        if pin:
            actual.add((current_rule, pin.group(1), pin.group(2)))

if actual != expected:
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    raise SystemExit(
        f"{stem} child-context ERC mismatch; missing={missing}, unexpected={unexpected}"
    )
print(f"PASS: {stem} has only {len(expected)} explicitly allowed off-sheet-context ERC findings")
PY

    install_report_if_changed "${report_tmp}" "${review_dir}/${review_stem}-ERC.rpt"
    install_pdf_if_changed "${pdf_tmp}" "${review_dir}/${review_stem}.pdf" "${review_stem}"
}

review_sheet "${SCRIPT_DIR}/PWR-SELECT/PowerSelector.kicad_sch" "PowerSelector-A0"
review_sheet "${SCRIPT_DIR}/CM5-CARRIER/CM5-Carrier.kicad_sch" "CM5-Carrier-A1"
review_sheet "${SCRIPT_DIR}/CM5-CARRIER/CM5-Core-Allocated.kicad_sch" "CM5-Core-Allocated-A1"
review_child_sheet "${SCRIPT_DIR}/CM5-CARRIER/Network-PCIe.kicad_sch" "Network-PCIe-A1"
review_child_sheet "${SCRIPT_DIR}/CM5-CARRIER/WWAN-SIM.kicad_sch" "WWAN-SIM-A1"
review_child_sheet "${SCRIPT_DIR}/CM5-CARRIER/Display-Harness.kicad_sch" "Display-Harness-A1"
review_child_sheet "${SCRIPT_DIR}/CM5-CARRIER/Audio-Control.kicad_sch" "Audio-Control-A1"
review_sheet "${SCRIPT_DIR}/CM5-CARRIER/Power-Regulators-A1.kicad_sch" "Power-Regulators-A1"

POWER_ERC="${SCRIPT_DIR}/CM5-CARRIER/REVIEW/Power-Regulators-A1-ERC.rpt"
if rg -q '^\[(multiple_net_names|pin_not_driven|power_pin_not_driven|pin_to_pin|label_dangling|wire_dangling)\]' "${POWER_ERC}"; then
    printf 'Power-sheet ERC contains a real connectivity warning: %s\n' "${POWER_ERC}" >&2
    exit 1
fi

review_child_sheet "${SCRIPT_DIR}/CM5-CARRIER/Thermal-IO.kicad_sch" "Thermal-IO-A1"
review_sheet "${SCRIPT_DIR}/SIM-SERVICE/Sim-Service.kicad_sch" "Sim-Service-A1"
review_sheet "${SCRIPT_DIR}/AUDIO-8X8/Audio-8x8.kicad_sch" "Audio-8x8-A1"
review_child_sheet "${SCRIPT_DIR}/AUDIO-8X8/Audio-TDM-Clock.kicad_sch" "Audio-TDM-Clock-A1"
review_sheet "${SCRIPT_DIR}/AUDIO-8X8/AK5558-ADC.kicad_sch" "AK5558-ADC-A1"
review_sheet "${SCRIPT_DIR}/AUDIO-8X8/AK4458-DAC.kicad_sch" "AK4458-DAC-A1"
review_sheet "${SCRIPT_DIR}/AUDIO-8X8/Audio-Inputs.kicad_sch" "Audio-Inputs-A1"
review_child_sheet "${SCRIPT_DIR}/AUDIO-8X8/Audio-Outputs.kicad_sch" "Audio-Outputs-A1"
review_sheet "${SCRIPT_DIR}/AUDIO-8X8/Audio-Power.kicad_sch" "Audio-Power-A1"

"${KICAD_CLI}" sch export netlist --format kicadxml \
    --output "${REVIEW_TMP}/PowerSelector-A0.xml" \
    "${SCRIPT_DIR}/PWR-SELECT/PowerSelector.kicad_sch"
"${KICAD_CLI}" sch export netlist --format kicadxml \
    --output "${REVIEW_TMP}/CM5-Carrier-A1.xml" \
    "${SCRIPT_DIR}/CM5-CARRIER/CM5-Carrier.kicad_sch"
"${KICAD_CLI}" sch export netlist --format kicadxml \
    --output "${REVIEW_TMP}/Thermal-IO-A1.xml" \
    "${SCRIPT_DIR}/CM5-CARRIER/Thermal-IO.kicad_sch"
"${KICAD_CLI}" sch export netlist --format kicadxml \
    --output "${REVIEW_TMP}/Audio-Control-A1.xml" \
    "${SCRIPT_DIR}/CM5-CARRIER/Audio-Control.kicad_sch"
"${KICAD_CLI}" sch export netlist --format kicadxml \
    --output "${REVIEW_TMP}/Sim-Service-A1.xml" \
    "${SCRIPT_DIR}/SIM-SERVICE/Sim-Service.kicad_sch"
"${KICAD_CLI}" sch export netlist --format kicadxml \
    --output "${REVIEW_TMP}/Audio-8x8-A1.xml" \
    "${SCRIPT_DIR}/AUDIO-8X8/Audio-8x8.kicad_sch"
for sheet in Audio-TDM-Clock AK5558-ADC AK4458-DAC Audio-Inputs Audio-Outputs Audio-Power; do
    "${KICAD_CLI}" sch export netlist --format kicadxml \
        --output "${REVIEW_TMP}/${sheet}-A1.xml" \
        "${SCRIPT_DIR}/AUDIO-8X8/${sheet}.kicad_sch"
done

install_xml_if_changed "${REVIEW_TMP}/PowerSelector-A0.xml" \
    "${SCRIPT_DIR}/PWR-SELECT/REVIEW/PowerSelector-A0.xml"
install_xml_if_changed "${REVIEW_TMP}/CM5-Carrier-A1.xml" \
    "${SCRIPT_DIR}/CM5-CARRIER/REVIEW/CM5-Carrier-A1.xml"
install_xml_if_changed "${REVIEW_TMP}/Thermal-IO-A1.xml" \
    "${SCRIPT_DIR}/CM5-CARRIER/REVIEW/Thermal-IO-A1.xml"
install_xml_if_changed "${REVIEW_TMP}/Audio-Control-A1.xml" \
    "${SCRIPT_DIR}/CM5-CARRIER/REVIEW/Audio-Control-A1.xml"
install_xml_if_changed "${REVIEW_TMP}/Sim-Service-A1.xml" \
    "${SCRIPT_DIR}/SIM-SERVICE/REVIEW/Sim-Service-A1.xml"
install_xml_if_changed "${REVIEW_TMP}/Audio-8x8-A1.xml" \
    "${SCRIPT_DIR}/AUDIO-8X8/REVIEW/Audio-8x8-A1.xml"
for sheet in Audio-TDM-Clock AK5558-ADC AK4458-DAC Audio-Inputs Audio-Outputs Audio-Power; do
    install_xml_if_changed "${REVIEW_TMP}/${sheet}-A1.xml" \
        "${SCRIPT_DIR}/AUDIO-8X8/REVIEW/${sheet}-A1.xml"
done

python3 "${SCRIPT_DIR}/export_schematic_bom.py" \
    --schematic "${SCRIPT_DIR}/PWR-SELECT/PowerSelector.kicad_sch" \
    --output "${PROJECT_ROOT}/docs/power_selector_bom_a1.csv"
python3 "${SCRIPT_DIR}/export_schematic_bom.py" \
    --schematic "${SCRIPT_DIR}/CM5-CARRIER/Power-Regulators-A1.kicad_sch" \
    --output "${PROJECT_ROOT}/docs/power_regulator_bom_a1.csv" \
    --exclude TP1190 \
    --exclude TP1191 \
    --exclude TP1192 \
    --exclude TP1193 \
    --exclude TP1194 \
    --exclude TP1195
python3 "${SCRIPT_DIR}/export_schematic_bom.py" \
    --schematic "${SCRIPT_DIR}/CM5-CARRIER/Thermal-IO.kicad_sch" \
    --output "${PROJECT_ROOT}/docs/thermal_io_bom_a1.csv" \
    --exclude TP1001 \
    --exclude TP1002 \
    --exclude TP1003
python3 "${SCRIPT_DIR}/export_schematic_bom.py" \
    --schematic "${SCRIPT_DIR}/CM5-CARRIER/Network-PCIe.kicad_sch" \
    --output "${PROJECT_ROOT}/docs/network_pcie_bom_a1.csv"
python3 "${SCRIPT_DIR}/export_schematic_bom.py" \
    --schematic "${SCRIPT_DIR}/CM5-CARRIER/WWAN-SIM.kicad_sch" \
    --output "${PROJECT_ROOT}/docs/wwan_sim_bom_a1.csv" \
    --exclude TP7201 \
    --exclude TP7202 \
    --exclude TP7203 \
    --exclude TP7204 \
    --exclude TP7205 \
    --exclude TP7206 \
    --exclude TP7207 \
    --exclude TP7208
python3 "${SCRIPT_DIR}/export_schematic_bom.py" \
    --schematic "${SCRIPT_DIR}/CM5-CARRIER/Display-Harness.kicad_sch" \
    --output "${PROJECT_ROOT}/docs/display_harness_bom_a1.csv"
python3 "${SCRIPT_DIR}/export_schematic_bom.py" \
    --schematic "${SCRIPT_DIR}/CM5-CARRIER/Audio-Control.kicad_sch" \
    --output "${PROJECT_ROOT}/docs/audio_control_bom_a1.csv" \
    --exclude U900
python3 "${SCRIPT_DIR}/export_schematic_bom.py" \
    --schematic "${SCRIPT_DIR}/SIM-SERVICE/Sim-Service.kicad_sch" \
    --output "${PROJECT_ROOT}/docs/sim_service_bom_a1.csv"
python3 "${SCRIPT_DIR}/PWR-SELECT/validate_power_selector.py"
python3 "${SCRIPT_DIR}/CM5-CARRIER/validate_cm5_pin_allocation.py"
python3 "${SCRIPT_DIR}/CM5-CARRIER/validate_power_regulators.py"
python3 "${SCRIPT_DIR}/CM5-CARRIER/validate_thermal_io.py"
python3 "${SCRIPT_DIR}/CM5-CARRIER/validate_network_pcie.py"
python3 "${SCRIPT_DIR}/CM5-CARRIER/validate_wwan_sim.py"
python3 "${SCRIPT_DIR}/CM5-CARRIER/validate_display_harness.py"
python3 "${SCRIPT_DIR}/CM5-CARRIER/validate_audio_control.py"
python3 "${SCRIPT_DIR}/SIM-SERVICE/validate_sim_service.py"
python3 "${SCRIPT_DIR}/AUDIO-8X8/export_audio_8x8_bom.py"
python3 "${SCRIPT_DIR}/AUDIO-8X8/validate_audio_8x8.py"
python3 "${SCRIPT_DIR}/validate_interface_contracts.py"
python3 "${SCRIPT_DIR}/SYSTEM/validate_system_schematic.py"
python3 "${SCRIPT_DIR}/audit_footprint_readiness.py"

SYSTEM_PDF="${REVIEW_TMP}/Radxa-CM5-ProComm-System.pdf"
"${KICAD_CLI}" sch export pdf \
    --output "${SYSTEM_PDF}" \
    "${SCRIPT_DIR}/SYSTEM/Radxa-CM5-ProComm-System.kicad_sch"
if [[ "$(pdfinfo "${SYSTEM_PDF}" | awk '/^Pages:/ {print $2}')" != "18" ]]; then
    printf 'Complete-system schematic export does not contain 18 pages.\n' >&2
    exit 1
fi

printf 'Detailed capture review passed: connected board roots have zero ERC errors; child-sheet context findings match the explicit allowlist; the system project exports 18 pages.\n'
