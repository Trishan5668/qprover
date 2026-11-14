from collections import Counter
from typing import Any

from qiskit import QuantumCircuit, transpile


def execute_counts(
    circuit: QuantumCircuit,
    shots: int = 1024,
    seed: int = 7,
    noise_model: Any | None = None,
) -> Counter[str]:
    """Execute a measured circuit with Aer without hiding simulator failures."""
    try:
        from qiskit_aer import AerSimulator
    except ImportError as exc:
        raise RuntimeError("qiskit-aer is required for local simulation") from exc
    simulator = AerSimulator(noise_model=noise_model)
    compiled = transpile(circuit, simulator, optimization_level=3, seed_transpiler=seed)
    result = simulator.run(compiled, shots=shots, seed_simulator=seed).result()
    return Counter(result.get_counts())
