from types import SimpleNamespace

import pytest

from qprover.budget import BudgetManager
from qprover.classical.baselines import exact
from qprover.quantum.embedding import choose_subgraph
from qprover.quantum.qaoa import repair_bitstring, run_qaoa, top_k_premise_sets
from qprover.quantum.runtime import HardwareConfigurationError, _job_usage, submit_sampler_job
from qprover.qubo import build_qubo


def test_qaoa_has_distinct_samples_and_near_optimal_energy():
    qubo = build_qubo([1.0, 0.8, 0.4, 0.2], {(0, 1): 0.1}, 2)
    result = run_qaoa(qubo, p=1, shots=256, seed=13)
    assert len(result.samples) > 1
    assert min(qubo.energy(bits) for bits in result.samples) <= exact(qubo, 2)[1] + 0.25


def test_repair_and_top_k_are_cardinality_constrained():
    qubo = build_qubo([1.0, 0.5, 0.2], {}, 1)
    repaired = repair_bitstring((1, 1, 0), 1, qubo)
    assert sum(repaired) == 1
    assert all(sum(bits) == 1 for bits in top_k_premise_sets({(0, 0, 0): 2, (1, 1, 0): 1}, qubo, 1, 2))


def test_runtime_mock_guards_and_calibration(tmp_path):
    with pytest.raises(HardwareConfigurationError):
        submit_sampler_job(object(), SimpleNamespace(depth=lambda: 1), 10, BudgetManager(tmp_path / "l"))
    assert _job_usage(SimpleNamespace(usage=lambda: {"seconds": 1.5})) == 1.5
    backend = SimpleNamespace(
        properties=lambda: SimpleNamespace(gate_error=lambda gate, edge: 0.01 if edge == [0, 1] else 0.2)
    )
    assert choose_subgraph([(0, 1), (1, 2), (2, 3)], 3, backend) == [0, 1, 2]
