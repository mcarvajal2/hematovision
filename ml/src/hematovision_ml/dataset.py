"""Read-only manifest access with deliberate separation of train, val and test."""

import csv
from pathlib import Path

from .freeze import DEFAULT_FREEZE_PATH, DEFAULT_MANIFEST_PATH, verify_frozen_manifest


def _validated_rows(manifest_path: Path | str, freeze_path: Path | str) -> list[dict[str, str]]:
    verify_frozen_manifest(manifest_path, freeze_path)
    with Path(manifest_path).open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _paths_for_split(
    split: str, manifest_path: Path | str, freeze_path: Path | str
) -> tuple[str, ...]:
    rows = _validated_rows(manifest_path, freeze_path)
    selected = tuple(row["path_original"] for row in rows if row["split_propuesto"] == split)
    assert all(row["split_propuesto"] != "cuarentena" for row in rows if row["split_propuesto"] == split)
    return selected


def get_train_paths(
    manifest_path: Path | str = DEFAULT_MANIFEST_PATH, freeze_path: Path | str = DEFAULT_FREEZE_PATH
) -> tuple[str, ...]:
    """Return frozen train paths only; this function never writes or reassigns the split."""
    return _paths_for_split("train", manifest_path, freeze_path)


def get_val_paths(
    manifest_path: Path | str = DEFAULT_MANIFEST_PATH, freeze_path: Path | str = DEFAULT_FREEZE_PATH
) -> tuple[str, ...]:
    """Return frozen validation paths only; this function never writes or reassigns the split."""
    return _paths_for_split("val", manifest_path, freeze_path)


def get_test_paths(
    *,
    allow_test_access: bool = False,
    manifest_path: Path | str = DEFAULT_MANIFEST_PATH,
    freeze_path: Path | str = DEFAULT_FREEZE_PATH,
) -> tuple[str, ...]:
    """Return test paths only after an explicit opt-in.

    Test is single-use per experiment and must never select hyperparameters or
    thresholds; those choices belong to validation. Passing ``True`` documents
    a deliberate access decision at each caller.
    """
    if not allow_test_access:
        raise PermissionError("test access requires allow_test_access=True")
    return _paths_for_split("test", manifest_path, freeze_path)
