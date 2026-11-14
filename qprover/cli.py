import json
from pathlib import Path

import typer

from .budget import BudgetManager
from .config import Settings
from .pipeline import run_pipeline

app = typer.Typer(no_args_is_help=True)


@app.command()
def simulate(n: int = typer.Option(20, min=1), shots: int = 1024) -> None:
    premises = [f"premise_{i}" for i in range(n)]
    source = "import Mathlib\nexample : (1 : Nat) + 0 = 1 := by simp\n"
    attempt = run_pipeline("1 + 0 = 1", premises, source, k=min(3, n), shots=shots)
    typer.echo(json.dumps({"selected_premises": attempt.selected_premises, "lean_status": attempt.result.status}))


@app.command()
def budget(ledger: Path = Path(".qpu_ledger.json"), cap: float = 540.0) -> None:
    manager = BudgetManager(ledger, cap)
    typer.echo(json.dumps(manager.status(), indent=2))


@app.command()
def run(
    confirm_hardware: bool = typer.Option(False),
    dry_run: bool = typer.Option(False),
    backend: str | None = None,
) -> None:
    settings = Settings.from_yaml()
    if dry_run:
        manager = BudgetManager(cap_seconds=settings.budget_cap_seconds)
        typer.echo(json.dumps({"dry_run": True, "estimated_seconds": manager.estimate(settings.shots, 20)}))
        return
    if settings.hardware_confirm_required and not confirm_hardware:
        raise typer.BadParameter("--confirm-hardware is required for hardware runs")
    manager = BudgetManager(cap_seconds=settings.budget_cap_seconds)
    manager.check(manager.estimate(settings.shots, settings.depth_limit))
    from .quantum.runtime import connect, select_backend
    selected = select_backend(connect(), backend, settings.min_qubits)
    status = selected.status()
    typer.echo(f"backend={selected.name} qubits={selected.num_qubits} queue={status.pending_jobs}")


@app.command()
def benchmark(dry_run: bool = typer.Option(False)) -> None:
    del dry_run
    simulate(20, 1024)


if __name__ == "__main__":
    app()
