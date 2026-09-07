"""Configurable, on-the-fly augmentation that is restricted to train."""

from typing import Any

import tensorflow as tf
from tensorflow import keras


class RandomShear(keras.layers.Layer):
    """Apply a random x-axis shear without materializing files on disk."""

    def __init__(self, shear_range: float, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.shear_range = float(shear_range)

    def call(self, images: tf.Tensor, training: bool | None = None) -> tf.Tensor:
        if not training or self.shear_range == 0:
            return images
        images = tf.convert_to_tensor(images)
        batched = images.shape.rank == 4
        batch = images if batched else images[tf.newaxis, ...]
        amount = tf.random.uniform((tf.shape(batch)[0],), -self.shear_range, self.shear_range)
        zeros = tf.zeros_like(amount)
        ones = tf.ones_like(amount)
        transforms = tf.stack([ones, amount, zeros, zeros, ones, zeros, zeros, zeros], axis=1)
        result = tf.raw_ops.ImageProjectiveTransformV3(
            images=batch,
            transforms=transforms,
            output_shape=tf.shape(batch)[1:3],
            interpolation="BILINEAR",
            fill_mode="NEAREST",
            fill_value=0.0,
        )
        return result if batched else result[0]

    def get_config(self) -> dict[str, Any]:
        return {**super().get_config(), "shear_range": self.shear_range}


def build_augmentation_pipeline(config: dict[str, Any]) -> keras.Sequential | None:
    """Build proposed historical-style transforms, or None when disabled."""
    if not config.get("enabled", True):
        return None
    return keras.Sequential(
        [
            keras.layers.RandomRotation(config.get("rotation_range", 20) / 360.0),
            keras.layers.RandomTranslation(
                config.get("height_shift_range", 0.2), config.get("width_shift_range", 0.2)
            ),
            RandomShear(config.get("shear_range", 0.2)),
            keras.layers.RandomZoom(
                config.get("zoom_range", 0.2),
                config.get("zoom_range", 0.2),
            ),
            keras.layers.RandomFlip(
                "horizontal_and_vertical"
                if config.get("horizontal_flip", True) and config.get("vertical_flip", True)
                else "horizontal"
                if config.get("horizontal_flip", True)
                else "vertical"
                if config.get("vertical_flip", True)
                else "horizontal"
            ),
        ],
        name="train_augmentation",
    )


def apply_augmentation(
    image: tf.Tensor, split: str, pipeline: keras.Sequential | None
) -> tf.Tensor:
    """Apply augmentation only to train; validation/test always remain unchanged."""
    if split == "train" and pipeline is not None:
        return pipeline(image, training=True)
    return image
