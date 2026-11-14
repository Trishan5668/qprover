import json
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LeanResult:
    status: str
    stdout: str
    stderr: str
    duration_seconds: float
    messages: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.status == "ok"


class LeanRunner:
    def __init__(self, project_dir: Path = Path("."), timeout_seconds: float = 30.0) -> None:
        self.project_dir = project_dir
        self.timeout_seconds = timeout_seconds

    def check(self, source: str) -> LeanResult:
        if re.search(r"\b(?:sorry|admit)\b", source) or re.search(r"\baxiom\b", source):
            return LeanResult("error", "", "", 0.0, ("forbidden sorry/admit/axiom",))
        start = time.monotonic()
        try:
            result = subprocess.run(
                ["lake", "env", "lean", "--stdin"],
                input=source,
                cwd=self.project_dir,
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except FileNotFoundError:
            return LeanResult("error", "", "Lean executable not found", time.monotonic() - start, ("Lean unavailable",))
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            return LeanResult("timeout", stdout, stderr, time.monotonic() - start, ("timeout",))
        messages = tuple(line for line in (result.stdout + "\n" + result.stderr).splitlines() if line.strip())
        return LeanResult("ok" if result.returncode == 0 and not any("error:" in m for m in messages) else "error",
                          result.stdout, result.stderr, time.monotonic() - start, messages)

    def log_attempt(self, directory: Path, record: dict[str, object]) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / "proof_attempts.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
