from qprover.config import Settings


def test_default_config_and_yaml(tmp_path):
    assert Settings().min_qubits == 127
    path = tmp_path / "config.yaml"
    path.write_text("problem_qubits: 8\np: 2\n", encoding="utf-8")
    settings = Settings.from_yaml(path)
    assert settings.problem_qubits == 8
    assert settings.p == 2
