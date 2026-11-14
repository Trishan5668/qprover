import math


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("vectors must have equal, non-zero length")
    denominator = math.sqrt(sum(x * x for x in left) * sum(y * y for y in right))
    return 0.0 if denominator == 0 else sum(x * y for x, y in zip(left, right)) / denominator


def rank_premises(relevance: list[float], k: int) -> list[int]:
    if not 0 <= k <= len(relevance):
        raise ValueError("k out of range")
    return sorted(range(len(relevance)), key=lambda i: relevance[i], reverse=True)[:k]

