from hematovision_ml.config import ExperimentConfig


def test_experiment_config_json_round_trip(tmp_path):
    config = ExperimentConfig()
    target = tmp_path / "experiment.json"
    config.save(target)
    restored = ExperimentConfig.load(target)
    assert restored == config
