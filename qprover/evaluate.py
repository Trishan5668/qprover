from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from collections.abc import Callable

from .classical.baselines import exact, greedy, random_search, simulated_annealing
from .qubo import QUBO
from .quantum.qaoa import run_qaoa


@dataclass(frozen=True)
class Evaluation:
    method: str
    energy: float
    wall_seconds: float
    diversity: int
    proof_success_at_k: float = 0.0
    qpu_seconds: float = 0.0
    energy_gap: float = 0.0


def evaluate(
    qubo: QUBO,
    k: int,
    shots: int = 1024,
    seed: int = 7,
    proof_checker: Callable[[tuple[int, ...]], bool] | None = None,
) -> list[Evaluation]:
    exact_energy = exact(qubo, k)[1] if qubo.n <= 20 else None
    outputs: list[Evaluation] = []
    methods: tuple[tuple[str, Callable[[], tuple[tuple[int, ...], float]]], ...] = (
        ("greedy", lambda: greedy(qubo, k)),
        ("annealing", lambda: simulated_annealing(qubo, k, seed=seed)),
        ("random", lambda: random_search(qubo, k, shots, seed)),
    )
    for name, function in methods:
        start = perf_counter()
        bits, energy = function()
        success = float(proof_checker(bits)) if proof_checker is not None else 0.0
        outputs.append(
            Evaluation(name, energy, perf_counter() - start, 1, success, 0.0, energy - (exact_energy or energy))
        )
    start = perf_counter()
    quantum = run_qaoa(qubo, shots=shots, seed=seed)
    energies = {bits: qubo.energy(bits) for bits in quantum.samples}
    best_bits, energy = min(energies.items(), key=lambda item: item[1])
    success = float(proof_checker(best_bits)) if proof_checker is not None else 0.0
    outputs.append(
        Evaluation(
            "quantum-simulator",
            energy,
            perf_counter() - start,
            len(quantum.samples),
            success,
            0.0,
            energy - (exact_energy or energy),
        )
    )
    if exact_energy is not None:
        outputs.append(Evaluation("exact", exact_energy, 0.0, 1, 0.0, 0.0, 0.0))
    return outputs


def plot_results(results: list[Evaluation], output: Path) -> None:
    import matplotlib.pyplot as plt

    output.parent.mkdir(parents=True, exist_ok=True)
    names = [result.method for result in results]
    energies = [result.energy for result in results]
    figure, axis = plt.subplots(figsize=(7, 4))
    axis.bar(names, energies)
    axis.set_ylabel("Best QUBO energy (lower is better)")
    axis.tick_params(axis="x", rotation=30)
    figure.tight_layout()
    figure.savefig(output)
    plt.close(figure)


def results_table(results: list[Evaluation]) -> str:
    rows = ["| Method | Energy gap | Diversity | Wall seconds | QPU seconds | Proof success@k |",
            "|---|---:|---:|---:|---:|---:|"]
    rows.extend(
        f"| {r.method} | {r.energy_gap:.4f} | {r.diversity} | {r.wall_seconds:.4f} | "
        f"{r.qpu_seconds:.4f} | {r.proof_success_at_k:.2f} |"
        for r in results
    )
    return "\n".join(rows)
