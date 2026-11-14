import json
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class JobRecord:
    job_id: str
    timestamp: float
    usage: float
    shots: int
    circuit_depth: int


class BudgetExceeded(RuntimeError):
    pass


class BudgetManager:
    def __init__(self, ledger_path: Path = Path(".qpu_ledger.json"), cap_seconds: float = 540.0) -> None:
        self.ledger_path = ledger_path
        self.cap_seconds = cap_seconds
        self._records: list[JobRecord] = self._load()
        self.calibration_seconds: float | None = None

    def _load(self) -> list[JobRecord]:
        if not self.ledger_path.exists():
            return []
        data = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        return [JobRecord(**item) for item in data]

    @property
    def spent(self) -> float:
        return sum(record.usage for record in self._records)

    @property
    def remaining(self) -> float:
        return max(0.0, self.cap_seconds - self.spent)

    def estimate(self, shots: int, depth: int) -> float:
        if shots <= 0 or depth < 0:
            raise ValueError("shots must be positive and depth non-negative")
        if self.calibration_seconds is None:
            return max(0.1, shots * max(depth, 1) / 100_000)
        return self.calibration_seconds * shots / 1000 * max(depth, 1) / 10

    def check(self, estimated_seconds: float) -> None:
        if estimated_seconds < 0:
            raise ValueError("estimate cannot be negative")
        if self.spent + estimated_seconds > self.cap_seconds:
            raise BudgetExceeded(
                f"QPU budget exceeded: spent={self.spent:.3f}s, "
                f"estimate={estimated_seconds:.3f}s, cap={self.cap_seconds:.3f}s"
            )

    def record(self, job_id: str, usage: float, shots: int, circuit_depth: int) -> None:
        if usage < 0:
            raise ValueError("usage cannot be negative")
        record = JobRecord(job_id, time.time(), usage, shots, circuit_depth)
        self._records.append(record)
        self.ledger_path.write_text(json.dumps([r.__dict__ for r in self._records], indent=2), encoding="utf-8")
        if self.calibration_seconds is None and shots <= 1000:
            self.calibration_seconds = usage / (shots / 1000)

    def status(self) -> dict[str, float]:
        return {"spent": self.spent, "remaining": self.remaining, "cap": self.cap_seconds}
