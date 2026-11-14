import pytest

from qprover.budget import BudgetManager


def test_budget_calibration_and_validation(tmp_path):
    manager = BudgetManager(tmp_path / "ledger.json")
    assert manager.estimate(100, 0) > 0
    manager.record("probe", 0.2, 100, 4)
    assert manager.calibration_seconds is not None
    assert manager.estimate(1000, 4) > 0
    with pytest.raises(ValueError):
        manager.estimate(0, 1)
