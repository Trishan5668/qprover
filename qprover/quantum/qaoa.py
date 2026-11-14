from collections import Counter
from dataclasses import dataclass
from typing import Any

from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from scipy.optimize import minimize

from ..ising import Ising, qubo_to_ising, to_sparse_pauli_op
from ..qubo import QUBO
from .simulator import execute_counts


@dataclass(frozen=True)
class QAOAResult:
    samples: dict[tuple[int, ...], int]
    depth: int
    parameters: tuple[float, ...]
    circuit: QuantumCircuit
    cost_operator: SparsePauliOp

    @property
    def counts(self) -> dict[str, int]:
        return {"".join(map(str, reversed(bits))): count for bits, count in self.samples.items()}


def ising_operator(ising: Ising) -> SparsePauliOp:
    return to_sparse_pauli_op(ising)


def _apply_cost(circuit: QuantumCircuit, ising: Ising, gamma: float) -> None:
    for index, value in enumerate(ising.fields):
        circuit.rz(2 * gamma * value, index)
    for (left, right), value in ising.couplings.items():
        circuit.cx(left, right)
        circuit.rz(2 * gamma * value, right)
        circuit.cx(left, right)


def build_qaoa_circuit(ising: Ising, parameters: tuple[float, ...], p: int) -> QuantumCircuit:
    if len(parameters) != 2 * p:
        raise ValueError("parameters must contain p gamma values followed by p beta values")
    circuit = QuantumCircuit(ising.n)
    circuit.h(range(ising.n))
    gammas, betas = parameters[:p], parameters[p:]
    for layer in range(p):
        _apply_cost(circuit, ising, gammas[layer])
        for index in range(ising.n):
            circuit.rx(2 * betas[layer], index)
    return circuit


def _tqa_initialization(p: int) -> tuple[float, ...]:
    gammas = tuple(0.35 * (layer + 1) / p for layer in range(p))
    betas = tuple(0.8 * (1 - layer / p) for layer in range(p))
    return gammas + betas


def _expectation(
    qubo: QUBO,
    ising: Ising,
    parameters: tuple[float, ...],
    p: int,
    seed: int,
) -> float:
    from qiskit_aer import AerSimulator

    circuit = build_qaoa_circuit(ising, parameters, p)
    circuit.save_expectation_value(ising_operator(ising), range(ising.n), label="cost")
    result = AerSimulator().run(circuit, seed_simulator=seed).result()
    return float(result.data(0)["cost"]) + qubo.offset


def repair_bitstring(bits: tuple[int, ...], k: int, qubo: QUBO) -> tuple[int, ...]:
    if not 0 <= k <= len(bits):
        raise ValueError("k must be between zero and the bitstring size")
    selected = [index for index, bit in enumerate(bits) if bit]
    if len(selected) > k:
        selected.sort(key=lambda i: qubo.energy(tuple(1 if j == i else 0 for j in range(qubo.n))), reverse=True)
        selected = selected[:k]
    elif len(selected) < k:
        remaining = [i for i, bit in enumerate(bits) if not bit]
        selected.extend(
            sorted(
                remaining,
                key=lambda i: qubo.energy(tuple(1 if j in selected + [i] else 0 for j in range(qubo.n))),
            )[: k - len(selected)]
        )
    return tuple(int(index in selected) for index in range(len(bits)))


def top_k_premise_sets(
    samples: dict[tuple[int, ...], int] | Counter[tuple[int, ...]],
    qubo: QUBO,
    k: int,
    limit: int,
) -> list[tuple[int, ...]]:
    repaired = {repair_bitstring(bits, k, qubo) for bits in samples}
    return sorted(repaired, key=qubo.energy)[:limit]


def run_qaoa(
    qubo: QUBO,
    p: int = 1,
    shots: int = 1024,
    seed: int = 7,
    noise_model: Any | None = None,
) -> QAOAResult:
    if p not in (1, 2):
        raise ValueError("p must be 1 or 2")
    ising = qubo_to_ising(qubo)
    initial = _tqa_initialization(p)
    def objective(values: Any) -> float:
        return _expectation(qubo, ising, tuple(float(x) for x in values), p, seed)
    optimized = minimize(
        objective,
        initial,
        method="COBYLA",
        options={"maxiter": 40 if qubo.n <= 12 else 12, "rhobeg": 0.5},
    )
    parameters = tuple(float(value) for value in optimized.x)
    circuit = build_qaoa_circuit(ising, parameters, p)
    measured = circuit.copy()
    measured.measure_all()
    raw_counts = execute_counts(measured, shots, seed, noise_model)
    samples: Counter[tuple[int, ...]] = Counter()
    for raw, count in raw_counts.items():
        bits = tuple(int(bit) for bit in reversed(raw.replace(" ", "")))
        samples[bits] += count
    return QAOAResult(dict(samples), circuit.depth(), parameters, circuit, ising_operator(ising))
