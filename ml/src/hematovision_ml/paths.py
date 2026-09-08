"""Portable resolution of image paths recorded in the frozen manifest.

manifest_v2.csv stores `path_original` relative to the historical dataset
root (D:\\Datasets\\dataset_hematologia on the machine that built it), with
a literal backslash as separator baked into the CSV string regardless of
the host operating system (DEC-003, frozen -- never re-split with pathlib
directly, PurePosixPath does not treat "\\" as a separator). This module
resolves those relative paths against a configurable dataset root without
ever reading or modifying the manifest's contents.
"""

from __future__ import annotations

import os
from pathlib import Path

DATASET_ROOT_ENV_VAR = "HEMATOVISION_DATASET_ROOT"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATASET_ROOT = PROJECT_ROOT / "ml" / "data" / "raw"


def dataset_root(explicit: Path | str | None = None) -> Path:
    """Resolve the dataset root: explicit argument > env var > project default."""
    if explicit is not None:
        return Path(explicit)
    override = os.environ.get(DATASET_ROOT_ENV_VAR)
    if override:
        return Path(override)
    return DEFAULT_DATASET_ROOT


def _split_manifest_path(path_original: str) -> list[str]:
    """Split a manifest path on its literal backslash separator.

    manifest_v2.csv always stores Windows-style separators regardless of
    the host OS reading it later. pathlib must not be trusted to split
    this string: PurePosixPath treats "\\" as an ordinary filename
    character, not a separator.
    """
    parts = [part for part in path_original.split("\\") if part not in ("", ".")]
    if not parts:
        raise ValueError(f"empty path_original: {path_original!r}")
    if ".." in parts:
        raise ValueError(f"path traversal rejected in path_original: {path_original!r}")
    return parts


def resolve_image_path(
    path_original: str, dataset_root_override: Path | str | None = None
) -> Path:
    """Resolve a manifest path_original into a path under the dataset root.

    Never reads or modifies manifest_v2.csv; operates purely on the string
    already extracted elsewhere (e.g. by dataset.py). Raises ValueError if
    the resolved path would escape the dataset root.
    """
    root = dataset_root(dataset_root_override).resolve()
    parts = _split_manifest_path(path_original)
    resolved = root.joinpath(*parts).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"path_original escapes dataset root: {path_original!r}")
    return resolved
