import json
from datetime import datetime, timezone
from pathlib import Path

import typer

from .budget import BudgetManager
from .config import Settings
from .pipeline import run_pipeline
from .qubo import build_qubo
from .quantum.qaoa import run_qaoa

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
    from .quantum.runtime import connect, run_probe, select_backend, submit_sampler_job, transpile_for_hardware
    from .quantum.qaoa import run_qaoa

    run_directory = Path("runs") / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_directory.mkdir(parents=True, exist_ok=True)
    selected = select_backend(connect(), backend, settings.min_qubits)
    probe_usage = run_probe(selected, manager, confirm_hardware)
    qubo = build_qubo([1.0 / (i + 1) for i in range(settings.problem_qubits)], {}, settings.problem_qubits // 2)
    trained = run_qaoa(qubo, settings.p, min(settings.shots, 4096), settings.seed)
    trained_circuit = trained.circuit.copy()
    trained_circuit.measure_all()
    compiled, used_p, used_n = transpile_for_hardware(
        trained_circuit, selected, settings.problem_qubits, settings.p, settings.depth_limit
    )
    job = submit_sampler_job(selected, compiled, settings.shots, manager, confirm_hardware, settings.job_mode)
    job_identifier = job.job_id() if callable(getattr(job, "job_id", None)) else job.job_id
    report = {
        "backend": str(selected.name),
        "qubits": int(selected.num_qubits),
        "queue": int(selected.status().pending_jobs),
        "probe_qpu_seconds": probe_usage,
        "trained_p": used_p,
        "trained_n": used_n,
        "depth": int(compiled.depth()),
        "job_id": str(job_identifier),
        "budget": manager.status(),
    }
    (run_directory / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    typer.echo(json.dumps(report, indent=2))


@app.command()
def benchmark(dry_run: bool = typer.Option(False)) -> None:
    settings = Settings.from_yaml()
    manager = BudgetManager(cap_seconds=settings.budget_cap_seconds)
    qubo = build_qubo([1.0 / (i + 1) for i in range(settings.problem_qubits)], {}, settings.problem_qubits // 2)
    result = run_qaoa(qubo, settings.p, min(settings.shots, 1024), settings.seed)
    report = {
        "dry_run": dry_run,
        "simulator_samples": len(result.samples),
        "estimated_qpu_seconds": manager.estimate(settings.shots, result.depth),
        "depth": result.depth,
    }
    typer.echo(json.dumps(report, indent=2))


if __name__ == "__main__":
    app()
