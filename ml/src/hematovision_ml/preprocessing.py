"""Deterministic image loading and preprocessing for the historical input size."""

from pathlib import Path

import tensorflow as tf

from .paths import dataset_root as configured_dataset_root
from .paths import resolve_image_path

IMAGE_SIZE = 150


def preprocess_image(image: tf.Tensor) -> tf.Tensor:
    """Resize an RGB image to 150x150 and rescale pixels to [0, 1]."""
    image = tf.image.resize(image, (IMAGE_SIZE, IMAGE_SIZE))
    return tf.cast(image, tf.float32) / 255.0


def load_and_preprocess_image(
    path: str | Path, dataset_root: Path | str | None = None
) -> tf.Tensor:
    """Read one manifest-relative image path without any random transform."""
    full_path = resolve_image_path(str(path), configured_dataset_root(dataset_root))
    image = tf.io.decode_image(tf.io.read_file(str(full_path)), channels=3, expand_animations=False)
    image.set_shape((None, None, 3))
    return preprocess_image(image)
