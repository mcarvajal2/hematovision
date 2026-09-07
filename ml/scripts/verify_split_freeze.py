"""Read-only verification of the DEC-003 frozen Phase 2 split."""

import csv
import hashlib
import io
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ML_DIR = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_split import (  # noqa: E402
    INPUT_CSV,
    OUTPUT_CSV,
    QUARANTINE_HASH,
    SEED,
    SPLITS,
    assign_splits,
    group_rows,
    read_rows,
)


FREEZE_FILE = ML_DIR / "split_freeze.json"


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def serialized_csv_bytes(rows, fieldnames):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def main():
    with open(FREEZE_FILE, "r", encoding="utf-8") as handle:
        freeze = json.load(handle)
    frozen_hash = freeze["source_manifest"]["output_sha256"]

    rows = read_rows(INPUT_CSV)
    fieldnames = list(rows[0].keys())
    assignments = assign_splits(rows)
    for row in rows:
        row["split_propuesto"] = assignments[row["path_original"]]

    recalculated_hash = hashlib.sha256(serialized_csv_bytes(rows, fieldnames)).hexdigest()
    groups = group_rows(rows)
    crossing_groups = {
        digest: sorted({row["split_propuesto"] for row in members})
        for digest, members in groups.items()
        if len({row["split_propuesto"] for row in members}) > 1
    }
    quarantine = groups.get(QUARANTINE_HASH, [])
    quarantine_ok = (
        len(quarantine) == 2
        and {row["split_propuesto"] for row in quarantine} == {"cuarentena"}
    )

    output_path = Path(OUTPUT_CSV)
    output_exists = output_path.exists()
    on_disk_hash = file_sha256(output_path) if output_exists else None
    checks = {
        "recalculated_manifest": "matched" if recalculated_hash == frozen_hash else "mismatch",
        "crossing_hash_groups": "matched" if not crossing_groups else "mismatch",
        "quarantine": "matched" if quarantine_ok else "mismatch",
        "on_disk_manifest": (
            "matched" if on_disk_hash == frozen_hash else "mismatch"
        ) if output_exists else "not_present",
    }
    summary = {
        "freeze_file": str(FREEZE_FILE),
        "decision": freeze.get("decision"),
        "seed": SEED,
        "expected_output_sha256": frozen_hash,
        "recalculated_output_sha256": recalculated_hash,
        "on_disk_output_sha256": on_disk_hash,
        "checks": checks,
        "crossing_groups": crossing_groups,
        "quarantine": {
            "hash": QUARANTINE_HASH,
            "rows": len(quarantine),
            "splits": sorted({row["split_propuesto"] for row in quarantine}),
            "ok": quarantine_ok,
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if any(value == "mismatch" for value in checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
