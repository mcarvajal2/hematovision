"""Construye el manifiesto de originales (Bodzas + PBC, sin `ig`) para el baseline de Fase 2.

Solo lectura sobre las imágenes fuente: no mueve, modifica, elimina ni aumenta nada.
No entrena ni carga TensorFlow/Keras. No inicializa DVC.

Escribe `ml/data/manifest_v1.csv` (fuera de Git, ver .gitignore) con columnas
path_original/fuente/clase_carpeta_origen/clase_final_9/sha256/tamano_bytes/split_propuesto,
agrupa por sha256 para detectar duplicados exactos y conflictos de etiqueta (mismo hash,
clase_final_9 distinta -- no se resuelven automáticamente), y propone un split 80/10/10
estratificado por clase a nivel de grupo-de-hash (no de archivo individual), sin congelarlo.

Ver docs/dataset-manifest.md para el inventario resultante y docs/phase2-plan.md para el
diseño completo. El mapeo de carpetas y los conteos esperados replican
docs/dataset-provenance.md; no re-decide la taxonomía ni el motivo de exclusión de `ig`.
"""

import os
import hashlib
import csv
import json
import random

DATASET_ROOT = r"D:\Datasets\dataset_hematologia"
OUTPUT_CSV = r"D:\Proyectos\hematovision\ml\data\manifest_v1.csv"

BODZAS = {
    "Basophile": "Basófilos",
    "Eosinophile": "Eosinófilos",
    "Lymphoblast": "Linfoblastos",
    "Lymphocyte": "Linfocitos",
    "Monocyte": "Monocitos",
    "Myeloblast": "Mieloblastos",
    "Neutrophile Band": "Neutrófilos",
    "Neutrophile Segment": "Neutrófilos",
    "Normoblast": "Eritroblastos",
}
PBC = {
    "basophil": "Basófilos",
    "eosinophil": "Eosinófilos",
    "erythroblast": "Eritroblastos",
    "lymphocyte": "Linfocitos",
    "monocyte": "Monocitos",
    "neutrophil": "Neutrófilos",
    "platelet": "Plaquetas",
}
EXPECTED = {
    "Basófilos": 2241,
    "Eosinófilos": 4134,
    "Eritroblastos": 2061,
    "Linfoblastos": 2557,
    "Linfocitos": 4260,
    "Mieloblastos": 2534,
    "Monocitos": 3460,
    "Neutrófilos": 6629,
    "Plaquetas": 2348,
}

def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()

def add_source(rows, errors, source_name, directory, class_map):
    for folder in sorted(class_map):
        root = os.path.join(directory, folder)
        if not os.path.isdir(root):
            errors.append({"path": root, "error": "directorio de clase ausente"})
            continue
        for current, dirs, files in os.walk(root):
            dirs.sort()
            for name in sorted(files):
                full = os.path.join(current, name)
                try:
                    rows.append({
                        "path_original": os.path.relpath(full, DATASET_ROOT),
                        "fuente": source_name,
                        "clase_carpeta_origen": folder,
                        "clase_final_9": class_map[folder],
                        "sha256": sha256_file(full),
                        "tamano_bytes": os.path.getsize(full),
                        "split_propuesto": "",
                    })
                except (OSError, IOError) as exc:
                    errors.append({"path": full, "error": str(exc)})

def main():
    rows, errors = [], []
    add_source(rows, errors, "Bodzas", os.path.join(DATASET_ROOT, "Labelled"), BODZAS)
    add_source(rows, errors, "PBC", os.path.join(DATASET_ROOT, "Labelled_2"), PBC)
    rows.sort(key=lambda item: item["path_original"])

    hash_groups = {}
    for row in rows:
        hash_groups.setdefault(row["sha256"], []).append(row)
    duplicate_groups = []
    conflicts = []
    for digest, members in sorted(hash_groups.items()):
        if len(members) > 1:
            entry = {
                "sha256": digest,
                "members": [{
                    "path_original": r["path_original"],
                    "fuente": r["fuente"],
                    "clase_final_9": r["clase_final_9"],
                } for r in members],
                "conflicto_etiqueta": len({r["clase_final_9"] for r in members}) > 1,
            }
            duplicate_groups.append(entry)
            if entry["conflicto_etiqueta"]:
                conflicts.append(entry)

    rng = random.Random(20260907)
    by_class = {}
    for digest, members in hash_groups.items():
        labels = {r["clase_final_9"] for r in members}
        if len(labels) == 1:
            label = next(iter(labels))
            by_class.setdefault(label, []).append((digest, members))

    for label in sorted(by_class):
        groups = by_class[label]
        rng.shuffle(groups)
        total = sum(len(members) for _, members in groups)
        targets = {
            "train": round(total * 0.80),
            "val": round(total * 0.10),
        }
        targets["test"] = total - targets["train"] - targets["val"]
        assigned = {"train": 0, "val": 0, "test": 0}
        for _, members in groups:
            size = len(members)
            candidates = ["train", "val", "test"]
            rng.shuffle(candidates)
            split = min(
                candidates,
                key=lambda candidate: sum(
                    abs((assigned[name] + (size if name == candidate else 0)) - targets[name])
                    for name in ("train", "val", "test")
                ),
            )
            for row in members:
                row["split_propuesto"] = split
            assigned[split] += size

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    columns = [
        "path_original", "fuente", "clase_carpeta_origen", "clase_final_9",
        "sha256", "tamano_bytes", "split_propuesto",
    ]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    class_counts = {}
    source_folder_counts = {}
    split_counts = {}
    for row in rows:
        label = row["clase_final_9"]
        class_counts[label] = class_counts.get(label, 0) + 1
        key = row["fuente"] + " | " + row["clase_carpeta_origen"]
        source_folder_counts[key] = source_folder_counts.get(key, 0) + 1
        split_counts.setdefault(label, {"train": 0, "val": 0, "test": 0, "sin_asignar": 0})
        if row["split_propuesto"]:
            split_counts[label][row["split_propuesto"]] += 1
        else:
            split_counts[label]["sin_asignar"] += 1
    summary = {
        "manifest_path": OUTPUT_CSV,
        "manifest_bytes": os.path.getsize(OUTPUT_CSV),
        "row_count": len(rows),
        "error_count": len(errors),
        "errors": errors,
        "class_counts": dict(sorted(class_counts.items())),
        "expected_class_counts": EXPECTED,
        "class_discrepancies": {
            label: {"actual": class_counts.get(label, 0), "expected": expected}
            for label, expected in EXPECTED.items()
            if class_counts.get(label, 0) != expected
        },
        "total_discrepancy": {"actual": len(rows), "expected": 30224} if len(rows) != 30224 else {},
        "source_folder_counts": dict(sorted(source_folder_counts.items())),
        "duplicate_group_count": len(duplicate_groups),
        "duplicate_file_count": sum(len(x["members"]) for x in duplicate_groups),
        "duplicate_groups": duplicate_groups,
        "conflict_group_count": len(conflicts),
        "conflicts": conflicts,
        "split_seed": 20260907,
        "split_random": "random.Random(20260907)",
        "split_counts": dict(sorted(split_counts.items())),
        "excluded_pbc_folder": "ig (no recorrida)",
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
