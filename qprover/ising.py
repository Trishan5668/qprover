from dataclasses import dataclass

from qiskit.quantum_info import SparsePauliOp

from .qubo import QUBO


@dataclass(frozen=True)
class Ising:
    fields: tuple[float, ...]
    couplings: dict[tuple[int, int], float]
    offset: float

    @property
    def n(self) -> int:
        return len(self.fields)

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


def to_sparse_pauli_op(ising: Ising) -> SparsePauliOp:
    """Return the cost Hamiltonian used by QAOA (without the scalar offset)."""
    terms: list[tuple[str, float]] = []
    for index, value in enumerate(ising.fields):
        label = ["I"] * ising.n
        label[ising.n - index - 1] = "Z"
        terms.append(("".join(label), value))
    for (left, right), value in ising.couplings.items():
        label = ["I"] * ising.n
        label[ising.n - left - 1] = "Z"
        label[ising.n - right - 1] = "Z"
        terms.append(("".join(label), value))
    return SparsePauliOp.from_list(terms or [("I" * ising.n, 0.0)])
