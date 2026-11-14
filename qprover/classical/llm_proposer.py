import json
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class Proposal:
    tactics: tuple[str, ...]
    premise_scores: tuple[float, ...]
    redundancy: dict[tuple[int, int], float]


class LLMProposer:
    """Offline deterministic proposer used when no endpoint is configured."""

    def propose(self, goal: str, premises: list[str]) -> Proposal:
        del goal
        scores = tuple(1.0 / (index + 1) for index in range(len(premises)))
        return Proposal(("simp", "aesop", "rfl"), scores, {})


class OpenAICompatibleProposer(LLMProposer):
    def __init__(self, endpoint: str, model: str = "local") -> None:
        self.endpoint = endpoint.rstrip("/")
        self.model = model

    def propose(self, goal: str, premises: list[str]) -> Proposal:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Return JSON with tactics (array of strings), scores (array of numbers), "
                        "and redundancy (object keyed 'i,j'). Goal: "
                        f"{goal}\nPremises:\n" + "\n".join(f"{i}: {p}" for i, p in enumerate(premises))
                    ),
                }
            ],
            "temperature": 0,
        }
        request = urllib.request.Request(
            f"{self.endpoint}/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read())
        content = body["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        redundancy: dict[tuple[int, int], float] = {
            (int(key.split(",")[0]), int(key.split(",")[1])): float(value)
            for key, value in parsed.get("redundancy", {}).items()
        }
        return Proposal(
            tuple(str(value) for value in parsed["tactics"]),
            tuple(float(value) for value in parsed["scores"]),
            redundancy,
        )
