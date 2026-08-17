#!/usr/bin/env python3
"""Build a checksum-controlled PCBWay archive after all release gates pass."""

from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "release-manifest-a0.csv"
OUTPUT = HERE / "output"
ARCHIVE = OUTPUT / "Radxa-CM5-ProComm-PCBWay-A0.zip"
CHECKSUMS = OUTPUT / "SHA256SUMS.txt"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    result = subprocess.run(
        [sys.executable, str(HERE / "validate_release.py"), "--release"],
        check=False,
    )
    if result.returncode:
        return result.returncode

    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    files = [
        (HERE / row["path_or_pattern"]).resolve()
        for row in rows
        if row["required"] == "YES" and row["state"] == "READY"
    ]
    files.extend([MANIFEST, HERE / "README.md"])

    OUTPUT.mkdir(exist_ok=True)
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(set(files)):
            archive.write(path, path.relative_to(HERE.parent.parent))

    CHECKSUMS.write_text(
        f"{sha256(ARCHIVE)}  {ARCHIVE.name}\n", encoding="ascii"
    )
    print(ARCHIVE)
    print(CHECKSUMS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

