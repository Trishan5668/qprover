from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkProblem:
    name: str
    goal: str
    premises: tuple[str, ...]
    expected_tactic: str


def load_benchmark() -> list[BenchmarkProblem]:
    return [
        BenchmarkProblem("add_zero", "n + 0 = n", ("Nat.add_zero n",), "simpa"),
        BenchmarkProblem("mul_one", "n * 1 = n", ("Nat.mul_one n",), "simpa"),
        BenchmarkProblem("zero_add", "0 + n = n", ("Nat.zero_add n",), "simpa"),
        BenchmarkProblem("eq_refl", "n = n", (), "rfl"),
        BenchmarkProblem("double_neg", "¬¬p → p", (), "intro h; by_contra hn; exact hn (h ?_)"),
    ]
