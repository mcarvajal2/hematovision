"""Deterministic image loading and preprocessing for the historical input size."""

from pathlib import Path

import tensorflow as tf

IMAGE_SIZE = 150
DATASET_ROOT = Path(r"D:\Datasets\dataset_hematologia")


def preprocess_image(image: tf.Tensor) -> tf.Tensor:
    """Resize an RGB image to 150x150 and rescale pixels to [0, 1]."""
    image = tf.image.resize(image, (IMAGE_SIZE, IMAGE_SIZE))
    return tf.cast(image, tf.float32) / 255.0


def load_and_preprocess_image(path: str | Path, dataset_root: Path | str = DATASET_ROOT) -> tf.Tensor:
    """Read one manifest-relative image path without any random transform."""
    full_path = Path(dataset_root) / Path(path)
    image = tf.io.decode_image(tf.io.read_file(str(full_path)), channels=3, expand_animations=False)
    image.set_shape((None, None, 3))
    return preprocess_image(image)
