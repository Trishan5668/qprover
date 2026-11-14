from qprover.classical.baselines import exact, greedy, random_search, simulated_annealing
from qprover.classical.premise_ranker import cosine_similarity, rank_premises
from qprover.evaluate import evaluate
from qprover.lean.benchmark import load_benchmark
from qprover.quantum.embedding import choose_subgraph
from qprover.qubo import QUBO


def test_baselines_and_evaluation():
    qubo = QUBO((1.0, -2.0, 0.5), {(0, 1): 0.1}, 0.0)
    assert len(exact(qubo, 1)[0]) == 3
    assert sum(greedy(qubo, 1)[0]) == 1
    assert sum(random_search(qubo, 1, 10)[0]) == 1
    assert sum(simulated_annealing(qubo, 1, 10)[0]) == 1
    assert {item.method for item in evaluate(qubo, 1)} >= {"greedy", "quantum-simulator"}


def test_ranker_embedding_and_benchmark():
    assert cosine_similarity([1, 0], [1, 0]) == 1
    assert rank_premises([0.1, 0.8, 0.3], 2) == [1, 2]
    assert len(load_benchmark()) >= 5
    assert choose_subgraph([(0, 1), (1, 2), (2, 3)], 3) == [0, 1, 2]
