from dataclasses import dataclass


@dataclass(frozen=True)
class Proposal:
    tactics: tuple[str, ...]
    premise_scores: tuple[float, ...]


class LLMProposer:
    """Deterministic offline proposer; an OpenAI-compatible adapter can replace it."""

    def propose(self, goal: str, premises: list[str]) -> Proposal:
        del goal
        scores = tuple(1.0 / (index + 1) for index in range(len(premises)))
        return Proposal(("simp", "aesop", "rfl"), scores)

