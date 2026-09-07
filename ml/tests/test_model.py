import numpy as np
import pytest

from hematovision_ml.model import HISTORIC_PARAMETER_COUNT, build_model, parameter_count


@pytest.fixture(scope="module")
def model():
    return build_model()


def test_model_summary_and_parameter_count_match_historical_reconstruction(model):
    lines: list[str] = []
    model.summary(print_fn=lines.append)
    assert any("Total params" in line for line in lines)
    assert parameter_count(model) == HISTORIC_PARAMETER_COUNT


def test_model_input_output_and_softmax(model):
    output = model(np.zeros((1, 150, 150, 3), dtype=np.float32), training=False).numpy()
    assert model.input_shape == (None, 150, 150, 3)
    assert model.output_shape == (None, 9)
    assert output.shape == (1, 9)
    assert np.sum(output[0]) == pytest.approx(1.0, abs=1e-6)
