from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class QUBO:
    linear: tuple[float, ...]
    quadratic: dict[tuple[int, int], float]
    offset: float = 0.0

    @property
    def n(self) -> int:
        return len(self.linear)

    def energy(self, bits: tuple[int, ...] | list[int]) -> float:
        if len(bits) != self.n:
            raise ValueError("bitstring length does not match QUBO")
        return self.offset + sum(a * x for a, x in zip(self.linear, bits)) + sum(
            value * bits[i] * bits[j] for (i, j), value in self.quadratic.items()
        )


def build_qubo(
    relevance: list[float],
    redundancy: dict[tuple[int, int], float],
    k: int,
    lambda_redundancy: float = 1.0,
    mu_cardinality: float = 2.0,
) -> QUBO:
    if not relevance:
        raise ValueError("at least one premise is required")
    if not 0 <= k <= len(relevance):
        raise ValueError("k must be between zero and the number of premises")
    linear = [-r + mu_cardinality * (1 - 2 * k) for r in relevance]
    quadratic: dict[tuple[int, int], float] = {}
    for i, j in combinations(range(len(relevance)), 2):
        quadratic[(i, j)] = lambda_redundancy * redundancy.get((i, j), redundancy.get((j, i), 0.0))
        quadratic[(i, j)] += 2 * mu_cardinality
    return QUBO(tuple(linear), quadratic, mu_cardinality * k * k)

