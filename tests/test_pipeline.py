from qprover.pipeline import run_pipeline


def test_simulation_pipeline_is_lean_gated():
    attempt = run_pipeline("1 + 0 = 1", ["a", "b"], "example : True := by trivial", k=1)
    assert attempt.selected_premises
    assert attempt.result.status in {"ok", "error"}
