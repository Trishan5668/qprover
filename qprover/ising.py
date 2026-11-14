from dataclasses import dataclass

from .qubo import QUBO


@dataclass(frozen=True)
class Ising:
    fields: tuple[float, ...]
    couplings: dict[tuple[int, int], float]
    offset: float

    def energy(self, spins: tuple[int, ...] | list[int]) -> float:
        return self.offset + sum(h * z for h, z in zip(self.fields, spins)) + sum(
            j * spins[i] * spins[k] for (i, k), j in self.couplings.items()
        )


def qubo_to_ising(qubo: QUBO) -> Ising:
    # x=(1-z)/2, preserving the QUBO energy exactly.
    h = [-a / 2 for a in qubo.linear]
    couplings: dict[tuple[int, int], float] = {}
    offset = qubo.offset + sum(qubo.linear) / 2
    for (i, j), value in qubo.quadratic.items():
        couplings[(i, j)] = value / 4
        h[i] -= value / 4
        h[j] -= value / 4
        offset += value / 4
    return Ising(tuple(h), couplings, offset)

