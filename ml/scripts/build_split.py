import os
import csv
import hashlib
import random
import json
import io

INPUT_CSV = r"D:\Proyectos\hematovision\ml\data\manifest_v1.csv"
OUTPUT_CSV = r"D:\Proyectos\hematovision\ml\data\manifest_v2.csv"
SEED = 20260907
QUARANTINE_HASH = "5c7c2002b0fec1f34093f672961aa13e3880fb5db0075e6a211d91f4e6ec68c7"
SPLITS = ("train", "val", "test")
FREEZE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "split_freeze.json")

def read_rows(path):
    with open(path, "r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))

def group_rows(rows):
    groups = {}
    for row in rows:
        groups.setdefault(row["sha256"], []).append(row)
    return groups

def assign_splits(rows):
    """Return path_original -> split using a fresh deterministic RNG.

    For every non-quarantine class, SHA-256 groups are shuffled with
    random.Random(20260907). Whole groups are then assigned one by one to
    the split that minimizes the sum of absolute deviations from 80/10/10
    target row counts. Candidate order is shuffled only to resolve ties.
    """
    groups = group_rows(rows)
    rng = random.Random(SEED)
    assignments = {}
    by_class = {}
    for digest, members in groups.items():
        if digest == QUARANTINE_HASH:
            for row in members:
                assignments[row["path_original"]] = "cuarentena"
            continue
        labels = {row["clase_final_9"] for row in members}
        if len(labels) != 1:
            raise ValueError("grupo con conflicto de etiqueta no cuarentenado: " + digest)
        by_class.setdefault(next(iter(labels)), []).append((digest, members))

    for label in sorted(by_class):
        groups_for_class = by_class[label]
        rng.shuffle(groups_for_class)
        total = sum(len(members) for _, members in groups_for_class)
        targets = {"train": round(total * 0.80), "val": round(total * 0.10)}
        targets["test"] = total - targets["train"] - targets["val"]
        assigned = {split: 0 for split in SPLITS}
        for _, members in groups_for_class:
            size = len(members)
            candidates = list(SPLITS)
            rng.shuffle(candidates)
            split = min(
                candidates,
                key=lambda candidate: sum(
                    abs((assigned[name] + (size if name == candidate else 0)) - targets[name])
                    for name in SPLITS
                ),
            )
            for row in members:
                assignments[row["path_original"]] = split
            assigned[split] += size
    return assignments

def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()

def csv_bytes(rows, fieldnames):
    """Serialize rows exactly as csv.DictWriter writes the output manifest."""
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")

def main():
    rows = read_rows(INPUT_CSV)
    fieldnames = list(rows[0].keys())
    if fieldnames != [
        "path_original", "fuente", "clase_carpeta_origen", "clase_final_9",
        "sha256", "tamano_bytes", "split_propuesto",
    ]:
        raise ValueError("columnas inesperadas: " + repr(fieldnames))

    first = assign_splits(rows)
    second = assign_splits(rows)
    reproducible = first == second
    if not reproducible:
        raise RuntimeError("las dos asignaciones reproducibles no coinciden")
    for row in rows:
        row["split_propuesto"] = first[row["path_original"]]

    groups = group_rows(rows)
    crossing_groups = {
        digest: sorted({row["split_propuesto"] for row in members})
        for digest, members in groups.items()
        if len({row["split_propuesto"] for row in members}) != 1
    }
    if crossing_groups:
        raise RuntimeError("grupo(s) de hash cruzan particiones: " + json.dumps(crossing_groups))
    quarantine = groups.get(QUARANTINE_HASH, [])
    if len(quarantine) != 2 or {row["split_propuesto"] for row in quarantine} != {"cuarentena"}:
        raise RuntimeError("cuarentena inválida")

    frozen_check = "not_frozen"
    if os.path.exists(FREEZE_FILE):
        with open(FREEZE_FILE, "r", encoding="utf-8") as handle:
            frozen_hash = json.load(handle)["source_manifest"]["output_sha256"]
        recalculated_hash = hashlib.sha256(csv_bytes(rows, fieldnames)).hexdigest()
        if recalculated_hash != frozen_hash:
            raise RuntimeError(
                "el split está congelado (DEC-003): esta ejecución reasignaría "
                "imágenes congeladas silenciosamente; se abortó antes de escribir "
                "manifest_v2.csv"
            )
        frozen_check = "matched"

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    class_split_counts = {}
    source_counts = {}
    total_split_counts = {}
    for row in rows:
        label, split = row["clase_final_9"], row["split_propuesto"]
        class_split_counts.setdefault(label, {"train": 0, "val": 0, "test": 0, "cuarentena": 0})
        class_split_counts[label][split] += 1
        source_counts.setdefault(row["fuente"], {"train": 0, "val": 0, "test": 0, "cuarentena": 0})
        source_counts[row["fuente"]][split] += 1
        total_split_counts[split] = total_split_counts.get(split, 0) + 1
    summary = {
        "input_csv": INPUT_CSV,
        "output_csv": OUTPUT_CSV,
        "output_sha256": file_sha256(OUTPUT_CSV),
        "output_bytes": os.path.getsize(OUTPUT_CSV),
        "rows": len(rows),
        "seed": SEED,
        "frozen_check": frozen_check,
        "reproducible": reproducible,
        "crossing_hash_groups": crossing_groups,
        "quarantine_hash": QUARANTINE_HASH,
        "quarantine_rows": [{"path_original": row["path_original"], "fuente": row["fuente"], "clase_final_9": row["clase_final_9"]} for row in quarantine],
        "class_split_counts": dict(sorted(class_split_counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "total_split_counts": dict(sorted(total_split_counts.items())),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
