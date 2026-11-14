from dataclasses import dataclass
from time import perf_counter

from .classical.baselines import exact, greedy, simulated_annealing
from .qubo import QUBO
from .quantum.qaoa import run_qaoa


@dataclass(frozen=True)
class Evaluation:
    method: str
    energy: float
    wall_seconds: float
    diversity: int


def evaluate(qubo: QUBO, k: int, shots: int = 1024, seed: int = 7) -> list[Evaluation]:
    outputs = []
    for name, function in (("greedy", greedy), ("annealing", simulated_annealing)):
        start = perf_counter()
        if name == "greedy":
            _, energy = function(qubo, k)
        else:
            _, energy = function(qubo, k, seed=seed)
        outputs.append(Evaluation(name, energy, perf_counter() - start, 1))
    start = perf_counter()
    quantum = run_qaoa(qubo, shots=shots, seed=seed)
    energy = min(qubo.energy(bits) for bits in quantum.samples)
    outputs.append(Evaluation("quantum-simulator", energy, perf_counter() - start, len(quantum.samples)))
    if qubo.n <= 20:
        _, energy = exact(qubo, k)
        outputs.append(Evaluation("exact", energy, 0.0, 1))
    return outputs
