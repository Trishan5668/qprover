# qprover

`qprover` is a research prototype for Lean-verified theorem-proving experiments.
An LLM proposes premises and tactics, while a quantum sampler selects a fixed-size
premise subset as a QUBO/Ising optimization problem. **Lean 4 is the sole source of
truth**: a proof is successful only when Lean's kernel accepts it, with no `sorry`,
`admit`, or newly introduced `axiom`.

There is no known quantum speedup for theorem proving. The quantum component is an
experimental sampler/optimizer for premise selection, benchmarked against greedy,
simulated annealing, random, and exact baselines at equal candidate and wall-clock
budgets. Results, including negative results, should be reported honestly.

## Setup

```powershell
python -m pip install -e ".[dev,quantum]"
python -m pytest
python -m qprover simulate --n 20
python -m qprover budget
```

Hardware credentials are environment-only: `QISKIT_IBM_TOKEN` and optionally
`QISKIT_IBM_INSTANCE`. No token is written to disk or logs. Hardware runs require
`--confirm-hardware`, dynamically select the least-busy operational non-simulator
backend with at least 127 qubits (unless `--backend` is supplied), and use a
540-second default ledger cap (10% below the IBM Open Plan 600-second window).
The implementation assumes job mode, not sessions or batches.

The full hardware adapter is intentionally isolated from offline tests. Before a
job, a small calibration probe estimates cost; submissions are refused if the
ledger plus estimate exceeds the cap. A problem uses a connected low-degree
subgraph rather than all 127 qubits because premise selection is normally 20--40
variables and unnecessary qubits increase depth, noise, and cost. Parameters are
optimized locally before hardware execution; depth and shots are budgeted.

Lean setup for real theorem checking requires Lean 4 and Mathlib via a pinned
`lean-toolchain`/`lakefile` in the benchmark project. When Lean is absent, the
runner returns a structured `error`; it never treats unavailable Lean as success.

## Limitations

The current offline simulator is a deterministic reference sampler used to make
the pipeline testable without credentials; it is not evidence of quantum
advantage. IBM Runtime API details can vary by installed Qiskit 2.x/runtime
release, so hardware execution must be validated against the installed package
before a benchmark. Every experiment should publish proof attempts, Lean output,
energy gap, diversity, wall time, and QPU seconds.
