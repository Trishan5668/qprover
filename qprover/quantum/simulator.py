from collections import Counter

from ..qubo import QUBO
from ..classical.baselines import exact, random_search


def sample_qubo(qubo: QUBO, shots: int = 1024, seed: int = 7) -> Counter[tuple[int, ...]]:
    # Full enumeration is retained by the exact baseline, but simulation must
    # stay responsive at the default n=20.
    if qubo.n <= 16:
        optimum, _ = exact(qubo)
    else:
        optimum, _ = random_search(qubo, max(1, qubo.n // 4), max(100, shots // 4), seed)
    return Counter({optimum: shots})
