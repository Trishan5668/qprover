import itertools
import math
import random
from ..qubo import QUBO

Solution = tuple[tuple[int, ...], float]


def _best(candidates: list[Solution]) -> Solution:
    return min(candidates, key=lambda item: item[1])


def exact(qubo: QUBO, k: int | None = None) -> Solution:
    if qubo.n > 20:
        raise ValueError("exact solver is limited to n <= 20")
    values = []
    for bits in itertools.product((0, 1), repeat=qubo.n):
        if k is None or sum(bits) == k:
            values.append((bits, qubo.energy(bits)))
    return _best(values)


def greedy(qubo: QUBO, k: int) -> Solution:
    chosen: list[int] = []
    for _ in range(k):
        options = [i for i in range(qubo.n) if i not in chosen]
        chosen.append(min(options, key=lambda i: qubo.energy(tuple(1 if j in chosen + [i] else 0 for j in range(qubo.n)))))
    bits = tuple(int(i in chosen) for i in range(qubo.n))
    return bits, qubo.energy(bits)


def random_search(qubo: QUBO, k: int, samples: int = 100, seed: int = 7) -> Solution:
    rng = random.Random(seed)
    candidates = []
    for _ in range(samples):
        selected = set(rng.sample(range(qubo.n), k))
        bits = tuple(int(i in selected) for i in range(qubo.n))
        candidates.append((bits, qubo.energy(bits)))
    return _best(candidates)


def simulated_annealing(
    qubo: QUBO, k: int, steps: int = 1000, seed: int = 7
) -> Solution:
    rng = random.Random(seed)
    current = set(rng.sample(range(qubo.n), k))
    def bits(selected: set[int]) -> tuple[int, ...]:
        return tuple(int(i in selected) for i in range(qubo.n))
    current_energy = qubo.energy(bits(current))
    best = (bits(current), current_energy)
    for step in range(steps):
        out = rng.choice(tuple(current))
        available = tuple(set(range(qubo.n)) - current)
        if not available:
            break
        new = set(current)
        new.remove(out)
        new.add(rng.choice(available))
        new_energy = qubo.energy(bits(new))
        temperature = max(0.01, 1.0 - step / steps)
        if new_energy < current_energy or rng.random() < math.exp((current_energy - new_energy) / temperature):
            current, current_energy = new, new_energy
            if new_energy < best[1]:
                best = (bits(new), new_energy)
    return best
