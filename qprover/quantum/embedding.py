def choose_subgraph(coupling_map: list[tuple[int, int]], n: int) -> list[int]:
    if n < 1:
        raise ValueError("n must be positive")
    nodes = sorted({node for edge in coupling_map for node in edge})
    if len(nodes) < n:
        raise ValueError("coupling map is too small")
    return nodes[:n]

