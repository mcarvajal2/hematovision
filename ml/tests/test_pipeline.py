from pathlib import Path

import numpy as np

from hematovision_ml.augmentation import apply_augmentation, build_augmentation_pipeline
from hematovision_ml.config import ExperimentConfig
from hematovision_ml.dataset import get_train_paths
from hematovision_ml.preprocessing import load_and_preprocess_image
from hematovision_ml.seeds import set_global_seed


class MarkerPipeline:
    def __init__(self):
        self.calls = 0

    def __call__(self, image, training=False):
        self.calls += 1
        return image + 1


def test_augmentation_only_invokes_pipeline_for_train():
    image = np.zeros((2, 2, 3), dtype=np.float32)
    marker = MarkerPipeline()
    assert np.array_equal(apply_augmentation(image, "val", marker), image)
    assert np.array_equal(apply_augmentation(image, "test", marker), image)
    assert marker.calls == 0
    assert np.array_equal(apply_augmentation(image, "train", marker), image + 1)
    assert marker.calls == 1


def test_disabled_augmentation_and_preprocessing_are_deterministic():
    config = ExperimentConfig()
    config.augmentation_config["enabled"] = False
    assert build_augmentation_pipeline(config.augmentation_config) is None
    path = get_train_paths()[0]
    dataset_root = Path(r"D:\Datasets\dataset_hematologia")
    first = load_and_preprocess_image(path, dataset_root=dataset_root).numpy()
    second = load_and_preprocess_image(path, dataset_root=dataset_root).numpy()
    assert first.shape == (150, 150, 3)
    assert np.array_equal(first, second)
    set_global_seed(42)
    assert np.array_equal(apply_augmentation(first, "train", None), first)
