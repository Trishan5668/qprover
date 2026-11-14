from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkProblem:
    name: str
    goal: str
    premises: tuple[str, ...]
    expected_tactic: str


_GOALS = (
    ("add_zero", "n + 0 = n", "simp"),
    ("zero_add", "0 + n = n", "simp"),
    ("mul_one", "n * 1 = n", "simp"),
    ("one_mul", "1 * n = n", "simp"),
    ("sub_self", "n - n = 0", "simp"),
    ("and_true", "p ∧ True ↔ p", "simp"),
    ("or_false", "p ∨ False ↔ p", "simp"),
    ("not_false", "¬ False", "simp"),
    ("eq_self", "n = n", "rfl"),
    ("le_refl", "n ≤ n", "omega"),
    ("zero_le", "0 ≤ n", "omega"),
    ("succ_pos", "0 < n + 1", "omega"),
    ("add_assoc", "a + b + c = a + (b + c)", "omega"),
    ("add_comm", "a + b = b + a", "omega"),
    ("mul_zero", "n * 0 = 0", "simp"),
    ("zero_mul", "0 * n = 0", "simp"),
    ("pow_zero", "n ^ 0 = 1", "simp"),
    ("pow_one", "n ^ 1 = n", "simp"),
    ("double_neg", "¬¬p ↔ p", "simp"),
    ("imp_true", "(p → True)", "simp"),
    ("true_and", "True ∧ p ↔ p", "simp"),
    ("false_or", "False ∨ p ↔ p", "simp"),
    ("list_length_nil", "List.length ([] : List Nat) = 0", "simp"),
    ("list_append_nil", "([] : List Nat) ++ xs = xs", "simp"),
    ("list_reverse_nil", "([].reverse : List Nat) = []", "simp"),
    ("map_id", "List.map id xs = xs", "simp"),
    ("filter_true", "List.filter (fun _ : Nat => True) xs = xs", "simp"),
    ("nat_cast_zero", "(0 : Int) = 0", "rfl"),
    ("nat_cast_one", "(1 : Int) = 1", "rfl"),
    ("abs_zero", "Int.natAbs 0 = 0", "rfl"),
    ("min_self", "min n n = n", "simp"),
    ("max_self", "max n n = n", "simp"),
    ("div_one", "n / 1 = n", "simp"),
    ("mod_one", "n % 1 = 0", "simp"),
    ("finite_empty", "Set.Finite (∅ : Set Nat)", "simp"),
)


def load_benchmark() -> list[BenchmarkProblem]:
    problems = []
    for name, goal, tactic in _GOALS:
        premises = (f"Mathlib premise for {name}", "Nat.add_comm", "List.map_id", "irrelevant distractor")
        problems.append(BenchmarkProblem(name, goal, premises, tactic))
    return problems
