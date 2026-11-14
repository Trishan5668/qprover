import math
import re


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("vectors must have equal, non-zero length")
    denominator = math.sqrt(sum(x * x for x in left) * sum(y * y for y in right))
    return 0.0 if denominator == 0 else sum(x * y for x, y in zip(left, right)) / denominator


def rank_premises(relevance: list[float], k: int) -> list[int]:
    if not 0 <= k <= len(relevance):
        raise ValueError("k out of range")
    return sorted(range(len(relevance)), key=lambda i: relevance[i], reverse=True)[:k]


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z_][A-Za-z0-9_']*", text.lower()))


def text_embedding(text: str, vocabulary: list[str]) -> list[float]:
    tokens = _tokens(text)
    return [float(token in tokens) for token in vocabulary]


def relevance_and_redundancy(goal: str, premises: list[str]) -> tuple[list[float], dict[tuple[int, int], float]]:
    vocabulary = sorted(_tokens(goal).union(*(map(_tokens, premises))))
    goal_vector = text_embedding(goal, vocabulary)
    vectors = [text_embedding(premise, vocabulary) for premise in premises]
    relevance = [cosine_similarity(goal_vector, vector) for vector in vectors]
    redundancy = {
        (left, right): cosine_similarity(vectors[left], vectors[right])
        for left in range(len(vectors))
        for right in range(left + 1, len(vectors))
    }
    return relevance, redundancy
