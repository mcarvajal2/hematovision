"""Serializable proposed defaults for a future reproducible experiment."""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .classes import CLASS_NAMES
from .freeze import DEFAULT_FREEZE_PATH, load_freeze


def _proposed_augmentation() -> dict[str, Any]:
    return {
        "rotation_range": 20,
        "width_shift_range": 0.2,
        "height_shift_range": 0.2,
        "shear_range": 0.2,
        "zoom_range": 0.2,
        "horizontal_flip": True,
        "vertical_flip": True,
        "enabled": True,
    }


def _proposed_callbacks() -> dict[str, Any]:
    return {
        "monitor": "val_loss",
        "early_stopping_patience": 12,
        "reduce_lr_patience": 6,
        "reduce_lr_factor": 0.2,
        "min_lr": 1e-6,
        "checkpoint_save_best_only": True,
    }


@dataclass
class ExperimentConfig:
    """Future EXP-REPRO configuration.

    Only the frozen split anchor, class order and image size are approved facts.
    ``training_seed``, augmentation, batch size, optimizer, epochs and callbacks
    are PROPOSED DEFAULTS, not approved scientific decisions or an authorization
    to train.
    """

    experiment_id: str = "EXP-REPRO"
    split_manifest_path: str = "ml/data/manifest_v2.csv"
    split_manifest_sha256: str = "010a820d46cb2bf43c4d922405da61003087215dc8315ceb284d08624acf31e1"
    model_architecture_id: str = "cnn_historic_reconstruction_v1"
    image_size: int = 150
    class_order: tuple[str, ...] = CLASS_NAMES
    split_seed: int = 20260907
    training_seed: int = 42
    preprocessing: dict[str, Any] = field(default_factory=lambda: {"resize": 150, "rescale": 1 / 255})
    augmentation_config: dict[str, Any] = field(default_factory=_proposed_augmentation)
    batch_size: int = 64
    optimizer: dict[str, Any] = field(
        default_factory=lambda: {"name": "adam", "learning_rate": 0.0004}
    )
    # PROPOSED default; the historical run stopped at epoch 62 via early stopping.
    epochs: int = 100
    callbacks: dict[str, Any] = field(default_factory=_proposed_callbacks)

    def __post_init__(self) -> None:
        freeze = load_freeze(DEFAULT_FREEZE_PATH)
        if self.split_manifest_sha256 != freeze["source_manifest"]["output_sha256"]:
            raise ValueError("split_manifest_sha256 must match ml/split_freeze.json")
        if self.split_seed != freeze["seed"]:
            raise ValueError("split_seed must match ml/split_freeze.json")
        if tuple(self.class_order) != CLASS_NAMES:
            raise ValueError("class_order must match the canonical published class order")
        if self.image_size != 150:
            raise ValueError("image_size must remain the confirmed 150 pixels")

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2, sort_keys=True)

    def save(self, path: Path | str) -> None:
        Path(path).write_text(self.to_json() + "\n", encoding="utf-8")

    @classmethod
    def from_json(cls, value: str) -> "ExperimentConfig":
        payload = json.loads(value)
        if "class_order" in payload:
            payload["class_order"] = tuple(payload["class_order"])
        return cls(**payload)

    @classmethod
    def load(cls, path: Path | str) -> "ExperimentConfig":
        return cls.from_json(Path(path).read_text(encoding="utf-8"))
