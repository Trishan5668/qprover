from dataclasses import dataclass

from ..qubo import QUBO
from .simulator import sample_qubo


@dataclass(frozen=True)
class QAOAResult:
    samples: dict[tuple[int, ...], int]
    depth: int
    parameters: tuple[float, ...]


def run_qaoa(qubo: QUBO, p: int = 1, shots: int = 1024, seed: int = 7) -> QAOAResult:
    if p not in (1, 2):
        raise ValueError("p must be 1 or 2")
    return QAOAResult(dict(sample_qubo(qubo, shots, seed)), depth=2 * p * qubo.n, parameters=(0.5,) * (2 * p))

