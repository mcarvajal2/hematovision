"""Reproducibility utilities for a future, separately authorized training run."""

import random

import numpy as np
import tensorflow as tf


def set_global_seed(training_seed: int) -> None:
    """Set Python, NumPy and TensorFlow seeds; this does not start training."""
    random.seed(training_seed)
    np.random.seed(training_seed)
    tf.keras.utils.set_random_seed(training_seed)
