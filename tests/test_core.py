from qprover.budget import BudgetExceeded, BudgetManager
from qprover.ising import qubo_to_ising
from qprover.qubo import build_qubo


def test_qubo_ising_energy_matches():
    qubo = build_qubo([1.0, 0.5, 0.2], {(0, 1): 0.3}, 2)
    ising = qubo_to_ising(qubo)
    for bits in ((0, 0, 0), (1, 0, 1), (1, 1, 0)):
        spins = tuple(1 - 2 * bit for bit in bits)
        assert abs(qubo.energy(bits) - ising.energy(spins)) < 1e-9


def test_budget_blocks_overrun(tmp_path):
    manager = BudgetManager(tmp_path / "ledger.json", cap_seconds=1.0)
    manager.record("probe", 0.8, 100, 5)
    try:
        manager.check(0.3)
    except BudgetExceeded:
        pass
    else:
        raise AssertionError("over-budget job was not blocked")

