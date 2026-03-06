from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ShellResult:
    command: str
    returncode: int
    stdout: str
    stderr: str
    new_log_files: list[str]

    @property
    def output(self) -> str:
        return f"{self.stdout}{self.stderr}"


def _collect_log_files(repo_root: Path) -> set[Path]:
    logs_dir = repo_root / "logs"
    if not logs_dir.exists():
        return set()
    return {path.resolve() for path in logs_dir.rglob("*.log") if path.is_file()}


def _run_shell(context, command: str, timeout: Optional[int] = None) -> ShellResult:
    log_files_before = _collect_log_files(context.repo_root)
    resolved_timeout = timeout if timeout is not None else context.default_timeout
    completed = subprocess.run(
        ["bash", "-lc", command],
        cwd=context.repo_root,
        capture_output=True,
        text=True,
        timeout=resolved_timeout,
        check=False,
    )
    log_files_after = _collect_log_files(context.repo_root)
    new_log_files = sorted(
        str(path.relative_to(context.repo_root))
        for path in (log_files_after - log_files_before)
    )
    result = ShellResult(
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        new_log_files=new_log_files,
    )
    context.last_result = result
    return result


def before_all(context):
    context.repo_root = Path(__file__).resolve().parents[1]
    context.default_timeout = int(os.getenv("AIR_QUALITY_BDD_TIMEOUT", "60"))
    context.last_result = None
    context.last_referenced_log_path = None
    context.run_shell = lambda command, timeout=None: _run_shell(
        context, command, timeout=timeout
    )


def before_scenario(context, scenario):
    context.last_result = None
    context.last_referenced_log_path = None
