from dataclasses import dataclass

from .classical.llm_proposer import LLMProposer
from .classical.premise_ranker import rank_premises
from .lean.runner import LeanResult, LeanRunner
from .qubo import build_qubo
from .quantum.qaoa import run_qaoa


@dataclass(frozen=True)
class ProofAttempt:
    selected_premises: tuple[int, ...]
    result: LeanResult


def run_pipeline(
    goal: str,
    premises: list[str],
    lean_source: str,
    k: int = 3,
    shots: int = 1024,
    seed: int = 7,
    lean_runner: LeanRunner | None = None,
) -> ProofAttempt:
    proposer = LLMProposer()
    proposal = proposer.propose(goal, premises)
    relevance = list(proposal.premise_scores)
    qubo = build_qubo(relevance, {}, min(k, len(premises)))
    result = run_qaoa(qubo, shots=shots, seed=seed)
    bits = min(result.samples, key=qubo.energy)
    selected = tuple(i for i, bit in enumerate(bits) if bit)
    if len(selected) != min(k, len(premises)):
        selected = tuple(rank_premises(relevance, min(k, len(premises))))
    runner = lean_runner or LeanRunner()
    checked = runner.check(lean_source)
    return ProofAttempt(selected, checked)
