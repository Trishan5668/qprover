from collections import defaultdict
from typing import Any


def _two_qubit_error(backend: Any, left: int, right: int) -> float:
    try:
        properties = backend.properties()
        return min(
            float(properties.gate_error("ecr", [left, right])),
            float(properties.gate_error("cz", [left, right])),
        )
    except (AttributeError, KeyError, TypeError, ValueError):
        return 0.0


def choose_subgraph(
    coupling_map: list[tuple[int, int]],
    n: int,
    backend: Any | None = None,
) -> list[int]:
    """Choose a connected low-error subgraph using backend calibration data."""
    if n < 1:
        raise ValueError("n must be positive")
    adjacency: dict[int, set[int]] = defaultdict(set)
    for left, right in coupling_map:
        adjacency[left].add(right)
        adjacency[right].add(left)
    if not adjacency:
        raise ValueError("coupling map is empty")
    best: list[int] = []
    for root in sorted(adjacency):
        selected = {root}
        while len(selected) < n:
            candidates = [
                node
                for node in adjacency
                if node not in selected and any(neighbor in selected for neighbor in adjacency[node])
            ]
            if not candidates:
                break
            selected.add(
                min(
                    candidates,
                    key=lambda node: min(
                        (_two_qubit_error(backend, node, neighbor) for neighbor in adjacency[node] if neighbor in selected),
                        default=0.0,
                    ),
                )
            )
        if len(selected) > len(best):
            best = sorted(selected)
        if len(selected) == n:
            return sorted(selected)
    if len(best) < n:
        raise ValueError(f"coupling map has no connected subgraph of size {n}")
    return best[:n]
