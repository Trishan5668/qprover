import importlib.metadata
from dataclasses import dataclass
from pathlib import Path

from .classical.llm_proposer import LLMProposer, Proposal
from .classical.premise_ranker import relevance_and_redundancy
from .lean.runner import LeanResult, LeanRunner
from .qubo import build_qubo
from .quantum.qaoa import run_qaoa, top_k_premise_sets


@dataclass(frozen=True)
class ProofAttempt:
    selected_premises: tuple[int, ...]
    result: LeanResult
    attempts: int = 1


def _source(goal: str, premises: list[str], selected: tuple[int, ...], tactics: tuple[str, ...]) -> str:
    tactic = tactics[0] if tactics else "simp"
    comments = "\n".join(f"-- selected premise {index}: {premises[index]}" for index in selected)
    return f"import Mathlib\n{comments}\nexample : {goal} := by\n  {tactic}\n"


def run_pipeline(
    goal: str,
    premises: list[str],
    lean_source: str | None = None,
    k: int = 3,
    shots: int = 1024,
    seed: int = 7,
    lean_runner: LeanRunner | None = None,
    run_directory: Path | None = None,
    proposer: LLMProposer | None = None,
    top_k: int = 5,
) -> ProofAttempt:
    selected_proposer = proposer or LLMProposer()
    proposal: Proposal = selected_proposer.propose(goal, premises)
    relevance, redundancy = relevance_and_redundancy(goal, premises)
    if any(proposal.premise_scores):
        relevance = list(proposal.premise_scores)
    qubo = build_qubo(relevance, proposal.redundancy or redundancy, min(k, len(premises)))
    result = run_qaoa(qubo, shots=shots, seed=seed)
    candidates = top_k_premise_sets(result.samples, qubo, min(k, len(premises)), top_k)
    runner = lean_runner or LeanRunner()
    last_result = LeanResult("error", "", "", 0.0, ("no candidate sets",))
    for attempt_number, selected in enumerate(candidates, 1):
        selected_indices = tuple(index for index, bit in enumerate(selected) if bit)
        source = lean_source if attempt_number == 1 and lean_source is not None else _source(
            goal, premises, selected_indices, proposal.tactics
        )
        checked = runner.check(source)
        last_result = checked
        if run_directory is not None:
            versions = {}
            for package in ("qiskit", "qiskit-aer", "scipy"):
                try:
                    versions[package] = importlib.metadata.version(package)
                except importlib.metadata.PackageNotFoundError:
                    versions[package] = "unavailable"
            runner.log_attempt(
                run_directory,
                {
                    "goal": goal,
                    "premises": [premises[index] for index in selected_indices],
                    "tactics": proposal.tactics,
                    "lean_source": source,
                    "result": checked.__dict__,
                    "package_versions": versions,
                    "seed": seed,
                },
            )
        if checked.ok:
            return ProofAttempt(selected_indices, checked, attempt_number)
    fallback = candidates[0] if candidates else tuple()
    return ProofAttempt(tuple(index for index, bit in enumerate(fallback) if bit), last_result, len(candidates))
