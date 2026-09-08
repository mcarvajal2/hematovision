"""Tests for portable resolution of frozen-manifest image paths."""

import hashlib
from pathlib import Path, PurePosixPath

import pytest

from hematovision_ml.dataset import (
    get_test_image_paths,
    get_test_paths,
    get_train_image_paths,
    get_train_paths,
    get_val_image_paths,
    get_val_paths,
)
from hematovision_ml.freeze import DEFAULT_MANIFEST_PATH
from hematovision_ml.paths import (
    DATASET_ROOT_ENV_VAR,
    _split_manifest_path,
    dataset_root,
    resolve_image_path,
)


def test_resolves_labelled_manifest_path(tmp_path: Path):
    assert resolve_image_path(r"Labelled\Basophile\x.png", tmp_path) == (
        tmp_path / "Labelled" / "Basophile" / "x.png"
    )


def test_resolves_labelled_2_manifest_path(tmp_path: Path):
    assert resolve_image_path(r"Labelled_2\eosinophil\x.jpg", tmp_path) == (
        tmp_path / "Labelled_2" / "eosinophil" / "x.jpg"
    )


def test_resolves_against_a_windows_like_root(tmp_path: Path):
    root = tmp_path / "dataset_hematologia"
    target = root / "Labelled" / "Basophile" / "x.png"
    target.parent.mkdir(parents=True)
    target.write_text("synthetic", encoding="utf-8")
    assert resolve_image_path(r"Labelled\Basophile\x.png", root) == target


def test_posix_pathlib_does_not_split_manifest_backslashes():
    path_original = r"Labelled\Basophile\x.png"
    assert PurePosixPath(path_original).parts == (path_original,)
    assert _split_manifest_path(path_original) == ["Labelled", "Basophile", "x.png"]


def test_literal_backslash_is_always_a_manifest_separator(tmp_path: Path):
    path_original = r"Labelled_2\eosinophil\x.jpg"
    assert _split_manifest_path(path_original) == ["Labelled_2", "eosinophil", "x.jpg"]
    assert resolve_image_path(path_original, tmp_path) == tmp_path / "Labelled_2" / "eosinophil" / "x.jpg"


def test_dataset_root_reads_environment_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    override = tmp_path / "from-environment"
    monkeypatch.setenv(DATASET_ROOT_ENV_VAR, str(override))
    assert dataset_root() == override


def test_explicit_dataset_root_overrides_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv(DATASET_ROOT_ENV_VAR, str(tmp_path / "from-environment"))
    explicit = tmp_path / "explicit"
    assert dataset_root(explicit) == explicit


@pytest.mark.parametrize("path_original", [r"..\etc\algo", r"Labelled\..\..\fuera"])
def test_rejects_path_traversal(path_original: str, tmp_path: Path):
    with pytest.raises(ValueError, match="path traversal"):
        resolve_image_path(path_original, tmp_path)


def test_resolved_split_paths_preserve_frozen_metadata_sets(tmp_path: Path):
    assert get_train_image_paths(tmp_path) == tuple(
        resolve_image_path(path, tmp_path) for path in get_train_paths()
    )
    assert get_val_image_paths(tmp_path) == tuple(
        resolve_image_path(path, tmp_path) for path in get_val_paths()
    )
    assert get_test_image_paths(allow_test_access=True, dataset_root=tmp_path) == tuple(
        resolve_image_path(path, tmp_path) for path in get_test_paths(allow_test_access=True)
    )


def test_resolved_test_paths_require_explicit_access():
    with pytest.raises(PermissionError, match="allow_test_access=True"):
        get_test_image_paths()


def test_quarantine_is_excluded_from_all_resolved_splits(tmp_path: Path):
    quarantined = {
        tmp_path / "Labelled_2" / "eosinophil" / "EO_225902.jpg",
        tmp_path / "Labelled_2" / "neutrophil" / "BNE_191112.jpg",
    }
    resolved = set(get_train_image_paths(tmp_path))
    resolved.update(get_val_image_paths(tmp_path))
    resolved.update(get_test_image_paths(allow_test_access=True, dataset_root=tmp_path))
    assert quarantined.isdisjoint(resolved)


def test_frozen_manifest_hash_is_unchanged():
    assert hashlib.sha256(DEFAULT_MANIFEST_PATH.read_bytes()).hexdigest() == (
        "010a820d46cb2bf43c4d922405da61003087215dc8315ceb284d08624acf31e1"
    )
