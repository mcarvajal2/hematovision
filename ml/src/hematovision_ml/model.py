"""Keras 3 reconstruction of the confirmed historical CNN architecture."""

from tensorflow import keras

from .classes import CLASS_NAMES

HISTORIC_PARAMETER_COUNT = 4_372_857


def build_model(*, compile_model: bool = False) -> keras.Sequential:
    """Build the untrained historical CNN reconstruction.

    Compilation is opt-in because this scaffolding must not initiate training.
    When requested, the optimizer values are proposed defaults, not approved
    experimental decisions.
    """
    layers: list[keras.layers.Layer] = [keras.layers.Input(shape=(150, 150, 3), name="image")]
    for block_index, filters in enumerate((16, 32, 64, 64), start=1):
        for convolution_index in range(8):
            layers.append(
                keras.layers.Conv2D(
                    filters,
                    (3, 3),
                    padding="same",
                    activation="relu",
                    # The notebook disables bias on the first convolution of
                    # each Conv+BN pair (1, 3, 5 and 7) in every block.
                    use_bias=convolution_index % 2 != 0,
                    name=f"block{block_index}_conv{convolution_index + 1}",
                )
            )
            layers.append(
                keras.layers.BatchNormalization(
                    name=f"block{block_index}_bn{convolution_index + 1}"
                )
            )
        layers.append(keras.layers.MaxPooling2D((2, 2), name=f"block{block_index}_pool"))

    regularizer = keras.regularizers.L2(0.0001)
    layers.extend(
        [
            keras.layers.Flatten(name="flatten"),
            keras.layers.Dense(512, activation="relu", kernel_regularizer=regularizer, name="dense_512_a"),
            keras.layers.Dropout(0.3, name="dropout_a"),
            keras.layers.Dense(1024, activation="relu", kernel_regularizer=regularizer, name="dense_1024"),
            keras.layers.Dropout(0.3, name="dropout_b"),
            keras.layers.Dense(512, activation="relu", kernel_regularizer=regularizer, name="dense_512_b"),
            keras.layers.Dropout(0.3, name="dropout_c"),
            keras.layers.Dense(len(CLASS_NAMES), activation="softmax", name="classifier"),
        ]
    )
    model = keras.Sequential(layers, name="cnn_historic_reconstruction_v1")
    if compile_model:
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.0004),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )
    return model


def parameter_count(model: keras.Model) -> int:
    """Return the total parameter count used to validate the reconstruction."""
    return int(model.count_params())
