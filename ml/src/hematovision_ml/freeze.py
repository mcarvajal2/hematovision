"""Read-only validation of the DEC-003 frozen split anchor."""

import csv
import hashlib
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FREEZE_PATH = PROJECT_ROOT / "ml" / "split_freeze.json"
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "ml" / "data" / "manifest_v2.csv"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_freeze(freeze_path: Path | str = DEFAULT_FREEZE_PATH) -> dict:
    path = Path(freeze_path)
    if not path.is_file():
        raise RuntimeError(f"frozen split anchor is missing: {path}")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def verify_frozen_manifest(
    manifest_path: Path | str = DEFAULT_MANIFEST_PATH,
    freeze_path: Path | str = DEFAULT_FREEZE_PATH,
) -> dict:
    """Validate the on-disk manifest against DEC-003 before it can be used.

    This function is read-only. It deliberately fails closed when either input
    is absent, the file hash differs, or the quarantined SHA-256 group is not
    exactly the frozen group of rows assigned to ``cuarentena``.
    """
    freeze = load_freeze(freeze_path)
    manifest = Path(manifest_path)
    if not manifest.is_file():
        raise RuntimeError(f"frozen split manifest is missing: {manifest}")
    expected_hash = freeze["source_manifest"]["output_sha256"]
    actual_hash = file_sha256(manifest)
    if actual_hash != expected_hash:
        raise RuntimeError(
            "frozen manifest does not match DEC-003: "
            f"expected {expected_hash}, got {actual_hash}"
        )

    with manifest.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    quarantine_hash = freeze["quarantine"]["sha256"]
    quarantined_rows = [row for row in rows if row["sha256"] == quarantine_hash]
    expected_rows = freeze["quarantine"]["rows"]
    if len(quarantined_rows) != expected_rows or any(
        row["split_propuesto"] != "cuarentena" for row in quarantined_rows
    ):
        raise RuntimeError("frozen manifest quarantine does not match DEC-002")
    return freeze
