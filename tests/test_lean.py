from qprover.lean.runner import LeanRunner


def test_forbidden_proof_terms_are_rejected():
    result = LeanRunner().check("theorem bad : True := by sorry")
    assert result.status == "error"
    assert not result.ok

