import os
from dataclasses import dataclass
from typing import Any


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
        if backend.num_qubits < min_qubits:
            raise HardwareConfigurationError(f"backend has fewer than {min_qubits} qubits")
        return backend
    backends = service.backends(min_num_qubits=min_qubits, operational=True, simulator=False)
    if not backends:
        raise HardwareConfigurationError("no operational IBM backend meets the qubit requirement")
    return min(backends, key=lambda b: b.status().pending_jobs)


def describe_backend(backend: Any) -> BackendInfo:
    status = backend.status()
    return BackendInfo(backend.name, backend.num_qubits, int(status.pending_jobs))


def submit_sampler_job(
    backend: Any,
    circuit: Any,
    shots: int,
    budget: Any,
    confirm_hardware: bool = False,
) -> Any:
    if not confirm_hardware:
        raise HardwareConfigurationError("hardware submission requires explicit confirmation")
    if shots > 4096:
        raise HardwareConfigurationError("shots exceed the configured default safety limit")
    depth = int(circuit.depth())
    estimate = budget.estimate(shots, depth)
    budget.check(estimate)
    try:
        from qiskit_ibm_runtime import SamplerV2
    except ImportError as exc:
        raise HardwareConfigurationError("install qiskit-ibm-runtime for hardware access") from exc
    sampler = SamplerV2(mode=backend)
    return sampler.run([circuit], shots=shots)


def connect(token: str | None = None, instance: str | None = None) -> Any:
    token = token or os.getenv("QISKIT_IBM_TOKEN")
    if not token:
        raise HardwareConfigurationError("QISKIT_IBM_TOKEN is required for hardware access")
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
    except ImportError as exc:
        raise HardwareConfigurationError("install qiskit-ibm-runtime for hardware access") from exc
    kwargs = {"token": token}
    if instance or os.getenv("QISKIT_IBM_INSTANCE"):
        kwargs["instance"] = instance or os.environ["QISKIT_IBM_INSTANCE"]
    return QiskitRuntimeService(**kwargs)
