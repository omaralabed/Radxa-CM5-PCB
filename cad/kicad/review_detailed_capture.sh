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

review_sheet "${SCRIPT_DIR}/PWR-SELECT/PowerSelector.kicad_sch" "PowerSelector-A0"
review_sheet "${SCRIPT_DIR}/CM5-CARRIER/CM5-Carrier.kicad_sch" "CM5-Carrier-A1"
review_sheet "${SCRIPT_DIR}/CM5-CARRIER/CM5-Core-Allocated.kicad_sch" "CM5-Core-Allocated-A1"
review_sheet "${SCRIPT_DIR}/CM5-CARRIER/Network-PCIe.kicad_sch" "Network-PCIe-A1"
review_sheet "${SCRIPT_DIR}/CM5-CARRIER/WWAN-SIM.kicad_sch" "WWAN-SIM-A1"
review_sheet "${SCRIPT_DIR}/CM5-CARRIER/Display-Harness.kicad_sch" "Display-Harness-A1"
review_sheet "${SCRIPT_DIR}/CM5-CARRIER/Audio-Control.kicad_sch" "Audio-Control-A1"
review_sheet "${SCRIPT_DIR}/CM5-CARRIER/Power-Regulators-A1.kicad_sch" "Power-Regulators-A1"

POWER_ERC="${SCRIPT_DIR}/CM5-CARRIER/REVIEW/Power-Regulators-A1-ERC.rpt"
if rg -q '^\[(multiple_net_names|pin_not_driven|power_pin_not_driven|pin_to_pin|label_dangling|wire_dangling)\]' "${POWER_ERC}"; then
    printf 'Power-sheet ERC contains a real connectivity warning: %s\n' "${POWER_ERC}" >&2
    exit 1
fi

review_sheet "${SCRIPT_DIR}/CM5-CARRIER/Thermal-IO.kicad_sch" "Thermal-IO-A1"
review_sheet "${SCRIPT_DIR}/AUDIO-8X8/Audio-8x8.kicad_sch" "Audio-8x8-A1"

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
    --output "${REVIEW_TMP}/Audio-8x8-A1.xml" \
    "${SCRIPT_DIR}/AUDIO-8X8/Audio-8x8.kicad_sch"

install_xml_if_changed "${REVIEW_TMP}/PowerSelector-A0.xml" \
    "${SCRIPT_DIR}/PWR-SELECT/REVIEW/PowerSelector-A0.xml"
install_xml_if_changed "${REVIEW_TMP}/CM5-Carrier-A1.xml" \
    "${SCRIPT_DIR}/CM5-CARRIER/REVIEW/CM5-Carrier-A1.xml"
install_xml_if_changed "${REVIEW_TMP}/Thermal-IO-A1.xml" \
    "${SCRIPT_DIR}/CM5-CARRIER/REVIEW/Thermal-IO-A1.xml"
install_xml_if_changed "${REVIEW_TMP}/Audio-8x8-A1.xml" \
    "${SCRIPT_DIR}/AUDIO-8X8/REVIEW/Audio-8x8-A1.xml"

python3 "${SCRIPT_DIR}/PWR-SELECT/validate_power_selector.py"
python3 "${SCRIPT_DIR}/CM5-CARRIER/validate_power_regulators.py"
python3 "${SCRIPT_DIR}/validate_interface_contracts.py"

printf 'Detailed capture review passed: all ten sheets have zero ERC errors.\n'
