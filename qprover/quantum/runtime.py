import os
from dataclasses import dataclass
from typing import Any

from qiskit import QuantumCircuit, transpile

from .embedding import choose_subgraph


class HardwareConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True)
class BackendInfo:
    name: str
    num_qubits: int
    pending_jobs: int


def select_backend(service: Any, override: str | None = None, min_qubits: int = 127) -> Any:
    if override:
        backend = service.backend(override)
        if int(backend.num_qubits) < min_qubits:
            raise HardwareConfigurationError(f"backend has fewer than {min_qubits} qubits")
        return backend
    backends = service.backends(min_num_qubits=min_qubits, operational=True, simulator=False)
    if not backends:
        raise HardwareConfigurationError("no operational IBM backend meets the qubit requirement")
    return min(backends, key=lambda backend: int(backend.status().pending_jobs))


def describe_backend(backend: Any) -> BackendInfo:
    status = backend.status()
    return BackendInfo(str(backend.name), int(backend.num_qubits), int(status.pending_jobs))


def _coupling_edges(backend: Any) -> list[tuple[int, int]]:
    coupling = getattr(backend, "coupling_map", None)
    if coupling is None:
        coupling = getattr(backend, "coupling_map", None)
    edges: Any = coupling.get_edges() if coupling is not None and hasattr(coupling, "get_edges") else coupling
    if not edges:
        raise HardwareConfigurationError("backend does not expose a coupling map")
    return [(int(edge[0]), int(edge[1])) for edge in edges]


def choose_circuit_layout(backend: Any, n: int) -> list[int]:
    return choose_subgraph(_coupling_edges(backend), n, backend)


def transpile_for_hardware(
    circuit: QuantumCircuit,
    backend: Any,
    n: int,
    p: int,
    depth_limit: int = 150,
) -> tuple[QuantumCircuit, int, int]:
    """Transpile with error-aware layout and DD; lower p/n until depth fits."""
    layout = choose_circuit_layout(backend, n)
    current = circuit
    current_p = p
    current_n = n
    while True:
        compiled = transpile(
            current,
            backend=backend,
            optimization_level=3,
            initial_layout=layout[:current_n],
            seed_transpiler=7,
        )
        try:
            from qiskit.transpiler import CouplingMap, PassManager
            from qiskit.transpiler.passes import ALAPScheduleAnalysis, PadDynamicalDecoupling
            from qiskit.circuit.library import XGate

            durations = backend.target.durations() if hasattr(backend, "target") else None
            if durations is not None:
                pm = PassManager([ALAPScheduleAnalysis(durations), PadDynamicalDecoupling(durations, [XGate()])])
                compiled = pm.run(compiled)
            del CouplingMap
        except (ImportError, AttributeError, TypeError, ValueError):
            pass
        two_qubit_depth = sum(1 for instruction in compiled.data if instruction.operation.num_qubits == 2)
        if two_qubit_depth <= depth_limit or (current_p == 1 and current_n <= 1):
            return compiled, current_p, current_n
        if current_p > 1:
            current_p -= 1
        elif current_n > 1:
            current_n -= 1
            current = current.remove_final_measurements(inplace=False)
            current = current.decompose()
        else:
            return compiled, current_p, current_n


def _job_usage(job: Any) -> float:
    usage = job.usage() if callable(getattr(job, "usage", None)) else getattr(job, "usage", None)
    if usage is None and callable(getattr(job, "metrics", None)):
        usage = job.metrics()
    if isinstance(usage, (int, float)):
        return float(usage)
    if isinstance(usage, dict):
        for key in ("seconds", "qpu_seconds", "usage_seconds"):
            if key in usage:
                return float(usage[key])
    raise HardwareConfigurationError("IBM job did not expose a numeric usage duration")


def _job_id(job: Any) -> str:
    value = job.job_id() if callable(getattr(job, "job_id", None)) else getattr(job, "job_id", None)
    if value is None:
        raise HardwareConfigurationError("IBM job did not expose a job id")
    return str(value)


def submit_sampler_job(
    backend: Any,
    circuit: QuantumCircuit,
    shots: int,
    budget: Any,
    confirm_hardware: bool = False,
    job_mode: bool = True,
) -> Any:
    if not confirm_hardware:
        raise HardwareConfigurationError("hardware submission requires explicit confirmation")
    if not job_mode:
        raise HardwareConfigurationError("Open Plan execution requires job mode")
    if shots > 4096:
        raise HardwareConfigurationError("shots exceed the configured default safety limit")
    estimate = budget.estimate(shots, circuit.depth())
    budget.check(estimate)
    try:
        from qiskit_ibm_runtime import SamplerV2
    except ImportError as exc:
        raise HardwareConfigurationError("install qiskit-ibm-runtime for hardware access") from exc
    sampler = SamplerV2(mode=backend)
    job = sampler.run([circuit], shots=shots)
    job.result()
    usage = _job_usage(job)
    budget.record(_job_id(job), usage, shots, circuit.depth())
    return job


def run_probe(backend: Any, budget: Any, confirm_hardware: bool = False) -> float:
    probe = QuantumCircuit(2)
    probe.h(0)
    probe.cx(0, 1)
    probe.measure_all()
    job = submit_sampler_job(backend, probe, 1000, budget, confirm_hardware)
    usage = _job_usage(job)
    budget.calibrate(usage, 1000)
    return usage


def connect(token: str | None = None, instance: str | None = None) -> Any:
    token = token or os.getenv("QISKIT_IBM_TOKEN")
    if not token:
        raise HardwareConfigurationError("QISKIT_IBM_TOKEN is required for hardware access")
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
    except ImportError as exc:
        raise HardwareConfigurationError("install qiskit-ibm-runtime for hardware access") from exc
    kwargs: dict[str, str] = {"token": token}
    resolved_instance = instance or os.getenv("QISKIT_IBM_INSTANCE")
    if resolved_instance:
        kwargs["instance"] = resolved_instance
    return QiskitRuntimeService(**kwargs)
