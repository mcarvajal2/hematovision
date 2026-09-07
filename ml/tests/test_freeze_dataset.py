import hashlib
import json

import pytest

from hematovision_ml.dataset import get_test_paths, get_train_paths, get_val_paths
from hematovision_ml.freeze import verify_frozen_manifest


def test_frozen_manifest_matches_dec_003():
    freeze = verify_frozen_manifest()
    assert freeze["decision"] == "DEC-003"


def test_frozen_manifest_rejects_wrong_content(tmp_path):
    manifest = tmp_path / "manifest.csv"
    manifest.write_text("path_original,sha256,split_propuesto\nfake,wrong,train\n", encoding="utf-8")
    freeze = {
        "source_manifest": {"output_sha256": hashlib.sha256(b"expected content").hexdigest()},
        "quarantine": {"sha256": "quarantine", "rows": 2},
    }
    freeze_path = tmp_path / "split_freeze.json"
    freeze_path.write_text(json.dumps(freeze), encoding="utf-8")
    with pytest.raises(RuntimeError, match="does not match"):
        verify_frozen_manifest(manifest, freeze_path)


def test_quarantine_is_excluded_and_splits_do_not_overlap():
    train = set(get_train_paths())
    validation = set(get_val_paths())
    test = set(get_test_paths(allow_test_access=True))
    assert train.isdisjoint(validation)
    assert train.isdisjoint(test)
    assert validation.isdisjoint(test)
    assert "Labelled_2\\eosinophil\\EO_225902.jpg" not in train | validation | test
    assert "Labelled_2\\neutrophil\\BNE_191112.jpg" not in train | validation | test


def test_test_access_requires_explicit_opt_in():
    with pytest.raises(PermissionError, match="allow_test_access"):
        get_test_paths()
