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
    updated_data_files: list[str]
    timed_out: bool
    timeout_seconds: Optional[int]

    @property
    def output(self) -> str:
        return f"{self.stdout}{self.stderr}"


def _collect_log_files(repo_root: Path) -> set[Path]:
    logs_dir = repo_root / "logs"
    if not logs_dir.exists():
        return set()
    return {path.resolve() for path in logs_dir.rglob("*.log") if path.is_file()}


def _normalize_output(raw_output) -> str:
    if raw_output is None:
        return ""
    if isinstance(raw_output, bytes):
        return raw_output.decode("utf-8", errors="ignore")
    return str(raw_output)


def _snapshot_data_files(repo_root: Path) -> dict[str, int]:
    data_dir = repo_root / "data"
    if not data_dir.exists():
        return {}
    snapshot = {}
    for path in data_dir.rglob("*"):
        if not path.is_file():
            continue
        rel_path = path.relative_to(repo_root).as_posix()
        snapshot[rel_path] = path.stat().st_mtime_ns
    return snapshot


def _run_shell(context, command: str, timeout: Optional[int] = None) -> ShellResult:
    log_files_before = _collect_log_files(context.repo_root)
    data_snapshot_before = _snapshot_data_files(context.repo_root)
    resolved_timeout = timeout if timeout is not None else context.default_timeout
    timed_out = False
    timeout_seconds = None

    try:
        completed = subprocess.run(
            ["bash", "-lc", command],
            cwd=context.repo_root,
            capture_output=True,
            text=True,
            timeout=resolved_timeout,
            check=False,
        )
        returncode = completed.returncode
        stdout = _normalize_output(completed.stdout)
        stderr = _normalize_output(completed.stderr)
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        timeout_seconds = resolved_timeout
        returncode = 124
        stdout = _normalize_output(exc.stdout)
        stderr = _normalize_output(exc.stderr)
        timeout_message = (
            f"\n[behave] Command timed out after {resolved_timeout}s: {command}\n"
        )
        stderr = f"{stderr}{timeout_message}"

    log_files_after = _collect_log_files(context.repo_root)
    new_log_files = sorted(
        str(path.relative_to(context.repo_root))
        for path in (log_files_after - log_files_before)
    )
    data_snapshot_after = _snapshot_data_files(context.repo_root)
    updated_data_files = sorted(
        rel_path
        for rel_path, updated_mtime_ns in data_snapshot_after.items()
        if rel_path not in data_snapshot_before
        or updated_mtime_ns > data_snapshot_before[rel_path]
    )
    result = ShellResult(
        command=command,
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
        new_log_files=new_log_files,
        updated_data_files=updated_data_files,
        timed_out=timed_out,
        timeout_seconds=timeout_seconds,
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
